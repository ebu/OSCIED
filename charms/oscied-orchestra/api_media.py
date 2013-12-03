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

import flask
from pytoolbox.encoding import to_bytes
from pytoolbox.flask import get_request_data
from library.oscied_lib.models import Media

from server import app, api_method_decorator, api_core, ok_200


# Medias management ----------------------------------------------------------------------------------------------------

@app.route(u'/media/count', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_media_count(auth_user=None, api_core=None, request=None):
    u"""Return the number of media assets."""
    data = get_request_data(request, accepted_keys=api_core.db_count_keys, qs_only_first_value=True, fail=False)
    return ok_200(api_core.get_medias_count(**data), include_properties=False)


@app.route(u'/media/HEAD', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_media_head(auth_user=None, api_core=None, request=None):
    u"""Return an array containing the informations about the media assets serialized to JSON."""
    data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, fail=False)
    return ok_200(api_core.get_medias(**data), include_properties=True)


@app.route(u'/media', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_media_get(auth_user=None, api_core=None, request=None):
    u"""
    Return an array containing the informations about the media assets serialized to JSON.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, fail=False)
    return ok_200(api_core.get_medias(load_fields=True, **data), include_properties=True)


@app.route(u'/media', methods=[u'POST'])
@api_method_decorator(api_core, allow_any=True)
def api_media_post(auth_user=None, api_core=None, request=None):
    u"""
    Register a media asset and add informations about it.

    This method only register already uploaded media asset to the shared storage.
    For example, the WebUI will upload a media asset to uploads path **before** registering it with this method.

    Medias in the shared storage are renamed with the following convention:
        ``storage_root``/medias/``user_id``/``media_id``

    When published or downloaded, media asset file-name will be ``filename``.
    Spaces ( ) are not allowed and they will be converted to underscores (_).

    Media asset's ``metadata`` must contain any valid JSON string. Only the ``title`` key is required.
    The orchestrator will automatically add ``add_date`` and ``duration`` to ``metadata``.

    .. note::

        Registration of external media assets (aka. http://) will be an interesting improvement.
    """
    data = get_request_data(request, qs_only_first_value=True)
    media = Media(user_id=auth_user._id, uri=data[u'uri'], filename=data[u'filename'], metadata=data[u'metadata'],
                  status=Media.READY)
    api_core.save_media(media)
    return ok_200(media, include_properties=True)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@app.route(u'/media/id/<id>/HEAD', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_media_id_head(id=None, auth_user=None, api_core=None, request=None):
    u"""Return the informations about a media asset serialized to JSON."""
    media = api_core.get_media(spec={u'_id': id})
    if not media:
        raise IndexError(to_bytes(u'No media asset with id {0}.'.format(id)))
    return ok_200(media, include_properties=True)


@app.route(u'/media/id/<id>', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_media_id_get(id=None, auth_user=None, api_core=None, request=None):
    u"""
    Return the informations about a media asset serialized to JSON.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    media = api_core.get_media(spec={'_id': id}, load_fields=True)
    if not media:
        raise IndexError(to_bytes(u'No media asset with id {0}.'.format(id)))
    return ok_200(media, include_properties=True)


@app.route(u'/media/id/<id>', methods=[u'PATCH', u'PUT'])
@api_method_decorator(api_core, allow_any=True)
def api_media_id_patch(id=None, auth_user=None, api_core=None, request=None):
    u"""Update the informations of a media asset (only metadata field can be updated)."""
    media = api_core.get_media(spec={u'_id': id})
    data = get_request_data(request, qs_only_first_value=True)
    if not media:
        raise IndexError(to_bytes(u'No media asset with id {0}.'.format(id)))
    if auth_user._id != media.user_id:
        flask.abort(403, u'You are not allowed to modify media asset with id {0}.'.format(id))
    if u'metadata' in data:
        media.metadata = data[u'metadata']
    api_core.save_media(media)
    return ok_200(u'The media asset "{0}" has been updated.'.format(media.filename), include_properties=False)


@app.route(u'/media/id/<id>', methods=[u'DELETE'])
@api_method_decorator(api_core, allow_any=True)
def api_media_id_delete(id=None, auth_user=None, api_core=None, request=None):
    u"""Remove a media asset from the shared storage and update informations about it (set status to DELETED)."""
    media = api_core.get_media(spec={u'_id': id})
    if not media:
        raise IndexError(to_bytes(u'No media asset with id {0}.'.format(id)))
    if auth_user._id != media.user_id:
        flask.abort(403, u'You are not allowed to delete media asset with id {0}.'.format(id))
    api_core.delete_media(media)
    return ok_200(u'The media asset "{0}" has been deleted.'.format(media.metadata[u'title']), include_properties=False)
