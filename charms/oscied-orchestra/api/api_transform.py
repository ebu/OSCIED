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
from pytoolbox.network.http import get_request_data
from oscied_lib.models import TransformProfile

from server import app, api_method_decorator, api_core, ok_200


# Transformation profiles management -----------------------------------------------------------------------------------

@app.route(u'/transform/profile/encoder', methods=[u'GET'])
@api_method_decorator(api_core, authenticate=False)
def api_transform_profile_encoder(api_core=None, request=None):
    u"""Return an array containing the names of the available encoders."""
    return ok_200(api_core.get_transform_profile_encoders(), include_properties=True)


@app.route(u'/transform/profile/count', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_profile_count(auth_user=None, api_core=None, request=None):
    u"""Return the number of transformation profiles."""
    data = get_request_data(request, accepted_keys=api_core.db_count_keys, qs_only_first_value=True, optional=True)
    return ok_200(api_core.get_transform_profiles_count(**data), include_properties=False)


@app.route(u'/transform/profile', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_profile_get(auth_user=None, api_core=None, request=None):
    u"""Return an array containing the transformation profiles serialized to JSON."""
    data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
    return ok_200(api_core.get_transform_profiles(**data), include_properties=True)


@app.route(u'/transform/profile', methods=[u'POST'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_profile_post(auth_user=None, api_core=None, request=None):
    u"""
    Add a transformation profile.

    The transformation profile's ``encoder_name`` attribute can be the following :

    * **copy** to bypass FFmpeg and do a simple file block copy ;
    * **ffmpeg** to transcode a media asset to another with FFMpeg ;
    * **dashcast** to transcode a media asset to MPEG-DASH with DashCast ;
    """
    data = get_request_data(request, qs_only_first_value=True)
    profile = TransformProfile(title=data[u'title'], description=data[u'description'],
                               encoder_name=data[u'encoder_name'], encoder_string=data[u'encoder_string'])
    api_core.save_transform_profile(profile)
    return ok_200(profile, include_properties=True)


@app.route(u'/transform/profile/id/<id>', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_profile_id_get(id=None, auth_user=None, api_core=None, request=None):
    u"""Return a transformation profile serialized to JSON."""
    profile = api_core.get_transform_profile(spec={u'_id': id})
    if not profile:
        raise IndexError(to_bytes(u'No transformation profile with id {0}.'.format(id)))
    return ok_200(profile, include_properties=True)


@app.route(u'/transform/profile/id/<id>', methods=[u'DELETE'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_profile_id_delete(id=None, auth_user=None, api_core=None, request=None):
    u"""Delete a transformation profile."""
    profile = api_core.get_transform_profile(spec={u'_id': id})
    if not profile:
        raise IndexError(to_bytes(u'No transformation profile with id {0}.'.format(id)))
    api_core.delete_transform_profile(profile)
    return ok_200(u'The transformation profile "{0}" has been deleted.'.format(profile.title),
                  include_properties=False)

# Transformation units management (encoders) ---------------------------------------------------------------------------

@app.route(u'/transform/unit/environment/<environment>/count', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, allow_any=True)
def api_transform_unit_count(environment=None, auth_user=None, api_core=None, request=None):
    u"""Return number of transformation units in the environment ``environment``."""
    return ok_200(api_core.get_transform_units_count(environment), include_properties=False)


@app.route(u'/transform/unit/environment/<environment>', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, allow_any=True)
def api_transform_unit_get(environment=None, auth_user=None, api_core=None, request=None):
    u"""Return an array containing the transformation units of environment ``environment`` serialized to JSON."""
    return ok_200(api_core.get_transform_units(environment), include_properties=False)


@app.route(u'/transform/unit/environment/<environment>', methods=[u'POST'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_transform_unit_post(environment=None, auth_user=None, api_core=None, request=None):
    u"""Ensure that ``num_units`` transformation units are deployed into environment ``environment``."""
    data = get_request_data(request, qs_only_first_value=True)
    api_core.ensure_num_transform_units(environment, int(data[u'num_units']), terminate=True)
    return ok_200(u'Ensured {0} transformation units into environment "{1}"'.format(data[u'num_units'], environment),
                  include_properties=False)


@app.route(u'/transform/unit/environment/<environment>', methods=[u'DELETE'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_transform_unit_delete(environment=None, auth_user=None, api_core=None, request=None):
    u"""Remove the transformation service from environment ``environment``."""
    api_core.ensure_transform_units(environment, None, terminate=True)
    return ok_200(u'Removed transformation service from environment "{0}"'.format(environment),
                  include_properties=False)


@app.route(u'/transform/unit/environment/<environment>/number/<number>', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, allow_any=True)
def api_transform_unit_number_get(environment=None, number=None, auth_user=None, api_core=None, request=None):
    u"""Return a transformation unit serialized to JSON."""
    unit = api_core.get_transform_unit(environment, number)
    if not unit:
        raise IndexError(to_bytes(u'Transformation unit {0} not found in environment {1}.'.format(number, environment)))
    return ok_200(unit, include_properties=True)


@app.route(u'/transform/unit/environment/<environment>/number/<number>', methods=[u'DELETE'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_transform_unit_number_delete(environment=None, number=None, auth_user=None, api_core=None, request=None):
    u"""Remove the transformation unit number ``number`` from environment ``environment``."""
    api_core.destroy_transform_unit(environment, number, terminate=True)
    return ok_200(u'The transformation unit {0} has been removed from environment {1}.'.format(number, environment),
                  include_properties=False)

# Transformation tasks (encoding) --------------------------------------------------------------------------------------

@app.route(u'/transform/queue', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_queue(auth_user=None, api_core=None, request=None):
    u"""Return an array containing the transformation queues serialized to JSON."""
    return ok_200(api_core.get_transform_queues(), include_properties=True)


@app.route(u'/transform/task/count', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_task_count(auth_user=None, api_core=None, request=None):
    u"""Return the number of transformation tasks."""
    data = get_request_data(request, accepted_keys=api_core.db_count_keys, qs_only_first_value=True, optional=True)
    return ok_200(api_core.get_transform_tasks_count(**data), include_properties=False)


@app.route(u'/transform/task/HEAD', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_task_head(auth_user=None, api_core=None, request=None):
    u"""
    Return an array containing the transformation tasks serialized as JSON.

    The transformation tasks attributes are appended with the Celery's ``async result`` of the tasks.
    """
    data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
    return ok_200(api_core.get_transform_tasks(**data), include_properties=True)


@app.route(u'/transform/task', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_task_get(auth_user=None, api_core=None, request=None):
    u"""
    Return an array containing the transformation tasks serialized to JSON.

    The transformation tasks attributes are appended with the Celery's ``async result`` of the tasks.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
    return ok_200(api_core.get_transform_tasks(load_fields=True, **data), include_properties=True)


@app.route(u'/transform/task', methods=[u'POST'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_task_post(auth_user=None, api_core=None, request=None):
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
    data = get_request_data(request, qs_only_first_value=True)
    task_id = api_core.launch_transform_task(
        auth_user._id, data[u'media_in_id'], data[u'profile_id'], data[u'filename'], data[u'metadata'],
        data[u'send_email'], data[u'queue'], u'/transform/callback')
    return ok_200(task_id, include_properties=True)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@app.route(u'/transform/task/id/<id>/HEAD', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_task_id_head(id=None, auth_user=None, api_core=None, request=None):
    u"""
    Return a transformation task serialized to JSON.

    The transformation task attributes are appended with the Celery's ``async result`` of the task.
    """
    task = api_core.get_transform_task(spec={u'_id': id})
    if not task:
        raise IndexError(to_bytes(u'No transformation task with id {0}.'.format(id)))
    return ok_200(task, include_properties=True)


@app.route(u'/transform/task/id/<id>', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_task_id_get(id=None, auth_user=None, api_core=None, request=None):
    u"""
    Return a transformation task serialized to JSON.

    The transformation task attributes are appended with the Celery's ``async result`` of the task.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    task = api_core.get_transform_task(spec={u'_id': id}, load_fields=True)
    if not task:
        raise IndexError(to_bytes(u'No transformation task with id {0}.'.format(id)))
    return ok_200(task, include_properties=True)


@app.route(u'/transform/task/id/<id>', methods=[u'DELETE'])
@api_method_decorator(api_core, allow_any=True)
def api_transform_task_id_delete(id=None, auth_user=None, api_core=None, request=None):
    u"""
    Revoke a transformation task.

    This method do not delete tasks from tasks database but set ``revoked`` attribute in tasks database and broadcast
    revoke request to transformation units with Celery. If the task is actually running it will be canceled.
    The output media asset will be deleted.
    """
    task = api_core.get_transform_task(spec={u'_id': id})
    if not task:
        raise IndexError(to_bytes(u'No transformation task with id {0}.'.format(id)))
    if auth_user._id != task.user_id:
        flask.abort(403, u'You are not allowed to revoke transformation task with id {0}.'.format(id))
    api_core.revoke_transform_task(task=task, terminate=True, remove=False, delete_media=True)
    return ok_200(u'The transformation task "{0}" has been revoked. Corresponding output media asset will be'
                  ' deleted.'.format(task._id), include_properties=False)
