#! /usr/bin/env python
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : ORCHESTRA
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012 OSCIED Team. All rights reserved.
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
# Retrieved from:
#   svn co https://claire-et-david.dyndns.org/prog/OSCIED

# FIXME mongo concurrency : http://emptysquare.net/blog/requests-in-python-and-mongodb/

import logging
import sys
from flask import Flask, abort, request, Response
from lib.Media import Media
from lib.Orchestra import Orchestra
from lib.OrchestraConfig import OrchestraConfig
from lib.TransformProfile import TransformProfile
from lib.User import User
from lib.Utilities import object2json, valid_uuid, setup_logging


# Global variables ---------------------------------------------------------------------------------

app = Flask(__name__)


# --------------------------------------------------------------------------------------------------
# http://publish.luisrei.com/articles/flaskrest.html

def requires_auth(request, allow_root=False, allow_node=False, allow_any=False, role=None, id=None,
                  mail=None):
    """
    This method implements Orchestra's RESTful API authentication logic. Here is ensured that an
    access to a method of the API is filtered based on rules (this method's parameters).
    HTTP user agent must authenticate through HTTP basic access authentication. The username must
    be user's email address and password must be user's secret. This not apply for system-users like
    root or node as they do not have any e-mail address.

    .. warning::

        Username and password are passed as plaintext, SSL/TLS is one of the way to improve security
        although this was not tested during my thesis.

    This method will abort request with HTTP 401 error if HTTP user agent doesn't authenticate.

    :param request: the request itself, credentials are retrieved from request authorization header
    :param allow_root: if set to `True` root system-user will be allowed
    :param allow_node: if set to `True` node system-user will be allowed
    :param allow_any: if set to `True` any authenticated user will be allowed
    :param role: if set to <name>, any user will "name" role set to `True` will be allowed
    :param id: if set to <uuid>, any user with _id equal to "uuid" will be allowed
    :param mail: if set to <mail>, any user with mail equal to "mail" will be allowed

    This method will abort request with HTTP 403 error if none of the following conditions are met.

    Example::

        # Allow any authenticated user
        @app.route('/my/example/route', methods=['GET'])
        def api_my_example_route():
            if request.method == 'GET':
                auth_user = requires_auth(request=request, allow_any=True)
                ...
                return ok_200('my return value', True)

        # Allow root system-user or any user with admin attribute set
        @app.route('/my/restricted/route', methods=['GET'])
        def api_my_restricted_route():
            if request.method == 'GET':
                auth_user = requires_auth(request=request, allow_root=True, allow_role='admin')
                ...
                return ok_200('my return value', True)
    """
    auth = request.authorization
    if not auth or auth.username is None or auth.password is None:
        abort(401, 'Authenticate.')  # Testing for None is maybe too much ... Security is like that
    username = auth.username
    password = auth.password
    root = (username == 'root' and password == orchestra.config.root_secret)
    node = (username == 'node' and password == orchestra.config.nodes_secret)
    user = None
    if not root and not node:
        user = orchestra.get_user({'mail': username}, secret=password)
        username = user.name if user else None
    if not root and not user and not node:
        abort(401, 'Authentication Failed.')
    if root and allow_root:
        logging.info('Allowed authenticated root')
        return orchestra.root_user
    if node and allow_node:
        logging.info('Allowed authenticated worker/node')
        return orchestra.nodes_user
    if user and allow_any:
        logging.info('Allowed authenticated user ' + user.name)
        return user
    if role and hasattr(user, role) and getattr(user, role):
        logging.info('Allowed authenticated user ' + user.name + ' with role ' + role)
        return user
    if id and user._id == id:
        logging.info('Allowed authenticated user ' + user.name + ' with id ' + id)
        return user
    if mail and user.mail == mail:
        logging.info('Allowed authenticated user ' + user.name + ' with mail ' + mail)
        return user
    abort(403, username)


# Utilities ----------------------------------------------------------------------------------------


def check_id(id):
    if not valid_uuid(id, False):
        abort(415, 'Wrong id format ' + id)


@app.errorhandler(400)
def error_400(value=None):
    response = Response(response=object2json({'status': 400, 'value': value}, False),
                        status=400, mimetype="application/json")
    response.status_code = 400
    return response


@app.errorhandler(401)
def error_401(value=None):
    response = Response(response=object2json({'status': 401, 'value': value}, False),
                        status=401, mimetype="application/json")
    response.status_code = 401
    return response


@app.errorhandler(403)
def error_403(value=None):
    response = Response(response=object2json({'status': 403, 'value': value}, False),
                        status=403, mimetype="application/json")
    response.status_code = 403
    return response


@app.errorhandler(404)
def error_404(value=None):
    response = Response(response=object2json({'status': 404, 'value': value}, False),
                        status=404, mimetype="application/json")
    response.status_code = 404
    return response


@app.errorhandler(415)
def error_415(value=None):
    response = Response(response=object2json({'status': 415, 'value': value}, False),
                        status=415, mimetype="application/json")
    response.status_code = 415
    return response


@app.errorhandler(501)
def error_501(value=None):
    response = Response(response=object2json({'status': 501, 'value': value}, False),
                        status=501, mimetype="application/json")
    response.status_code = 501
    return response


def ok_200(value, include_properties):
    response = Response(response=object2json({'status': 200, 'value': value}, include_properties),
                        status=200, mimetype="application/json")
    response.status_code = 200
    return response


# Index --------------------------------------------------------------------------------------------

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def api_root():
    """
    Return an about string.

    This method is actually used by Orchestra charm's hooks to check API's status.

    **Example request**:

    .. sourcecode:: http

        GET / HTTP/1.1
        Host: example.com
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200, "value":
          "Orchestra : EBU's OSCIED Orchestrator by David Fischer 2012\\n"
        }

    :Allowed: Any user (including unauthenticated)
    :statuscode 200: OK
    """
    return "Orchestra : EBU's OSCIED Orchestrator by David Fischer 2012\n"


# System management --------------------------------------------------------------------------------

@app.route('/flush', methods=['POST'])
def api_flush():
    """
    Flush Orchestrator's database.

    This method is useful for test/development purposes.

    **Example request**:

    .. sourcecode:: http

        POST /flush HTTP/1.1
        Host: example.com
        Header: root:password
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {"status": 200, "value": "Orchestra database flushed !"}

    :Allowed: Only root
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_root=True)
    orchestra.flush_db()
    return ok_200('Orchestra database flushed !', False)


# Users management ---------------------------------------------------------------------------------

@app.route('/user/login', methods=['GET'])
def api_user_login():
    """
    Return authenticated user serialized to JSON if authentication passed (without ``secret`` field).

    This method is useful for WebUI to simulate stateful login scheme and get informations about the
    user.

    .. note::

        This is kind of duplicate with API's GET /user/id/`id` method ...

    **Example request**:

    .. sourcecode:: http

        GET /user/login HTTP/1.1
        Host: somewhere.com
        Header: tabby@bernex.ch:miaow
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "c4daa8a6-6be4-11e2-ae91-3085a9accb47",
            "first_name": "Tabby",
            "last_name": "Fischer",
            "name": "Tabby Fischer",
            "mail": "tabby@bernex.ch",
            "admin_platform": false
          }
        }

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    auth_user = requires_auth(request=request, allow_any=True)
    delattr(auth_user, 'secret')  # do not send back user's secret
    return ok_200(auth_user, True)


@app.route('/user/count', methods=['GET'])
def api_user_count():
    """
    Return users count.

    **Example request**:

    .. sourcecode:: http

        GET /user/count HTTP/1.1
        Host: somewhere.com
        Header: bram@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {"status": 200, "value": 5000}

    :Allowed: Root and any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_root=True, allow_any=True)
    return ok_200(orchestra.get_users_count(), False)


@app.route('/user', methods=['GET'])
def api_user_get():
    """
    Return an array containing the users serialized to JSON (without ``secret`` fields).

    **Example request**:

    .. sourcecode:: http

        GET /user HTTP/1.1
        Host: somewhere.com
        Header: peter@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": [{"_id": "...", "...": "..."}, {"_id": "..."}]
        }

    :Allowed: Root and user with admin_platform attribute set
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_root=True, role='admin_platform')
    return ok_200(orchestra.get_users(specs=None, fields={'secret': 0}), True)


@app.route('/user', methods=['POST'])
def api_user_post():
    """
    Add an user.

    **Example request**:

    .. sourcecode:: http

        POST /user HTTP/1.1
        Host: somewhere.com
        Header: kouadi@oscied.org:oscied
        Accept: application/json
        Content-Type: application/json

        {
          "first_name": "Laurent",
          "last_name": "Nicolet",
          "mail": "laurent@comique.ch",
          "secret": "genevois_style",
          "admin_platform": false
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "8bda488c-6be8-11e2-89b7-3085a9accb47",
            "first_name": "Laurent",
            "last_name": "Nicolet",
            "name": "Laurent Nicolet",
            "mail": "laurent@comique.ch",
            "admin_platform": false
          }
        }

    :Allowed: Root and user with admin_platform attribute set
    :query first_name: New user's first name (required)
    :query last_name: New user's last name (required)
    :query mail: New user's email address (required)
    :query secret: New user's secret (required)
    :query admin_platform: New user's admin_platform (required)
    :statuscode 200: OK
    :statuscode 400: on type or value error
    :statuscode 400: Key ``key`` not found.
    :statuscode 400: The email address ``mail`` is already used by another user.
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 415: Requires (valid) json content-type.
    """
    requires_auth(request=request, allow_root=True, role='admin_platform')
    try:
        data = request.json
        if not data:
            abort(415, 'Requires json content-type.')
    except:
        abort(415, 'Requires valid json content-type.')
    try:
        user = User(None, data['first_name'], data['last_name'], data['mail'], data['secret'],
                          data['admin_platform'])
        orchestra.save_user(user, hash_secret=True)
    except (ValueError, TypeError) as error:
        abort(400, str(error))
    except KeyError as error:
        abort(400, 'Key ' + str(error) + ' not found.')
    delattr(user, 'secret')  # do not send back user's secret
    return ok_200(user, True)


@app.route('/user/id/<id>', methods=['GET'])
def api_user_id_get(id):
    """
    Return an user serialized to JSON (without ``secret`` field).

    **Example request**:

    .. sourcecode:: http

        GET /user/id/c4daa8a6-6be4-11e2-ae91-3085a9accb47 HTTP/1.1
        Host: somewhere.com
        Header: michael@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "c4daa8a6-6be4-11e2-ae91-3085a9accb47",
            "first_name": "Tabby",
            "last_name": "Fischer",
            "name": "Tabby Fischer",
            "mail": "tabby@bernex.ch",
            "admin_platform": false
          }
        }

    :Allowed: Root and any user
    :param id: id of user to get
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No user with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    """
    check_id(id)
    requires_auth(request=request, allow_root=True, allow_any=True)
    user = orchestra.get_user(specs={'_id': id}, fields={'secret': 0})
    if not user:
        abort(404, 'No user with id ' + id + '.')
    return ok_200(user, True)


@app.route('/user/id/<id>', methods=['PATCH', 'PUT'])
def api_user_id_patch(id):
    """
    Update an user.

    User's admin_platform attribute can only be modified by root or any authenticated user with
    admin_platform attribute set.

    **Example request**:

    .. sourcecode:: http

        PUT /user/id/8bda488c-6be8-11e2-89b7-3085a9accb47 HTTP/1.1
        Host: somewhere.com
        Header: loic@oscied.org:oscied
        Accept: application/json
        Content-Type: application/json

        {
          "mail": "laurent.nicolet@comiques.ch",
          "secret": "gnevois_style",
          "admin_platform": true
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": "The user \\"Laurent Nicolet\\" has been updated."
        }

    :Allowed: Root, user with admin_platform attribute set or the user itself
    :param id: id of user to get
    :query first_name: User's first name (optional)
    :query last_name: User's last name (optional)
    :query mail: User's email address (optional)
    :query secret: User's secret (optional)
    :query admin_platform: User's admin_platform (optional)
    :statuscode 200: OK
    :statuscode 400: on type or value error
    :statuscode 400: Key ``key`` not found.
    :statuscode 400: The email address ``mail`` is already used by another user.
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No user with id ``id``
    :statuscode 415: Wrong id format ``id``.
    :statuscode 415: Requires (valid) json content-type.
    """
    check_id(id)
    auth_user = requires_auth(request=request, allow_root=True, role='admin_platform', id=id)
    user = orchestra.get_user(specs={'_id': id})
    try:
        data = request.json
    except:
        abort(415, 'Requires valid json content-type.')
    if not data:
        abort(415, 'Requires json content-type.')
    if not user:
        abort(404, 'No user with id ' + id + '.')
    try:
        old_name = user.name
        first_name = data['first_name'] if 'first_name' in data else user.first_name
        last_name = data['last_name'] if 'last_name' in data else user.last_name
        mail = data['mail'] if 'mail' in data else user.mail
        secret = data['secret'] if 'secret' in data else user.secret
        ap = user.admin_platform
        if auth_user.admin_platform and 'admin_platform' in data:
            ap = data['admin_platform']
        new_user = User(id, first_name, last_name, mail, secret, ap)
        orchestra.save_user(new_user, hash_secret=True)
    except (ValueError, TypeError) as error:
        abort(400, str(error))
    except KeyError as error:
        abort(400, 'Key ' + str(error) + ' not found.')
    return ok_200('The user "' + old_name + '" has been updated.', False)


@app.route('/user/id/<id>', methods=['DELETE'])
def api_user_id_delete(id):
    """
    Delete an user.

    **Example request**:

    .. sourcecode:: http

        DELETE /user/id/8bda488c-6be8-11e2-89b7-3085a9accb47 HTTP/1.1
        Host: somewhere.com
        Header: laurent.nicolet@comiques.ch:gnevois_style
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": "The user \\"Laurent Nicolet\\" has been deleted."
        }

    :Allowed: Root, user with admin_platform attribute set or the user itself
    :param id: id of user to delete
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No user with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    """
    check_id(id)
    requires_auth(request=request, allow_root=True, role='admin_platform', id=id)
    user = orchestra.get_user(specs={'_id': id})
    if not user:
        abort(404, 'No user with id ' + id + '.')
    orchestra.delete_user(user)
    return ok_200('The user "' + user.name + '" has been deleted.', False)


# Medias management --------------------------------------------------------------------------------

@app.route('/media/count', methods=['GET'])
def api_media_count():
    """
    Return medias count.

    **Example request**:

    .. sourcecode:: http

        GET /media/count HTTP/1.1
        Host: somewhere.com
        Header: tewfiq@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {"status": 200, "value": 8000}

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_medias_count(), False)


@app.route('/media/HEAD', methods=['GET'])
def api_media_head():
    """
    Return an array containing the medias serialized to JSON.

    **Example request**:

    .. sourcecode:: http

        GET /media/HEAD HTTP/1.1
        Host: somewhere.com
        Header: andres@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": [{"_id": "...", "...": "..."}, {"_id": "..."}]
        }

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_medias(), True)


@app.route('/media', methods=['GET'])
def api_media_get():
    """
    Return an array containing the medias serialized to JSON.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.

    **Example request**:

    .. sourcecode:: http

        GET /media HTTP/1.1
        Host: somewhere.com
        Header: nabil@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": [{"_id": "...", "...": "..."}, {"_id": "..."}]
        }

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_medias(load_fields=True), True)


@app.route('/media', methods=['POST'])
def api_media_post():
    """
    Add a media.

    This method handle registration of already uploaded media to the shared storage.
    For example, the WebUI will upload a media to uploads path **before** registering it
    with this method.

    Medias in the shared storage are renamed with the following convention:
        ``storage_root``/medias/``user_id``/``media_id``

    When published or downloaded, media will be renamed to ``virtual_filename``.
    Spaces ( ) are not allowed and they will be converted to underscores (_).

    Media's ``metadata`` must contain any valid JSON string. Only the ``title`` key is required.
    The orchestrator will automatically add ``add_date`` and ``duration`` to ``metadata``.

    .. note::

        Registration of external media (aka. http://) will be an interesting improvement.

    **Example request**:

    .. sourcecode:: http

        POST /media HTTP/1.1
        Host: somewhere.com
        Header: d@f.com:oscied
        Accept: application/json
        Content-Type: application/json

        {
          "uri": "glusterfs://<address>/medias_volume/uploads/
                  Project London - Official Trailer [2009].mp4",
          "virtual_filename": "Project_London_trailer_2009.mp4",
          "metadata":
          {
            "title": "Project London - Official Trailer (2009)"
          }
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "96590fdc-74f8-11e2-8c58-3085a9acc651",
            "user_id": "1298f206-74f8-11e2-9b82-3085a9acc11b",
            "parent_id": null,
            "uri": "glusterfs://<address>/medias_volume/medias/
                    <user_id>/<media_id>",
            "public_uris": null,
            "virtual_filename": "Project_London_trailer_2009.mp4",
            "metadata": {
              "add_date": "2013-02-02 14:05",
              "duration": "00:02:44.88", "size": 54871886,
              "title": "Project London - Official Trailer (2009)"
            },
            "status": "READY"
          }
        }

    :Allowed: Any user can do that
    :query uri: Media's source URI, actually only shared storage's URI are handled (required)
    :query virtual_filename: Media's filename when downloaded or published (required)
    :query metadata: JSON string containing metadatas about the media (required)
    :statuscode 200: OK
    :statuscode 400: on type or value error
    :statuscode 400: Key ``key`` not found.
    :statuscode 400: The media uri ``uri`` is already used by another media.
    :statuscode 400: Title key is required in media metadata.
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: An error occured : ``OSError``
    :statuscode 415: Requires (valid) json content-type.
    :statuscode 501: FIXME Add of external uri not implemented.
    """
    auth_user = requires_auth(request=request, allow_any=True)
    try:
        data = request.json
    except:
        abort(415, 'Requires valid json content-type.')
    if not data:
        abort(415, 'Requires json content-type.')
    try:
        media = Media(None, auth_user._id, None, data['uri'], None,
                      data['virtual_filename'], data['metadata'], 'READY')
        orchestra.save_media(media)
    except (ValueError, TypeError) as error:
        abort(400, str(error))
    except KeyError as error:
        abort(400, 'Key ' + str(error) + ' not found.')
    except IndexError as error:
        abort(404, str(error))
    except NotImplementedError as error:
        abort(501, str(error))
    return ok_200(media, True)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@app.route('/media/id/<id>/HEAD', methods=['GET'])
def api_media_id_head(id):
    """
    Return a media serialized to JSON.

    **Example request**:

    .. sourcecode:: http

        GET /media/id/96590fdc-74f8-11e2-8c58-3085a9acc651/HEAD HTTP/1.1
        Host: somewhere.com
        Header: monique@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "b8b9ae78-74f8-11e2-8dae-3085a9accbc1",
            "user_id": "4e8ec55e-74f7-11e2-8451-3085a9acc8e0b",
            "parent_id": null,
            "uri": "glusterfs://<address>/medias_volume/medias/
                    <user_id>/<media_id>",
            "public_uris": null,
            "virtual_filename": "Psy_gangnam_style.flv",
            "metadata": {
              "duration": "00:04:12.16",
              "add_date": "2013-02-11 22:37",
              "title": "Psy - Gangnam Style",
              "size": 183190475
            },
            "status": "READY"
          }
        }

    :Allowed: Any user
    :param id: id of media to get
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No media with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    """
    check_id(id)
    requires_auth(request=request, allow_any=True)
    media = orchestra.get_media(specs={'_id': id})
    if not media:
        abort(404, 'No media with id ' + id + '.')
    return ok_200(media, True)


@app.route('/media/id/<id>', methods=['GET'])
def api_media_id_get(id):
    """
    Return a media serialized to JSON.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.

    **Example request**:

    .. sourcecode:: http

        GET /media/id/96590fdc-74f8-11e2-8c58-3085a9acc651 HTTP/1.1
        Host: somewhere.com
        Header: estelle@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "b8b9ae78-74f8-11e2-8dae-3085a9accbc1",
            "user": {
            "_id": "4e8ec55e-74f7-11e2-8451-3085a9acc8e0b",
              "first_name": "David",
              "last_name": "Fischer",
              "name": "David Fischer",
              "mail": "d@f.com",
              "admin_platform": true
            },
            "parent": null,
            "uri": "glusterfs://<address>/medias_volume/medias/
                    <user_id>/<media_id>",
            "public_uris": null,
            "virtual_filename": "Psy_gangnam_style.flv",
            "metadata": {
              "duration": "00:04:12.16",
              "add_date": "2013-02-11 22:37",
              "title": "Psy - Gangnam Style",
              "size": 183190475
            },
            "status": "READY"
          }
        }

    :Allowed: Any user
    :param id: id of media to get
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No media with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    :statuscode 415: Requires json content-type.
    """
    check_id(id)
    requires_auth(request=request, allow_any=True)
    media = orchestra.get_media(specs={'_id': id}, load_fields=True)
    if not media:
        abort(404, 'No media with id ' + id + '.')
    return ok_200(media, True)


@app.route('/media/id/<id>', methods=['PATCH', 'PUT'])
def api_media_id_patch(id):
    """
    Update a media (only virtual_filename and metadata field can be updated).

   **Example request**:

    .. sourcecode:: http

        PUT /media/id/a396fe66-74ee-11e2-89ad-3085a9accbb8 HTTP/1.1
        Host: somewhere.com
        Header: anthony@oscied.org:oscied
        Accept: application/json
        Content-Type: application/json

        {"virtual_filename": "the_fifth_element.mp4"}

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": "The media \\"fifth_element.mp4\\" has been updated."
        }

    :Allowed: Only the author of the media
    :param id: media's id
    :query virtual_filename: Media's filename when downloaded or published (optional)
    :query metadata: JSON string containing metadatas about the media (optional)
    :statuscode 200: OK
    :statuscode 400: Key ``key`` not found. *or* on type or value error
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 403: You are not allowed to modify media with id ``id``.
    :statuscode 404: No media with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    :statuscode 415: Requires (valid) json content-type.
    """
    check_id(id)
    auth_user = requires_auth(request=request, allow_any=True)
    media = orchestra.get_media(specs={'_id': id})
    try:
        data = request.json
    except:
        abort(415, 'Requires valid json content-type.')
    if not data:
        abort(415, 'Requires json content-type.')
    if not media:
        abort(404, 'No media with id ' + id + '.')
    if auth_user._id != media.user_id:
        abort(403, 'You are not allowed to modify media with id ' + id + '.')
    try:
        old_virtual_filename = media.virtual_filename
        if 'virtual_filename' in data:
            media.virtual_filename = data['virtual_filename']
        if 'metadata' in data:
            media.metadata = data['metadata']
        orchestra.save_media(media)
    except (ValueError, TypeError) as error:
        abort(400, str(error))
    except KeyError as error:
        abort(400, 'Key ' + str(error) + ' not found.')
    return ok_200('The media "' + old_virtual_filename + '" has been updated.', False)


@app.route('/media/id/<id>', methods=['DELETE'])
def api_media_id_delete(id):
    """
    Delete a media.

    The media file is removed from the shared storage and media's status is set to DELETED.

   **Example request**:

    .. sourcecode:: http

        DELETE /media/id/a396fe66-74ee-11e2-89ad-3085a9accbb8 HTTP/1.1
        Host: somewhere.com
        Header: sandro@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": "The media \\"fifth_element.mp4\\" has been deleted."
        }

    :Allowed: Only the author of the media
    :param id: id of media to delete
    :statuscode 200: OK
    :statuscode 400: Cannot delete the media, it is actually in use by transform job with id ``id`` and status ``status``.
    :statuscode 400: Cannot delete the media, it is actually in use by publish job with id ``id`` and status ``status``.
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 403: You are not allowed to delete media with id ``id``.
    :statuscode 404: No media with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    :statuscode 501: FIXME Delete of external uri not implemented.
    """
    check_id(id)
    auth_user = requires_auth(request=request, allow_any=True)
    media = orchestra.get_media(specs={'_id': id})
    if not media:
        abort(404, 'No media with id ' + id + '.')
    if auth_user._id != media.user_id:
        abort(403, 'You are not allowed to delete media with id ' + id + '.')
    try:
        orchestra.delete_media(media)
    except ValueError as error:
        abort(400, str(error))
    except NotImplementedError as error:
        abort(501, str(error))
    return ok_200('The media "' + media.metadata['title'] + '" has been deleted.', False)


# Transform profiles management --------------------------------------------------------------------

@app.route('/transform/profile/encoder', methods=['GET'])
def api_transform_profile_encoder():
    """
    Return an array containing the names of the transform profile encoders.

    **Example request**:

    .. sourcecode:: http

        GET /transform/profile/encoder HTTP/1.1
        Host: somewhere.com
        Header: martin@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": ["copy", "ffmpeg", "dashcast"]
        }

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_transform_profile_encoders(), True)


@app.route('/transform/profile/count', methods=['GET'])
def api_transform_profile_count():
    """
    Return profiles count.

    **Example request**:

    .. sourcecode:: http

        GET /transform/profile/count HTTP/1.1
        Host: somewhere.com
        Header: nabil@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {"status": 200, "value": 100}

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_transform_profiles_count(), False)


@app.route('/transform/profile', methods=['GET'])
def api_transform_profile_get():
    """
    Return an array containing the transform profiles serialized to JSON.

    **Example request**:

    .. sourcecode:: http

        GET /transform/profile HTTP/1.1
        Host: somewhere.com
        Header: michel@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": [{"_id": "...", "...": "..."}, {"_id": "..."}]}

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_transform_profiles(), True)


@app.route('/transform/profile', methods=['POST'])
def api_transform_profile_post():
    """
    Add a transform profile.

    The transform profile's ``encoder_name`` attribute can be the following :

    * **copy** to bypass FFmpeg and do a simple file block copy ;
    * **ffmpeg** to transcode a media to another with FFMpeg ;
    * **dashcast** to transcode a media to MPEG-DASH with DashCast ;

    **Example request**:

    .. sourcecode:: http

        POST /transform/profile HTTP/1.1
        Host: somewhere.com
        Header: daniel@oscied.org:oscied
        Accept: application/json
        Content-Type: application/json

        {
          "title": "To MP4",
          "description": "Convert to MP4 (container)",
          "encoder_name": "ffmpeg",
          "encoder_string": "-acodec copy -vcodec copy -f mp4"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "c316ff1a-74f8-11e2-82d4-3085a9accd33",
            "title": "To MP4",
            "description": "Convert to MP4 (container)",
            "encoder_name": "ffmpeg",
            "encoder_string": "-acodec copy -vcodec copy -f mp4"
          }
        }

    :Allowed: Any user
    :query title: New profile's title (required)
    :query description: New profile's description (required)
    :query encoder_name: New profile's encoder name (required)
    :query encoder_string: New profile's encoder-specific string (required)
    :statuscode 200: OK
    :statuscode 400: Key ``key`` not found. *or* on type or value error
    :statuscode 400: Duplicate transform profile title ``profile``.
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 415: Requires (valid) json content-type.
    """
    requires_auth(request=request, allow_any=True)
    try:
        data = request.json
    except:
        abort(415, 'Requires valid json content-type.')
    if not data:
        abort(415, 'Requires json content-type.')
    try:
        profile = TransformProfile(None, data['title'], data['description'], data['encoder_name'],
                                   data['encoder_string'])
        orchestra.save_transform_profile(profile)
    except (ValueError, TypeError) as error:
        print str(error)
        abort(400, str(error))
    except KeyError as error:
        print str(error)
        abort(400, 'Key ' + str(error) + ' not found.')
    return ok_200(profile, True)


@app.route('/transform/profile/id/<id>', methods=['GET'])
def api_transform_profile_id_get(id):
    """
    Return a transform profile serialized to JSON.

    **Example request**:

    .. sourcecode:: http

        GET /transform/profile/id/c316ff1a-74f8-11e2-82d4-3085a9accd33 HTTP/1.1
        Host: somewhere.com
        Header: francois@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "c316ff1a-74f8-11e2-82d4-3085a9accd33",
            "title": "To MP4",
            "description": "Convert to MP4 (container)",
            "encoder_name": "ffmpeg",
            "encoder_string": "-acodec copy -vcodec copy -f mp4"
          }
        }

    :Allowed: Any user
    :param id: id of profile to get
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No transform profile with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    """
    check_id(id)
    requires_auth(request=request, allow_any=True)
    profile = orchestra.get_transform_profile(specs={'_id': id})
    if not profile:
        abort(404, 'No transform profile with id ' + id + '.')
    return ok_200(profile, True)


@app.route('/transform/profile/id/<id>', methods=['DELETE'])
def api_transform_profile_id_delete(id):
    """
    Delete a transform profile.

    **Example request**:

    .. sourcecode:: http

        DELETE /transform/profile/id/c316ff1a-(...)-3085a9accd33 HTTP/1.1
        Host: somewhere.com
        Header: dimitri@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": "The transform profile \\"To MP4\\" has been deleted."
        }

    :Allowed: Any user
    :param id: id of profile to delete
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No transform profile with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    """
    check_id(id)
    requires_auth(request=request, allow_any=True)
    profile = orchestra.get_transform_profile(specs={'_id': id})
    if not profile:
        abort(404, 'No transform profile with id ' + id)
    orchestra.delete_transform_profile(profile)
    return ok_200('The transform profile "' + profile.title + '" has been deleted.', False)


# Transformation workers (encoders) ----------------------------------------------------------------

## return transform worker list
#@app.route('/transform/worker', methods = ['GET'])
#def api_transform_unit():
#    return 'List of all transform units (TODO)\n'

## return a transform worker
#@app.route('/transform/worker/id/<id>', methods = ['GET'])
#def api_transform_unit_show(id):
#    try:
#        unit_id = uuid.UUID('{'+id+'}');
#    except ValueError:
#         abort(415)
#    return 'Informations about transform unit ' + str(unit_id)+' (TODO)\n'


# Transformation jobs (encoding) -------------------------------------------------------------------

@app.route('/transform/queue', methods=['GET'])
def api_transform_queue():
    """
    Return an array containing the transform queues serialized to JSON.

    **Example request**:

    .. sourcecode:: http

        GET /transform/queue HTTP/1.1
        Host: somewhere.com
        Header: marco@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": ["transform_amazon", "transform_ebu_geneva"]
        }

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_transform_queues(), True)


@app.route('/transform/job/count', methods=['GET'])
def api_transform_job_count():
    """
    Return transform jobs count.

    **Example request**:

    .. sourcecode:: http

        GET /transform/job/count HTTP/1.1
        Host: somewhere.com
        Header: marylene@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {"status": 200, "value": 15260}

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_transform_jobs_count(), False)


@app.route('/transform/job/HEAD', methods=['GET'])
def api_transform_job_head():
    """
    Return an array containing the transform jobs serialized as JSON.

    The transform jobs attributes are appended with the Celery's ``async result`` of the jobs.

    **Example request**:

    .. sourcecode:: http

        GET /transform/job/HEAD HTTP/1.1
        Host: somewhere.com
        Header: thomas@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": [{"_id": "...", "...": "..."}, {"_id": "..."}]
        }

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_transform_jobs(), True)


@app.route('/transform/job', methods=['GET'])
def api_transform_job_get():
    """
    Return an array containing the transform jobs serialized to JSON.

    The transform jobs attributes are appended with the Celery's ``async result`` of the jobs.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.

    **Example request**:

    .. sourcecode:: http

        GET /transform/job HTTP/1.1
        Host: somewhere.com
        Header: antoinette@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": [{"_id": "...", "...": "..."}, {"_id": "..."}]
        }

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_transform_jobs(load_fields=True), True)


@app.route('/transform/job', methods=['POST'])
def api_transform_job_post():
    """
    Launch a transform job.

    Any user can launch a transform job using any media as input and any transform profile.
    This is linked to media and transform profile API methods access policies.

    The output media is registered to the database with the PENDING status and the ``parent_id``
    field is set to input media's ``id``. This permit to know relation between medias !

    The orchestrator will automatically add ``add_date`` to ``statistic``.

    .. note::

        Interesting enhancement would be to :

        * Schedule obs by specifying start time (...) ;
        * Handle the registration of jobs related to PENDING medias ;

    **Example request**:

    .. sourcecode:: http

        POST /transform/job HTTP/1.1
        Host: somewhere.com
        Header: tabby@bernex.ch:miaow
        Accept: application/json
        Content-Type: application/json

        {
          "media_in_id": "a396fe66-74ee-11e2-89ad-3085a9accbb8",
          "profile_id": "c316ff1a-74f8-11e2-82d4-3085a9accd33",
          "virtual_filename": "avatar.mp4",
          "metadata": {"title": "Avatar (1080p)"},
          "queue": "transform_ebu-geneva"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {"status": 200, "value": "ea9088f0-74f8-11e2-b780-3085a9acccb2a"}

    :Allowed: Any user
    :query media_in_id: New job input media's id (required)
    :query profile_id: New job profile's id (required)
    :query virtual_filename: New job output media's virtual_filename (required)
    :query metadata: New  job output media's metadata (required)
    :query queue: The transform queue used to route the new job (required)
    :statuscode 200: OK
    :statuscode 400: Key ``key`` not found. *or* on type or value error
    :statuscode 400: Unable to transmit job to workers of queue ``queue``.
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No user with id ``id``.
    :statuscode 404: No media with id ``media_in_id``.
    :statuscode 404: No profile with id ``profile_id``.
    :statuscode 404: No transform queue with name ``queue``.
    :statuscode 415: Required (valid) json content-type.
    :statuscode 501: Cannot launch the job, input media status is ``status``.
    """
    auth_user = requires_auth(request=request, allow_any=True)
    try:
        data = request.json
    except:
        abort(415, 'Requires valid json content-type.')
    if not data:
        abort(415, 'Requires json content-type.')
    try:
        job_id = orchestra.launch_transform_job(auth_user._id, data['media_in_id'],
            data['profile_id'], data['virtual_filename'], data['metadata'], data['queue'],
            '/transform/callback')
    except (ValueError, TypeError) as error:
        abort(400, str(error))
    except KeyError as error:
        abort(400, 'Key ' + str(error) + ' not found.')
    except IndexError as error:
        abort(404, str(error))
    except NotImplementedError as error:
        abort(501, str(error))
    return ok_200(job_id, True)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@app.route('/transform/job/id/<id>/HEAD', methods=['GET'])
def api_transform_job_id_head(id):
    """
    Return a transform job serialized to JSON.

    The transform job attributes are appended with the Celery's ``async result`` of the job.

    **Example request**:

    .. sourcecode:: http

        GET /transform/job/id/48c111c8-74f8-11e2-a7a8-3085a9acc6c4/HEAD HTTP/1.1
        Host: somewhere.com
        Header: edoardo@oscied.org:oscied
        Accept: application/json
        Content-Type: application/json

    **Example response**:

    Floating numbers are here with "" for autoflask to work !!

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "48c111c8-74f8-11e2-a7a8-3085a9acc6c4",
            "user_id": "4e8a1bce-74f3-11e2-9660-3085a9acce0b",
            "media_in_id": "a8a165b8-74f7-11e2-a59e-3085a9acc049",
            "media_out_id": "52ea73ac-74f3-11e2-afdb-3085a9acc5ff",
            "profile_id": "55da66d6-74f3-11e2-9dff-3085a9acce4e",
            "statistic": {
              "add_date": "2013-02-11 22:44",
              "start_date": "2013-02-11 22:44",
              "elapsed_time": "19.241864919662476",
              "eta_time": 0, "percent": 100,
              "media_in_size": 54871886, "media_in_duration": "00:02:44.88",
              "media_out_size": 25601528, "media_out_duration": "00:00:01.95"
            },
            "revoked": false,
            "status": "SUCCESS"
          }
        }

    :Allowed: Any user
    :param id: id of job to get
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No transform job with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    """
    check_id(id)
    requires_auth(request=request, allow_any=True)
    job = orchestra.get_transform_job(specs={'_id': id})
    if not job:
        abort(404, 'No transform job with id ' + id + '.')
    return ok_200(job, True)


@app.route('/transform/job/id/<id>', methods=['GET'])
def api_transform_job_id_get(id):
    """
    Return a transform job serialized to JSON.

    The transform job attributes are appended with the Celery's ``async result`` of the job.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.

    **Example request**:

    .. sourcecode:: http

        GET /transform/job/id/ea9088f0-74f8-11e2-b780-3085a9acccb2a HTTP/1.1
        Host: somewhere.com
        Header: claire@oscied.org:oscied
        Accept: application/json
        Content-Type: application/json

    **Example response**:

    Floating numbers are here with "" for autoflask to work !!

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "48c111c8-74f8-11e2-a7a8-3085a9acc6c4",
            "user": {
              "_id": "4e8ec55e-74f7-11e2-8451-3085a9acc8e0b",
              "first_name": "David",
              "last_name": "Fischer",
              "name": "David Fischer",
              "mail": "d@f.com",
              "admin_platform": true
            },
            "media_in": {
              "_id": "a8a165b8-74f7-11e2-a59e-3085a9acc049",
              "user_id": "4e8a1bce-74f3-11e2-9660-3085a9acce0b",
              "parent_id": null,
              "uri": "glusterfs://<address>/medias_volume/medias/
                      <user_id>/<media_id>",
              "public_uris": {
                "c697f528-74f7-11e2-96a3-3085a9accc5d":
                "http://10.0.3.254/medias/<user_id>/<media_id>/
                 Project_London_trailer_2009.mp4"
              },
              "virtual_filename": "Project_London_trailer_2009.mp4",
              "metadata": {
                "add_date": "2013-02-11 22:37",
                "duration": "00:02:44.88", "size": 54871886,
                "title": "Project London - Official Trailer (2009)"
              },
              "status": "PUBLISHED"
            },
            "media_out": {
              "_id": "52ea73ac-74f3-11e2-afdb-3085a9acc5ff",
              "user_id": "4e8ec55e-74f7-11e2-8451-3085a9acc8e0b",
              "parent_id": "a8a165b8-74f7-11e2-a59e-3085a9acc049",
              "uri": "glusterfs://<address>/medias_volume/medias/
                      <user_id>/<media_id>",
              "public_uris": null,
              "virtual_filename": "project_london.mp2",
              "metadata": {
                "add_date": "2013-02-11 22:44",
                "duration": "00:00:01.95", "size": 25601528,
                "title": "Project London MP2"
              }
              "status": "READY"
            },
            "profile": {
              "_id": "55da66d6-74f3-11e2-9dff-3085a9acce4e",
              "title": "To MP2",
              "description":
                "Convert video track to MPEG-2 format, copy audio track",
              "encoder_name": "ffmpeg",
              "encoder_string":
                "-acodec copy -vcodec mpeg2video -f mpeg2video"
            },
            "statistic": {
                "add_date": "2013-02-11 22:44",
                "start_date": "2013-02-11 22:44",
                "elapsed_time": "19.241864919662476",
                "eta_time": 0, "percent": 100,
                "media_in_size": 54871886, "media_in_duration": "00:02:44.88",
                "media_out_size": 25601528, "media_out_duration": "00:00:01.95"
            },
            "revoked": false,
            "status": "SUCCESS"
          }
        }

    :Allowed: Any user
    :param id: id of job to get
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No transform job with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    """
    check_id(id)
    requires_auth(request=request, allow_any=True)
    job = orchestra.get_transform_job(specs={'_id': id}, load_fields=True)
    if not job:
        abort(404, 'No transform job with id ' + id + '.')
    return ok_200(job, True)


@app.route('/transform/job/id/<id>', methods=['DELETE'])
def api_transform_job_id_delete(id):
    """
    Revoke a transform job.

    This method do not delete jobs from jobs database but set ``revoked`` attribute in jobs database
    and broadcast revoke request to transform units with Celery. If the job is actually running it
    will be canceled. The output media will be deleted.

    **Example request**:

    .. sourcecode:: http

        DELETE /transform/job/id/ea9088f0-74f8-11e2-b780-3085a9acccb2a HTTP/1.1
        Host: somewhere.com
        Header: tabby@bernex.ch:miaow
        Accept: application/json
        Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": "The transform job \\"<job_id>\\" has been revoked.
                    Corresponding output media will be deleted."
        }

    :Allowed: Only author of the job
    :param id: id of job to delete
    :statuscode 200: OK
    :statuscode 400: on value error
    :statuscode 400: Transform job ``id`` is already revoked !
    :statuscode 400: Cannot revoke a transform job with status ``status``.
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 403: You are not allowed to revoke transform job with id ``id``.
    :statuscode 404: No transform job with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    """
    check_id(id)
    auth_user = requires_auth(request=request, allow_any=True)
    job = orchestra.get_transform_job(specs={'_id': id})
    if not job:
        abort(404, 'No transform job with id ' + id + '.')
    if auth_user._id != job.user_id:
        abort(403, 'You are not allowed to revoke transform job with id ' + id + '.')
    try:
        orchestra.revoke_transform_job(job=job, terminate=True, remove=False, delete_media=True)
    except ValueError as error:
        abort(400, str(error))
    return ok_200('The transform job "' + job._id +
                  '" has been revoked. Corresponding output media will be deleted.', False)


# Publishing jobs ----------------------------------------------------------------------------------

@app.route('/publish/queue', methods=['GET'])
@app.route('/publisher/queue', methods=['GET'])
@app.route('/unpublish/queue', methods=['GET'])
def api_publish_queue():
    """
    Return an array containing the publish queues.

    **Example request**:

    .. sourcecode:: http

        GET /publish/queue HTTP/1.1
        Host: somewhere.com
        Header: jean-claude@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": ["publisher_london", "publisher_ebu_geneva"]
        }

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_publisher_queues(), True)


@app.route('/publish/job/count', methods=['GET'])
def api_publish_job_count():
    """
    Return publish jobs count.

    **Example request**:

    .. sourcecode:: http

        GET /publish/job/count HTTP/1.1
        Host: somewhere.com
        Header: sophie@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {"status": 200, "value": 3904}

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_publish_jobs_count(), False)


@app.route('/publish/job/HEAD', methods=['GET'])
def api_publish_job_head():
    """
    Return an array containing the publish jobs serialized as JSON.

    The publish jobs attributes are appended with the Celery's ``async result`` of the jobs.

    **Example request**:

    .. sourcecode:: http

        GET /publish/job/HEAD HTTP/1.1
        Host: somewhere.com
        Header: antonin@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": [{"_id": "...", "...": "..."}, {"_id": "..."}]
        }

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_publish_jobs(), True)


@app.route('/publish/job', methods=['GET'])
def api_publish_job_get():
    """
    Return an array containing the publish jobs serialized to JSON.

    The publish jobs attributes are appended with the Celery's ``async result`` of the jobs.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.

    **Example request**:

    .. sourcecode:: http

        GET /publish/job HTTP/1.1
        Host: somewhere.com
        Header: melanie@oscied.org:oscied
        Accept: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": [{"_id": "...", "...": "..."}, {"_id": "..."}]
        }

    :Allowed: Any user
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    """
    requires_auth(request=request, allow_any=True)
    return ok_200(orchestra.get_publish_jobs(load_fields=True), True)


@app.route('/publish/job', methods=['POST'])
def api_publish_job_post():
    """
    Launch a publish job.

    Any user can launch a publish job using any media as input.
    This is linked to media API methods access policy.

    The orchestrator will automatically add ``add_date`` to ``statistic``.

    .. note::

        Interesting enhancements would be to :

        * Schedule jobs by specifying start time (...)
        * Handle the registration of jobs related to PENDING medias
        * Permit to publish a media on more than one (1) publication queue
        * Permit to unpublish a media vbia a unpublish (broadcast) message

    **Example request**:

    .. sourcecode:: http

        POST /publish/job HTTP/1.1
        Host: somewhere.com
        Header: tabby@bernex.ch:miaow
        Accept: application/json
        Content-Type: application/json

        {
          "media_id": "a396fe66-74ee-11e2-89ad-3085a9accbb8",
          "queue": "publish_london"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": "73abcf7e-74ef-11e2-9322-3085a9accc9b9"
        }

    :Allowed: Any user
    :query media_id: New job input media's id (required)
    :query queue: The publish queue used to route job (required)
    :statuscode 200: OK
    :statuscode 400: Key ``key`` not found. *or* on type or value error
    :statuscode 400: Unable to transmit job to workers of queue ``queue``.
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No user with id ``id``.
    :statuscode 404: No media with id ``media_id``.
    :statuscode 404: No publish queue with name ``queue``.
    :statuscode 415: Required (valid) json content-type.
    :statuscode 501: Cannot launch the job, input media status is ``status``.
    :statuscode 501: Cannot launch the job, input media will be published by
                     another job with id ``id``.
    """
    auth_user = requires_auth(request=request, allow_any=True)
    try:
        data = request.json
    except:
        abort(415, 'Requires valid json content-type.')
    if not data:
        abort(415, 'Requires json content-type.')
    try:
        job_id = orchestra.launch_publish_job(auth_user._id, data['media_id'],
                                              data['queue'], '/publish/callback')
    except (ValueError, TypeError) as error:
        abort(400, str(error))
    except KeyError as error:
        abort(400, 'Key ' + str(error) + ' not found.')
    except IndexError as error:
        abort(404, str(error))
    except NotImplementedError as error:
        abort(501, str(error))
    return ok_200(job_id, True)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@app.route('/publish/job/id/<id>/HEAD', methods=['GET'])
def api_publish_job_id_head(id):
    """
    Return a publish job serialized to JSON.

    The publish job attributes are appended with the Celery's ``async result`` of the job.

    **Example request**:

    .. sourcecode:: http

        GET /publish/job/id/c697f528-74f7-11e2-96a3-3085a9accc5d/HEAD HTTP/1.1
        Host: somewhere.com
        Header: tabby@bernex.ch:miaow
        Accept: application/json

    **Example response**:

    Floating numbers are here with "" for autoflask to work !!

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "c697f528-74f7-11e2-96a3-3085a9accc5d"
            "user_id": "4e8ec55e-74f7-11e2-8451-3085a9acc8e0b",
            "media_id": "a8a165b8-74f7-11e2-a59e-3085a9acc049",
            "publish_uri": "http://<publish_uri>/medias/<user_id>/<media_id>/
                            Project_London_trailer_2009.mp4",
            "statistic":
            {
              "add_date": "2013-02-11 22:38",
              "start_date": "2013-02-11 22:38",
              "elapsed_time": "0.5068690776824951",
              "eta_time": 0, "percent": 100,
              "media_size": 54871886, "publish_size": 54871886,
              "pid": 18307, "hostname": "famille-local-oscied-publisher-0"
            },
            "revoked": false,
            "status": "SUCCESS"
          }
        }

    :Allowed: Any user
    :param id: id of job to get
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No publish job with id ``id``.
    """
    check_id(id)
    requires_auth(request=request, allow_any=True)
    job = orchestra.get_publish_job(specs={'_id': id})
    if not job:
        abort(404, 'No publish job with id ' + id + '.')
    return ok_200(job, True)


@app.route('/publish/job/id/<id>', methods=['GET'])
def api_publish_job_id_get(id):
    """
    Return a publish job serialized to JSON.

    The publish job attributes are appended with the Celery's ``async result`` of the job.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.


    **Example request**:

    .. sourcecode:: http

        GET /publish/job/id/c697f528-74f7-11e2-96a3-3085a9accc5d HTTP/1.1
        Host: somewhere.com
        Header: tabby@bernex.ch:miaow
        Accept: application/json

    **Example response**:

    Floating numbers are here with "" for autoflask to work !!

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": {
            "_id": "c697f528-74f7-11e2-96a3-3085a9accc5d",
            "publish_uri": "http://<address>/medias/<user_id>/<media_id>/
                            Project_London_trailer_2009.mp4",
            "media": {
              "_id": "a8a165b8-74f7-11e2-a59e-3085a9acc049",
              "user_id": "4e8ec55e-74f7-11e2-8451-3085a9acc8e0b",
              "parent_id": null,
              "uri": "glusterfs://<address>/medias_volume/medias/
                      <user_id>/<media_id>",
              "public_uris": {
                "c697f528-74f7-11e2-96a3-3085a9accc5d":
                "http://<address>/medias/<user_id>/<media_id>/
                 Project_London_trailer_2009.mp4"
              },
              "virtual_filename": "Project_London_trailer_2009.mp4",
              "metadata": {
                "duration": "00:02:44.88", "add_date": "2013-02-11 22:37",
                "size": 54871886,
                "title": "Project London - Official Trailer (2009)"
              },
              "status": "PUBLISHED"
            },
            "user": { "name": "David Fischer", "...": "..." },
            "statistic": {
              "add_date": "2013-02-11 22:38", "start_date": "2013-02-11 22:38"
              "media_size": 54871886, "publish_size": 54871886,
              "elapsed_time": "0.5068690776824951",
              "eta_time": 0, "percent": 100,
              "pid": 18307, "hostname": "famille-local-oscied-publisher-0"
            },
            "revoked": false,
            "status": "SUCCESS"
          }
        }

    :Allowed: Any user
    :param id: id of job to get
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No publish job with id ``id``.
    """
    check_id(id)
    requires_auth(request=request, allow_any=True)
    job = orchestra.get_publish_job(specs={'_id': id}, load_fields=True)
    if not job:
        abort(404, 'No publish job with id ' + id + '.')
    return ok_200(job, True)


@app.route('/publish/job/id/<id>', methods=['DELETE'])
def api_publish_job_id_delete(id):
    """
    Revoke a publish job.

    This method do not delete jobs from jobs database but set ``revoked`` attribute in jobs database
    and broadcast revoke request to publisher units with Celery. If the job is actually running it
    will be canceled. The output publication media will be deleted.

    **Example request**:

    .. sourcecode:: http

        DELETE /pulish/job/id/c697f528-74f7-11e2-96a3-3085a9accc5d HTTP/1.1
        Host: somewhere.com
        Header: tabby@bernex.ch:miaow
        Accept: application/json
        Content-Type: application/json

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {
          "status": 200,
          "value": "The publish job \\"<job_id>\\" has been revoked.
                    Corresponding media will be unpublished from here."
        }

    :Allowed: Only author of the job
    :param id: id of job to delete
    :statuscode 200: OK
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 403: You are not allowed to revoke publish job with id ``id``.
    :statuscode 404: No publish job with id ``id``.
    :statuscode 415: Wrong id format ``id``.
    """
    check_id(id)
    auth_user = requires_auth(request=request, allow_any=True)
    job = orchestra.get_publish_job(specs={'_id': id})
    if not job:
        abort(404, 'No publish job with id ' + id + '.')
    if auth_user._id != job.user_id:
        abort(403, 'You are not allowed to revoke publish job with id ' + id + '.')
    orchestra.revoke_publish_job(job=job, terminate=True, remove=False)
    logging.info('here will be launched an unpublish job')
    #orchestra.launch_unpublish_job(auth_user._id, job, '/unpublish/callback')
    return ok_200('The publish job "' + job._id + '" has been revoked. ' +
                  'Corresponding media will be unpublished from here.', False)


# Workers (nodes) hooks ----------------------------------------------------------------------------

@app.route('/transform/callback', methods=['POST'])
def api_transform_job_hook_0():
    """
    This method is called by transform workers when they finish their work.

    If job is successful, the orchestrator will set media's status to READY.
    Else, the orchestrator will append ``error_details`` to ``statistic`` attribute of job.

    The media will be deleted if job failed (even the worker already take care of that).

    **Example request**:

    .. sourcecode:: http

        POST /transform/callback HTTP/1.1
        Host: somewhere.com
        Header: node:abcdef
        Accept: application/json
        Content-Type: application/json

        {
          "job_id": "1b96dcd6-7460-11e2-a06d-3085a9accb47",
          "status": "SUCCESS"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {"status": 200, "value": "Your work is much appreciated, thanks !"}

    :Allowed: Node
    :query job_id: Job's id (required)
    :query status: Job's status (SUCCESS) or error's details (required)
    :statuscode 200: OK
    :statuscode 400: Key ``key`` not found. *or* on type or value error
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No transform job with id ``id``.
    :statuscode 404: Unable to find output media with id ``id``.
    :statuscode 415: Requires (valid) json content-type.
    """
    requires_auth(request=request, allow_node=True)
    try:
        data = request.json
    except:
        abort(415, 'Requires valid json content-type.')
    if not data:
        abort(415, 'Requires json content-type.')
    try:
        job_id = data['job_id']
        status = data['status']
        logging.debug('job ' + job_id + ', status ' + status)
        orchestra.transform_callback(job_id, status)
    except IndexError as error:
        abort(404, str(error))
    except (ValueError, TypeError) as error:
        abort(400, str(error))
    except KeyError as error:
        abort(400, 'Key ' + str(error) + ' not found.')
    return ok_200('Your work is much appreciated, thanks !', False)


@app.route('/publish/callback', methods=['POST'])
def api_publish_job_hook_0():
    """
    This method is called by publisher workers when they finish their work.

    If job is successful, the orchestrator will update ``publish_uri`` attribute of job,
    set media's status to SUCCESS and update ``public_uris`` attribute.
    Else, the orchestrator will append ``error_details`` to ``statistic`` attribute of job.

    **Example request**:

    .. sourcecode:: http

        POST /publish/callback HTTP/1.1
        Host: somewhere.com
        Header: node:abcdef
        Accept: application/json
        Content-Type: application/json

        {
          "job_id": "1b96dcd6-7460-11e2-a06d-3085a9accb47",
          "publish_uri": "http://<address>/medias/<user_id>/<media_id>/
                          Project_London_trailer_2009.mp4",
          "status": "SUCCESS"
        }

    **Example response**:

    .. sourcecode:: http

        HTTP/1.1 200 OK
        Vary: Accept
        Content-Type: application/json

        {"status": 200, "value": "Your work is much appreciated, thanks !"}

    :Allowed: Node
    :query job_id: Job's id (required)
    :query publish_uri: Publication URI of the media (required)
    :query status: Job's status (SUCCESS) or error's details (required)
    :statuscode 200: OK
    :statuscode 400: Key ``key`` not found. *or* on type or value error
    :statuscode 401: Authenticate.
    :statuscode 403: Authentication Failed.
    :statuscode 404: No publish job with id ``id``.
    :statuscode 404: Unable to find media with id ``id``.
    :statuscode 415: Requires (valid) json content-type.
    """
    requires_auth(request=request, allow_node=True)
    try:
        data = request.json
    except:
        abort(415, 'Requires valid json content-type.')
    if not data:
        abort(415, 'Requires json content-type.')
    try:
        job_id = data['job_id']
        publish_uri = data['publish_uri'] if 'publish_uri' in data else None
        status = data['status']
        logging.debug('job ' + job_id + ', publish_uri ' + publish_uri + ', status ' + status)
        orchestra.publish_callback(job_id, publish_uri, status)
    except IndexError as error:
        abort(404, str(error))
    except (ValueError, TypeError) as error:
        abort(400, str(error))
    except KeyError as error:
        abort(400, 'Key ' + str(error) + ' not found.')
    return ok_200('Your work is much appreciated, thanks !', False)


# @app.route('/unpublish/callback', methods=['POST'])
# def api_unpublish_job_hook_0():

#     # This method will be ALWAYS called by publisher workers when they finish their work.
#     # The orchestrator will update it's internal state (only workers/nodes can do that)
#     if request.method == 'POST':
#         requires_auth(request=request, allow_node=True)
#         data = request.json
#         if not data:
#             abort(415, 'Requires json content-type')
#         try:
#             job_id = data['job_id']
#             publish_job_id = data['publish_job_id']
#             status = data['status']
#             logging.debug('job ' + job_id + ', publish_job_id ' + publish_job_id + ', status ' + status)
#             orchestra.unpublish_callback(job_id, publish_job_id, status)
#         except (ValueError, TypeError) as error:
#             abort(400, str(error))
#         except KeyError as error:
#             abort(400, 'Key ' + str(error) + ' not found')
#         except IndexError as error:
#             abort(404, str(error))
#         return ok_200('Your work is much appreciated, thanks !', False)

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':

    try:
        config = OrchestraConfig.read('config.json')
        setup_logging('orchestra.log', config.log_level)
        logging.info('OSCIED Orchestra by David Fischer 2013')
        logging.info('Configuration : ' + str(object2json(config, True)))

        if not config.storage_uri:
            logging.warning('Shared storage is not set in configuration ... exiting')
            sys.exit(0)

        if not config.mongo_connection:
            logging.warning('MongoDB is not set in configuration ... exiting')
            sys.exit(0)

        if not config.rabbit_connection:
            logging.warning('RabbitMQ is not set in configuration ... exiting')
            sys.exit(0)

        orchestra = Orchestra(config)
        logging.info('Start REST API')
        app.run(host='0.0.0.0', debug=orchestra.config.verbose)

    except Exception as error:
        logging.exception(str(error))
        logging.exception('Orchestra ... exiting')
        sys.exit(1)
