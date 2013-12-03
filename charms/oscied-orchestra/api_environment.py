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

from pytoolbox.flask import get_request_data

from server import app, api_method_decorator, api_core, ok_200


# Environments management ----------------------------------------------------------------------------------------------

@app.route(u'/environment/count', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_environment_count(auth_user=None, api_core=None, request=None):
    u"""Return the number of environments."""
    (environments, default) = api_core.get_environments()
    return ok_200(len(environments), False)


@app.route(u'/environment/HEAD', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_environment_get_head(auth_user=None, api_core=None, request=None):
    u"""Return an array containing the environments serialized to JSON."""
    (environments, default) = api_core.get_environments()
    return ok_200({u'environments': environments, u'default': default}, include_properties=False)


@app.route(u'/environment', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_environment_get(auth_user=None, api_core=None, request=None):
    u"""Return an array containing the environments (with status) serialized to JSON."""
    (environments, default) = api_core.get_environments(get_status=True)
    return ok_200({u'environments': environments, u'default': default}, include_properties=False)


@app.route(u'/environment', methods=[u'POST'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_environment_post(auth_user=None, api_core=None, request=None):
    u"""Add a new environment."""
    data = get_request_data(request, qs_only_first_value=True)
    return ok_200(api_core.add_environment(data[u'name'], data[u'type'], data[u'region'], data[u'access_key'],
                  data[u'secret_key'], data[u'control_bucket']), include_properties=False)


@app.route(u'/environment/name/<name>/HEAD', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_environment_name_get_head(name=None, auth_user=None, api_core=None, request=None):
    u"""Return an environment containing his status serialized to JSON."""
    return ok_200(api_core.get_environments(name), include_properties=False)


@app.route(u'/environment/name/<name>', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_environment_name_get(name=None, auth_user=None, api_core=None, request=None):
    u"""Return an environment serialized to JSON."""
    return ok_200(api_core.get_environment(name, get_status=True), include_properties=False)


@app.route(u'/environment/name/<name>', methods=[u'DELETE'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_environment_name_delete(name=None, auth_user=None, api_core=None, request=None):
    u"""Remove an environment (destroy services and unregister it)."""
    return ok_200(api_core.delete_environment(name, remove=True), include_properties=False)
