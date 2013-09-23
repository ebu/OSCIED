# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : ORCHESTRA
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
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
# Retrieved from https://github.com/EBU-TI/OSCIED

import logging, random, string, sys, time
from flask import abort
from kitchen.text.converters import to_bytes
from library.oscied_lib.oscied_api import ABOUT, get_test_api_core, OrchestraAPICore
from library.oscied_lib.oscied_config import OrchestraLocalConfig
from library.oscied_lib.oscied_config_test import ORCHESTRA_CONFIG_TEST
from library.oscied_lib.oscied_models import Media, User, TransformProfile
from library.oscied_lib.pyutils.py_flask import check_id, get_request_data, json_response2dict, map_exceptions
from library.oscied_lib.pyutils.py_logging import setup_logging
from library.oscied_lib.pyutils.py_serialization import object2json
from library.oscied_lib.pyutils.py_unicode import configure_unicode
from utils import action, json_only, only_logged_user, user_info, PlugItSendFile


# Global variables -----------------------------------------------------------------------------------------------------

# FIXME
global PI_BASE_URL

orchestra = None


# Main method ----------------------------------------------------------------------------------------------------------

def main(flask_app, is_mock):
    global orchestra
    try:
        configure_unicode()
        config = ORCHESTRA_CONFIG_TEST if is_mock else OrchestraLocalConfig.read(u'local_config.pkl')
        setup_logging(filename=u'orchestra.log', console=True, level=config.log_level)
        logging.info(ABOUT)
        logging.info(u'Configuration : {0}'.format(unicode(object2json(config, True))))

        if not config.storage_uri():
            logging.warning(u'Shared storage is not set in configuration ... exiting')
            sys.exit(0)

        if not config.mongo_admin_connection:
            logging.warning(u'MongoDB is not set in configuration ... mocking')

        if not config.rabbit_connection:
            logging.warning(u'RabbitMQ is not set in configuration ... exiting')
            sys.exit(0)

        orchestra = get_test_api_core(u'../../scenarios/current/') if is_mock else OrchestraAPICore(config)
        logging.info(u'Start REST API')
        #app.config['PROPAGATE_EXCEPTIONS'] = True
        flask_app.run(host=u'0.0.0.0', debug=orchestra.config.verbose)

    except Exception as error:
        logging.exception(error)
        logging.exception(u'Orchestra ... exiting')
        sys.exit(1)


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


# Users management -----------------------------------------------------------------------------------------------------

@action(u'/user/login', methods=[u'GET'])
@json_only()
def api_user_login(request):
    u"""
    Return authenticated user serialized to JSON if authentication passed (without ``secret`` field).

    This method is useful for WebUI to simulate stateful login scheme and get informations about the user.

    .. note::

        This is kind of duplicate with API's GET /user/id/`id` method ...
    """
    try:
        auth_user = orchestra.requires_auth(request=request, allow_any=True)
        delattr(auth_user, u'secret')  # do not send back user's secret
        return orchestra.ok_200(auth_user, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/user/count', methods=[u'GET'])
@json_only()
def api_user_count(request):
    u"""Return the number of users."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_count_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_users_count(**data), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/user', methods=[u'GET'])
@json_only()
def api_user_get(request):
    u"""Return an array containing the users serialized to JSON (without ``secret`` fields)."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        data = get_request_data(request, accepted_keys=orchestra.db_find_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_users(**data), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/user', methods=[u'POST'])
@json_only()
def api_user_post(request):
    u"""Add a user."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        data = get_request_data(request, qs_only_first_value=True)
        user = User(first_name=data[u'first_name'], last_name=data[u'last_name'], mail=data[u'mail'],
                    secret=data[u'secret'], admin_platform=data[u'admin_platform'])
        orchestra.save_user(user, hash_secret=True)
        delattr(user, u'secret')  # do not send back user's secret
        return orchestra.ok_200(user, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/user/id/<id>', methods=[u'GET'])
@json_only()
def api_user_id_get(request, id):
    u"""Return a user serialized to JSON (without ``secret`` field)."""
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_root=True, allow_any=True)
        user = orchestra.get_user(spec={u'_id': id}, fields={u'secret': 0})
        if not user:
            raise IndexError(to_bytes(u'No user with id {0}.'.format(id)))
        return orchestra.ok_200(user, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/user/id/<id>', methods=[u'PATCH', u'PUT'])
@json_only()
def api_user_id_patch(request, id):
    u"""
    Update an user.

    User's admin_platform attribute can only be modified by root or any authenticated user with admin_platform attribute
    set.
    """
    try:
        check_id(id)
        auth_user = orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform', id=id)
        user = orchestra.get_user(spec={u'_id': id})
        data = get_request_data(request, qs_only_first_value=True)
        if not user:
            raise IndexError(to_bytes(u'No user with id {0}.'.format(id)))
        old_name = user.name
        if u'first_name' in data:
            user.first_name = data[u'first_name']
        if u'last_name' in data:
            user.last_name = data[u'last_name']
        if u'mail' in data:
            user.mail = data[u'mail']
        if u'secret' in data:
            user.secret = data[u'secret']
        if auth_user.admin_platform and u'admin_platform' in data:
            user.admin_platform = data[u'admin_platform']
        orchestra.save_user(user, hash_secret=True)
        return orchestra.ok_200(u'The user "{0}" has been updated.'.format(old_name), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/user/id/<id>', methods=[u'DELETE'])
@json_only()
def api_user_id_delete(request, id):
    u"""Delete a user."""
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform', id=id)
        user = orchestra.get_user(spec={u'_id': id})
        if not user:
            raise IndexError(to_bytes(u'No user with id {0}.'.format(id)))
        orchestra.delete_user(user)
        return orchestra.ok_200(u'The user "{0}" has been deleted.'.format(user.name), include_properties=False)
    except Exception as e:
        map_exceptions(e)


# Medias management ----------------------------------------------------------------------------------------------------

@action(u'/media/count', methods=[u'GET'])
@json_only()
def api_media_count(request):
    u"""Return the number of media assets."""
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_count_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_medias_count(**data), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/media/HEAD', methods=[u'GET'])
@json_only()
def api_media_head(request):
    u"""Return an array containing the informations about the media assets serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_find_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_medias(**data), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/media', methods=[u'GET'])
@json_only()
def api_media_get(request):
    u"""
    Return an array containing the informations about the media assets serialized to JSON.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, accepted_keys=orchestra.db_find_keys, qs_only_first_value=True, fail=False)
        return orchestra.ok_200(orchestra.get_medias(load_fields=True, **data), include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/media', methods=[u'POST'])
@json_only()
@user_info(props=['pk'])
def api_media_post(request):
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
    try:
        auth_user = orchestra.requires_auth(request=request, allow_any=True)
        data = get_request_data(request, qs_only_first_value=True)
        media = Media(user_id=auth_user._id, uri=data[u'uri'], filename=data[u'filename'], metadata=data[u'metadata'],
                      status=Media.READY)
        orchestra.save_media(media)
        return orchestra.ok_200(media, include_properties=True)
    except Exception as e:
        map_exceptions(e)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@action(u'/media/id/<id>/HEAD', methods=[u'GET'])
@json_only()
def api_media_id_head(request, id):
    u"""Return the informations about a media asset serialized to JSON."""
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_any=True)
        media = orchestra.get_media(spec={u'_id': id})
        if not media:
            raise IndexError(to_bytes(u'No media asset with id {0}.'.format(id)))
        return orchestra.ok_200(media, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/media/id/<id>', methods=[u'GET'])
@json_only()
def api_media_id_get(request, id):
    u"""
    Return the informations about a media asset serialized to JSON.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        check_id(id)
        orchestra.requires_auth(request=request, allow_any=True)
        media = orchestra.get_media(spec={'_id': id}, load_fields=True)
        if not media:
            raise IndexError(to_bytes(u'No media asset with id {0}.'.format(id)))
        return orchestra.ok_200(media, include_properties=True)
    except Exception as e:
        map_exceptions(e)


@action(u'/media/id/<id>', methods=[u'PATCH', u'PUT'])
@json_only()
@user_info(props=['pk'])
def api_media_id_patch(request, id):
    u"""Update the informations of a media asset (only metadata field can be updated)."""
    try:
        check_id(id)
        auth_user = orchestra.requires_auth(request=request, allow_any=True)
        media = orchestra.get_media(spec={u'_id': id})
        data = get_request_data(request, qs_only_first_value=True)
        if not media:
            raise IndexError(to_bytes(u'No media asset with id {0}.'.format(id)))
        if auth_user._id != media.user_id:
            abort(403, u'You are not allowed to modify media asset with id {0}.'.format(id))
        if u'metadata' in data:
            media.metadata = data[u'metadata']
        orchestra.save_media(media)
        return orchestra.ok_200(u'The media asset "{0}" has been updated.'.format(media.filename),
                                include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/media/id/<id>', methods=[u'DELETE'])
@json_only()
@user_info(props=['pk'])
def api_media_id_delete(request, id):
    u"""Remove a media asset from the shared storage and update informations about it (set status to DELETED)."""
    try:
        check_id(id)
        auth_user = orchestra.requires_auth(request=request, allow_any=True)
        media = orchestra.get_media(spec={u'_id': id})
        if not media:
            raise IndexError(to_bytes(u'No media asset with id {0}.'.format(id)))
        if auth_user._id != media.user_id:
            abort(403, u'You are not allowed to delete media asset with id {0}.'.format(id))
        orchestra.delete_media(media)
        return orchestra.ok_200(u'The media asset "{0}" has been deleted.'.format(media.metadata[u'title']),
                                include_properties=False)
    except Exception as e:
        map_exceptions(e)


# Environments management ----------------------------------------------------------------------------------------------

@action(u'/environment/count', methods=[u'GET'])
@json_only()
def api_environment_count(request):
    u"""Return the number of environments."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        (environments, default) = orchestra.get_environments()
        return orchestra.ok_200(len(environments), False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment/HEAD', methods=[u'GET'])
@json_only()
def api_environment_get_head(request):
    u"""Return an array containing the environments serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        (environments, default) = orchestra.get_environments()
        return orchestra.ok_200({u'environments': environments, u'default': default}, include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment', methods=[u'GET'])
@json_only()
def api_environment_get(request):
    u"""Return an array containing the environments (with status) serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        (environments, default) = orchestra.get_environments(get_status=True)
        return orchestra.ok_200({u'environments': environments, u'default': default}, include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment', methods=[u'POST'])
@json_only()
def api_environment_post(request):
    u"""Add a new environment."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        data = get_request_data(request, qs_only_first_value=True)
        return orchestra.ok_200(orchestra.add_environment(data[u'name'], data[u'type'], data[u'region'],
                                data[u'access_key'], data[u'secret_key'], data[u'control_bucket']),
                                include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment/name/<name>/HEAD', methods=[u'GET'])
@json_only()
def api_environment_name_get_head(request, name):
    u"""Return an environment containing his status serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        return orchestra.ok_200(orchestra.get_environments(name), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment/name/<name>', methods=[u'GET'])
@json_only()
def api_environment_name_get(request, name):
    u"""Return an environment serialized to JSON."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        return orchestra.ok_200(orchestra.get_environment(name, get_status=True), include_properties=False)
    except Exception as e:
        map_exceptions(e)


@action(u'/environment/name/<name>', methods=[u'DELETE'])
@json_only()
def api_environment_name_delete(request, name):
    u"""Remove an environment (destroy services and unregister it)."""
    try:
        orchestra.requires_auth(request=request, allow_root=True, role=u'admin_platform')
        return orchestra.ok_200(orchestra.delete_environment(name, remove=True), include_properties=False)
    except Exception as e:
        map_exceptions(e)


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
        task_id = data[u'task_id']
        publish_uri = data[u'publish_uri'] if u'publish_uri' in data else None
        status = data[u'status']
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
        task_id = data[u'task_id']
        publish_uri = data[u'publish_uri'] if u'publish_uri' in data else None
        status = data[u'status']
        logging.debug(u'task {0}, revoked publish_uri {1}, status {2}'.format(task_id, publish_uri, status))
        orchestra.publisher_revoke_callback(task_id, publish_uri, status)
        return orchestra.ok_200(u'Your work is much appreciated, thanks !', include_properties=False)
    except Exception as e:
        map_exceptions(e)


# ----------------------------------------------------------------------------------------------------------------------

@action(route=u'/medias', template=u'medias/home.html', methods=[u'GET'])
@only_logged_user()
def view_medias(request):
    u"""Show the media assets home page."""
    return {}


@action(route=u'/medias/list', template=u'medias/list.html', methods=[u'GET'])
@only_logged_user()
def view_medias_list(request):
    u"""Show the media assets list page."""
    medias = json_response2dict(api_media_get(request), remove_underscore=True)
    return {u'medias': medias, u'refresh_rate': 5}


@action(route=u'/medias/force_download/<id>', methods=[u'GET'])
@only_logged_user()
def get_medias(request, id):
    u"""Download a media asset."""
    medias = api_media_id_get(request, id)
    uri = medias[u'value'].api_uri
    filename = medias[u'value'].filename
    return PlugItSendFile(uri, None, as_attachment=True, attachment_filename=filename)

@action(route=u'/upload_files/upload_video', template=u'medias/uploaded_done.html', methods=[u'POST'])
@only_logged_user()
@user_info(props=[u'pk'])
def upload_media(request):
    u"""Upload a media asset."""
    try:
        auth_user = request.args.get(u'ebuio_u_pk') or request.form.get(u'ebuio_u_pk')
        metadata = {u'title': request.form.get(u'title', u'')}
        filename = request.form.get(u'filename')
        random_temp_name = (u''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(42)) +
                            str(time.time()))  # Probably random enough

        tmp_file = orchestra.config.storage_medias_path() + '/' + random_temp_name
        tmp_uri = orchestra.config.storage_medias_uri() + '/' + random_temp_name

        file = request.files[u'file']
        file.save(tmp_file)

        from werkzeug import secure_filename
        filename = secure_filename(file.filename)

        media = Media(None, auth_user, None, tmp_uri, None, filename, metadata, u'READY')
        orchestra.save_media(media)

        return {u'success': True}
    except Exception as e:
        map_exceptions(e)


@action(route=u'/medias/delete/<id>', methods=[u'DELETE'])
@only_logged_user()
@user_info(props=[u'pk'])
@json_only()
def delete_medias(request, id):
    u"""Delete a media asset."""
    result = json_response2dict(api_media_id_delete(request, id), remove_underscore=True)
    return {u'result': result}


@action(route=u'/transform/profiles', template=u'transform/profiles/home.html', methods=[u'GET'])
@only_logged_user()
def view_transform_profiles(request):
    u"""Show the transformation profiles home page."""
    encoders = json_response2dict(api_transform_profile_encoder(request), remove_underscore=True)
    return {u'encoders': encoders}


@action(route=u'/transform/profiles/list', template=u'transform/profiles/list.html', methods=[u'GET'])
@only_logged_user()
def view_transform_profiles_list(request):
    u"""Show the transformation profiles list page."""
    profiles = json_response2dict(api_transform_profile_get(request), remove_underscore=True)
    return {u'profiles': profiles, u'refresh_rate': 5}


@action(route=u'/transform/profiles/add', methods=[u'POST'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_transform_profiles_add(request):
    u"""Add a transformation profile."""
    profile = json_response2dict(api_transform_profile_post(request), remove_underscore=True)
    return {u'profile': profile}


@action(route=u'/transform/profiles/delete/<id>', methods=[u'GET'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_transform_profiles_delete(request, id):
    u"""Delete a transformation profile."""
    msg = json_response2dict(api_transform_profile_id_delete(request, id), remove_underscore=True)
    return {u'msg': msg}


@action(route=u'/transform/tasks', template=u'transform/tasks/home.html', methods=[u'GET'])
@only_logged_user()
def view_transform_tasks(request):
    u"""Show the transformation tasks home page."""
    medias = json_response2dict(api_media_head(request), remove_underscore=True)
    profiles = json_response2dict(api_transform_profile_get(request), remove_underscore=True)
    queues = json_response2dict(api_transform_queue(request), remove_underscore=True)
    return {u'medias': medias, u'profiles': profiles, u'queues': queues}


@action(route=u'/transform/tasks/list', template=u'transform/tasks/list.html', methods=[u'GET'])
@only_logged_user()
def view_transform_tasks_list(request):
    u"""Show the transformation tasks list page."""
    tasks = json_response2dict(api_transform_task_get(request), remove_underscore=True)
    return {u'tasks': tasks, u'refresh_rate': 5}


@action(route=u'/transform/tasks/launch', methods=[u'POST'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_transform_tasks_launch(request):
    u"""Launch a transformation task."""
    task_id = json_response2dict(api_transform_task_post(request), remove_underscore=True)
    return {u'task_id': task_id}


@action(route=u'/publisher/tasks', template=u'publisher/tasks/home.html', methods=[u'GET'])
@only_logged_user()
def view_publisher_tasks(request):
    u"""Show the publication tasks home page."""
    medias = json_response2dict(api_media_head(request),      remove_underscore=True)
    queues = json_response2dict(api_publisher_queue(request), remove_underscore=True)
    return {u'medias': medias, u'queues': queues}


@action(route=u'/publisher/tasks/list', template=u'publisher/tasks/list.html', methods=[u'GET'])
@only_logged_user()
def view_publisher_tasks_list(request):
    u"""Show the publication tasks list page."""
    tasks = json_response2dict(api_publisher_task_get(request), remove_underscore=True)
    return {u'tasks': tasks, u'refresh_rate': 5}


@action(route=u'/publisher/tasks/launch', methods=[u'POST'])
@only_logged_user()
@json_only()
@user_info(props=[u'pk'])
def view_publisher_tasks_launch(request):
    u"""Launch a publication task."""
    task_id = json_response2dict(api_publisher_task_post(request), remove_underscore=True)
    return {u'task_id': task_id}


@action(route=u'/menuBar', template=u'menuBar.html')
def menu_bar(request):
    u"""Dummy action to load the menu-bar."""
    return {}
