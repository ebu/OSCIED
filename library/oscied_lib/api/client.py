# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : David Fischer (david.fischer.ch@gmail.com)
#  Copyright       : Copyright (c) 2012-2013 EBU. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of EBU Technology & Innovation OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/ebu/OSCIED

from __future__ import absolute_import

import os, re
from pytoolbox.encoding import to_bytes
from pytoolbox.flask import map_exceptions
from pytoolbox.juju import get_unit_path, juju_do
from pytoolbox.serialization import dict2object
from pytoolbox.subprocess import rsync, ssh
from requests import get, post

from ..models import Media, User, TransformProfile, PublisherTask, TransformTask
from .base import OsciedCRUDMapper


class OrchestraAPIClient(object):
    u"""Map all functions of the orchestrator RESTful API in the form of a client class with attributes and methods."""

    def __init__(self, hostname, port=5000, api_unit=u'oscied-orchestra/0', api_local_config=u'local_config.pkl',
                 auth=None, id_rsa=u'~/.ssh/id_rsa', environment=u'default', timeout=10.0):
        self.api_url = u'{0}:{1}'.format(hostname, port)
        self.api_unit = api_unit
        self.api_local_config = api_local_config
        self.auth = auth
        self.root_auth = auth if (auth is not None and not isinstance(auth, User) and auth[0] == u'root') else None
        self.id_rsa = os.path.abspath(os.path.expanduser(id_rsa))
        self.environment = environment
        self.timeout = timeout
        self.storage_path = self.storage_address = self.storage_mountpoint = None
        self.users = OsciedCRUDMapper(self, u'user', User)
        self.medias = OsciedCRUDMapper(self, u'media', Media)
        self.environments = OsciedCRUDMapper(self, u'environment', None, u'name')
        self.transform_profiles = OsciedCRUDMapper(self, u'transform/profile', TransformProfile)
        self.transform_units = OsciedCRUDMapper(self, u'transform/unit', None, u'number', True)
        self.transform_tasks = OsciedCRUDMapper(self, u'transform/task', TransformTask)
        self.publisher_units = OsciedCRUDMapper(self, u'publisher/unit', None, u'number', True)
        self.publisher_tasks = OsciedCRUDMapper(self, u'publisher/task', PublisherTask)
        # FIXME api_transform_unit_number_get, api_transform_unit_number_delete ...

    # Miscellaneous methods of the API ---------------------------------------------------------------------------------

    @property
    def about(self):
        return self.do_request(get, self.api_url)

    def flush(self):
        return self.do_request(post, u'{0}/flush'.format(self.api_url))

    def login(self, user_or_mail, secret=None, update_auth=True):
        if isinstance(user_or_mail, User):
            auth = user_or_mail.credentials
        elif secret is not None:
            auth = (user_or_mail, secret)
        else:
            raise ValueError(to_bytes(u'User_or_mail is neither a valid instance of User nor a mail with a secret '
                                      'following.'))
        user_dict = self.do_request(get, u'{0}/user/login'.format(self.api_url), auth)
        user = dict2object(User, user_dict, inspect_constructor=True)
        if update_auth:
            # Recover user's secret
            user.secret = auth[1]
            self.auth = user
        return user

    def login_or_add(self, user):
        u"""Return logged ``user`` and take care of adding this ``user`` if login is not successful (as root)."""
        try:
            return self.login(user)
        except:
            self.auth = self.root_auth
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
        auth = auth.credentials if isinstance(auth, User) else auth
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

    def upload_media(self, filename, backup_in_remote=True):
        u"""Upload a media asset by rsync-ing the local file to the shared storage mount point of the orchestrator !"""
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

        if backup_in_remote:
            # Mirror the local file into a 'backup' directory on the shared storage, then into the destination directory
            print(rsync(filename, u'{0}:{1}'.format(host, bkp_path), makedest=True, archive=True, progress=True,
                  rsync_path=u'sudo rsync', extra='ssh -i {0}'.format(self.id_rsa))['stdout'])
            sync_bkp_to_upload = u'sudo rsync -ah --progress {0} {1}'.format(bkp_path, dst_path)
            print(ssh(host, id=self.id_rsa, remote_cmd=sync_bkp_to_upload)['stdout'])
        else:
            # Mirror the local file into the destination directory of the shared storage
            print(rsync(filename, u'{0}:{1}'.format(host, dst_path), makedest=True, archive=True, progress=True,
                  rsync_path=u'sudo rsync', extra='ssh -i {0}'.format(self.id_rsa))['stdout'])
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
