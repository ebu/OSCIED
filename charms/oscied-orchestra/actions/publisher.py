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
from library.oscied_lib.pytoolbox.encoding import to_bytes
from library.oscied_lib.pytoolbox.flask import check_id, get_request_data, map_exceptions
from plugit_utils import action, json_only

from . import orchestra


# Publication units management -----------------------------------------------------------------------------------------

@action(u'/publisher/unit/environment/<environment>/count', methods=[u'GET'])
@json_only()
def api_publisher_unit_count(request, environment):
    u"""Return publication units count of environment ``environment``."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, allow_any=True)
        return orchestra.ok_200(orchestra.get_publisher_units_count(environment), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/unit/environment/<environment>', methods=[u'GET'])
@json_only()
def api_publisher_unit_get(request, environment):
    u"""Return an array containing the publication units of environment ``environment`` serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, allow_any=True)
        return orchestra.ok_200(orchestra.get_publisher_units(environment), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/unit/environment/<environment>', methods=[u'POST'])
@json_only()
def api_publisher_unit_post(request, environment):
    u"""Ensure that ``num_units`` publication units are deployed into environment ``environment``."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        data = get_request_data(request, qs_only_first_value=True)
        orchestra.ensure_publisher_units(environment, int(data[u'num_units']), terminate=True)
        return orchestra.ok_200(u'Ensured {0} publication units into environment "{1}"'.format(data[u'num_units'],
                                environment), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/unit/environment/<environment>', methods=[u'DELETE'])
@json_only()
def api_publisher_unit_delete(request, environment):
    u"""Remove the publication service from environment ``environment``."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        orchestra.destroy_publisher_units(environment, None, terminate=True)
        return orchestra.ok_200(u'Removed publication service from environment "{0}"'.format(environment),
                                include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/unit/environment/<environment>/number/<number>', methods=[u'GET'])
@json_only()
def api_publisher_unit_number_get(request, environment, number):
    u"""Return a publication unit serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, allow_any=True)
        unit = orchestra.get_publisher_unit(environment, number)
        if not unit:
            raise IndexError(to_bytes(u'Publication unit {0} not found in environment {1}.'.format(
                             number, environment)))
        return orchestra.ok_200(unit, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/unit/environment/<environment>/number/<number>', methods=[u'DELETE'])
@json_only()
def api_publisher_unit_number_delete(request, environment, number):
    u"""Remove publication unit number ``number`` from environment ``environment``."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        orchestra.destroy_publisher_unit(environment, number, terminate=True)
        return orchestra.ok_200(u'The publication unit {0} has been removed of environment {1}.'.format(number,
                                environment), include_properties=False)
    except Exception as e:
        map_exceptions(e)


# Publishing tasks -----------------------------------------------------------------------------------------------------

@action(u'/publisher/queue', methods=[u'GET'])
@json_only()
def api_publisher_queue(request):
    u"""Return an array containing the publication queues."""
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        return orchestra.ok_200(orchestra.get_publisher_queues(), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/task/count', methods=[u'GET'])
@json_only()
def api_publisher_task_count(request):
    u"""Return the number of publication tasks."""
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_count_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_publisher_tasks_count(**data), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/task/HEAD', methods=[u'GET'])
@json_only()
def api_publisher_task_head(request):
    u"""
    Return an array containing the publication tasks serialized as JSON.

    The publication tasks attributes are appended with the Celery's ``async result`` of the tasks.
    """
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_find_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_publisher_tasks(**data), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/task', methods=[u'GET'])
@json_only()
def api_publisher_task_get(request):
    u"""
    Return an array containing the publication tasks serialized to JSON.

    The publication tasks attributes are appended with the Celery's ``async result`` of the tasks.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_find_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_publisher_tasks(load_fields=True, **data), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/task', methods=[u'POST'])
@json_only()
def api_publisher_task_post(request):
    u"""
    Launch a publication task.

    Any user can launch a publication task using any media asset as input.
    This is linked to media asset API methods access policy.

    The orchestrator will automatically add ``add_date`` to ``statistic``.

    .. note::

        Interesting enhancements would be to :

        * Schedule tasks by specifying start time (...)
        * Handle the registration of tasks related to PENDING medias
        * Permit to publication a media asset on more than one (1) publication queue
    """
    try:
        auth_user = orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, qs_only_first_value=True)
        task_id = orchestra.launch_publisher_task(auth_user._id, data[u'media_id'], data[u'send_email'], data[u'queue'],
                                                  u'/publisher/callback')
        return orchestra.ok_200(task_id, include_properties=True)
    except Exception as e:
        map_exceptions(e)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@action(u'/publisher/task/id/<id>/HEAD', methods=[u'GET'])
@json_only()
def api_publisher_task_id_head(request, id):
    u"""
    Return a publication task serialized to JSON.

    The publication task attributes are appended with the Celery's ``async result`` of the task.
    """
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_any=True)
        task = orchestra.get_publisher_task(spec={u'_id': id})
        if not task:
            raise IndexError(to_bytes(u'No publication task with id {0}.'.format(id)))
        return orchestra.ok_200(task, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/task/id/<id>', methods=[u'GET'])
@json_only()
def api_publisher_task_id_get(request, id):
    u"""
    Return a publication task serialized to JSON.

    The publication task attributes are appended with the Celery's ``async result`` of the task.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_any=True)
        task = orchestra.get_publisher_task(spec={u'_id': id}, load_fields=True)
        if not task:
            raise IndexError(to_bytes(u'No publication task with id {0}.'.format(id)))
        return orchestra.ok_200(task, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/task/id/<id>', methods=[u'DELETE'])
@json_only()
def api_publisher_task_id_delete(request, id):
    u"""
    Revoke a publication task.

    This method do not delete tasks from tasks database but set ``revoked`` attribute in tasks database and broadcast
    revoke request to publication units with Celery. If the task is actually running it will be canceled.
    The media asset will be removed from the publication unit.
    """
    try:
        check_id(id)
        auth_user = orchestra.requires_auth(request=request, allow_any=True)
        task = orchestra.get_publisher_task(spec={u'_id': id})
        if not task:
            raise IndexError(to_bytes(u'No publication task with id {0}.'.format(id)))
        if auth_user._id != task.user_id:
            abort(403, u'You are not allowed to revoke publication task with id {0}.'.format(id))
        orchestra.revoke_publisher_task(task=task, callback_url=u'/publisher/revoke/callback', terminate=True,
                                        remove=False)
        return orchestra.ok_200(u'The publication task "{0}" has been revoked. Corresponding media asset will be unpubl'
                                'ished from here.'.format(task._id), include_properties=False)
    except Exception as e:
        map_exceptions(e)
