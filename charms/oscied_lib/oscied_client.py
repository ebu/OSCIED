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

import requests
from oscied_lib.oscied_models import Media, User, TransformProfile, TransformTask
from pyutils.py_serialization import object2json


class OsciedCRUDMapper(object):

    def __init__(self, do_request, api_url, cls, id_prefix='id', environment=None):
        self.api_url = api_url
        self.cls = cls
        self.id_prefix = id_prefix
        self.environment = environment
        self.do_request = do_request

    def get_url(self, index=None, extra=None):
        environment = u'/environment/{0}'.format(self.environment) if self.environment else u''
        index = u'' if index is None else u'/{0}/{1}'.format(self.id_prefix, index)
        return u'{0}{1}{2}{3}'.format(self.api_url, environment, index, u'' if extra is None else extra)

    def __len__(self):
        return self.do_request(requests.get, self.get_url(extra='/count'))

    def __getitem__(self, index):
        response_dict = self.do_request(requests.get, self.get_url(index))
        return response_dict if self.cls is None else self.cls(**response_dict)

    def __setitem__(self, index, value):
        return self.do_request(requests.patch, self.get_url(index), data=object2json(value, include_properties=True))

    def __delitem__(self, index):
        return self.do_request(requests.delete, self.get_url(index))

    def __contains__(self, value):
        if hasattr(value, '_id'):
            value = value._id
        try:
            return self.do_request(requests.get, self.get_url(value))
        except:
            return False
        return True

    def add(self, value):
        return self.do_request(requests.post, self.get_url(), data=object2json(value, include_properties=True))

    def list(self, head=False):
        values = []
        response_dict = self.do_request(requests.get, self.get_url(extra=('/HEAD' if head else None)))
        if self.cls is None:
            return response_dict
        for value_dict in response_dict:
            values.append(self.cls(**value_dict))
        return values


class EnvironmentsCRUDMapper(OsciedCRUDMapper):

    def __init__(self, do_request, api_url):
        super(EnvironmentsCRUDMapper, self).__init__(
            do_request, u'{0}/environment'.format(api_url), None, id_prefix='name')


class TransformUnitCRUDMapper(OsciedCRUDMapper):

    def __init__(self, do_request, api_url):
        super(TransformUnitCRUDMapper, self).__init__(
            do_request, u'{0}/transform/unit'.format(api_url), None, id_prefix='number', environment='default')

    def add(self, num_units):
        return super(TransformUnitCRUDMapper, self).add({'num_units': num_units})

    def remove(self, num_units):
        value = {'num_units': num_units}
        return self.do_request(requests.delete, self.get_url(), data=object2json(value, include_properties=True))


class OrchestraAPIClient(object):

    def __init__(self, hostname, port=5000, auth=None):
        self.api_url = u'{0}:{1}'.format(hostname, port)
        self.auth = auth

        USER_API_URL = u'{0}/user'.format(self.api_url)
        MEDIA_API_URL = u'{0}/media'.format(self.api_url)
        TRANSFORM_PROFILE_API_URL = u'{0}/transform/profile'.format(self.api_url)
        TRANSFORM_TASK_API_URL = u'{0}/transform/task'.format(self.api_url)

        self.users = OsciedCRUDMapper(self.do_request, USER_API_URL, User)
        self.medias = OsciedCRUDMapper(self.do_request, MEDIA_API_URL, Media)
        self.environments = EnvironmentsCRUDMapper(self.do_request, self.api_url)
        self.transform_profiles = OsciedCRUDMapper(self.do_request, TRANSFORM_PROFILE_API_URL, TransformProfile)
        self.transform_units = TransformUnitCRUDMapper(self.do_request, self.api_url)
        self.transform_tasks = OsciedCRUDMapper(self.do_request, TRANSFORM_TASK_API_URL, TransformTask)
        # FIXME api_transform_unit_number_get, api_transform_unit_number_delete ...

    def do_request(self, method, resource, auth=None, data=None):
        headers = {u'Content-type': u'application/json', u'Accept': u'application/json'}
        auth = auth or self.auth
        auth = (auth.mail, auth.secret) if isinstance(auth, User) else auth
        json_dict = method(u'http://{0}'.format(resource), auth=auth, data=data, headers=headers).json()
        if json_dict[u'status'] == 200:
            return json_dict[u'value']
        else:
            raise IOError(json_dict)

    # Mapping of the API methods ---------------------------------------------------------------------------------------

    @property
    def about(self):
        return self.do_request(requests.get, self.api_url)

    def flush(self):
        return self.do_request(requests.post, u'{0}/flush'.format(self.api_url))

    def login(self, mail, secret, update_auth=True):
        user = User(**self.do_request(requests.get, u'{0}/user/login'.format(self.api_url), (mail, secret)))
        if update_auth:
            user.secret = secret
            self.auth = user
        return user

    @property
    def encoders(self):
        return self.do_request(requests.get, u'{0}/transform/profile/encoder'.format(self.api_url))

    @property
    def transform_queues(self):
        return self.do_request(requests.get, u'{0}/transform/queue'.format(self.api_url))

    @property
    def publisher_queues(self):
        return self.do_request(requests.get, u'{0}/publisher/queue'.format(self.api_url))
