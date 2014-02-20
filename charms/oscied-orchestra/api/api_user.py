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

from pytoolbox.encoding import to_bytes
from pytoolbox.network.http import get_request_data
from oscied_lib.models import User

from server import app, api_method_decorator, api_core, ok_200


# Users management -----------------------------------------------------------------------------------------------------

@app.route(u'/user/login', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_user_login(auth_user=None, api_core=None, request=None):
    u"""
    Return authenticated user serialized to JSON if authentication passed (without ``secret`` field).

    This method is useful for WebUI to simulate stateful login scheme and get informations about the user.

    .. note::

        This is kind of duplicate with API's GET /user/id/`id` method ...
    """
    delattr(auth_user, u'secret')  # do not send back user's secret
    return ok_200(auth_user, include_properties=True)


@app.route(u'/user/count', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, allow_any=True)
def api_user_count(auth_user=None, api_core=None, request=None):
    u"""Return the number of users."""
    data = get_request_data(request, accepted_keys=api_core.db_count_keys, qs_only_first_value=True, optional=True)
    return ok_200(api_core.get_users_count(**data), include_properties=False)


@app.route(u'/user', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_user_get(auth_user=None, api_core=None, request=None):
    u"""Return an array containing the users serialized to JSON (without ``secret`` fields)."""
    data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
    return ok_200(api_core.get_users(**data), include_properties=True)


@app.route(u'/user', methods=[u'POST'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_user_post(auth_user=None, api_core=None, request=None):
    u"""Add a user."""
    data = get_request_data(request, qs_only_first_value=True)
    user = User(first_name=data[u'first_name'], last_name=data[u'last_name'], mail=data[u'mail'],
                secret=data[u'secret'], admin_platform=data[u'admin_platform'])
    api_core.save_user(user, hash_secret=True)
    delattr(user, u'secret')  # do not send back user's secret
    return ok_200(user, include_properties=True)


@app.route(u'/user/id/<id>', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, allow_any=True)
def api_user_id_get(id=None, auth_user=None, api_core=None, request=None):
    u"""Return a user serialized to JSON (without ``secret`` field)."""
    user = api_core.get_user(spec={u'_id': id}, fields={u'secret': 0})
    if not user:
        raise IndexError(to_bytes(u'No user with id {0}.'.format(id)))
    return ok_200(user, include_properties=True)


@app.route(u'/user/id/<id>', methods=[u'PATCH', u'PUT'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform', allow_same_id=True)
def api_user_id_patch(id=None, auth_user=None, api_core=None, request=None):
    u"""
    Update an user.

    User's admin_platform attribute can only be modified by root or any authenticated user with admin_platform attribute
    set.
    """
    user = api_core.get_user(spec={u'_id': id})
    data = get_request_data(request, qs_only_first_value=True)
    if not user:
        raise IndexError(to_bytes(u'No user with id {0}.'.format(id)))
    old_name = user.name
    if u'first_name' in data:
        user.first_name = data[u'first_name']
    if u'last_name' in data:
        user.last_name = data[u'last_name']
    if u'mail' in data:
        user.mail = data[u'mail']
    if u'secret' in data:
        user.secret = data[u'secret']
    if auth_user.admin_platform and u'admin_platform' in data:
        user.admin_platform = data[u'admin_platform']
    api_core.save_user(user, hash_secret=True)
    return ok_200(u'The user "{0}" has been updated.'.format(old_name), include_properties=False)


@app.route(u'/user/id/<id>', methods=[u'DELETE'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform', allow_same_id=True)
def api_user_id_delete(id=None, auth_user=None, api_core=None, request=None):
    u"""Delete a user."""
    user = api_core.get_user(spec={u'_id': id})
    if not user:
        raise IndexError(to_bytes(u'No user with id {0}.'.format(id)))
    api_core.delete_user(user)
    return ok_200(u'The user "{0}" has been deleted.'.format(user.name), include_properties=False)
