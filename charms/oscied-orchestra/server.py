#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket, struct
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory, make_response, abort, send_file
from flask.views import View
from werkzeug.exceptions import HTTPException
from library.oscied_lib.pyutils.py_flask import json_response

import actions
from utils import md5Checksum, PlugItRedirect, PlugItSendFile

# Global parameters
DEBUG = True
MOCK = False

# PlugIt Parameters
PI_ALLOWED_NETWORKS = [u'127.0.0.1/32']  # IP allowed to use the PlugIt API
PI_BASE_URL = u'/'                       # Specify API endpoint allowing to share calls with another API
PI_META_CACHE = 0 if DEBUG else 5 * 60   # Number of seconds meta informations should be cached

## Does not edit code bellow !

# API version parameters
PI_API_NAME, PI_API_VERSION = u'EBUio-PlugIt', u'1'

STATIC_FOLDER = u'media'
STATIC_URL_PATH = PI_BASE_URL + STATIC_FOLDER

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path=STATIC_URL_PATH)


def check_ip(request):

    def address_in_network(ip, network):
        u"""Return True if the ``ip`` address is in the ``network``."""
        #http://stackoverflow.com/questions/819355/how-can-i-check-if-an-ip-is-in-a-network-in-python
        ipaddr = struct.unpack(u'=L', socket.inet_aton(ip))[0]
        netaddr, bits = network.split(u'/')
        if int(bits) == 0:
            return True
        netmask = struct.unpack(u'=L', socket.inet_aton(netaddr))[0] & ((2L << int(bits)-1) - 1)
        return ipaddr & netmask == netmask

    for network in PI_ALLOWED_NETWORKS:
        if address_in_network(request.remote_addr, network):
            return True

    abort(404)
    return False


@app.route(PI_BASE_URL + u'ping')
def ping():
    u"""The ping method: Just return the data provided."""
    if check_ip(request):
        return jsonify(data=request.args.get(u'data', u''))


@app.route(PI_BASE_URL + u'version')
def version():
    u"""The version method: Return current information about the version."""
    return jsonify(result=u'Ok', version=PI_API_VERSION, protocol=PI_API_NAME)


class MetaView(View):
    u"""The dynamic view (based on the current action) for the /meta method."""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):

        if not check_ip(request):
            return

        response_obj = {}

        # Template information
        response_obj[u'template_tag'] = (u'' if self.action.pi_api_template == u'' else
                                         md5Checksum(u'templates/{0}'.format(self.action.pi_api_template)))

        for attribute in (
            # User restriction
            u'pi_api_only_logged_user', u'pi_api_only_member_user', u'pi_api_only_admin_user',
            # Cache information
            u'pi_api_cache_time', u'pi_api_cache_by_user',
            # Only json
            u'pi_api_user_info', u'pi_api_json_only'):
            if hasattr(self.action, attribute):
                response_obj[attribute] = getattr(self.action, attribute)

        # Add the cache headers and return final response
        response = make_response(jsonify(response_obj))
        expires = datetime.utcnow() + timedelta(seconds=PI_META_CACHE)
        expires = expires.strftime(u'%a, %d %b %Y %H:%M:%S GMT')
        response.headers[u'Expire'] = expires
        response.headers[u'Cache-Control'] = u'public, max-age={0}'.format(PI_META_CACHE)
        return response


class TemplateView(View):
    u"""The dynamic view (based on the current action) for the /template method."""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):
        if check_ip(request):
            # We just return the content of the template
            return send_from_directory(u'templates/', self.action.pi_api_template)


class ActionView(View):
    u"""The dynamic view (based on the current action) for the /action method."""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):

        if not check_ip(request):
            return

        # Call the action
        try:
            result = self.action(request, *args, **kwargs)
        except HTTPException as e:
            return jsonify({u'ebuio_abort': e.description})

        # Is it a redirect ?
        if isinstance(result, PlugItRedirect):
            response = make_response(u'')
            response.headers[u'EbuIo-PlugIt-Redirect'] = result.url
            if result.no_prefix:
                response.headers[u'EbuIo-PlugIt-Redirect-NoPrefix'] = u'True'
            return response
        elif isinstance(result, PlugItSendFile):
            response = send_file(result.filename, mimetype=result.mimetype, as_attachment=result.as_attachment,
                                 attachment_filename=result.attachment_filename)
            response.headers[u'EbuIo-PlugIt-ItAFile'] = u'True'
            return response

        return jsonify(result)


# Register the 3 URLs (meta, template, action) for each actions
# We test for each element in the module actions if it's an action (added by the decorator in utils)
for act in dir(actions):
    obj = getattr(actions, act)
    if hasattr(obj, u'pi_api_action') and obj.pi_api_action:
        # We found an action and we can now add it to our routes

        # Meta
        app.add_url_rule(u'{0}meta{1}'.format(PI_BASE_URL, obj.pi_api_route),
                         view_func=MetaView.as_view(u'meta_{0}'.format(act), action=obj))

        # Template
        app.add_url_rule(u'{0}template{1}'.format(PI_BASE_URL, obj.pi_api_route),
                         view_func=TemplateView.as_view(u'template_{0}'.format(act), action=obj))

        # Action
        app.add_url_rule(u'{0}action{1}'.format(PI_BASE_URL, obj.pi_api_route),
                         view_func=ActionView.as_view(u'action_{0}'.format(act), action=obj),
                         methods=obj.pi_api_methods)


# Responses ------------------------------------------------------------------------------------------------------------

@app.errorhandler(400)
def error_400(value=None):
    return json_response(400, value=value, include_properties=False)


@app.errorhandler(401)
def error_401(value=None):
    return json_response(401, value=value, include_properties=False)


@app.errorhandler(403)
def error_403(value=None):
    return json_response(403, value=value, include_properties=False)


@app.errorhandler(404)
def error_404(value=None):
    return json_response(404, value=value, include_properties=False)


@app.errorhandler(415)
def error_415(value=None):
    return json_response(415, value=value, include_properties=False)


@app.errorhandler(500)
def error_500(value=None):
    return json_response(500, value=value, include_properties=False)


@app.errorhandler(501)
def error_501(value=None):
    return json_response(501, value=value, include_properties=False)


# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    actions.main(flask_app=app, mock=MOCK)
