#! /usr/bin/env python
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012 OSCIED Team. All rights reserved.
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
# Retrieved from:
#   svn co https://claire-et-david.dyndns.org/prog/OSCIED

import logging
import pymongo
import Publisher
import Transform
from Storage import Storage
from celery import states
#from celery import current_app
#from celery.task.control import inspect
from celery.task.control import revoke
#from celery.events.state import state
from Callback import Callback
from Media import Media
from PublishJob import PublishJob
from TransformProfile import TransformProfile
from TransformJob import TransformJob
from User import User
from Utilities import object2json, datetime_now, UUID_ZERO, valid_uuid


class Orchestra(object):

    def __init__(self, config):
        self.config = config
        self._db = pymongo.Connection(config.mongo_connection)['orchestra']
        self.root_user = User(UUID_ZERO, 'root', 'oscied', 'root@oscied.org',
                              self.config.root_secret, True)
        self.nodes_user = User(UUID_ZERO, 'nodes', 'oscied', 'nodes@oscied.org',
                               self.config.nodes_secret, False)

    # ----------------------------------------------------------------------------------------------

    def flush_db(self):
        self._db.drop_collection('users')
        self._db.drop_collection('medias')
        self._db.drop_collection('transform_profiles')
        self._db.drop_collection('transform_jobs')
        self._db.drop_collection('publish_jobs')
        self._db.drop_collection('unpublish_jobs')
        logging.info("Orchestra database's collections dropped !")

    # ----------------------------------------------------------------------------------------------

    def save_user(self, user):
        user.is_valid(True)
        if self.get_user({'mail': user.mail, '_id': {'$ne': user._id}}, {'_id': 1}):
            raise ValueError('The email address ' + user.mail + ' is already used by another user.')
        self._db.users.save(user.__dict__)

    def get_user(self, specs, fields=None):
        entity = self._db.users.find_one(specs, fields)
        if not entity:
            return None
        return User.load(object2json(entity, False))

    def delete_user(self, user):
        if valid_uuid(user, False):
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
        if valid_uuid(media, False):
            media = self.get_media({'_id': media})
        media.is_valid(True)
        job = self.get_transform_job({'media_in_id': media._id}, append_result=True)
        if job and (job.status in states.UNREADY_STATES or job.status == 'PROGRESS'):
            raise ValueError('Cannot delete the media, it is actually in use by transform ' +
                             'job with id ' + job._id + ' and status ' + job.status + '.')
        job = self.get_publish_job({'media_id': media._id}, append_result=True)
        if job and (job.status in states.UNREADY_STATES or job.status == 'PROGRESS'):
            raise ValueError('Cannot delete the media, it is actually in use by publish ' +
                             'job with id ' + job._id + ' and status ' + job.status + '.')
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
        if valid_uuid(profile, False):
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

    def get_transform_queues(self):
        return self.config.transform_queues

    def launch_transform_job(self, user_id, media_in_id, profile_id, virtual_filename, metadata,
                             queue, callback_url):
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
        if not media_in.status in('READY', 'PUBLISHED',):
            raise NotImplementedError('Cannot launch the job, input media status is ' +
                                      media_in.status + '.')
        media_out = Media(None, user_id, media_in_id, None, None, virtual_filename, metadata,
                          'PENDING')
        media_out.uri = Storage.media_uri(self.config, media_out, True)
        self.save_media(media_out)  # Save pending output media
        # FIXME create a one-time password to avoid fixed secret authentication ...
        callback = Callback(self.config.api_url + callback_url, 'node', self.config.nodes_secret)
        result = Transform.transform_job.apply_async(
            args=(
                object2json(user, False), object2json(media_in, False),
                object2json(media_out, False), object2json(profile, False),
                object2json(callback, False)),
            queue=queue)
        if not result.id:
            raise ValueError('Unable to transmit job to workers of queue ' + queue + '.')
        logging.info('New transform job ' + result.id + ' launched.')
        job = TransformJob(result.id, user._id, media_in._id, media_out._id, profile._id)
        job.add_statistic('add_date', datetime_now(), True)
        self._db.transform_jobs.save(job.__dict__)
        return result.id

    def get_transform_job(self, specs, fields=None, load_fields=False, append_result=True):
        entity = self._db.transform_jobs.find_one(specs, fields)
        if not entity:
            return None
        job = TransformJob.load(object2json(entity, False))
        if load_fields:
            job.load_fields(self.get_user({'_id': job.user_id}, {'secret': 0}),
                            self.get_media({'_id': job.media_in_id}),
                            self.get_media({'_id': job.media_out_id}),
                            self.get_transform_profile({'_id': job.profile_id}))
        if append_result:
            job.append_async_result()
        return job

    def update_transform_job(self, job):
        raise NotImplementedError('maybe in a near future.')

    def revoke_transform_job(self, job, terminate=False, remove=False, delete_media=False):
        """ This do not delete jobs from jobs database (if remove=False) but set revoked attribute
        in jobs database and broadcast revoke request to transform units with Celery. If the job is
        actually running it will be cancelled if terminated = True. The output media will be deleted
        if corresponding argument, delete_media = True. """
        # FIXME verify that no pending jobs needs the media that will be created by the job !
        if valid_uuid(job, False):
            job = self.get_transform_job({'_id': job})
        job.is_valid(True)
        if job.revoked:
            raise ValueError('Transform job ' + job._id + ' is already revoked !')
        if job.status in states.READY_STATES:
            raise ValueError('Cannot revoke a transform job with status ' + job.status + '.')
        job.revoked = True
        revoke(job._id, terminate=terminate)
        self._db.transform_jobs.save(job.__dict__)
        if delete_media and valid_uuid(job.media_out_id, False):
            self.delete_media(job.media_out_id)
        if remove:
            self._db.transform_jobs.remove({'_id': job._id})

    def get_transform_jobs(self, specs=None, fields=None, load_fields=False, append_result=True):
        jobs = []
        for entity in list(self._db.transform_jobs.find(specs, fields)):
            job = TransformJob.load(object2json(entity, False))
            if load_fields:
                job.load_fields(self.get_user({'_id': job.user_id}, {'secret': 0}),
                                self.get_media({'_id': job.media_in_id}),
                                self.get_media({'_id': job.media_out_id}),
                                self.get_transform_profile({'_id': job.profile_id}))
            if append_result:
                job.append_async_result()
            jobs.append(job)
        return jobs
        # FIXME this is celery's way to do that:
        #for task in state.itertasks():
        #    print task
        #for entity in entities:
        #    job = get_transform_job_helper(entity._id)

    def get_transform_jobs_count(self, specs=None):
        return self._db.transform_jobs.find(specs, {'_id': 1}).count()

    # ----------------------------------------------------------------------------------------------

    def get_publisher_queues(self):
        return self.config.publisher_queues

    def launch_publish_job(self, user_id, media_id, queue, callback_url):
        user = self.get_user({'_id': user_id}, {'secret': 0})
        if not user:
            raise IndexError('No user with id ' + user_id + '.')
        media = self.get_media({'_id': media_id})
        if not media:  # FIXME maybe a media access control here
            raise IndexError('No media with id ' + media_id + '.')
        if not queue in self.config.publisher_queues:
            raise IndexError('No publisher queue with name ' + queue + '.')
        if not media.status in ('READY',):
            raise NotImplementedError('Cannot launch the job, input media status is ' +
                                      media.status + '.')
        other = self.get_publish_job({'media_id': media._id})
        if other and other.status not in states.READY_STATES and not other.revoked:
            raise NotImplementedError('Cannot launch the job, input media will be published by '
                + 'another job with id ' + other._id + '.')
        # FIXME create a one-time password to avoid fixed secret authentication ...
        callback = Callback(self.config.api_url + callback_url, 'node', self.config.nodes_secret)
        result = Publisher.publish_job.apply_async(
            args=(
                object2json(user, False), object2json(media, False), object2json(callback, False)),
            queue=queue)
        if not result.id:
            raise ValueError('Unable to transmit job to workers of queue ' + queue + '.')
        logging.info('New publish job ' + result.id + ' launched.')
        job = PublishJob(result.id, user._id, media._id, None)
        job.add_statistic('add_date', datetime_now(), True)
        self._db.publish_jobs.save(job.__dict__)
        return result.id

    def get_publish_job(self, specs, fields=None, load_fields=False, append_result=True):
        entity = self._db.publish_jobs.find_one(specs, fields)
        if not entity:
            return None
        job = PublishJob.load(object2json(entity, False))
        if load_fields:
            job.load_fields(self.get_user({'_id': job.user_id}, {'secret': 0}),
                            self.get_media({'_id': job.media_id}))
        if append_result:
            job.append_async_result()
        return job

    def update_publish_job(self, job):
        raise NotImplementedError('maybe in a near future.')

    def revoke_publish_job(self, job, terminate=False, remove=False):
        """ This do not delete jobs from jobs database (if remove=False) but set revoked attribute
        in tasks database and broadcast revoke request to publisher units with celery. If the job is
        actually running it will be cancelled if terminated = True. The output media will be deleted
        """
        if valid_uuid(job, False):
            job = self.get_publish_job({'_id': job})
        job.is_valid(True)
        if job.revoked:
            raise ValueError('Publish job ' + job._id + ' is already revoked !')
        if job.status in states.READY_STATES:
            raise ValueError('Cannot revoke a publish job with status ' + job.status + '.')
        job.revoked = True
        revoke(job._id, terminate=terminate)
        self._db.publish_jobs.save(job.__dict__)
        if remove:
            self._db.publish_jobs.remove({'_id': job._id})

    def get_publish_jobs(self, specs=None, fields=None, load_fields=False, append_result=True):
        jobs = []
        for entity in list(self._db.publish_jobs.find(specs, fields)):
            job = PublishJob.load(object2json(entity, False))
            if load_fields:
                job.load_fields(self.get_user({'_id': job.user_id}, {'secret': 0}),
                                self.get_media({'_id': job.media_id}))
            if append_result:
                job.append_async_result()
            jobs.append(job)
        return jobs
        # FIXME this is celery's way to do that:
        #for task in state.itertasks():
        #    print task
        #for entity in entities:
        #    job = get_publish_job_helper(entity._id)

    def get_publish_jobs_count(self, specs=None):
        return self._db.publish_jobs.find(specs, {'_id': 1}).count()

    # ----------------------------------------------------------------------------------------------

    def transform_callback(self, job_id, status):
        job = self.get_transform_job({'_id': job_id})
        if not job:
            raise IndexError('No transform job with id ' + job_id + '.')
        media_out = self.get_media({'_id': job.media_out_id})
        if not media_out:
            raise IndexError('Unable to find output media with id ' + job.media_out_id + '.')
        if status == 'SUCCESS':
            media_out.status = 'READY'
            self.save_media(media_out)
            logging.info('%s Media %s is now READY' % (job_id, media_out.virtual_filename))
        else:
            self.delete_media(media_out)
            job.add_statistic('error_details', status.replace('\n', '\\n'), True)
            self._db.transform_jobs.save(job.__dict__)
            logging.info('%s Error: %s' % (job_id, status))
            logging.info('%s Media %s is now deleted' % (job_id, media_out.virtual_filename))

    def publish_callback(self, job_id, publish_uri, status):
        job = self.get_publish_job({'_id': job_id})
        if not job:
            raise IndexError('No publish job with id ' + job_id + '.')
        media = self.get_media({'_id': job.media_id})
        if not media:
            raise IndexError('Unable to find media with id ' + job.media_id + '.')
        if status == 'SUCCESS':
            media.status = 'PUBLISHED'
            if not media.public_uris:
                media.public_uris = {}
            job.publish_uri = publish_uri
            media.public_uris[job_id] = publish_uri
            self._db.publish_jobs.save(job.__dict__)
            self.save_media(media)
            logging.info('%s Media %s is now PUBLISHED' % (job_id, media.virtual_filename))
        else:
            job.add_statistic('error_details', status.replace('\n', '\\n'), True)
            self._db.publish_jobs.save(job.__dict__)
            logging.info('%s Error: %s' % (job_id, status))
            logging.info('%s Media %s is not modified' % (job_id, media.virtual_filename))

