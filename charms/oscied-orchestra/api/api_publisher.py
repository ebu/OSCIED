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

from server import app, api_method_decorator, api_core, ok_200


# Publication units management -----------------------------------------------------------------------------------------

@app.route(u'/publisher/unit/environment/<environment>/count', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, allow_any=True)
def api_publisher_unit_count(environment=None, auth_user=None, api_core=None, request=None):
    u"""Return publication units count of environment ``environment``."""
    return ok_200(api_core.get_publisher_units_count(environment), include_properties=False)


@app.route(u'/publisher/unit/environment/<environment>', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, allow_any=True)
def api_publisher_unit_get(environment=None, auth_user=None, api_core=None, request=None):
    u"""Return an array containing the publication units of environment ``environment`` serialized to JSON."""
    return ok_200(api_core.get_publisher_units(environment), include_properties=False)


@app.route(u'/publisher/unit/environment/<environment>', methods=[u'POST'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_publisher_unit_post(environment=None, auth_user=None, api_core=None, request=None):
    u"""Ensure that ``num_units`` publication units are deployed into environment ``environment``."""
    data = get_request_data(request, qs_only_first_value=True)
    api_core.ensure_publisher_units(environment, int(data[u'num_units']), terminate=True)
    return ok_200(u'Ensured {0} publication units into environment "{1}"'.format(data[u'num_units'], environment),
                  include_properties=False)


@app.route(u'/publisher/unit/environment/<environment>', methods=[u'DELETE'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_publisher_unit_delete(environment=None, auth_user=None, api_core=None, request=None):
    u"""Remove the publication service from environment ``environment``."""
    api_core.destroy_publisher_units(environment, None, terminate=True)
    return ok_200(u'Removed publication service from environment "{0}"'.format(environment), include_properties=False)


@app.route(u'/publisher/unit/environment/<environment>/number/<number>', methods=[u'GET'])
@api_method_decorator(api_core, allow_root=True, allow_any=True)
def api_publisher_unit_number_get(environment=None, number=None, auth_user=None, api_core=None, request=None):
    u"""Return a publication unit serialized to JSON."""
    unit = api_core.get_publisher_unit(environment, number)
    if not unit:
        raise IndexError(to_bytes(u'Publication unit {0} not found in environment {1}.'.format(number, environment)))
    return ok_200(unit, include_properties=True)


@app.route(u'/publisher/unit/environment/<environment>/number/<number>', methods=[u'DELETE'])
@api_method_decorator(api_core, allow_root=True, role=u'admin_platform')
def api_publisher_unit_number_delete(environment=None, number=None, auth_user=None, api_core=None, request=None):
    u"""Remove publication unit number ``number`` from environment ``environment``."""
    api_core.destroy_publisher_unit(environment, number, terminate=True)
    return ok_200(u'The publication unit {0} has been removed of environment {1}.'.format(number, environment),
                  include_properties=False)

# Publishing tasks -----------------------------------------------------------------------------------------------------

@app.route(u'/publisher/queue', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_publisher_queue(auth_user=None, api_core=None, request=None):
    u"""Return an array containing the publication queues."""
    return ok_200(api_core.get_publisher_queues(), include_properties=True)


@app.route(u'/publisher/task/count', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_publisher_task_count(auth_user=None, api_core=None, request=None):
    u"""Return the number of publication tasks."""
    data = get_request_data(request, accepted_keys=api_core.db_count_keys, qs_only_first_value=True, optional=True)
    return ok_200(api_core.get_publisher_tasks_count(**data), include_properties=False)


@app.route(u'/publisher/task/HEAD', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_publisher_task_head(auth_user=None, api_core=None, request=None):
    u"""
    Return an array containing the publication tasks serialized as JSON.

    The publication tasks attributes are appended with the Celery's ``async result`` of the tasks.
    """
    data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
    return ok_200(api_core.get_publisher_tasks(**data), include_properties=True)


@app.route(u'/publisher/task', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_publisher_task_get(auth_user=None, api_core=None, request=None):
    u"""
    Return an array containing the publication tasks serialized to JSON.

    The publication tasks attributes are appended with the Celery's ``async result`` of the tasks.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    data = get_request_data(request, accepted_keys=api_core.db_find_keys, qs_only_first_value=True, optional=True)
    return ok_200(api_core.get_publisher_tasks(load_fields=True, **data), include_properties=True)


@app.route(u'/publisher/task', methods=[u'POST'])
@api_method_decorator(api_core, allow_any=True)
def api_publisher_task_post(auth_user=None, api_core=None, request=None):
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
    data = get_request_data(request, qs_only_first_value=True)
    task_id = api_core.launch_publisher_task(auth_user._id, data[u'media_id'], data[u'send_email'], data[u'queue'],
                                             u'/publisher/callback')
    return ok_200(task_id, include_properties=True)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@app.route(u'/publisher/task/id/<id>/HEAD', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_publisher_task_id_head(id=None, auth_user=None, api_core=None, request=None):
    u"""
    Return a publication task serialized to JSON.

    The publication task attributes are appended with the Celery's ``async result`` of the task.
    """
    task = api_core.get_publisher_task(spec={u'_id': id})
    if not task:
        raise IndexError(to_bytes(u'No publication task with id {0}.'.format(id)))
    return ok_200(task, include_properties=True)


@app.route(u'/publisher/task/id/<id>', methods=[u'GET'])
@api_method_decorator(api_core, allow_any=True)
def api_publisher_task_id_get(id=None, auth_user=None, api_core=None, request=None):
    u"""
    Return a publication task serialized to JSON.

    The publication task attributes are appended with the Celery's ``async result`` of the task.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    task = api_core.get_publisher_task(spec={u'_id': id}, load_fields=True)
    if not task:
        raise IndexError(to_bytes(u'No publication task with id {0}.'.format(id)))
    return ok_200(task, include_properties=True)


@app.route(u'/publisher/task/id/<id>', methods=[u'DELETE'])
@api_method_decorator(api_core, allow_any=True)
def api_publisher_task_id_delete(id=None, auth_user=None, api_core=None, request=None):
    u"""
    Revoke a publication task.

    This method do not delete tasks from tasks database but set ``revoked`` attribute in tasks database and broadcast
    revoke request to publication units with Celery. If the task is actually running it will be canceled.
    The media asset will be removed from the publication unit.
    """
    task = api_core.get_publisher_task(spec={u'_id': id})
    if not task:
        raise IndexError(to_bytes(u'No publication task with id {0}.'.format(id)))
    if auth_user._id != task.user_id:
        flask.abort(403, u'You are not allowed to revoke publication task with id {0}.'.format(id))
    api_core.revoke_publisher_task(task=task, callback_url=u'/publisher/revoke/callback', terminate=True, remove=False)
    return ok_200(u'The publication task "{0}" has been revoked. Corresponding media asset will be unpublished from'
                  ' here.'.format(task._id), include_properties=False)
