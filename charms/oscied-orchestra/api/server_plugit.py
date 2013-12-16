#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : ORCHESTRA
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

from __future__ import absolute_import, division, print_function, unicode_literals

import flask, logging
from functools import wraps
from pytoolbox.flask import check_id, map_exceptions


# http://publish.luisrei.com/articles/flaskrest.html
def api_method_decorator(api_core, authenticate=True, allow_root=False, allow_node=False, allow_any=False, role=None,
                         allow_same_id=False):
    def decorate(func):
        @wraps(func)
        def wrapper(**kwargs):
            try:
                 # Get id from the API method's arguments and check it if present
                id = kwargs.get(u'id')
                if id is not None:
                    check_id(id)
                kwargs[u'api_core'] = api_core  # Add API core instance to
                # Get request from API method's arguments, set it to Flask's request if not present
                request = kwargs[u'request'] = kwargs.get(u'request', flask.request)
                # Authenticate the request with the security rules if enabled
                if authenticate:
                    auth = request.authorization
                    if not auth or auth.username is None or auth.password is None:
                        flask.abort(401, u'Authenticate.')  # Testing for None is maybe overkill
                    username = auth.username
                    password = auth.password
                    root = (username == u'root' and password == api_core.config.root_secret)
                    node = (username == u'node' and password == api_core.config.node_secret)
                    if not root and not node:
                        flask.abort(401, u'Authentication Failed.')
                    if root:
                        logging.info(u'Allowed authenticated root')
                        kwargs[u'auth_user'] = api_core.root_user
                    elif node and allow_node:
                        logging.info(u'Allowed authenticated worker/node')
                        kwargs[u'auth_user'] = api_core.node_user
                    else:
                        flask.abort(403, username)
                # Return the API method with some arguments updated
                return func(**kwargs)
            except Exception as e:
                map_exceptions(e)
        return wrapper
    return decorate
