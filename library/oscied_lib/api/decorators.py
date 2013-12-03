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

import flask, logging
from functools import wraps
from pytoolbox.flask import check_id, map_exceptions


# http://publish.luisrei.com/articles/flaskrest.html
def api_method_decorator(api_core, authenticate=True, allow_root=False, allow_node=False, allow_any=False, role=None,
                         allow_same_id=False):
    logging.info(u'creating the decorator with {0}'.format(api_core)) # FIXME DEBUG
    def decorate(func):
        @wraps(func)
        def wrapper(**kwargs):
            u"""
            This decorator implements Orchestra's RESTful API (standalone only) authentication logic. Here is ensured
            that an access to a method of the API is filtered based on rules (this method's parameters). HTTP user agent
            must authenticate through HTTP basic access authentication. The username must be user's email address and
            password must be user's secret. This not apply for system-users like root or node as they do not have any
            e-mail address.

            .. warning::

                Username and password are passed as plaintext, SSL/TLS is one of the way to improve security although
                this was not tested during my thesis.

            This method will abort request with HTTP 401 error if HTTP user agent doesn't authenticate.

            :param request: the request itself, credentials are retrieved from request authorization header
            :param allow_root: if set to `True` root system-user will be allowed
            :param allow_node: if set to `True` node system-user will be allowed
            :param allow_any: if set to `True` any authenticated user will be allowed
            :param allow_same_id: if set to <uuid>, any user with _id equal to "uuid" will be allowed
            :param role: if set to <name>, any user will "name" role set to `True` will be allowed

            This method will abort request with HTTP 403 error if none of the following conditions are met.

            Example::

                # Do not check authentication
                @action(u'/my/example/route', methods=[u'GET'])
                @api_method_decorator(api_core, authenticate=False)
                def api_method0(api_core=None, request=None):
                    ...
                    return ok_200(u'My return value', include_properties=False)

                # Allow any authenticated user
                @action(u'/my/restricted/route', methods=[u'GET'])
                @api_method_decorator(api_core, allow_any=True)
                def api_method1(api_core=None, auth_user=None, request=None):
                    ...
                    return ok_200(u'My return value', include_properties=False)

                # Allow root system-user or any user with admin attribute set
                @action(u'/my/restricted/route//with/variables/<extra>/<stuff>', methods=[u'GET'])
                @api_method_decorator(api_core, allow_root=True, allow_role='admin')
                def api_method2(extra=None, stuff=None, api_core=None, auth_user=None, request=None):
                    ...
                    return ok_200(u'Extra is "{0}"'.format(extra), include_properties=False)

                # Allow any user with admin attribute set or any user with id equal to id extracted from the URL
                @action(u'/my/restricted/route/<id>', methods=[u'GET'])
                @api_method_decorator(api_core, allow_role='admin', allow_same_id=True)
                def api_method3(id=None, api_core=None, auth_user=None, request=None):
                    ...
                    return ok_200(u'Id is "{0}"'.format(id), include_properties=False)
            """
            logging.info(u'called the decorator with {0}'.format(api_core)) # FIXME DEBUG
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
                    user = None
                    if not root and not node:
                        user = api_core.get_user({u'mail': username}, secret=password)
                        username = user.name if user else None
                    if not root and not user and not node:
                        flask.abort(401, u'Authentication Failed.')
                    if root and allow_root:
                        logging.info(u'Allowed authenticated root')
                        kwargs[u'auth_user'] = api_core.root_user
                    elif node and allow_node:
                        logging.info(u'Allowed authenticated worker/node')
                        kwargs[u'auth_user'] = api_core.node_user
                    elif user and allow_any:
                        logging.info(u'Allowed authenticated user {0}'.format(user.name))
                        kwargs[u'auth_user'] = user
                    elif allow_same_id and user._id == id:
                        logging.info(u'Allowed authenticated user {0} with id {1}'.format(user.name, id))
                        kwargs[u'auth_user'] = user
                    elif role and hasattr(user, role) and getattr(user, role):
                        logging.info(u'Allowed authenticated user {0} with role {1}'.format(user.name, role))
                        kwargs[u'auth_user'] = user
                    else:
                        flask.abort(403, username)
                # Return the API method with some arguments updated
                return func(**kwargs)
            except Exception as e:
                map_exceptions(e)
        return wrapper
    return decorate
