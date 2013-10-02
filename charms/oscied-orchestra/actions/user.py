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

from __future__ import absolute_import

from library.oscied_lib.models import User
from library.oscied_lib.pytoolbox.encoding import to_bytes
from library.oscied_lib.pytoolbox.flask import check_id, get_request_data, map_exceptions
from plugit_utils import action, json_only

from . import orchestra


# Users management -----------------------------------------------------------------------------------------------------

@action(u'/user/login', methods=[u'GET'])
@json_only()
def api_user_login(request):
    u"""
    Return authenticated user serialized to JSON if authentication passed (without ``secret`` field).

    This method is useful for WebUI to simulate stateful login scheme and get informations about the user.

    .. note::

        This is kind of duplicate with API's GET /user/id/`id` method ...
    """
    try:
        auth_user = orchestra.requires_auth(request=request, allow_any=True)
        delattr(auth_user, u'secret')  # do not send back user's secret
        return orchestra.ok_200(auth_user, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/user/count', methods=[u'GET'])
@json_only()
def api_user_count(request):
    u"""Return the number of users."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_count_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_users_count(**data), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/user', methods=[u'GET'])
@json_only()
def api_user_get(request):
    u"""Return an array containing the users serialized to JSON (without ``secret`` fields)."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        data = get_request_data(request, accepted_keys=orchestra.db_find_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_users(**data), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/user', methods=[u'POST'])
@json_only()
def api_user_post(request):
    u"""Add a user."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        data = get_request_data(request, qs_only_first_value=True)
        user = User(first_name=data[u'first_name'], last_name=data[u'last_name'], mail=data[u'mail'],
                    secret=data[u'secret'], admin_platform=data[u'admin_platform'])
        orchestra.save_user(user, hash_secret=True)
        delattr(user, u'secret')  # do not send back user's secret
        return orchestra.ok_200(user, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/user/id/<id>', methods=[u'GET'])
@json_only()
def api_user_id_get(request, id):
    u"""Return a user serialized to JSON (without ``secret`` field)."""
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_root=True, allow_any=True)
        user = orchestra.get_user(spec={u'_id': id}, fields={u'secret': 0})
        if not user:
            raise IndexError(to_bytes(u'No user with id {0}.'.format(id)))
        return orchestra.ok_200(user, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/user/id/<id>', methods=[u'PATCH', u'PUT'])
@json_only()
def api_user_id_patch(request, id):
    u"""
    Update an user.

    User's admin_platform attribute can only be modified by root or any authenticated user with admin_platform attribute
    set.
    """
    try:
        check_id(id)
        auth_user = orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform', id=id)
        user = orchestra.get_user(spec={u'_id': id})
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
        orchestra.save_user(user, hash_secret=True)
        return orchestra.ok_200(u'The user "{0}" has been updated.'.format(old_name), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/user/id/<id>', methods=[u'DELETE'])
@json_only()
def api_user_id_delete(request, id):
    u"""Delete a user."""
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform', id=id)
        user = orchestra.get_user(spec={u'_id': id})
        if not user:
            raise IndexError(to_bytes(u'No user with id {0}.'.format(id)))
        orchestra.delete_user(user)
        return orchestra.ok_200(u'The user "{0}" has been deleted.'.format(user.name), include_properties=False)
    except Exception as e:
        map_exceptions(e)
