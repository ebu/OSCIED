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

import datetime, logging, os, random, string, time
from pytoolbox.network.http import get_request_data
from werkzeug import secure_filename

from oscied_lib.models import Media, TransformProfile
from plugit.utils import action, json_only, only_logged_user, user_info, PlugItSendFile
from server import api_core


# borrowed from https://github.com/davidfischer-ch/pytoolbox/blob/master/pytoolbox/django/templatetags/pytoolbox_tags.py
def secs_to_time(value):
    try:
        return (datetime.datetime.min + datetime.timedelta(seconds=float(value))).time()
    except (TypeError, ValueError):
        if not value:
            return datetime.time(second=0)
    return u''


def remove_underscores(things):
    if not things:
        return things
    if hasattr(things, u'_id'):
        things.id = things._id
        del things._id
    elif isinstance(things, list):
        for thing in things:
            if hasattr(thing, u'_id'):
                thing.id = thing._id
                del thing._id
    return things


@action(route=u'/medias', template=u'medias/home.html', methods=[u'GET'])
@only_logged_user()
def view_medias(request):
    u"""Show the media assets home page."""
    return {}


@action(route=u'/medias/list', template=u'medias/list.html', methods=[u'GET'])
@only_logged_user()
def view_medias_list(request):
    u"""Show the media assets list page."""
    try:
        data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
        data.setdefault(u'skip', 50)  # ask for the last 50 media assets if skip is not provided
        return {u'medias': remove_underscores(api_core.get_medias(**data)), u'refresh_rate': 5}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)], u'refresh_rate': 30}


@action(route=u'/medias/force_download/<id>', methods=[u'GET'])
@only_logged_user()
def get_medias(request, id):
    u"""Download a media asset."""
    try:
        media = api_core.get_media(spec={u'_id': id})
        if not media:
            return {u'errors': [u'Media with id {0} does not exist.'.format(id)]}
        return PlugItSendFile(media.api_uri, None, as_attachment=True, attachment_filename=media.filename)
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)]}


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
        return {u'errors': [unicode(e)]}


@action(route=u'/medias/delete/<id>', methods=[u'DELETE'])
@only_logged_user()
@user_info(props=[u'pk'])
@json_only()
def delete_medias(request, id):
    u"""Delete a media asset."""
    try:
        auth_user = request.args.get(u'ebuio_u_pk') or request.form.get(u'ebuio_u_pk')
        media = api_core.get_media(spec={u'_id': id})
        if not media:
            return {u'errors': [u'No media asset with id {0}.'.format(id)]}
        if auth_user != media.user_id:
            return {u'errors': [u'You are not allowed to delete media asset with id {0}.'.format(id)]}
        api_core.delete_media(media)
        return {u'infos': [u'The media asset "{0}" has been deleted.'.format(media.metadata[u'title'])]}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)]}


@action(route=u'/transform/profiles', template=u'transform/profiles/home.html', methods=[u'GET'])
@only_logged_user()
def view_transform_profiles(request):
    u"""Show the transformation profiles home page."""
    try:
        return {u'encoders': remove_underscores(api_core.get_transform_profile_encoders())}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)]}


@action(route=u'/transform/profiles/list', template=u'transform/profiles/list.html', methods=[u'GET'])
@only_logged_user()
def view_transform_profiles_list(request):
    u"""Show the transformation profiles list page."""
    try:
        data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
        return {u'profiles': remove_underscores(api_core.get_transform_profiles(**data)), u'refresh_rate': 5}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)], u'refresh_rate': 30}


@action(route=u'/transform/profiles/add', methods=[u'POST'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_transform_profiles_add(request):
    u"""Add a transformation profile."""
    try:
        data = get_request_data(request, qs_only_first_value=True)
        profile = TransformProfile(title=data[u'title'], description=data[u'description'],
                                   encoder_name=data[u'encoder_name'], encoder_string=data[u'encoder_string'])
        api_core.save_transform_profile(profile)
        return {u'infos': [u"Profile '{0}' was created successfully.".format(profile.title)]}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)]}

@action(route=u'/transform/profiles/delete/<id>', methods=[u'DELETE'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_transform_profiles_delete(request, id):
    u"""Delete a transformation profile."""
    try:
        profile = api_core.get_transform_profile(spec={u'_id': id})
        if not profile:
            return {u'errors': [u'No transformation profile with id {0}.'.format(id)]}
        api_core.delete_transform_profile(profile)
        return {u'infos': [u'The transformation profile "{0}" has been deleted.'.format(profile.title)]}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)]}


@action(route=u'/transform/tasks', template=u'transform/tasks/home.html', methods=[u'GET'])
@only_logged_user()
def view_transform_tasks(request):
    u"""Show the transformation tasks home page."""
    try:
        data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
        profiles = remove_underscores(api_core.get_transform_profiles(**data))
        data.setdefault(u'skip', 50)  # ask for the last 50 media assets if skip is not provided
        data.setdefault(u'spec', {u'status': Media.READY})  # filter the media assets that cannot be transformed
        # FIXME add more filters
        medias = remove_underscores(api_core.get_medias(**data))
        queues = remove_underscores(api_core.get_transform_queues())
        return {u'medias': medias, u'profiles': profiles, u'queues': queues}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)]}


@action(route=u'/transform/tasks/list', template=u'transform/tasks/list.html', methods=[u'GET'])
@only_logged_user()
def view_transform_tasks_list(request):
    u"""Show the transformation tasks list page."""
    try:
        data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
        tasks = remove_underscores(api_core.get_transform_tasks(**data))
        data.setdefault(u'skip', 50)  # ask for the last 50 media assets if skip is not provided
        for task in tasks:
            task.profile = remove_underscores(api_core.get_transform_profile(spec={u'_id': task.profile_id}))
            task.media_in = remove_underscores(api_core.get_media(spec={u'_id': task.media_in_id}))
            task.media_out = remove_underscores(api_core.get_media(spec={u'_id': task.media_out_id}))
            task.statistic[u'elapsed_time'] = secs_to_time(task.statistic.get(u'elapsed_time', 0)).strftime(u'%H:%M:%S')
            task.statistic[u'eta_time'] = secs_to_time(task.statistic.get(u'eta_time', 0)).strftime(u'%H:%M:%S')
        return {u'tasks': tasks, u'refresh_rate': 5}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)], u'refresh_rate': 30}


@action(route=u'/transform/tasks/launch', methods=[u'POST'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_transform_tasks_launch(request):
    u"""Launch a transformation task."""
    try:
        auth_user = request.args.get(u'ebuio_u_pk') or request.form.get(u'ebuio_u_pk')
        data = get_request_data(request, qs_only_first_value=True)
        task_id = api_core.launch_transform_task(
            user_id=auth_user, media_in_id=data[u'media_in_id'], profile_id=data[u'profile_id'],
            filename=data[u'filename'], metadata={u'title': data[u'title']}, send_email=False, queue=data[u'queue'],
            callback_url=u'/transform/callback')
        return {u'task_id': task_id}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)]}


@action(u'/transform/tasks/revoke/<id>', methods=[u'DELETE'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def api_transform_tasks_revoke(request, id):
    u"""Revoke a transformation task."""
    try:
        auth_user = request.args.get(u'ebuio_u_pk') or request.form.get(u'ebuio_u_pk')
        task = api_core.get_transform_task(spec={u'_id': id})
        if not task:
            return {u'errors': [u'No transformation task with id {0}.'.format(id)]}
        if auth_user != task.user_id:
            return {u'errors': [u'You are not allowed to revoke transformation task with id {0}.'.format(id)]}
        api_core.revoke_transform_task(task=task, terminate=True, remove=False, delete_media=True)
        return {u'infos': [u'The transformation task "{0}" has been revoked. Corresponding output media asset will be'
                ' deleted.'.format(task._id)]}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)]}


@action(route=u'/publisher/tasks', template=u'publisher/tasks/home.html', methods=[u'GET'])
@only_logged_user()
def view_publisher_tasks(request):
    u"""Show the publication tasks home page."""
    try:
        data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
        data.setdefault(u'skip', 50)  # ask for the last 50 media assets if skip is not provided
        data.setdefault(u'spec', {u'status': Media.READY})  # filter the media assets that cannot be published
        # FIXME add more filters
        medias = remove_underscores(api_core.get_medias(**data))
        queues = remove_underscores(api_core.get_publisher_queues())
        return {u'medias': medias, u'queues': queues}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)]}


@action(route=u'/publisher/tasks/list', template=u'publisher/tasks/list.html', methods=[u'GET'])
@only_logged_user()
def view_publisher_tasks_list(request):
    u"""Show the publication tasks list page."""
    try:
        data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
        data.setdefault(u'skip', 50)  # ask for the last 50 media assets if skip is not provided
        tasks = remove_underscores(api_core.get_publisher_tasks(**data))
        for task in tasks:
            task.media = remove_underscores(api_core.get_media(spec={u'_id': task.media_id}))
            task.statistic[u'elapsed_time'] = secs_to_time(task.statistic.get(u'elapsed_time', 0)).strftime(u'%H:%M:%S')
            task.statistic[u'eta_time'] = secs_to_time(task.statistic.get(u'eta_time', 0)).strftime(u'%H:%M:%S')
        return {u'tasks': tasks, u'refresh_rate': 5}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)], u'refresh_rate': 30}


@action(route=u'/publisher/tasks/launch', methods=[u'POST'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_publisher_tasks_launch(request):
    u"""Launch a publication task."""
    try:
        auth_user = request.args.get(u'ebuio_u_pk') or request.form.get(u'ebuio_u_pk')
        data = get_request_data(request, qs_only_first_value=True)
        task_id = api_core.launch_publisher_task(user_id=auth_user, media_id=data[u'media_id'], send_email=False,
                                                 queue=data[u'queue'], callback_url=u'/publisher/callback')
        return {u'infos': [u"Publication task '{0}' was launched successfully.".format(task_id)]}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)]}


@action(route=u'/publisher/tasks/revoke/<id>', methods=[u'DELETE'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_publisher_tasks_revoke(request, id):
    u"""Revoke a publication task."""
    try:
        auth_user = request.args.get(u'ebuio_u_pk') or request.form.get(u'ebuio_u_pk')
        task = api_core.get_publisher_task(spec={u'_id': id})
        if not task:
            return {u'errors': [u'No publication task with id {0}.'.format(id)]}
        if auth_user != task.user_id:
            return {u'errors': [u'You are not allowed to revoke publication task with id {0}.'.format(id)]}
        api_core.revoke_publisher_task(task=task, callback_url=u'/publisher/revoke/callback', terminate=True,
                                       remove=False)
        return {u'infos': [u'The publication task "{0}" has been revoked. Corresponding media asset will be unpublished '
                u'from here.'.format(task._id)]}
    except Exception as e:
        logging.exception(e)
        return {u'errors': [unicode(e)]}


@action(route=u'/status', template=u'status/home.html', methods=[u'GET'])
@only_logged_user()
def view_status(request):
    u"""Show the status home page."""
    return {}


@action(route=u'/menuBar', template=u'menuBar.html')
def menu_bar(request):
    u"""Dummy action to load the menu-bar."""
    return {}
