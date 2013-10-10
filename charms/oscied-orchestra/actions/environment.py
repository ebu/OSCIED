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

from pytoolbox.flask import get_request_data, map_exceptions
from plugit_utils import action, json_only

from . import orchestra


# Environments management ----------------------------------------------------------------------------------------------

@action(u'/environment/count', methods=[u'GET'])
@json_only()
def api_environment_count(request):
    u"""Return the number of environments."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        (environments, default) = orchestra.get_environments()
        return orchestra.ok_200(len(environments), False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment/HEAD', methods=[u'GET'])
@json_only()
def api_environment_get_head(request):
    u"""Return an array containing the environments serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        (environments, default) = orchestra.get_environments()
        return orchestra.ok_200({u'environments': environments, u'default': default}, include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment', methods=[u'GET'])
@json_only()
def api_environment_get(request):
    u"""Return an array containing the environments (with status) serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        (environments, default) = orchestra.get_environments(get_status=True)
        return orchestra.ok_200({u'environments': environments, u'default': default}, include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment', methods=[u'POST'])
@json_only()
def api_environment_post(request):
    u"""Add a new environment."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        data = get_request_data(request, qs_only_first_value=True)
        return orchestra.ok_200(orchestra.add_environment(data[u'name'], data[u'type'], data[u'region'],
                                data[u'access_key'], data[u'secret_key'], data[u'control_bucket']),
                                include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment/name/<name>/HEAD', methods=[u'GET'])
@json_only()
def api_environment_name_get_head(request, name):
    u"""Return an environment containing his status serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        return orchestra.ok_200(orchestra.get_environments(name), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment/name/<name>', methods=[u'GET'])
@json_only()
def api_environment_name_get(request, name):
    u"""Return an environment serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        return orchestra.ok_200(orchestra.get_environment(name, get_status=True), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment/name/<name>', methods=[u'DELETE'])
@json_only()
def api_environment_name_delete(request, name):
    u"""Remove an environment (destroy services and unregister it)."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        return orchestra.ok_200(orchestra.delete_environment(name, remove=True), include_properties=False)
    except Exception as e:
        map_exceptions(e)
