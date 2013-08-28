#!/usr/bin/env python
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

import logging, mongomock, os, pymongo, re, smtplib, uuid
from celery import states
#from celery import current_app
#from celery.task.control import inspect
from celery.task.control import revoke
#from celery.events.state import state
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from kitchen.text.converters import to_bytes
from random import randint
from requests import get, patch, post, delete
import PublisherWorker, TransformWorker
from oscied_config_test import ORCHESTRA_CONFIG_TEST
from oscied_models import Media, User, TransformProfile, PublishTask, TransformTask, ENCODERS_NAMES
from oscied_util import Callback, Storage
import pyutils.py_juju as juju
from pyutils.pyutils import UUID_ZERO
from pyutils.py_datetime import datetime_now
from pyutils.py_flask import map_exceptions
from pyutils.py_juju import get_unit_path, juju_do
from pyutils.py_serialization import dict2object, object2dict, object2json
from pyutils.py_unicode import csv_reader
from pyutils.py_subprocess import rsync, ssh
from pyutils.py_validation import valid_uuid

# FIXME use mongodb uniqueness constraints (e.g. user mail, profile title)

class OsciedCRUDMapper(object):

    def __init__(self, api_client, method=u'', cls=None, id_prefix=u'id', environment=False):
        self.api_client = api_client
        self.method = method
        self.cls = cls
        self.id_prefix = id_prefix
        self.environment = environment

    def get_url(self, index=None, extra=None):
        environment = u'environment/{0}'.format(self.api_client.environment) if self.environment else u''
        index = u'{0}/{1}'.format(self.id_prefix, index) if index else None
        return u'/'.join(filter(None, [self.api_client.api_url, self.method, environment, index, extra]))

    def __len__(self):
        return self.api_client.do_request(get, self.get_url(extra=u'count'))

    def __getitem__(self, index):
        response_dict = self.api_client.do_request(get, self.get_url(index))
        return response_dict if self.cls is None else dict2object(self.cls, response_dict, inspect_constructor=True)

    def __setitem__(self, index, value):
        return self.api_client.do_request(patch, self.get_url(index), data=object2json(value, include_properties=True))

    def __delitem__(self, index):
        return self.api_client.do_request(delete, self.get_url(index))

    def __contains__(self, value):
        if hasattr(value, '_id'):
            value = value._id
        try:
            return self.api_client.do_request(get, self.get_url(value))
        except:
            return False
        return True

    def add(self, *args, **kwargs):
        if not(bool(args) ^ bool(kwargs)):
            raise ValueError(to_bytes(u'You must set args OR kwargs.'))
        if args and len(args) != 1:
            raise ValueError(to_bytes(u'args should contain only 1 value.'))
        value = args[0] if args else kwargs
        response = self.api_client.do_request(post, self.get_url(), data=object2json(value, include_properties=False))
        instance = dict2object(self.cls, response, inspect_constructor=True) if self.cls else response
        # Recover user's secret
        if isinstance(instance, User):
            instance.secret = value.secret if args else kwargs[u'secret']
        return instance

    def list(self, head=False):
        values = []
        response_dict = self.api_client.do_request(get, self.get_url(extra=(u'HEAD' if head else None)))
        if self.cls is None:
            return response_dict
        for value_dict in response_dict:
            values.append(dict2object(self.cls, value_dict, inspect_constructor=True))
        return values


# ----------------------------------------------------------------------------------------------------------------------

class OrchestraAPIClient(object):

    def __init__(self, hostname, port=5000, api_unit=u'oscied-orchestra/0', api_local_config=u'local_config.pkl',
                 auth=None, id_rsa='~/.ssh/id_rsa', environment='default', timeout=10.0):
        self.api_url = u'{0}:{1}'.format(hostname, port)
        self.api_unit = api_unit
        self.api_local_config = api_local_config
        self.auth = auth
        self.id_rsa = os.path.abspath(os.path.expanduser(id_rsa))
        self.environment = environment
        self.timeout = timeout
        self.storage_path = self.storage_address = self.storage_mountpoint = None
        self.users = OsciedCRUDMapper(self, 'user', User)
        self.medias = OsciedCRUDMapper(self, 'media', Media)
        self.environments = OsciedCRUDMapper(self, 'environment', None, 'name')
        self.transform_profiles = OsciedCRUDMapper(self, 'transform/profile', TransformProfile)
        self.transform_units = OsciedCRUDMapper(self, 'transform/unit', None, 'number', True)
        self.transform_tasks = OsciedCRUDMapper(self, 'transform/task', TransformTask)
        # FIXME api_transform_unit_number_get, api_transform_unit_number_delete ...

    # Miscellaneous methods of the API ---------------------------------------------------------------------------------

    @property
    def about(self):
        return self.do_request(get, self.api_url)

    def flush(self):
        return self.do_request(post, u'{0}/flush'.format(self.api_url))

    def login(self, mail, secret, update_auth=True):
        user_dict = self.do_request(get, u'{0}/user/login'.format(self.api_url), (mail, secret))
        user = dict2object(User, user_dict, inspect_constructor=True)
        if update_auth:
            # Recover user's secret
            user.secret = secret
            self.auth = user
        return user

    def login_or_add(self, user, add_auth):
        try:
            return self.login(user.mail, user.secret)
        except:
            self.auth = add_auth
            self.auth = self.users.add(user)
            return self.auth

    @property
    def encoders(self):
        return self.do_request(get, u'{0}/transform/profile/encoder'.format(self.api_url))

    @property
    def transform_queues(self):
        return self.do_request(get, u'{0}/transform/queue'.format(self.api_url))

    @property
    def publisher_queues(self):
        return self.do_request(get, u'{0}/publisher/queue'.format(self.api_url))

    # ------------------------------------------------------------------------------------------------------------------

    def do_request(self, verb, resource, auth=None, data=None):
        u"""Execute a method of the API."""
        headers = {u'Content-type': u'application/json', u'Accept': u'application/json'}
        auth = auth or self.auth
        auth = (auth.mail, auth.secret) if isinstance(auth, User) else auth
        url = u'http://{0}'.format(resource)
        return map_exceptions(verb(url, auth=auth, data=data, headers=headers, timeout=self.timeout).json())

    # More complex methods not directly related to the API -------------------------------------------------------------

    def get_unit_local_config(self, service, number, local_config=u'local_config.pkl', option=None):
        u"""Parse local_config.pkl of a actually running charm instance !"""
        # Example : sS'storage_address' p29 S'ip-10-245-189-174.ec2.internal' p30
        # FIXME use test vector (OSCIED note on lastpass) to unit-test get_unit_local_config
        value = juju_do(u'ssh', environment=self.environment, options=[
            u'{0}/{1}'.format(service, number), u'sudo cat {0}'.format(get_unit_path(service, number, local_config))])
        if not option:
            return value
        try:
            return re.findall(ur".*S'{0}' p[0-9]+ .'*([^ ']*)".format(option), value, re.DOTALL | re.MULTILINE)[0]
        except:
            return None
        # from tempfile import NamedTemporaryFile
        # f = NamedTemporaryFile(delete=False)
        # try:
        #     f.write(value)
        #     import pickle
        #     f.seek(0)
        #     p = pickle.load(f)
        #     f.close()
        # finally:
        #     os.remove(f.name)

    def upload_media(self, filename):
        u"""Upload a media by rsync-ing the local file to the shared storage mount point of the orchestrator !"""
        # FIXME detect name based on hostname ?
        os.chmod(self.id_rsa, 0600)
        service, number = self.api_unit.split(u'/')
        host = u'ubuntu@{0}'.format(self.api_url.split(u':')[0])

        cfg, get = self.api_local_config, self.get_unit_local_config
        p = self.storage_path       = self.storage_path       or get(service, number, cfg, option=u'storage_path')
        a = self.storage_address    = self.storage_address    or get(service, number, cfg, option=u'storage_address')
        m = self.storage_mountpoint = self.storage_mountpoint or get(service, number, cfg, option=u'storage_mountpoint')
        bkp_path = os.path.join(p, u'uploads_bkp/')
        dst_path = os.path.join(p, u'uploads/')

        print(rsync(filename, u'{0}:{1}'.format(host, bkp_path), makedest=True, archive=True, progress=True,
              rsync_path=u'sudo rsync', extra='ssh -i {0}'.format(self.id_rsa))['stdout'])
        sync_bkp_to_upload = u'sudo rsync -ah --progress {0} {1}'.format(bkp_path, dst_path)
        print(ssh(host, id=self.id_rsa, remote_cmd=sync_bkp_to_upload)['stdout'])
        ssh(host, id=self.id_rsa, remote_cmd=u'sudo chown www-data:www-data {0} -R'.format(dst_path))

        return u'{0}://{1}/{2}/uploads/{3}'.format(u'glusterfs', a, m, os.path.basename(filename))

    def remove_medias(self):
        u"""Remove all medias from the shared storage mount point of the orchestrator !"""
        # FIXME detect name based on hostname ?
        os.chmod(self.id_rsa, 0600)
        service, number = self.api_unit.split(u'/')
        host = u'ubuntu@{0}'.format(self.api_url.split(u':')[0])

        cfg, get = self.api_local_config, self.get_unit_local_config
        p = self.storage_path = self.storage_path or get(service, number, cfg, option=u'storage_path')
        medias_path = os.path.join(p, u'medias/*')

        ssh(host, id=self.id_rsa, remote_cmd=u'sudo rm -rf {0}'.format(medias_path))


# ----------------------------------------------------------------------------------------------------------------------

class OrchestraAPICore(object):

    # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Constructor >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    def __init__(self, config):
        self.config = config
        if self.is_mock:
            self._db = mongomock.Connection().orchestra
        else:
            self._db = pymongo.Connection(config.mongo_admin_connection)[u'orchestra']
        self.root_user = User(u'root', u'oscied', u'root@oscied.org', self.config.root_secret, True, _id=UUID_ZERO)
        self.node_user = User(u'node', u'oscied', u'node@oscied.org', self.config.node_secret, False, _id=UUID_ZERO)

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

    def send_email(self, to_addresses, subject, text_plain, text_html=None):
        if not self.config.email_server:
            logging.debug(u'E-mail delivery is disabled in configuration.')
            return {}
        part1 = MIMEText(text_plain, u'plain')
        part2 = MIMEText(text_html, u'html') if text_html else None
        msg = part1 if not part2 else MIMEMultipart(u'alternative')
        msg[u'Subject'] = subject
        msg[u'From'] = self.config.email_address
        msg[u'To'] = u', '.join(to_addresses) if isinstance(to_addresses, dict) else to_addresses
        if part2:
            msg.attach(part1)
            msg.attach(part2)
        try:
            server = smtplib.SMTP(self.config.email_server)
            if self.config.email_tls:
                server.starttls()
            server.login(self.config.email_username, self.config.email_password)
            result = server.sendmail(self.config.email_address, to_addresses, msg.as_string())
            logging.info(u'E-mail delivery {0}, result {1}'.format(msg, result))
            return result
        finally:
            server.quit()

    def send_email_task(self, task, status, media=None, media_out=None):
        if task.send_email:
            user = self.get_user({u'_id': task.user_id}, {u'mail': 1})
            if not user:
                raise IndexError(to_bytes(u'Unable to find user with id {0}.'.format(task.user_id)))
            if isinstance(task, TransformTask):
                media_in = self.get_media({u'_id': task.media_in_id})
                if not media_in:
                    # FIXME maybe do not raise but put default value or return ?
                    raise IndexError(to_bytes(u'Unable to find input media with id {0}.'.format(task.media_in_id)))
                profile = self.get_transform_profile({u'_id': task.profile_id})
                if not profile:
                    # FIXME maybe do not raise but put default value or return ?
                    raise IndexError(to_bytes(u'Unable to find profile with id {0}.'.format(task.profile_id)))
                task.load_fields(user, media_in, media_out, profile)
                template, name = self.config.email_ttask_template, u'Transformation'
            elif isinstance(task, PublishTask):
                task.load_fields(user, media)
                template, name = self.config.email_ptask_template, u'Publication'
            else:
                return  # FIXME oups
            task.append_async_result()
            with open(template, u'r', u'utf-8') as template_file:
                text_plain = Template(template_file.read()).render(object2dict(task, include_properties=True))
                # FIXME YourFormatter().format(template_file.read(), task)
            self.send_email(task.user.mail, u'OSCIED - {0} task {1} {2}'.format(name, task._id, status), text_plain)

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
        user = dict2object(User, entity, inspect_constructor=True)
        return user if secret is None or user.verify_secret(secret) else None

    def delete_user(self, user):
        # FIXME issue #16 (https://github.com/ebu/OSCIED/issues/16)
        # entity = self.get_user({'_id': user_id}, {'secret': 0})
        # if not entity:
        #     raise IndexError(to_bytes(u'No user with id {0}.'.format(id)))
        # self._db.users.remove({'_id': entity._id})
        # return dict2object(User, entity, inspect_constructor=True)
        if valid_uuid(user, none_allowed=False):
            user = self.get_user({u'_id': user}, {u'secret': 0})
        user.is_valid(True)
        self._db.users.remove({u'_id': user._id})

    def get_users(self, specs=None, fields=None):
        users = []
        for entity in list(self._db.users.find(specs, fields)):
            users.append(dict2object(User, entity, inspect_constructor=True))
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
        media = dict2object(Media, entity, inspect_constructor=True)
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
            media = dict2object(Media, entity, inspect_constructor=True)
            if load_fields:
                media.load_fields(self.get_user({u'_id': media.user_id}, {u'secret': 0}),
                                  self.get_media({u'_id': media.parent_id}))
            medias.append(media)
        return medias

    def get_medias_count(self, specs=None):
        return self._db.medias.find(specs, {u'_id': 1}).count()

    # ------------------------------------------------------------------------------------------------------------------

    def add_environment(self, name, type, region, access_key, secret_key, control_bucket):
        return juju.add_environment(name, type, region, access_key, secret_key, control_bucket,
                                    self.config.charms_release, environments=self.config.juju_config_file)

    def delete_environment(self, name, remove=False):
        u"""
        .. warning:: TODO test & debug of environment methods, especially delete !
        """
        return juju.destroy_environment(name, remove_default=False, remove=remove,
                                        environments=self.config.juju_config_file)

    def get_environment(self, name, get_status=False):
        return juju.get_environment(name, get_status=get_status, environments=self.config.juju_config_file)

    def get_environments(self, get_status=False):
        return juju.get_environments(get_status=get_status, environments=self.config.juju_config_file)

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
        return dict2object(TransformProfile, entity, inspect_constructor=True)

    def delete_transform_profile(self, profile):
        if valid_uuid(profile, none_allowed=False):
            profile = self.get_profile({u'_id': profile})
        profile.is_valid(True)
        self._db.transform_profiles.remove({u'_id': profile._id})

    def get_transform_profiles(self, specs=None, fields=None):
        profiles = []
        for entity in list(self._db.transform_profiles.find(specs, fields)):
            profiles.append(dict2object(TransformProfile, entity, inspect_constructor=True))
        return profiles

    def get_transform_profiles_count(self, specs=None):
        return self._db.transform_profiles.find(specs, {u'_id': 1}).count()

    # ------------------------------------------------------------------------------------------------------------------

    def add_or_deploy_transform_units(self, environment, num_units):
        environments, default = self.get_environments()
        if environment == 'default':
            environment = default
        same_environment = (environment == default)
        config = juju.load_unit_config(self.config.transform_config)
        config[u'rabbit_queues'] = u'transform_{0}'.format(environment)
        if not same_environment:
            raise NotImplementedError(to_bytes(u'Unable to launch transformation units into non-default environment '
                                      '{0} (default is {1}).'.format(environment, default)))
            config[u'mongo_connection'] = self.config.mongo_node_connection
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

    def destroy_transform_unit(self, environment, number, destroy_machine):
        juju.destroy_unit(environment, self.config.transform_service, number, destroy_machine)
        if self.get_transform_units_count(environment) == 0:
            return juju.destroy_service(environment, self.config.transform_service, fail=False)

    def destroy_transform_units(self, environment, num_units, destroy_machine):
        u"""

        .. warning::

            FIXME implement more robust resources listing and removing, sometimes juju fail during a call
            (e.g. destroy_transform_units with num_units=10) and then some machines are not destroyed.
            Maybe implement a garbage collector method callable by user when he want to destroy useless machines ?
        """
        units = self.get_transform_units(environment)
        numbers = []
        for unit_number in units.iterkeys():
            num_units -= 1
            if num_units < 0:
                break
            juju.destroy_unit(environment, self.config.transform_service, unit_number, destroy_machine)
            numbers.append(unit_number)
        if self.get_transform_units_count(environment) == 0:
            juju.destroy_service(environment, self.config.transform_service, fail=False)
        return numbers

    # ------------------------------------------------------------------------------------------------------------------

    def get_transform_queues(self):
        return self.config.transform_queues

    def launch_transform_task(self, user_id, media_in_id, profile_id, filename, metadata, send_email, queue,
                              callback_url):
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
        callback = Callback(self.config.api_url + callback_url, u'node', self.config.node_secret)
        if self.is_mock:
            result_id = unicode(uuid.uuid4())
        else:
            result = TransformWorker.transform_task.apply_async(
                args=(object2json(media_in, False), object2json(media_out, False), object2json(profile, False),
                      object2json(callback, False)), queue=queue)
            result_id = result.id
        if not result_id:
            raise ValueError(to_bytes(u'Unable to transmit task to workers of queue {0}.'.format(queue)))
        logging.info(u'New transformation task {0} -> queue {1}.'.format(result_id, queue))
        task = TransformTask(user._id, media_in._id, media_out._id, profile._id, send_email=send_email, _id=result_id)
        task.add_statistic(u'add_date', datetime_now(), True)
        self._db.transform_tasks.save(task.__dict__)
        return result_id

    def get_transform_task(self, specs, fields=None, load_fields=False, append_result=True):
        entity = self._db.transform_tasks.find_one(specs, fields)
        if not entity:
            return None
        task = dict2object(TransformTask, entity, inspect_constructor=True)
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
            task = dict2object(TransformTask, entity, inspect_constructor=True)
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

    def launch_publish_task(self, user_id, media_id, send_email, queue, callback_url):
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
        if len(media.public_uris) > 0:
            raise NotImplementedError(to_bytes(u'Cannot launch the task, input media is already published.'))
        other = self.get_publish_task({u'media_id': media._id})
        if other and other.status not in states.READY_STATES and other.status != states.REVOKED:
            raise NotImplementedError(to_bytes(u'Cannot launch the task, input media will be published by another task '
                                      'with id {0}.'.format(other._id)))
        # FIXME create a one-time password to avoid fixed secret authentication ...
        callback = Callback(self.config.api_url + callback_url, u'node', self.config.node_secret)
        if self.is_mock:
            result_id = unicode(uuid.uuid4())
        else:
            result = PublisherWorker.publish_task.apply_async(
                args=(object2json(media, False), object2json(callback, False)), queue=queue)
            result_id = result.id
        if not result_id:
            raise ValueError(to_bytes(u'Unable to transmit task to workers of queue {0}.'.format(queue)))
        logging.info(u'New publication task {0} -> queue {1}.'.format(result_id, queue))
        task = PublishTask(user._id, media._id, send_email=send_email, _id=result_id)
        task.add_statistic(u'add_date', datetime_now(), True)
        self._db.publish_tasks.save(task.__dict__)
        return result_id

    def get_publish_task(self, specs, fields=None, load_fields=False, append_result=True):
        entity = self._db.publish_tasks.find_one(specs, fields)
        if not entity:
            return None
        task = dict2object(PublishTask, entity, inspect_constructor=True)
        if load_fields:
            task.load_fields(self.get_user({u'_id': task.user_id}, {u'secret': 0}),
                             self.get_media({u'_id': task.media_id}))
        if append_result:
            task.append_async_result()
        return task

    def update_publish_task_and_media(self, task, publish_uri=None, revoke_task_id=None, status=None):
        if status:
            task.status = status
            media = self.get_media({u'_id': task.media_id})
            if not media:
                raise IndexError(to_bytes(u'Unable to find media with id {0}.'.format(task.media_id)))
            if task.status == states.SUCCESS:
                task.publish_uri = publish_uri
                media.public_uris[task._id] = publish_uri
            elif task.status == states.REVOKED:
                try:  # Remove if missing or not !
                    del media.public_uris[task._id]
                except:
                    pass
            elif task.status == 'REVOKING':
                task.revoke_task_id = revoke_task_id
            self.save_media(media)  # FIXME do not save if not modified.
            self._db.publish_tasks.save(task.__dict__)  # FIXME The same here.
            return media
        return None

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
            raise ValueError(to_bytes(u'Cannot revoke a publication task with status {0}.'.format(task.status)))
        if not self.is_mock:
            revoke(task._id, terminate=terminate)
        if task.status == states.SUCCESS and not self.is_mock:
            # Send revoke task to the worker that published the media
            callback = Callback(self.config.api_url + callback_url, u'node', self.config.node_secret)
            queue = task.get_hostname()
            result = PublisherWorker.revoke_publish_task.apply_async(
                args=(task.publish_uri, object2json(callback, False)), queue=queue)
            if not result.id:
                raise ValueError(to_bytes(u'Unable to transmit task to queue {0}.'.format(queue)))
            logging.info(u'New revoke publication task {0} -> queue {1}.'.format(result.id, queue))
            self.update_publish_task_and_media(task, revoke_task_id=result.id, status='REVOKING')
        else:
            self.update_publish_task_and_media(task, status=states.REVOKED)
        if remove:
            self._db.publish_tasks.remove({u'_id': task._id})

    def get_publish_tasks(self, specs=None, fields=None, load_fields=False, append_result=True):
        tasks = []
        for entity in list(self._db.publish_tasks.find(specs, fields)):
            task = dict2object(PublishTask, entity, inspect_constructor=True)
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
            #self.send_email_task(task, u'SUCCESS', media_out=media_out)
        else:
            self.delete_media(media_out)
            task.add_statistic(u'error_details', status.replace(u'\n', u'\\n'), True)
            self._db.transform_tasks.save(task.__dict__)
            logging.info(u'{0} Error: {1}'.format(task_id, status))
            logging.info(u'{0} Media {1} is now deleted'.format(task_id, media_out.filename))
            #self.send_email_task(task, u'ERROR', media_out=media_out)

    def publish_callback(self, task_id, publish_uri, status):
        task = self.get_publish_task({u'_id': task_id})
        if not task:
            raise IndexError(to_bytes(u'No publication task with id {0}.'.format(task_id)))
        if status == states.SUCCESS:
            media = self.update_publish_task_and_media(task, publish_uri=publish_uri, status=status)
            logging.info(u'{0} Media {1} is now PUBLISHED'.format(task_id, media.filename))
            #self.send_email_task(task, u'SUCCESS', media=media)
        else:
            task.add_statistic(u'error_details', status.replace(u'\n', u'\\n'), True)
            self._db.publish_tasks.save(task.__dict__)
            logging.info(u'{0} Error: {1}'.format(task_id, status))
            logging.info(u'{0} Media {1} is not modified'.format(task_id, media.filename))
            #self.send_email_task(task, u'ERROR', media=None)

    def publish_revoke_callback(self, task_id, publish_uri, status):
        task = self.get_publish_task({u'revoke_task_id': task_id})
        if not task:
            raise IndexError(to_bytes(u'No publication task with revoke_task_id {0}.'.format(task_id)))
        if status == states.SUCCESS:
            media = self.update_publish_task_and_media(task, status=states.REVOKED)
            logging.info(u'{0} Media {1} is now {2}'.format(task_id, media.filename, media.status))
        else:
            task.add_statistic('revoke_error_details', status.replace(u'\n', u'\\n'), True)
            self._db.publish_tasks.save(task.__dict__)
            logging.info(u'{0} Error: {1}'.format(task_id, status))
            logging.info(u'{0} Media {1} is not modified'.format(task_id, media.filename))


# ----------------------------------------------------------------------------------------------------------------------

def init_api(api_core_or_client, api_init_csv_directory, flush=False):

    is_core = isinstance(api_core_or_client, OrchestraAPICore)
    orchestra = api_core_or_client if is_core else None
    api_client = api_core_or_client if not is_core else None

    if flush:
        if is_core:
            orchestra.flush_db()
            # FIXME remove media files
        else:
            api_client.flush()
            api_client.remove_medias()

    users, reader = [], csv_reader(os.path.join(api_init_csv_directory, u'users.csv'))
    for first_name, last_name, email, secret, admin_platform in reader:
        user = User(first_name, last_name, email, secret, admin_platform)
        users.append(user)
        print(u'Adding user {0}'.format(user.name))
        if is_core:
            orchestra.save_user(user, hash_secret=True)
        else:
            api_client.users.add(user)
    users = orchestra.get_users() if is_core else users# api_client.users.list()

    i, reader = 0, csv_reader(os.path.join(api_init_csv_directory, u'medias.csv'))
    for local_filename, filename, title in reader:
        user = users[i]
        print(os.getcwd())
        media = Media(user_id=user._id, filename=filename, metadata={u'title': title})
        if not os.path.exists(local_filename):
            print(u'Skip media {0}, file "{1}" Not found.'.format(media.metadata[u'title'], local_filename))
            continue
        print(u'Adding media {0} as user {1}'.format(media.metadata[u'title'], user.name))
        if is_core:
            #orchestra.config. bla bla -> get media.uri
            orchestra.save_media(media)
        else:
            api_client.auth = user
            media.uri = api_client.upload_media(local_filename)
            api_client.medias.add(media)
        i = (i + 1) % len(users)

    i, reader = 0, csv_reader(os.path.join(api_init_csv_directory, u'tprofiles.csv'))
    for title, description, encoder_name, encoder_string in reader:
        user = users[i]
        profile = TransformProfile(title, description, encoder_name, encoder_string)
        print(u'Adding transformation profile {0} as user {1}'.format(profile.title, user.name))
        if is_core:
            orchestra.save_transform_profile(profile)
        else:
            api_client.auth = user
            api_client.transform_profiles.add(profile)
        i = (i + 1) % len(users)

    if not is_core:
        return

    reader = csv_reader(os.path.join(api_init_csv_directory, u'ttasks.csv'))
    for user_email, in_filename, profile_title, out_filename, out_title, send_email, queue in reader:
        user = orchestra.get_user({u'mail': user_email})
        if not user:
            raise IndexError(to_bytes(u'No user with e-mail address {0}.'.format(user_email)))
        media_in = orchestra.get_media({u'filename': in_filename})
        if not media_in:
            raise IndexError(to_bytes(u'No media with filename {0}.'.format(in_filename)))
        profile = orchestra.get_transform_profile({u'title': profile_title})
        if not profile:
            raise IndexError(to_bytes(u'No transformation profile with title {0}.'.format(profile_title)))
        print(u'Launching transformation task {0} with profile {1} as user {2}.'.format(media_in.metadata[u'title'],
              profile.title, user.name))
        metadata = {u'title': out_title}
        orchestra.launch_transform_task(user._id, media_in._id, profile._id, out_filename, metadata, send_email, queue,
                                        u'/transform/callback')


# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pyutils.py_unicode import configure_unicode
    configure_unicode()
    orchestra = OrchestraAPICore(ORCHESTRA_CONFIG_TEST)
    init_api(orchestra, u'../../scenarios/current')
    print(u'There are {0} registered users.'.format(len(orchestra.get_users())))
    print(u'There are {0} available media assets.'.format(len(orchestra.get_medias())))
    print(u'There are {0} available transformation profiles.'.format(len(orchestra.get_transform_profiles())))
    print(u'There are {0} launched transformation tasks.'.format(len(orchestra.get_transform_tasks())))
