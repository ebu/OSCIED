#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**********************************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/ebu/OSCIED

import logging, mongomock, os, pymongo, uuid
from celery import states
#from celery import current_app
#from celery.task.control import inspect
from celery.task.control import revoke
#from celery.events.state import state
from kitchen.text.converters import to_bytes
from random import randint
import Publisher, Transform
from Callback import Callback
from Media import Media
from PublishTask import PublishTask
from Storage import Storage
from TransformProfile import TransformProfile, ENCODERS_NAMES
from TransformTask import TransformTask
from User import User
import pyutils.py_juju as juju
from pyutils.pyutils import UUID_ZERO
from pyutils.py_datetime import datetime_now
from pyutils.py_serialization import object2json
from pyutils.py_validation import valid_uuid
from pyutils.py_unicode import csv_reader


class Orchestra(object):

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Constructor >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    def __init__(self, config):
        self.config = config
        if self.is_mock:
            self._db = mongomock.Connection().orchestra
        else:
            self._db = pymongo.Connection(config.mongo_admin_connection)[u'orchestra']
        self.root_user = User(u'root', u'oscied', u'root@oscied.org', self.config.root_secret, True, _id=UUID_ZERO)
        self.nodes_user = User(u'nodes', u'oscied', u'nodes@oscied.org', self.config.nodes_secret, False, _id=UUID_ZERO)

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Properties >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    @property
    def is_mock(self):
        return not self.config.mongo_admin_connection

    @property
    def about(self):
        return (u"Orchestra : EBU's OSCIED Orchestrator by David Fischer 2012-2013")

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Functions >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    def flush_db(self):
        self._db.drop_collection(u'users')
        self._db.drop_collection(u'medias')
        self._db.drop_collection(u'transform_profiles')
        self._db.drop_collection(u'transform_tasks')
        self._db.drop_collection(u'publish_tasks')
        logging.info(u"Orchestra database's collections dropped !")

    # ------------------------------------------------------------------------------------------------------------------

    def save_user(self, user, hash_secret):
        user.is_valid(True)
        if self.get_user({u'mail': user.mail, u'_id': {u'$ne': user._id}}, {u'_id': 1}):
            raise ValueError(to_bytes(u'The email address {0} is already used by another user.'.format(user.mail)))
        if hash_secret:
            user.hash_secret()
        self._db.users.save(user.__dict__)

    def get_user(self, specs, fields=None, secret=None):
        entity = self._db.users.find_one(specs, fields)
        if not entity:
            return None
        user = User.from_json(object2json(entity, False))
        return user if secret is None or user.verify_secret(secret) else None

    def delete_user(self, user):
        # FIXME issue #16 (https://github.com/ebu/OSCIED/issues/16)
        # entity = self.get_user({'_id': user_id}, {'secret': 0})
        # if not entity:
        #     raise IndexError(to_bytes(u'No user with id {0}.'.format(id)))
        # self._db.users.remove({'_id': entity._id})
        # return User.from_json(object2json(entity, False))
        if valid_uuid(user, none_allowed=False):
            user = self.get_user({u'_id': user}, {u'secret': 0})
        user.is_valid(True)
        self._db.users.remove({u'_id': user._id})

    def get_users(self, specs=None, fields=None):
        users = []
        for entity in list(self._db.users.find(specs, fields)):
            users.append(User.from_json(object2json(entity, False)))
        return users

    def get_users_count(self, specs=None):
        return self._db.users.find(specs, {u'_id': 1}).count()

    # ------------------------------------------------------------------------------------------------------------------

    def save_media(self, media):
        media.is_valid(True)
        if self.get_media({u'uri': media.uri, u'_id': {u'$ne': media._id}}, {u'_id': 1}):
            raise ValueError(to_bytes(u'The media uri {0} is already used by another media.'.format(media.uri)))
        if not media.get_metadata(u'title'):
            raise ValueError(to_bytes(u'Title key is required in media metadata.'))
        if media.status != u'DELETED':
            if self.is_mock:
                size = randint(10*1024*1024, 10*1024*1024*1024)
                duration = u'%02d:%02d:%02d' % (randint(0, 2), randint(0, 59), randint(0, 59))
            else:
                size, duration = Storage.add_media(self.config, media)
        else:
            size, duration = (0, 0)
        media.add_metadata(u'size', size, True)
        if duration:
            media.add_metadata(u'duration', duration, True)
        media.add_metadata(u'add_date', datetime_now(), True)
        self._db.medias.save(media.__dict__)

    def get_media(self, specs, fields=None, load_fields=False):
        entity = self._db.medias.find_one(specs, fields)
        if not entity:
            return None
        media = Media.from_json(object2json(entity, False))
        if load_fields:
            media.load_fields(self.get_user({u'_id': media.user_id}, {u'secret': 0}),
                              self.get_media({u'_id': media.parent_id}))
        return media

    def delete_media(self, media):
        if valid_uuid(media, none_allowed=False):
            media = self.get_media({u'_id': media})
        media.is_valid(True)
        task = self.get_transform_task({u'media_in_id': media._id}, append_result=True)
        if task and (task.status in states.UNREADY_STATES or task.status == u'PROGRESS'):
            raise ValueError(to_bytes(u'Cannot delete the media, it is actually in use by transformation task with id '
                             '{0} and status {1}.'.format(task._id, task.status)))
        task = self.get_publish_task({u'media_id': media._id}, append_result=True)
        if task and (task.status in states.UNREADY_STATES or task.status == u'PROGRESS'):
            raise ValueError(to_bytes(u'Cannot delete the media, it is actually in use by publication task with id {0} '
                             'and status {1}.'.format(task._id, task.status)))
        media.status = u'DELETED'
        self.save_media(media)
        #self._db.medias.remove({'_id': media._id})
        Storage.delete_media(self.config, media)

    def get_medias(self, specs=None, fields=None, load_fields=False):
        medias = []
        for entity in list(self._db.medias.find(specs, fields)):
            media = Media.from_json(object2json(entity, False))
            if load_fields:
                media.load_fields(self.get_user({u'_id': media.user_id}, {u'secret': 0}),
                                  self.get_media({u'_id': media.parent_id}))
            medias.append(media)
        return medias

    def get_medias_count(self, specs=None):
        return self._db.medias.find(specs, {u'_id': 1}).count()

    # ------------------------------------------------------------------------------------------------------------------

    def add_environment(self, name, type, region, access_key, secret_key, control_bucket):
        return juju.add_environment(self.config.juju_config_file, name, type, region, access_key, secret_key,
                                    control_bucket, self.config.charms_release)

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
            raise ValueError(to_bytes(u'No environment with name {0}.'.format(name)))

    # ------------------------------------------------------------------------------------------------------------------

    def get_transform_profile_encoders(self):
        return ENCODERS_NAMES

    def save_transform_profile(self, profile):
        profile.is_valid(True)
        # FIXME exact matching !
        if self.get_transform_profile({u'title': profile.title, u'_id': {u'$ne': profile._id}}, {u'_id': 1}):
            raise ValueError(to_bytes(u'Duplicate transformation profile title {0}.'.format(profile.title)))
        self._db.transform_profiles.save(profile.__dict__)

    def get_transform_profile(self, specs, fields=None):
        entity = self._db.transform_profiles.find_one(specs, fields)
        if not entity:
            return None
        return TransformProfile.from_json(object2json(entity, False))

    def delete_transform_profile(self, profile):
        if valid_uuid(profile, none_allowed=False):
            profile = self.get_profile({u'_id': profile})
        profile.is_valid(True)
        self._db.transform_profiles.remove({u'_id': profile._id})

    def get_transform_profiles(self, specs=None, fields=None):
        profiles = []
        for entity in list(self._db.transform_profiles.find(specs, fields)):
            profiles.append(TransformProfile.from_json(object2json(entity, False)))
        return profiles

    def get_transform_profiles_count(self, specs=None):
        return self._db.transform_profiles.find(specs, {u'_id': 1}).count()

    # ------------------------------------------------------------------------------------------------------------------

    def add_or_deploy_transform_units(self, environment, num_units):
        environments, default = self.get_environments()
        same_environment = (environment == default)
        config = juju.load_unit_config(self.config.transform_config)
        config[u'rabbit_queues'] = u'transform_{0}'.format(environment)
        if not same_environment:
            raise NotImplementedError(to_bytes(u'Unable to launch transformation units into non-default environment '
                                      '{0} (default is {1}).'.format(environment, default)))
            config[u'mongo_connection'] = self.config.mongo_nodes_connection
            config[u'rabbit_connection'] = self.config.rabbit_connection
            # FIXME copy storage configuration, first method
            config[u'storage_address'] = self.config.storage_address
            config[u'storage_fstype'] = self.config.storage_fstype
            config[u'storage_mountpoint'] = self.config.storage_mountpoint
            config[u'storage_options'] = self.config.storage_options
        juju.save_unit_config(self.config.charms_config, self.config.transform_service, config)
        juju.add_or_deploy_units(environment, self.config.transform_service, num_units,
                                 config=self.config.charms_config, local=True, release=self.config.charms_release,
                                 repository=self.config.charms_repository)
        if same_environment:
            try:
                try:
                    juju.add_relation(environment, self.config.orchestra_service, self.config.transform_service,
                                      u'transform', u'transform')
                except RuntimeError as e:
                    raise NotImplementedError(to_bytes(u'Orchestra service must be available and running on default '
                                              'environment {0}, reason : {1}'.format(default, e)))
                try:
                    juju.add_relation(environment, self.config.storage_service, self.config.transform_service)
                except RuntimeError as e:
                    raise NotImplementedError(to_bytes(u'Storage service must be available and running on default '
                                              'environment {0}, reason : {1}'.format(default, e)))
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

            FIXME implement more robust resources listing and removing, sometimes juju fail during a call
            (e.g. remove_transform_units with num_units=10) and then some machines are not terminated.
            Maybe implement a garbage collector method callable by user when he want to terminate useless machines ?
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

    # ------------------------------------------------------------------------------------------------------------------

    def get_transform_queues(self):
        return self.config.transform_queues

    def launch_transform_task(self, user_id, media_in_id, profile_id, filename, metadata, queue, callback_url):
        user = self.get_user({u'_id': user_id}, {u'secret': 0})
        if not user:
            raise IndexError(to_bytes(u'No user with id {0}.'.format(user_id)))
        media_in = self.get_media({u'_id': media_in_id})
        if not media_in:  # FIXME maybe a media access control here
            raise IndexError(to_bytes(u'No media with id {0}.'.format(media_in_id)))
        profile = self.get_transform_profile({u'_id': profile_id})
        if not profile:  # FIXME maybe a profile access control here
            raise IndexError(to_bytes(u'No transformation profile with id {0}.'.format(profile_id)))
        if not queue in self.config.transform_queues:
            raise IndexError(to_bytes(u'No transformation queue with name {0}.'.format(queue)))
        media_out = Media(user_id, media_in_id, None, None, filename, metadata, u'PENDING')
        media_out.uri = self.config.storage_medias_uri(media_out)
        TransformTask.validate_task(media_in, profile, media_out)
        self.save_media(media_out)  # Save pending output media
        # FIXME create a one-time password to avoid fixed secret authentication ...
        callback = Callback(self.config.api_url + callback_url, u'node', self.config.nodes_secret)
        if self.is_mock:
            result_id = unicode(uuid.uuid4())
        else:
            result = Transform.transform_task.apply_async(
                args=(object2json(media_in, False), object2json(media_out, False), object2json(profile, False),
                      object2json(callback, False)), queue=queue)
            result_id = result.id
        if not result_id:
            raise ValueError(to_bytes(u'Unable to transmit task to workers of queue {0}.'.format(queue)))
        logging.info(u'New transformation task {0} -> queue {1}.'.format(result_id, queue))
        task = TransformTask(user._id, media_in._id, media_out._id, profile._id, _id=result_id)
        task.add_statistic(u'add_date', datetime_now(), True)
        self._db.transform_tasks.save(task.__dict__)
        return result_id

    def get_transform_task(self, specs, fields=None, load_fields=False, append_result=True):
        entity = self._db.transform_tasks.find_one(specs, fields)
        if not entity:
            return None
        task = TransformTask.from_json(object2json(entity, False))
        if load_fields:
            task.load_fields(self.get_user({u'_id': task.user_id}, {u'secret': 0}),
                             self.get_media({u'_id': task.media_in_id}),
                             self.get_media({u'_id': task.media_out_id}),
                             self.get_transform_profile({u'_id': task.profile_id}))
        if append_result:
            task.append_async_result()
        return task

    def revoke_transform_task(self, task, terminate=False, remove=False, delete_media=False):
        u"""
        This do not delete tasks from tasks database (if remove=False) but set revoked attribute in tasks database and
        broadcast revoke request to transformation units with Celery. If the task is actually running it will be
        cancelled if terminated = True. The output media will be deleted if corresponding argument, delete_media = True.
        """
        # FIXME verify that no pending tasks needs the media that will be created by the task !
        if valid_uuid(task, none_allowed=False):
            task = self.get_transform_task({u'_id': task})
        task.is_valid(True)
        if task.status == states.REVOKED:
            raise ValueError(to_bytes(u'Transformation task {0} is already revoked !'.format(task._id)))
        if task.status in states.READY_STATES:
            raise ValueError(to_bytes(u'Cannot revoke a transformation task with status {0}.'.format(task.status)))
        task.status = states.REVOKED
        if self.is_mock:
            pass  # FIXME TODO
        else:
            revoke(task._id, terminate=terminate)
        self._db.transform_tasks.save(task.__dict__)
        if delete_media and valid_uuid(task.media_out_id, none_allowed=False):
            self.delete_media(task.media_out_id)
        if remove:
            self._db.transform_tasks.remove({u'_id': task._id})

    def get_transform_tasks(self, specs=None, fields=None, load_fields=False, append_result=True):
        tasks = []
        for entity in list(self._db.transform_tasks.find(specs, fields)):
            task = TransformTask.from_json(object2json(entity, False))
            if load_fields:
                task.load_fields(self.get_user({u'_id': task.user_id}, {u'secret': 0}),
                                 self.get_media({u'_id': task.media_in_id}),
                                 self.get_media({u'_id': task.media_out_id}),
                                 self.get_transform_profile({u'_id': task.profile_id}))
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
        return self._db.transform_tasks.find(specs, {u'_id': 1}).count()

    # ------------------------------------------------------------------------------------------------------------------

    def get_publisher_queues(self):
        return self.config.publisher_queues

    def launch_publish_task(self, user_id, media_id, queue, callback_url):
        user = self.get_user({u'_id': user_id}, {u'secret': 0})
        if not user:
            raise IndexError(to_bytes(u'No user with id {0}.'.format(user_id)))
        media = self.get_media({u'_id': media_id})
        if not media:  # FIXME maybe a media access control here
            raise IndexError(to_bytes(u'No media with id {0}.'.format(media_id)))
        if not queue in self.config.publisher_queues:
            raise IndexError(to_bytes(u'No publication queue with name {0}.'.format(queue)))
        if media.status != u'READY':
            raise NotImplementedError(to_bytes(u'Cannot launch the task, input media status is {0}.'.format(
                                      media.status)))
        other = self.get_publish_task({u'media_id': media._id})
        if other and other.status not in states.READY_STATES and other.status != states.REVOKED:
            raise NotImplementedError(to_bytes(u'Cannot launch the task, input media will be published by another task '
                                      'with id {0}.'.format(other._id)))
        # FIXME create a one-time password to avoid fixed secret authentication ...
        callback = Callback(self.config.api_url + callback_url, u'node', self.config.nodes_secret)
        if self.is_mock:
            result_id = unicode(uuid.uuid4())
        else:
            result = Publisher.publish_task.apply_async(
                args=(object2json(media, False), object2json(callback, False)), queue=queue)
            result_id = result.id
        if not result_id:
            raise ValueError(to_bytes(u'Unable to transmit task to workers of queue {0}.'.format(queue)))
        logging.info(u'New publication task {0} -> queue {1}.'.format(result_id, queue))
        task = PublishTask(user._id, media._id, _id=result_id)
        task.add_statistic(u'add_date', datetime_now(), True)
        self._db.publish_tasks.save(task.__dict__)
        return result_id

    def get_publish_task(self, specs, fields=None, load_fields=False, append_result=True):
        entity = self._db.publish_tasks.find_one(specs, fields)
        if not entity:
            return None
        task = PublishTask.from_json(object2json(entity, False))
        if load_fields:
            task.load_fields(self.get_user({u'_id': task.user_id}, {u'secret': 0}),
                             self.get_media({u'_id': task.media_id}))
        if append_result:
            task.append_async_result()
        return task

    def update_publish_task(self, task):
        raise NotImplementedError(to_bytes(u'maybe in a near future.'))

    def revoke_publish_task(self, task, callback_url, terminate=False, remove=False):
        u"""
        This do not delete tasks from tasks database (if remove=False) but set revoked attribute in tasks database and
        broadcast revoke request to publication units with celery. If the task is actually running it will be cancelled
        if terminated = True. In any case, the output media will be deleted (task running or successfully finished).
        """
        if valid_uuid(task, none_allowed=False):
            task = self.get_publish_task({u'_id': task})
        task.is_valid(True)
        if task.status in (states.REVOKED, 'REVOKING'):
            raise ValueError(to_bytes(u'Publication task {0} is already revoked !'.format(task._id)))
        if task.status in states.READY_STATES:
            raise ValueError(to_bytes(u'Cannot revoke a publication task with status {0}.'.format(task.status)))
        if self.is_mock:
            pass  # FIXME TODO
            task.status = states.REVOKED
        else:
            revoke(task._id, terminate=terminate)
            if task.status == states.SUCCESS:
                # Send revoke task to the worker that published the media
                callback = Callback(self.config.api_url + callback_url, u'node', self.config.nodes_secret)
                queue = task.get_hostname()
                result = Publisher.revoke_publish_task.apply_async(
                    args=(task.publish_uri, object2json(callback, False)), queue=queue)
                if not result.id:
                    raise ValueError(to_bytes(u'Unable to transmit task to queue {0}.'.format(queue)))
                logging.info(u'New revoke publication task {0} -> queue {1}.'.format(result.id, queue))
                task.revoke_task_id = result.id
                task.status = 'REVOKING'
            else:
                task.status = states.REVOKED
        self._db.publish_tasks.save(task.__dict__)
        if remove:
            self._db.publish_tasks.remove({u'_id': task._id})

    def get_publish_tasks(self, specs=None, fields=None, load_fields=False, append_result=True):
        tasks = []
        for entity in list(self._db.publish_tasks.find(specs, fields)):
            task = PublishTask.from_json(object2json(entity, False))
            if load_fields:
                task.load_fields(self.get_user({u'_id': task.user_id}, {u'secret': 0}),
                                 self.get_media({u'_id': task.media_id}))
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
        return self._db.publish_tasks.find(specs, {u'_id': 1}).count()

    # ------------------------------------------------------------------------------------------------------------------

    def transform_callback(self, task_id, status):
        task = self.get_transform_task({u'_id': task_id})
        if not task:
            raise IndexError(to_bytes(u'No transformation task with id {0}.'.format(task_id)))
        media_out = self.get_media({u'_id': task.media_out_id})
        if not media_out:
            raise IndexError(to_bytes(u'Unable to find output media with id {0}.'.format(task.media_out_id)))
        if status == states.SUCCESS:
            media_out.status = u'READY'
            self.save_media(media_out)
            logging.info(u'{0} Media {1} is now READY'.format(task_id, media_out.filename))
        else:
            self.delete_media(media_out)
            task.add_statistic(u'error_details', status.replace(u'\n', u'\\n'), True)
            self._db.transform_tasks.save(task.__dict__)
            logging.info(u'{0} Error: {1}'.format(task_id, status))
            logging.info(u'{0} Media {1} is now deleted'.format(task_id, media_out.filename))

    def publish_callback(self, task_id, publish_uri, status):
        task = self.get_publish_task({u'_id': task_id})
        if not task:
            raise IndexError(to_bytes(u'No publication task with id {0}.'.format(task_id)))
        media = self.get_media({u'_id': task.media_id})
        if not media:
            raise IndexError(to_bytes(u'Unable to find media with id {0}.'.format(task.media_id)))
        if status == states.SUCCESS:
            media.status = u'PUBLISHED'
            if not media.public_uris:
                media.public_uris = {}
            task.publish_uri = publish_uri
            media.public_uris[task_id] = publish_uri
            self._db.publish_tasks.save(task.__dict__)
            self.save_media(media)
            logging.info(u'{0} Media {1} is now PUBLISHED'.format(task_id, media.filename))
        else:
            task.add_statistic('error_details', status.replace(u'\n', u'\\n'), True)
            self._db.publish_tasks.save(task.__dict__)
            logging.info(u'{0} Error: {1}'.format(task_id, status))
            logging.info(u'{0} Media {1} is not modified'.format(task_id, media.filename))

    def publish_revoke_callback(self, task_id, publish_uri, status):
        task = self.get_publish_task({u'revoke_task_id': task_id})
        if not task:
            raise IndexError(to_bytes(u'No publication task with revoke_task_id {0}.'.format(task_id)))
        media = self.get_media({u'_id': task.media_id})
        if not media:
            raise IndexError(to_bytes(u'Unable to find media with id {0}.'.format(task.media_id)))
        if status == states.SUCCESS:
            del media.public_uris[task._id]
            media.status = u'READY' if len(media.public_uris) == 0 else u'PUBLISHED'
            task.status = states.REVOKED
            self.save_media(media)
            self._db.publish_tasks.save(task.__dict__)
            logging.info(u'{0} Media {1} is now {2}'.format(task_id, media.filename, media.status))
        else:
            task.add_statistic('revoke_error_details', status.replace(u'\n', u'\\n'), True)
            self._db.publish_tasks.save(task.__dict__)
            logging.info(u'{0} Error: {1}'.format(task_id, status))
            logging.info(u'{0} Media {1} is not modified'.format(task_id, media.filename))


def get_test_orchestra(api_init_csv_directory):
    from OrchestraConfig import ORCHESTRA_CONFIG_TEST
    orchestra = Orchestra(ORCHESTRA_CONFIG_TEST)
    reader = csv_reader(os.path.join(api_init_csv_directory, u'users.csv'))
    for first_name, last_name, email, secret, admin_platform in reader:
        user = User(first_name, last_name, email, secret, admin_platform)
        print(u'Adding user {0}'.format(user.name))
        orchestra.save_user(user, hash_secret=True)
    users = orchestra.get_users()
    i, reader = 0, csv_reader(os.path.join(api_init_csv_directory, u'medias.csv'))
    for uri, filename, title in reader:
        media = Media(users[i]._id, None, uri, None, filename, {u'title': title}, u'READY')
        print(u'Adding media {0}'.format(media.metadata[u'title']))
        orchestra.save_media(media)
        i = (i + 1) % len(users)
    reader = csv_reader(os.path.join(api_init_csv_directory, u'tprofiles.csv'))
    for title, description, encoder_name, encoder_string in reader:
        profile = TransformProfile(None, title, description, encoder_name, encoder_string)
        print(u'Adding transformation profile {0}'.format(profile.title))
        orchestra.save_transform_profile(profile)
    reader = csv_reader(os.path.join(api_init_csv_directory, u'ttasks.csv'))
    for user_email, in_filename, profile_title, out_filename, out_title, queue in reader:
        user = orchestra.get_user({u'mail': user_email})
        if not user:
            raise IndexError(to_bytes(u'No user with e-mail address {0}.'.format(user_email)))
        media_in = orchestra.get_media({u'filename': in_filename})
        if not media_in:
            raise IndexError(to_bytes(u'No media with filename {0}.'.format(in_filename)))
        profile = orchestra.get_transform_profile({u'title': profile_title})
        if not profile:
            raise IndexError(to_bytes(u'No transformation profile with title {0}.'.format(profile_title)))
        print(u'Launching transformation task {0} with profile {1}'.format(media_in.metadata[u'title'], profile.title))
        metadata = {u'title': out_title}
        orchestra.launch_transform_task(user._id, media_in._id, profile._id, out_filename, metadata, queue,
                                        u'/transform/callback')
    return orchestra


# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pyutils.py_unicode import configure_unicode
    configure_unicode()
    orchestra = get_test_orchestra(u'../../config/api')
    print(u'They are {0} registered users.'.format(len(orchestra.get_users())))
    print(u'They are {0} available medias.'.format(len(orchestra.get_medias())))
    print(u'They are {0} available transformation profiles.'.format(len(orchestra.get_transform_profiles())))
    print(u'They are {0} launched transformation tasks.'.format(len(orchestra.get_transform_tasks())))
