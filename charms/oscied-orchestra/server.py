#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : ORCHESTRA
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/EBU-TI/OSCIED

from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory, make_response
from flask.views import View

import actions
from utils import md5Checksum
from oscied_lib.pyutils.flaski import json_response


# PlugIt Parameters
DEBUG = True

# PI_META_CACHE specify the number of seconds meta informations should be cached
if DEBUG:
    PI_META_CACHE = 0  # No cache
else:
    PI_META_CACHE = 5 * 60  # 5 minutes

## Does not edit code bellow !

# API version parameters
PI_API_VERSION = '1'
PI_API_NAME = 'EBUio-PlugIt'

#
PLUGIT_PREFIX = '/'  # FIXME '/ceciestsecret/'

app = Flask(__name__, static_folder='media')


@app.route(PLUGIT_PREFIX + "ping")
def ping():
    """The ping method: Just return the data provided"""
    return jsonify(data=request.args.get('data', ''))


@app.route(PLUGIT_PREFIX + "version")
def version():
    """The version method: Return current information about the version"""
    return jsonify(result='Ok', version=PI_API_VERSION, protocol=PI_API_NAME)


class MetaView(View):
    """The dynamic view (based on the current action) for the /meta method"""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):
        objResponse = {}

        # Template information
        if self.action.pi_api_template != "":
            objResponse['template_tag'] = md5Checksum('templates/' + self.action.pi_api_template)
        else:
            objResponse['template_tag'] = ""

        # User restrictions
        if hasattr(self.action, 'pi_api_only_logged_user'):
            objResponse['only_logged_user'] = self.action.pi_api_only_logged_user

        if hasattr(self.action, 'pi_api_only_member_user'):
            objResponse['only_member_user'] = self.action.pi_api_only_member_user

        if hasattr(self.action, 'pi_api_only_admin_user'):
            objResponse['only_admin_user'] = self.action.pi_api_only_admin_user

        # Cache information
        if hasattr(self.action, 'pi_api_cache_time'):
            objResponse['cache_time'] = self.action.pi_api_cache_time

        if hasattr(self.action, 'pi_api_cache_by_user'):
            objResponse['cache_by_user'] = self.action.pi_api_cache_by_user

        # User information requested
        if hasattr(self.action, 'pi_api_user_info'):
            objResponse['user_info'] = self.action.pi_api_user_info

        # Only json
        if hasattr(self.action, 'pi_api_json_only'):
            objResponse['json_only'] = self.action.pi_api_json_only

        # Add the cache headers
        response = make_response(jsonify(objResponse))

        expires = datetime.utcnow() + timedelta(seconds=PI_META_CACHE)
        expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")

        response.headers['Expire'] = expires
        response.headers['Cache-Control'] = 'public, max-age=' + str(PI_META_CACHE)

        # Return the final response
        return response


class TemplateView(View):
    """The dynamic view (based on the current action) for the /template method"""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):
        # We just return the content of the template
        return send_from_directory('templates/', self.action.pi_api_template)


class ActionView(View):
    """The dynamic view (based on the current action) for the /action method"""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):
        # Call the action
        result = self.action(request, *args, **kwargs)

        # Is it a redirect ?
        if result.__class__.__name__ == 'PlugItRedirect':
            response = make_response("")
            response.headers['EbuIo-PlugIt-Redirect'] = result.url
            if result.no_prefix:
                response.headers['EbuIo-PlugIt-Redirect-NoPrefix'] = 'True'
            return response

        return jsonify(result)


# Register the 3 URLs (meta, template, action) for each actions
# We test for each element in the module actions if it's an action (added by the decorator in utils)
for act in dir(actions):
    obj = getattr(actions, act)
    if hasattr(obj, 'pi_api_action') and obj.pi_api_action:
        # We found an action and we can now add it to our routes

        # Meta
        app.add_url_rule(PLUGIT_PREFIX + 'meta' + obj.pi_api_route, view_func=MetaView.as_view('meta_' + act, action=obj))

        # Template
        app.add_url_rule(PLUGIT_PREFIX + 'template' + obj.pi_api_route, view_func=TemplateView.as_view('template_' + act, action=obj))

        # Action
        app.add_url_rule(PLUGIT_PREFIX + 'action' + obj.pi_api_route, view_func=ActionView.as_view('action_' + act, action=obj), methods=obj.pi_api_methods)


# Responses ----------------------------------------------------------------------------------------

@app.errorhandler(400)
def error_400(value=None):
    return json_response(400, value)


@app.errorhandler(401)
def error_401(value=None):
    return json_response(401, value)


@app.errorhandler(403)
def error_403(value=None):
    return json_response(403, value)


@app.errorhandler(404)
def error_404(value=None):
    return json_response(404, value)


@app.errorhandler(415)
def error_415(value=None):
    return json_response(415, value)


@app.errorhandler(500)
def error_500(value=None):
    return json_response(500, value)


@app.errorhandler(501)
def error_501(value=None):
    return json_response(501, value)


def ok_200(value, include_properties):
    return json_response(200, value, include_properties)

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    actions.main(flask_app=app)
