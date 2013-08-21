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

from requests import get, patch, post, delete
from oscied_models import Media, User, TransformProfile, TransformTask
from pyutils.py_flask import map_exceptions
from pyutils.py_serialization import object2json


class OsciedCRUDMapper(object):

    def __init__(self, api_client, method='', cls=None, id_prefix='id', environment=False):
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
        return self.api_client.do_request(get, self.get_url(extra='count'))

    def __getitem__(self, index):
        response_dict = self.do_request(get, self.get_url(index))
        return response_dict if self.cls is None else self.cls(**response_dict)

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
            raise ValueError(u'You must set args OR kwargs.')
        if args and len(args) != 1:
            raise ValueError(u'args should contain only 1 value.')
        value = args[0] if args else kwargs
        return self.api_client.do_request(post, self.get_url(), data=object2json(value, include_properties=False))

    def list(self, head=False):
        values = []
        response_dict = self.api_client.do_request(get, self.get_url(extra=('HEAD' if head else None)))
        if self.cls is None:
            return response_dict
        for value_dict in response_dict:
            values.append(self.cls(**value_dict))
        return values


class OrchestraAPIClient(object):

    def __init__(self, hostname, port=5000, auth=None, timeout=10.0):
        self.api_url = u'{0}:{1}'.format(hostname, port)
        self.auth = auth
        self.timeout = timeout
        self.users = OsciedCRUDMapper(self, 'user', User)
        self.medias = OsciedCRUDMapper(self, 'media', Media)
        self.environments = OsciedCRUDMapper(self, 'environment', None, 'name')
        self.transform_profiles = OsciedCRUDMapper(self, 'transform/profile', TransformProfile)
        self.transform_units = OsciedCRUDMapper(self, 'transform/unit', None, 'number', True)
        self.transform_tasks = OsciedCRUDMapper(self, 'transform/task', TransformTask)
        # FIXME api_transform_unit_number_get, api_transform_unit_number_delete ...

    def do_request(self, verb, resource, auth=None, data=None):
        headers = {u'Content-type': u'application/json', u'Accept': u'application/json'}
        auth = auth or self.auth
        auth = (auth.mail, auth.secret) if isinstance(auth, User) else auth
        url = u'http://{0}'.format(resource)
        return map_exceptions(verb(url, auth=auth, data=data, headers=headers, timeout=self.timeout).json())

    # Mapping of the API methods ---------------------------------------------------------------------------------------

    @property
    def about(self):
        return self.do_request(get, self.api_url)

    def flush(self):
        return self.do_request(post, u'{0}/flush'.format(self.api_url))

    def login(self, mail, secret, update_auth=True):
        user = User(**self.do_request(get, u'{0}/user/login'.format(self.api_url), (mail, secret)))
        if update_auth:
            user.secret = secret
            self.auth = user
        return user

    @property
    def encoders(self):
        return self.do_request(get, u'{0}/transform/profile/encoder'.format(self.api_url))

    @property
    def transform_queues(self):
        return self.do_request(get, u'{0}/transform/queue'.format(self.api_url))

    @property
    def publisher_queues(self):
        return self.do_request(get, u'{0}/publisher/queue'.format(self.api_url))
