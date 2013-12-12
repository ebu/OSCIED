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

import logging, os, random, string, time
from pytoolbox.flask import map_exceptions
from werkzeug import secure_filename

from oscied_lib.models import Media
from plugit.utils import action, json_only, only_logged_user, user_info, PlugItSendFile
from server import api_core

from api_media import api_media_head, api_media_id_get, api_media_id_delete
from api_publisher import api_publisher_task_get, api_publisher_task_post, api_publisher_queue
from api_transform import (api_transform_profile_encoder, api_transform_profile_get, api_transform_profile_post,
                           api_transform_profile_id_delete, api_transform_task_get, api_transform_task_post,
                           api_transform_queue)

from pytoolbox.serialization import json2object, object2dictV2


def get_value(response, remove_underscore):
    u"""Convert the value of an API response (JSON {'status':, 'value':}) to a dictionary."""
    return object2dictV2(json2object(dict, response.data, False), remove_underscore)[u'value']


@action(route=u'/medias', template=u'medias/home.html', methods=[u'GET'])
@only_logged_user()
def view_medias(request):
    u"""Show the media assets home page."""
    return {}


@action(route=u'/medias/list', template=u'medias/list.html', methods=[u'GET'])
@only_logged_user()
def view_medias_list(request):
    u"""Show the media assets list page."""

    medias = get_value(api_media_head(request=request), remove_underscore=True)
    return {u'medias': medias, u'refresh_rate': 5}


@action(route=u'/medias/force_download/<id>', methods=[u'GET'])
@only_logged_user()
def get_medias(request, id):
    u"""Download a media asset."""
    medias = api_media_id_get(id=id, request=request)
    return PlugItSendFile(medias[u'value'].api_uri, None, as_attachment=True,
                          attachment_filename=medias[u'value'].filename)


@action(route=u'/upload_files/upload_video', template=u'medias/uploaded_done.html', methods=[u'POST'])
@only_logged_user()
@user_info(props=[u'pk'])
def upload_media(request):
    u"""Upload a media asset."""
    try:
        auth_user = request.args.get(u'ebuio_u_pk') or request.form.get(u'ebuio_u_pk')
        # FIXME use temporary filename generator from python standard library ?
        random_temp_name = (u''.join(random.choice(string.digits + string.ascii_uppercase) for x in range(42)) +
                            unicode(time.time()))

        tmp_filename = os.path.join(api_core.config.storage_medias_path(), random_temp_name)
        tmp_uri = os.path.join(api_core.config.storage_medias_uri(), random_temp_name)
        tmp_file = request.files[u'file']
        tmp_file.save(tmp_filename)
        media = Media(user_id=auth_user, uri=tmp_uri, filename=secure_filename(tmp_file.filename),
                      metadata={u'title': request.form.get(u'title', u'')}, status=Media.READY)
        api_core.save_media(media)
        return {u'success': True}
    except Exception as e:
        logging.exception(e)
        map_exceptions(e)


@action(route=u'/medias/delete/<id>', methods=[u'DELETE'])
@only_logged_user()
@user_info(props=[u'pk'])
@json_only()
def delete_medias(request, id):
    u"""Delete a media asset."""
    result = get_value(api_media_id_delete(id=id, request=request), remove_underscore=True)
    return {u'result': result}


@action(route=u'/transform/profiles', template=u'transform/profiles/home.html', methods=[u'GET'])
@only_logged_user()
def view_transform_profiles(request):
    u"""Show the transformation profiles home page."""
    encoders = get_value(api_transform_profile_encoder(request=request), remove_underscore=True)
    return {u'encoders': encoders}


@action(route=u'/transform/profiles/list', template=u'transform/profiles/list.html', methods=[u'GET'])
@only_logged_user()
def view_transform_profiles_list(request):
    u"""Show the transformation profiles list page."""
    profiles = get_value(api_transform_profile_get(request=request), remove_underscore=True)
    return {u'profiles': profiles, u'refresh_rate': 5}


@action(route=u'/transform/profiles/add', methods=[u'POST'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_transform_profiles_add(request):
    u"""Add a transformation profile."""
    profile = get_value(api_transform_profile_post(request=request), remove_underscore=True)
    return {u'profile': profile}


@action(route=u'/transform/profiles/delete/<id>', methods=[u'DELETE'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_transform_profiles_delete(request, id):
    u"""Delete a transformation profile."""
    msg = get_value(api_transform_profile_id_delete(id=id, request=request), remove_underscore=True)
    return {u'msg': msg}


@action(route=u'/transform/tasks', template=u'transform/tasks/home.html', methods=[u'GET'])
@only_logged_user()
def view_transform_tasks(request):
    u"""Show the transformation tasks home page."""
    medias = get_value(api_media_head(request=request), remove_underscore=True)
    profiles = get_value(api_transform_profile_get(request=request), remove_underscore=True)
    queues = get_value(api_transform_queue(request=request), remove_underscore=True)
    return {u'medias': medias, u'profiles': profiles, u'queues': queues}


@action(route=u'/transform/tasks/list', template=u'transform/tasks/list.html', methods=[u'GET'])
@only_logged_user()
def view_transform_tasks_list(request):
    u"""Show the transformation tasks list page."""
    tasks = get_value(api_transform_task_get(request=request), remove_underscore=True)
    return {u'tasks': tasks, u'refresh_rate': 5}


@action(route=u'/transform/tasks/launch', methods=[u'POST'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_transform_tasks_launch(request):
    u"""Launch a transformation task."""
    task_id = get_value(api_transform_task_post(request=request), remove_underscore=True)
    return {u'task_id': task_id}


@action(route=u'/publisher/tasks', template=u'publisher/tasks/home.html', methods=[u'GET'])
@only_logged_user()
def view_publisher_tasks(request):
    u"""Show the publication tasks home page."""
    medias = get_value(api_media_head(request=request),      remove_underscore=True)
    queues = get_value(api_publisher_queue(request=request), remove_underscore=True)
    return {u'medias': medias, u'queues': queues}


@action(route=u'/publisher/tasks/list', template=u'publisher/tasks/list.html', methods=[u'GET'])
@only_logged_user()
def view_publisher_tasks_list(request):
    u"""Show the publication tasks list page."""
    tasks = get_value(api_publisher_task_get(request=request), remove_underscore=True)
    return {u'tasks': tasks, u'refresh_rate': 5}


@action(route=u'/publisher/tasks/launch', methods=[u'POST'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_publisher_tasks_launch(request):
    u"""Launch a publication task."""
    task_id = get_value(api_publisher_task_post(request=request), remove_underscore=True)
    return {u'task_id': task_id}


@action(route=u'/menuBar', template=u'menuBar.html')
def menu_bar(request):
    u"""Dummy action to load the menu-bar."""
    return {}
