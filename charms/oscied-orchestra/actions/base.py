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

import logging
from library.oscied_lib.pytoolbox.flask import get_request_data, map_exceptions
from plugit_utils import action, json_only

from . import orchestra


# Index ----------------------------------------------------------------------------------------------------------------

@action(u'/', methods=[u'GET'])
@json_only()
def api_root(request):
    u"""
    Return an about string. This method is actually used by Orchestra charm's hooks to check API's status.
    """
    try:
        return orchestra.ok_200(orchestra.about, include_properties=False)
    except Exception as e:
        map_exceptions(e)


# System management ----------------------------------------------------------------------------------------------------

@action(u'/flush', methods=[u'POST'])
@json_only()
def api_flush(request):
    u"""Flush Orchestrator's database. This method is useful for testing and development purposes."""
    try:
        orchestra.requires_auth(request=request, allow_root=True)
        orchestra.flush_db()
        return orchestra.ok_200(u'Orchestra database flushed !', include_properties=False)
    except Exception as e:
        map_exceptions(e)


# Workers (nodes) hooks ------------------------------------------------------------------------------------------------

@action(u'/transform/callback', methods=[u'POST'])
@json_only()
def api_transform_task_hook(request):
    u"""
    This method is called by transformation workers when they finish their work.

    If task is successful, the orchestrator will set media's status to READY.
    Else, the orchestrator will append ``error_details`` to ``statistic`` attribute of task.

    The media asset will be deleted if task failed (even the worker already take care of that).
    """
    try:
        orchestra.requires_auth(request=request, allow_node=True)
        data = get_request_data(request, qs_only_first_value=True)
        task_id, status = data[u'task_id'], data[u'status']
        logging.debug(u'task {0}, status {1}'.format (task_id, status))
        orchestra.transform_callback(task_id, status)
        return orchestra.ok_200(u'Your work is much appreciated, thanks !', include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/callback', methods=[u'POST'])
@json_only()
def api_publisher_task_hook(request):
    u"""
    This method is called by publication workers when they finish their work.

    If the task is successful, the orchestrator will update ``publish_uri`` attribute of the task, set media asset's
    status to SUCCESS and update ``public_uris`` attribute.
    Else, the orchestrator will append ``error_details`` to ``statistic`` attribute of the task.
    """
    try:
        orchestra.requires_auth(request=request, allow_node=True)
        data = get_request_data(request, qs_only_first_value=True)
        task_id, publish_uri, status = data[u'task_id'], data.get(u'publish_uri'), data[u'status']
        logging.debug(u'task {0}, publish_uri {1}, status {2}'.format(task_id, publish_uri, status))
        orchestra.publisher_callback(task_id, publish_uri, status)
        return orchestra.ok_200(u'Your work is much appreciated, thanks !', include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/publisher/revoke/callback', methods=[u'POST'])
@json_only()
def api_revoke_publisher_task_hook(request):
    u"""
    This method is called by publication workers when they finish their work (revoke).

    If the task is successful, the orchestrator will update media asset's ``status`` and ``public_uris`` attribute.
    Else, the orchestrator will append ``error_details`` to ``statistic`` attribute of the task.
    """
    try:
        orchestra.requires_auth(request=request, allow_node=True)
        data = get_request_data(request, qs_only_first_value=True)
        task_id, publish_uri, status = data[u'task_id'], data.get(u'publish_uri'), data[u'status']
        logging.debug(u'task {0}, revoked publish_uri {1}, status {2}'.format(task_id, publish_uri, status))
        orchestra.publisher_revoke_callback(task_id, publish_uri, status)
        return orchestra.ok_200(u'Your work is much appreciated, thanks !', include_properties=False)
    except Exception as e:
        map_exceptions(e)
