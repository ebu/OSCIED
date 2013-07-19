#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/EBU-TI/OSCIED

import logging, pymongo
from celery import states
#from celery import current_app
#from celery.task.control import inspect
from celery.task.control import revoke
#from celery.events.state import state
import Publisher, Transform
from Callback import Callback
from Media import Media
from PublishTask import PublishTask
from Storage import Storage
from TransformProfile import TransformProfile, ENCODERS_NAMES
from TransformTask import TransformTask
from User import User
import pyutils.juju as juju
from pyutils.pyutils import object2json, datetime_now, UUID_ZERO, valid_uuid


class Orchestra(object):

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Constructor >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    def __init__(self, config):
        self.config = config
        self._db = pymongo.Connection(config.mongo_admin_connection)['orchestra']
        self.root_user = User(UUID_ZERO, 'root', 'oscied', 'root@oscied.org',
                              self.config.root_secret, True)
        self.nodes_user = User(UUID_ZERO, 'nodes', 'oscied', 'nodes@oscied.org',
                               self.config.nodes_secret, False)

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Properties >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    @property
    def about(self):
        return ('Orchestra : EBU\'s OSCIED Orchestrator by David Fischer 2012-2013')

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Functions >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    def flush_db(self):
        self._db.drop_collection('users')
        self._db.drop_collection('medias')
        self._db.drop_collection('transform_profiles')
        self._db.drop_collection('transform_tasks')
        self._db.drop_collection('publish_tasks')
        self._db.drop_collection('unpublish_tasks')
        logging.info("Orchestra database's collections dropped !")

    # ----------------------------------------------------------------------------------------------

    def save_user(self, user, hash_secret):
        user.is_valid(True)
        if self.get_user({'mail': user.mail, '_id': {'$ne': user._id}}, {'_id': 1}):
            raise ValueError('The email address ' + user.mail + ' is already used by another user.')
        if hash_secret:
            user.hash_secret()
        self._db.users.save(user.__dict__)

    def get_user(self, specs, fields=None, secret=None):
        entity = self._db.users.find_one(specs, fields)
        if not entity:
            return None
        user = User.load(object2json(entity, False))
        return user if secret is None or user.verify_secret(secret) else None

    def delete_user(self, user):
        # FIXME issue #16 (https://github.com/ebu/OSCIED/issues/16)
        # entity = self.get_user({'_id': user_id}, {'secret': 0})
        # if not entity:
        #     raise IndexError('No user with id ' + id + '.')
        # self._db.users.remove({'_id': entity._id})
        # return User.load(object2json(entity, False))
        if valid_uuid(user, none_allowed=False):
            user = self.get_user({'_id': user}, {'secret': 0})
        user.is_valid(True)
        self._db.users.remove({'_id': user._id})

    def get_users(self, specs=None, fields=None):
        users = []
        for entity in list(self._db.users.find(specs, fields)):
            users.append(User.load(object2json(entity, False)))
        return users

    def get_users_count(self, specs=None):
        return self._db.users.find(specs, {'_id': 1}).count()

    # ----------------------------------------------------------------------------------------------

    def save_media(self, media):
        media.is_valid(True)
        if self.get_media({'uri': media.uri, '_id': {'$ne': media._id}}, {'_id': 1}):
            raise ValueError('The media uri ' + media.uri + ' is already used by another media.')
        if not media.get_metadata('title'):
            raise ValueError('Title key is required in media metadata.')
        if media.status not in ('DELETED'):
            size, duration = Storage.add_media(self.config, media)
        else:
            size, duration = (0, 0)
        media.add_metadata('size', size, True)
        if duration:
            media.add_metadata('duration', duration, True)
        media.add_metadata('add_date', datetime_now(), True)
        self._db.medias.save(media.__dict__)

    def get_media(self, specs, fields=None, load_fields=False):
        entity = self._db.medias.find_one(specs, fields)
        if not entity:
            return None
        media = Media.load(object2json(entity, False))
        if load_fields:
            media.load_fields(self.get_user({'_id': media.user_id}, {'secret': 0}),
                              self.get_media({'_id': media.parent_id}))
        return media

    def delete_media(self, media):
        if valid_uuid(media, none_allowed=False):
            media = self.get_media({'_id': media})
        media.is_valid(True)
        task = self.get_transform_task({'media_in_id': media._id}, append_result=True)
        if task and (task.status in states.UNREADY_STATES or task.status == 'PROGRESS'):
            raise ValueError('Cannot delete the media, it is actually in use by transform ' +
                             'task with id ' + task._id + ' and status ' + task.status + '.')
        task = self.get_publish_task({'media_id': media._id}, append_result=True)
        if task and (task.status in states.UNREADY_STATES or task.status == 'PROGRESS'):
            raise ValueError('Cannot delete the media, it is actually in use by publish ' +
                             'task with id ' + task._id + ' and status ' + task.status + '.')
        media.status = 'DELETED'
        self.save_media(media)
        #self._db.medias.remove({'_id': media._id})
        Storage.delete_media(self.config, media)

    def get_medias(self, specs=None, fields=None, load_fields=False):
        medias = []
        for entity in list(self._db.medias.find(specs, fields)):
            media = Media.load(object2json(entity, False))
            if load_fields:
                media.load_fields(self.get_user({'_id': media.user_id}, {'secret': 0}),
                                  self.get_media({'_id': media.parent_id}))
            medias.append(media)
        return medias

    def get_medias_count(self, specs=None):
        return self._db.medias.find(specs, {'_id': 1}).count()

    # ----------------------------------------------------------------------------------------------

    def add_environment(self, name, type, region, access_key, secret_key, control_bucket):
        return juju.add_environment(self.config.juju_config_file, name, type, region, access_key,
                                    secret_key, control_bucket, self.config.charms_release)

    def delete_environment(self, name, remove=False):
        u"""
        .. warning:: TODO test & debug of environment methods, especially delete !
        """
        return juju.destroy_environment(self.config.juju_config_file, name, remove)

    def get_environments(self):
        return juju.get_environments(self.config.juju_config_file, get_status=False)

    def get_environment(self, name):
        (environments, default) = self.get_environments()
        if name not in environments:
            raise ValueError('No environment with name %s.' % name)

    # ----------------------------------------------------------------------------------------------

    def get_transform_profile_encoders(self):
        return ENCODERS_NAMES

    def save_transform_profile(self, profile):
        profile.is_valid(True)
        if self.get_transform_profile(
                {'title': profile.title, '_id': {'$ne': profile._id}}, {'_id': 1}):
            raise ValueError('Duplicate transform profile title ' + profile.title + '.')
        self._db.transform_profiles.save(profile.__dict__)

    def get_transform_profile(self, specs, fields=None):
        entity = self._db.transform_profiles.find_one(specs, fields)
        if not entity:
            return None
        return TransformProfile.load(object2json(entity, False))

    def delete_transform_profile(self, profile):
        if valid_uuid(profile, none_allowed=False):
            profile = self.get_profile({'_id': profile})
        profile.is_valid(True)
        self._db.transform_profiles.remove({'_id': profile._id})

    def get_transform_profiles(self, specs=None, fields=None):
        profiles = []
        for entity in list(self._db.transform_profiles.find(specs, fields)):
            profiles.append(TransformProfile.load(object2json(entity, False)))
        return profiles

    def get_transform_profiles_count(self, specs=None):
        return self._db.transform_profiles.find(specs, {'_id': 1}).count()

    # ----------------------------------------------------------------------------------------------

    def add_or_deploy_transform_units(self, environment, num_units):
        environments, default = self.get_environments()
        same_environment = (environment == default)
        config = juju.load_unit_config(self.config.transform_config)
        config['rabbit_queues'] = 'transform_%s' % environment
        if not same_environment:
            raise NotImplementedError('Unable to launch transform units into non-default '
                                      'environment %s (default is %s).' % (environment, default))
            config['mongo_connection'] = self.config.mongo_nodes_connection
            config['rabbit_connection'] = self.config.rabbit_connection
            # FIXME copy storage configuration, first method
            config['storage_address'] = self.config.storage_address
            config['storage_fstype'] = self.config.storage_fstype
            config['storage_mountpoint'] = self.config.storage_mountpoint
            config['storage_options'] = self.config.storage_options
        juju.save_unit_config(self.config.charms_config, self.config.transform_service, config)
        juju.add_or_deploy_units(environment, self.config.transform_service, num_units,
                                 config=self.config.charms_config, local=True,
                                 release=self.config.charms_release,
                                 repository=self.config.charms_repository)
        if same_environment:
            try:
                try:
                    juju.add_relation(environment, self.config.orchestra_service,
                                      self.config.transform_service, 'transform', 'transform')
                except RuntimeError as e:
                    raise NotImplementedError('Orchestra service must be available and running on '
                                              'default environment %s, reason : %s', (default, e))
                try:
                    juju.add_relation(environment, self.config.storage_service,
                                      self.config.transform_service)
                except RuntimeError as e:
                    raise NotImplementedError('Storage service must be available and running on '
                                              'default environment %s, reason : %s', (default, e))
            except NotImplementedError:
                juju.destroy_service(environment, self.config.transform_service)
                raise

    def get_transform_unit(self, environment, number):
        return juju.get_unit(environment, self.config.transform_service, number)

    def get_transform_units(self, environment):
        return juju.get_units(environment, self.config.transform_service)

    def get_transform_units_count(self, environment):
        return juju.get_units_count(environment, self.config.transform_service)

    def remove_transform_unit(self, environment, number, terminate):
        juju.remove_unit(environment, self.config.transform_service, number, terminate)
        if self.get_transform_units_count(environment) == 0:
            return juju.destroy_service(environment, self.config.transform_service, fail=False)

    def remove_transform_units(self, environment, num_units, terminate):
        u"""

        .. warning::

            FIXME implement more robust resources listing and removing, sometimes juju fail during a
            call (e.g. remove_transform_units with num_units=10) and then some machines are not
            terminated. Maybe implement a garbage collector method calleable by user when he want to
            terminate useless machines ?
        """
        units = self.get_transform_units(environment)
        numbers = []
        for unit_number in units.iterkeys():
            num_units -= 1
            if num_units < 0:
                break
            juju.remove_unit(environment, self.config.transform_service, unit_number, terminate)
            numbers.append(unit_number)
        if self.get_transform_units_count(environment) == 0:
            juju.destroy_service(environment, self.config.transform_service, fail=False)
        return numbers

    # ----------------------------------------------------------------------------------------------

    def get_transform_queues(self):
        return self.config.transform_queues

    def launch_transform_task(self, user_id, media_in_id, profile_id, filename, metadata, queue,
                              callback_url):
        user = self.get_user({'_id': user_id}, {'secret': 0})
        if not user:
            raise IndexError('No user with id ' + user_id + '.')
        media_in = self.get_media({'_id': media_in_id})
        if not media_in:  # FIXME maybe a media access control here
            raise IndexError('No media with id ' + media_in_id + '.')
        profile = self.get_transform_profile({'_id': profile_id})
        if not profile:  # FIXME maybe a profile access control here
            raise IndexError('No profile with id ' + profile_id + '.')
        if not queue in self.config.transform_queues:
            raise IndexError('No transform queue with name ' + queue + '.')
        media_out = Media(None, user_id, media_in_id, None, None, filename, metadata, 'PENDING')
        media_out.uri = self.config.storage_medias_uri(media_out)
        TransformTask.validate_task(media_in, profile, media_out)
        self.save_media(media_out)  # Save pending output media
        # FIXME create a one-time password to avoid fixed secret authentication ...
        callback = Callback(self.config.api_url + callback_url, 'node', self.config.nodes_secret)
        result = Transform.transform_task.apply_async(
            args=(object2json(user,      False), object2json(media_in, False),
                  object2json(media_out, False), object2json(profile,  False),
                  object2json(callback,  False)),
            queue=queue)
        if not result.id:
            raise ValueError('Unable to transmit task to workers of queue ' + queue + '.')
        logging.info('New transform task ' + result.id + ' launched.')
        task = TransformTask(result.id, user._id, media_in._id, media_out._id, profile._id)
        task.add_statistic('add_date', datetime_now(), True)
        self._db.transform_tasks.save(task.__dict__)
        return result.id

    def get_transform_task(self, specs, fields=None, load_fields=False, append_result=True):
        entity = self._db.transform_tasks.find_one(specs, fields)
        if not entity:
            return None
        task = TransformTask.load(object2json(entity, False))
        if load_fields:
            task.load_fields(self.get_user({'_id': task.user_id}, {'secret': 0}),
                             self.get_media({'_id': task.media_in_id}),
                             self.get_media({'_id': task.media_out_id}),
                             self.get_transform_profile({'_id': task.profile_id}))
        if append_result:
            task.append_async_result()
        return task

    def revoke_transform_task(self, task, terminate=False, remove=False, delete_media=False):
        """ This do not delete tasks from tasks database (if remove=False) but set revoked attribute
        in tasks database and broadcast revoke request to transform units with Celery. If the task
        is actually running it will be cancelled if terminated = True. The output media will be
        deleted if corresponding argument, delete_media = True. """
        # FIXME verify that no pending tasks needs the media that will be created by the task !
        if valid_uuid(task, none_allowed=False):
            task = self.get_transform_task({'_id': task})
        task.is_valid(True)
        if task.revoked:
            raise ValueError('Transform task ' + task._id + ' is already revoked !')
        if task.status in states.READY_STATES:
            raise ValueError('Cannot revoke a transform task with status ' + task.status + '.')
        task.revoked = True
        revoke(task._id, terminate=terminate)
        self._db.transform_tasks.save(task.__dict__)
        if delete_media and valid_uuid(task.media_out_id, none_allowed=False):
            self.delete_media(task.media_out_id)
        if remove:
            self._db.transform_tasks.remove({'_id': task._id})

    def get_transform_tasks(self, specs=None, fields=None, load_fields=False, append_result=True):
        tasks = []
        for entity in list(self._db.transform_tasks.find(specs, fields)):
            task = TransformTask.load(object2json(entity, False))
            if load_fields:
                task.load_fields(self.get_user({'_id': task.user_id}, {'secret': 0}),
                                 self.get_media({'_id': task.media_in_id}),
                                 self.get_media({'_id': task.media_out_id}),
                                 self.get_transform_profile({'_id': task.profile_id}))
            if append_result:
                task.append_async_result()
            tasks.append(task)
        return tasks
        # FIXME this is celery's way to do that:
        #for task in state.itertasks():
        #    print task
        #for entity in entities:
        #    task = get_transform_task_helper(entity._id)

    def get_transform_tasks_count(self, specs=None):
        return self._db.transform_tasks.find(specs, {'_id': 1}).count()

    # ----------------------------------------------------------------------------------------------

    def get_publisher_queues(self):
        return self.config.publisher_queues

    def launch_publish_task(self, user_id, media_id, queue, callback_url):
        user = self.get_user({'_id': user_id}, {'secret': 0})
        if not user:
            raise IndexError('No user with id ' + user_id + '.')
        media = self.get_media({'_id': media_id})
        if not media:  # FIXME maybe a media access control here
            raise IndexError('No media with id ' + media_id + '.')
        if not queue in self.config.publisher_queues:
            raise IndexError('No publisher queue with name ' + queue + '.')
        if not media.status in ('READY',):
            raise NotImplementedError('Cannot launch the task, input media status is ' +
                                      media.status + '.')
        other = self.get_publish_task({'media_id': media._id})
        if other and other.status not in states.READY_STATES and not other.revoked:
            raise NotImplementedError('Cannot launch the task, input media will be published by '
                                      + 'another task with id ' + other._id + '.')
        # FIXME create a one-time password to avoid fixed secret authentication ...
        callback = Callback(self.config.api_url + callback_url, 'node', self.config.nodes_secret)
        result = Publisher.publish_task.apply_async(
            args=(object2json(user, False), object2json(media, False),
                  object2json(callback, False)),
            queue=queue)
        if not result.id:
            raise ValueError('Unable to transmit task to workers of queue ' + queue + '.')
        logging.info('New publish task ' + result.id + ' launched.')
        task = PublishTask(result.id, user._id, media._id, None)
        task.add_statistic('add_date', datetime_now(), True)
        self._db.publish_tasks.save(task.__dict__)
        return result.id

    def get_publish_task(self, specs, fields=None, load_fields=False, append_result=True):
        entity = self._db.publish_tasks.find_one(specs, fields)
        if not entity:
            return None
        task = PublishTask.load(object2json(entity, False))
        if load_fields:
            task.load_fields(self.get_user({'_id': task.user_id}, {'secret': 0}),
                            self.get_media({'_id': task.media_id}))
        if append_result:
            task.append_async_result()
        return task

    def update_publish_task(self, task):
        raise NotImplementedError('maybe in a near future.')

    def revoke_publish_task(self, task, terminate=False, remove=False):
        """ This do not delete tasks from tasks database (if remove=False) but set revoked attribute
        in tasks database and broadcast revoke request to publisher units with celery. If the task
        is actually running it will be cancelled if terminated = True. The output media will be
        deleted
        """
        if valid_uuid(task, none_allowed=False):
            task = self.get_publish_task({'_id': task})
        task.is_valid(True)
        if task.revoked:
            raise ValueError('Publish task ' + task._id + ' is already revoked !')
        if task.status in states.READY_STATES:
            raise ValueError('Cannot revoke a publish task with status ' + task.status + '.')
        task.revoked = True
        revoke(task._id, terminate=terminate)
        self._db.publish_tasks.save(task.__dict__)
        if remove:
            self._db.publish_tasks.remove({'_id': task._id})

    def get_publish_tasks(self, specs=None, fields=None, load_fields=False, append_result=True):
        tasks = []
        for entity in list(self._db.publish_tasks.find(specs, fields)):
            task = PublishTask.load(object2json(entity, False))
            if load_fields:
                task.load_fields(self.get_user({'_id': task.user_id}, {'secret': 0}),
                                 self.get_media({'_id': task.media_id}))
            if append_result:
                task.append_async_result()
            tasks.append(task)
        return tasks
        # FIXME this is celery's way to do that:
        #for task in state.itertasks():
        #    print task
        #for entity in entities:
        #    task = get_publish_task_helper(entity._id)

    def get_publish_tasks_count(self, specs=None):
        return self._db.publish_tasks.find(specs, {'_id': 1}).count()

    # ----------------------------------------------------------------------------------------------

    def transform_callback(self, task_id, status):
        task = self.get_transform_task({'_id': task_id})
        if not task:
            raise IndexError('No transform task with id ' + task_id + '.')
        media_out = self.get_media({'_id': task.media_out_id})
        if not media_out:
            raise IndexError('Unable to find output media with id ' + task.media_out_id + '.')
        if status == 'SUCCESS':
            media_out.status = 'READY'
            self.save_media(media_out)
            logging.info('%s Media %s is now READY' % (task_id, media_out.filename))
        else:
            self.delete_media(media_out)
            task.add_statistic('error_details', status.replace('\n', '\\n'), True)
            self._db.transform_tasks.save(task.__dict__)
            logging.info('%s Error: %s' % (task_id, status))
            logging.info('%s Media %s is now deleted' % (task_id, media_out.filename))

    def publish_callback(self, task_id, publish_uri, status):
        task = self.get_publish_task({'_id': task_id})
        if not task:
            raise IndexError('No publish task with id ' + task_id + '.')
        media = self.get_media({'_id': task.media_id})
        if not media:
            raise IndexError('Unable to find media with id ' + task.media_id + '.')
        if status == 'SUCCESS':
            media.status = 'PUBLISHED'
            if not media.public_uris:
                media.public_uris = {}
            task.publish_uri = publish_uri
            media.public_uris[task_id] = publish_uri
            self._db.publish_tasks.save(task.__dict__)
            self.save_media(media)
            logging.info('%s Media %s is now PUBLISHED' % (task_id, media.filename))
        else:
            task.add_statistic('error_details', status.replace('\n', '\\n'), True)
            self._db.publish_tasks.save(task.__dict__)
            logging.info('%s Error: %s' % (task_id, status))
            logging.info('%s Media %s is not modified' % (task_id, media.filename))
