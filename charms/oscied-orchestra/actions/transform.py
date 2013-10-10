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

from flask import abort
from pytoolbox.encoding import to_bytes
from pytoolbox.flask import check_id, get_request_data, map_exceptions
from library.oscied_lib.models import TransformProfile
from plugit_utils import action, json_only, user_info

from . import orchestra


# Transformation profiles management -----------------------------------------------------------------------------------

@action(u'/transform/profile/encoder', methods=[u'GET'])
@json_only()
def api_transform_profile_encoder(request):
    u"""Return an array containing the names of the available encoders."""
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        return orchestra.ok_200(orchestra.get_transform_profile_encoders(), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/profile/count', methods=[u'GET'])
@json_only()
def api_transform_profile_count(request):
    u"""Return the number of transformation profiles."""
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_count_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_transform_profiles_count(**data), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/profile', methods=[u'GET'])
@json_only()
def api_transform_profile_get(request):
    u"""Return an array containing the transformation profiles serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_find_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_transform_profiles(**data), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/profile', methods=[u'POST'])
@json_only()
def api_transform_profile_post(request):
    u"""
    Add a transformation profile.

    The transformation profile's ``encoder_name`` attribute can be the following :

    * **copy** to bypass FFmpeg and do a simple file block copy ;
    * **ffmpeg** to transcode a media asset to another with FFMpeg ;
    * **dashcast** to transcode a media asset to MPEG-DASH with DashCast ;
    """
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, qs_only_first_value=True)
        profile = TransformProfile(title=data[u'title'], description=data[u'description'],
                                   encoder_name=data[u'encoder_name'], encoder_string=data[u'encoder_string'])
        orchestra.save_transform_profile(profile)
        return orchestra.ok_200(profile, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/profile/id/<id>', methods=[u'GET'])
@json_only()
def api_transform_profile_id_get(request, id):
    u"""Return a transformation profile serialized to JSON."""
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_any=True)
        profile = orchestra.get_transform_profile(spec={u'_id': id})
        if not profile:
            raise IndexError(to_bytes(u'No transformation profile with id {0}.'.format(id)))
        return orchestra.ok_200(profile, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/profile/id/<id>', methods=[u'DELETE'])
@json_only()
def api_transform_profile_id_delete(request, id):
    u"""Delete a transformation profile."""
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_any=True)
        profile = orchestra.get_transform_profile(spec={u'_id': id})
        if not profile:
            raise IndexError(to_bytes(u'No transformation profile with id {0}.'.format(id)))
        orchestra.delete_transform_profile(profile)
        return orchestra.ok_200(u'The transformation profile "{0}" has been deleted.'.format(profile.title),
                                include_properties=False)
    except Exception as e:
        map_exceptions(e)


# Transformation units management (encoders) ---------------------------------------------------------------------------

@action(u'/transform/unit/environment/<environment>/count', methods=[u'GET'])
@json_only()
def api_transform_unit_count(request, environment):
    u"""Return number of transformation units in the environment ``environment``."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, allow_any=True)
        return orchestra.ok_200(orchestra.get_transform_units_count(environment), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/unit/environment/<environment>', methods=[u'GET'])
@json_only()
def api_transform_unit_get(request, environment):
    u"""Return an array containing the transformation units of environment ``environment`` serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, allow_any=True)
        return orchestra.ok_200(orchestra.get_transform_units(environment), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/unit/environment/<environment>', methods=[u'POST'])
@json_only()
def api_transform_unit_post(request, environment):
    u"""Ensure that ``num_units`` transformation units are deployed into environment ``environment``."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        data = get_request_data(request, qs_only_first_value=True)
        orchestra.ensure_num_transform_units(environment, int(data[u'num_units']), terminate=True)
        return orchestra.ok_200(u'Ensured {0} transformation units into environment "{1}"'.format(data[u'num_units'],
                                environment), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/unit/environment/<environment>', methods=[u'DELETE'])
@json_only()
def api_transform_unit_delete(request, environment):
    u"""Remove the transformation service from environment ``environment``."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        orchestra.ensure_transform_units(environment, None, terminate=True)
        return orchestra.ok_200(u'Removed transformation service from environment "{0}"'.format(environment),
                                include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/unit/environment/<environment>/number/<number>', methods=[u'GET'])
@json_only()
def api_transform_unit_number_get(request, environment, number):
    u"""Return a transformation unit serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, allow_any=True)
        unit = orchestra.get_transform_unit(environment, number)
        if not unit:
            raise IndexError(to_bytes(u'Transformation unit {0} not found in environment {1}.'.format(number,
                             environment)))
        return orchestra.ok_200(unit, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/unit/environment/<environment>/number/<number>', methods=[u'DELETE'])
@json_only()
def api_transform_unit_number_delete(request, environment, number):
    u"""Remove the transformation unit number ``number`` from environment ``environment``."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        orchestra.destroy_transform_unit(environment, number, terminate=True)
        return orchestra.ok_200(u'The transformation unit {0} has been removed from environment {1}.'.format(number,
                                environment), include_properties=False)
    except Exception as e:
        map_exceptions(e)


# Transformation tasks (encoding) --------------------------------------------------------------------------------------

@action(u'/transform/queue', methods=[u'GET'])
@json_only()
def api_transform_queue(request):
    u"""Return an array containing the transformation queues serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        return orchestra.ok_200(orchestra.get_transform_queues(), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/task/count', methods=[u'GET'])
@json_only()
def api_transform_task_count(request):
    u"""Return the number of transformation tasks."""
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_count_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_transform_tasks_count(**data), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/task/HEAD', methods=[u'GET'])
@json_only()
def api_transform_task_head(request):
    u"""
    Return an array containing the transformation tasks serialized as JSON.

    The transformation tasks attributes are appended with the Celery's ``async result`` of the tasks.
    """
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_find_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_transform_tasks(**data), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/task', methods=[u'GET'])
@json_only()
def api_transform_task_get(request):
    u"""
    Return an array containing the transformation tasks serialized to JSON.

    The transformation tasks attributes are appended with the Celery's ``async result`` of the tasks.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_find_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_transform_tasks(load_fields=True, **data), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/task', methods=[u'POST'])
@json_only()
@user_info(props=['pk'])
def api_transform_task_post(request):
    u"""
    Launch a transformation task.

    Any user can launch a transformation task using any media asset as input and any transformation profile.
    This is linked to media assets and transformation profile API methods access policies.

    The output media asset is registered to the database with the PENDING status and the ``parent_id`` field is set to
    input media asset's ``id``. This permit to know relation between media assets !

    The orchestrator will automatically add ``add_date`` to ``statistic``.

    .. note::

        Interesting enhancement would be to :

        * Schedule obs by specifying start time (...) ;
        * Handle the registration of tasks related to PENDING medias ;
    """
    try:
        auth_user = orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, qs_only_first_value=True)
        task_id = orchestra.launch_transform_task(
            auth_user._id, data[u'media_in_id'], data[u'profile_id'], data[u'filename'], data[u'metadata'],
            data[u'send_email'], data[u'queue'], u'/transform/callback')
        return orchestra.ok_200(task_id, include_properties=True)
    except Exception as e:
        map_exceptions(e)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@action(u'/transform/task/id/<id>/HEAD', methods=[u'GET'])
@json_only()
def api_transform_task_id_head(request, id):
    u"""
    Return a transformation task serialized to JSON.

    The transformation task attributes are appended with the Celery's ``async result`` of the task.
    """
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_any=True)
        task = orchestra.get_transform_task(spec={u'_id': id})
        if not task:
            raise IndexError(to_bytes(u'No transformation task with id {0}.'.format(id)))
        return orchestra.ok_200(task, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/task/id/<id>', methods=[u'GET'])
@json_only()
def api_transform_task_id_get(request, id):
    u"""
    Return a transformation task serialized to JSON.

    The transformation task attributes are appended with the Celery's ``async result`` of the task.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_any=True)
        task = orchestra.get_transform_task(spec={u'_id': id}, load_fields=True)
        if not task:
            raise IndexError(to_bytes(u'No transformation task with id {0}.'.format(id)))
        return orchestra.ok_200(task, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/transform/task/id/<id>', methods=[u'DELETE'])
@json_only()
@user_info(props=['pk'])
def api_transform_task_id_delete(request, id):
    u"""
    Revoke a transformation task.

    This method do not delete tasks from tasks database but set ``revoked`` attribute in tasks database and broadcast
    revoke request to transformation units with Celery. If the task is actually running it will be canceled.
    The output media asset will be deleted.
    """
    try:
        check_id(id)
        auth_user = orchestra.requires_auth(request=request, allow_any=True)
        task = orchestra.get_transform_task(spec={u'_id': id})
        if not task:
            raise IndexError(to_bytes(u'No transformation task with id {0}.'.format(id)))
        if auth_user._id != task.user_id:
            abort(403, u'You are not allowed to revoke transformation task with id {0}.'.format(id))
        orchestra.revoke_transform_task(task=task, terminate=True, remove=False, delete_media=True)
        return orchestra.ok_200(u'The transformation task "{0}" has been revoked. Corresponding output media asset will'
                                ' be deleted.'.format(task._id), include_properties=False)
    except Exception as e:
        map_exceptions(e)
