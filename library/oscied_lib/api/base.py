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

from pytoolbox.encoding import to_bytes
from pytoolbox.serialization import dict2object, object2json
from requests import get, patch, post, delete

from ..models import User

ABOUT = u"Orchestra : EBU's OSCIED Orchestrator by David Fischer 2012-2013"


class OsciedCRUDMapper(object):
    u"""Map the CRUD operations of the orchestrator RESTful API into a utility class for OrchestraAPIClient."""

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
        if hasattr(value, u'_id'):
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

    def count(self, **data):
        return self.api_client.do_request(get, self.get_url(extra=u'count'),
                                          data=object2json(data, include_properties=False))

    def list(self, head=False, **data):
        values = []
        response_dict = self.api_client.do_request(get, self.get_url(extra=(u'HEAD' if head else None)),
                                                   data=object2json(data, include_properties=False))
        if self.cls is None:
            return response_dict
        for value_dict in response_dict:
            values.append(dict2object(self.cls, value_dict, inspect_constructor=True))
        return values