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

import logging, sys, uuid
from flask import abort
from oscied_lib.Media import Media
from oscied_lib.Orchestra import Orchestra, get_test_orchestra
from oscied_lib.OrchestraConfig import OrchestraConfig, ORCHESTRA_CONFIG_TEST
from oscied_lib.TransformProfile import TransformProfile
from oscied_lib.User import User
from oscied_lib.pyutils.flaski import check_id, get_request_json, map_exceptions
from oscied_lib.pyutils.pyutils import object2json, setup_logging
from utils import action, json_only, only_logged_user, user_info, PlugItSendFile
from server import ok_200

# Global variables ---------------------------------------------------------------------------------

#flask_app = None
orchestra = None


# Main ---------------------------------------------------------------------------------------------

def main(flask_app, mock):
    global orchestra
    try:
        config = ORCHESTRA_CONFIG_TEST if mock else OrchestraConfig.read('local_config.pkl')
        setup_logging(filename='orchestra.log', console=True, level=config.log_level)
        logging.info('OSCIED Orchestra by David Fischer 2013')
        logging.info('Configuration : ' + str(object2json(config, True)))

        if not config.storage_uri():
            logging.warning('Shared storage is not set in configuration ... exiting')
            sys.exit(0)

        if not config.mongo_admin_connection:
            logging.warning('MongoDB is not set in configuration ... mocking')

        if not config.rabbit_connection:
            logging.warning('RabbitMQ is not set in configuration ... exiting')
            sys.exit(0)

        orchestra = get_test_orchestra('../../config/api') if mock else Orchestra(config)
        print('They are %s registered users.' % len(orchestra.get_users()))
        print('They are %s available medias.' % len(orchestra.get_medias()))
        print('They are %s available transform profiles.' % len(orchestra.get_transform_profiles()))
        print('They are %s launched transformation tasks.' % len(orchestra.get_transform_tasks()))
        logging.info('Start REST API')
        #flask_app.config['PROPAGATE_EXCEPTIONS'] = True
        flask_app.run(host='0.0.0.0', debug=orchestra.config.verbose)

    except Exception as error:
        logging.exception(str(error))
        logging.exception('Orchestra ... exiting')
        sys.exit(1)


# --------------------------------------------------------------------------------------------------
# http://publish.luisrei.com/articles/flaskrest.html

def requires_auth(request, **kwargs):
    u"""
    Bypass user authentication and get informations from PlugIt Client running on EBU-io website.

    .. warning::

        Removed description from branch called issue75_ebuio.
    """
    args = request.form if request.form.get('ebuio_u_username') else request.args
    if args.get('ebuio_u_username'):
        logging.info('User is %s' % args['ebuio_u_username'])
        user = orchestra.get_user(specs={'mail': args['ebuio_u_email']})
        if user is None:
            user = User(None,
                        first_name=args.get('ebuio_u_first_name') or 'First name',
                        last_name=args.get('ebuio_u_last_name') or 'Last name',
                        mail=args['ebuio_u_email'],
                        secret=str(uuid.uuid4()),
                        admin_platform=args.get('ebuio_u_ebuio_admin') == 'True')
            logging.info('Create new EBU-io user %s' % user.name)
            if not user.is_valid(False):
                msg = 'Missing on or more informations about EBU-io user.'
                logging.exception(msg)
                raise ValueError(msg)
            # Ensure that user's informations are available in our database
            orchestra.save_user(user, hash_secret=True)
        else:
            logging.info('Use existing EBU-io user %s' % user.name)
        return user
    # This is probably a worker node (transform of publisher) that want to trigger a callback
    return None


def response2dict(response, remove_underscore):
    value = []
    if response['status'] == 200:
        try:
            for thing in response['value']:
                value.append(object2dict(thing, remove_underscore))
        except TypeError:
            value.append(object2dict(response['value'], remove_underscore))
    return value


def object2dict(something, remove_underscore):
    if isinstance(something, dict):
        something_dict = {}
        for key, value in something.iteritems():
            if remove_underscore and key[0] == '_':
                key = key[1:]
            something_dict[key] = object2dict(value, remove_underscore)
        return something_dict
    elif hasattr(something, "__iter__"):
        return [object2dict(value, remove_underscore) for value in something]
    elif hasattr(something, "__dict__"):
        something_dict = {}
        for key, value in something.__dict__.iteritems():
            if remove_underscore and key[0] == '_':
                key = key[1:]
            something_dict[key] = object2dict(value, remove_underscore)
        return something_dict
    return something


# def object2dict(something, remove_underscore):
#     something_dict = something.__dict__ if hasattr(something, '__dict__') else something
#     if remove_underscore:
#         # FIXME this only works on _id
#         try:
#             something_dict['id'] = something_dict.pop('_id')
#         except AttributeError:
#             pass
#     return something_dict


# Index --------------------------------------------------------------------------------------------

@action('/', methods=['GET'])
@json_only()
def api_root(request):
    """
    Return an about string.

    This method is actually used by Orchestra charm's hooks to check API's status.
    """
    try:
        return ok_200(orchestra.about, False)
    except Exception as e:
        map_exceptions(e)


# System management --------------------------------------------------------------------------------

@action('/flush', methods=['POST'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_flush(request):
    """
    Flush Orchestrator's database. This method is useful for testing / development purposes.
    """
    try:
        requires_auth(request=request, allow_root=True)
        orchestra.flush_db()
        return ok_200('Orchestra database flushed !', False)
    except Exception as e:
        map_exceptions(e)


# Medias management --------------------------------------------------------------------------------

@action('/media/count', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_media_count(request):
    """
    Return medias count.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_medias_count(), False)
    except Exception as e:
        map_exceptions(e)


@action('/media/HEAD', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_media_head(request):
    """
    Return an array containing the medias serialized to JSON.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_medias(), True)
    except Exception as e:
        map_exceptions(e)


@action('/media', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_media_get(request):
    """
    Return an array containing the medias serialized to JSON.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_medias(load_fields=False), True)  # FIXME enable load_fields
    except Exception as e:
        map_exceptions(e)


@action('/media', methods=['POST'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_media_post(request):
    """
    Add a media.

    This method handle registration of already uploaded media to the shared storage.
    For example, the WebUI will upload a media to uploads path **before** registering it
    with this method.

    Medias in the shared storage are renamed with the following convention:
        ``storage_root``/medias/``user_id``/``media_id``

    When published or downloaded, media file-name will be ``filename``.
    Spaces ( ) are not allowed and they will be converted to underscores (_).

    Media's ``metadata`` must contain any valid JSON string. Only the ``title`` key is required.
    The orchestrator will automatically add ``add_date`` and ``duration`` to ``metadata``.

    .. note::

        Registration of external media (aka. http://) will be an interesting improvement.
    """
    try:
        auth_user = requires_auth(request=request, allow_any=True)
        data = get_request_json(request)
        media = Media(None, auth_user._id, None, data['uri'], None, data['filename'],
                      data['metadata'], 'READY')
        orchestra.save_media(media)
        return ok_200(media, True)
    except Exception as e:
        map_exceptions(e)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@action('/media/id/<id>/HEAD', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_media_id_head(request, id):
    """
    Return a media serialized to JSON.
    """
    try:
        check_id(id)
        requires_auth(request=request, allow_any=True)
        media = orchestra.get_media(specs={'_id': id})
        if not media:
            raise IndexError('No media with id %s.' % id)
        return ok_200(media, True)
    except Exception as e:
        map_exceptions(e)


@action('/media/id/<id>', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_media_id_get(request, id):
    """
    Return a media serialized to JSON.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        check_id(id)
        requires_auth(request=request, allow_any=True)
        media = orchestra.get_media(specs={'_id': id}, load_fields=True)
        if not media:
            raise IndexError('No media with id %s.' % id)
        return ok_200(media, True)
    except Exception as e:
        map_exceptions(e)


@action('/media/id/<id>', methods=['PATCH', 'PUT'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_media_id_patch(request, id):
    """
    Update a media (only metadata field can be updated).
    """
    try:
        check_id(id)
        auth_user = requires_auth(request=request, allow_any=True)
        media = orchestra.get_media(specs={'_id': id})
        data = get_request_json(request)
        if not media:
            raise IndexError('No media with id %s.' % id)
        if auth_user._id != media.user_id:
            abort(403, 'You are not allowed to modify media with id %s.' % id)
        if 'metadata' in data:
            media.metadata = data['metadata']
        orchestra.save_media(media)
        return ok_200('The media "%s" has been updated.' % media.filename, False)
    except Exception as e:
        map_exceptions(e)


@action('/media/id/<id>', methods=['DELETE'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_media_id_delete(request, id):
    """
    Delete a media.

    The media file is removed from the shared storage and media's status is set to DELETED.
    """
    try:
        check_id(id)
        auth_user = requires_auth(request=request, allow_any=True)
        media = orchestra.get_media(specs={'_id': id})
        if not media:
            raise IndexError('No media with id %s.' % id)
        if auth_user._id != media.user_id:
            abort(403, 'You are not allowed to delete media with id %s.' % id)
        orchestra.delete_media(media)
        return ok_200('The media "%s" has been deleted.' % media.metadata['title'], False)
    except Exception as e:
        map_exceptions(e)


# Environments management --------------------------------------------------------------------------

@action('/environment/count', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_environment_count(request):
    """
    Return environments count.

    **Example request**:
    """
    try:
        requires_auth(request=request, allow_root=True, allow_any=True)
        return ok_200(orchestra.get_environments_count(), False)
    except Exception as e:
        map_exceptions(e)


@action('/environment', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_environment_get(request):
    """
    Return an array containing the environments serialized to JSON.

    **Example request**:
    """
    try:
        requires_auth(request=request, allow_root=True, allow_any=True)
        (environments, default) = orchestra.get_environments()
        return ok_200({'environments': environments, 'default': default}, False)
    except Exception as e:
        map_exceptions(e)


@action('/environment', methods=['POST'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_environment_post(request):
    """
    Add a new environment.

    **Example request**:
    """
    try:
        requires_auth(request=request, allow_root=True, role='admin_platform')
        data = get_request_json(request)
        return ok_200(orchestra.add_environment(data['name'], data['type'], data['region'],
                      data['access_key'], data['secret_key'], data['control_bucket']), False)
    except Exception as e:
        map_exceptions(e)


@action('/environment/name/<name>', methods=['DELETE'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_environment_name_delete(request, name):
    """
    Remove an environment (destroy services and unregister it).

    **Example request**:
    """
    try:
        requires_auth(request=request, allow_root=True, role='admin_platform')
        return ok_200(orchestra.delete_environment(name, remove=True), False)
    except Exception as e:
        map_exceptions(e)


# Transform profiles management --------------------------------------------------------------------

@action('/transform/profile/encoder', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_profile_encoder(request):
    """
    Return an array containing the names of the transform profile encoders.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_transform_profile_encoders(), True)
    except Exception as e:
        map_exceptions(e)


@action('/transform/profile/count', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_profile_count(request):
    """
    Return profiles count.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_transform_profiles_count(), False)
    except Exception as e:
        map_exceptions(e)


@action('/transform/profile', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_profile_get(request):
    """
    Return an array containing the transform profiles serialized to JSON.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_transform_profiles(), True)
    except Exception as e:
        map_exceptions(e)


@action('/transform/profile', methods=['POST'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_profile_post(request):
    """
    Add a transform profile.

    The transform profile's ``encoder_name`` attribute can be the following :

    * **copy** to bypass FFmpeg and do a simple file block copy ;
    * **ffmpeg** to transcode a media to another with FFMpeg ;
    * **dashcast** to transcode a media to MPEG-DASH with DashCast ;
    """
    try:
        requires_auth(request=request, allow_any=True)
        data = get_request_json(request)
        profile = TransformProfile(None, data['title'], data['description'], data['encoder_name'],
                                   data['encoder_string'])
        orchestra.save_transform_profile(profile)
        return ok_200(profile, True)
    except Exception as e:
        map_exceptions(e)


@action('/transform/profile/id/<id>', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_profile_id_get(request, id):
    """
    Return a transform profile serialized to JSON.
    """
    try:
        check_id(id)
        requires_auth(request=request, allow_any=True)
        profile = orchestra.get_transform_profile(specs={'_id': id})
        if not profile:
            raise IndexError('No transform profile with id %s.' % id)
        return ok_200(profile, True)
    except Exception as e:
        map_exceptions(e)


@action('/transform/profile/id/<id>', methods=['DELETE'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_profile_id_delete(request, id):
    """
    Delete a transform profile.
    """
    try:
        check_id(id)
        requires_auth(request=request, allow_any=True)
        profile = orchestra.get_transform_profile(specs={'_id': id})
        if not profile:
            raise IndexError('No transform profile with id %s.' % id)
        orchestra.delete_transform_profile(profile)
        return ok_200('The transform profile "%s" has been deleted.' % profile.title, False)
    except Exception as e:
        map_exceptions(e)


# Transformation units management (encoders) -------------------------------------------------------

@action('/transform/unit/environment/<environment>/count', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_unit_count(request, environment):
    """
    Return transform units count of environment ``environment``.
    """
    try:
        requires_auth(request=request, allow_root=True, allow_any=True)
        return ok_200(orchestra.get_transform_units_count(environment), False)
    except Exception as e:
        map_exceptions(e)


@action('/transform/unit/environment/<environment>', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_unit_get(request, environment):
    """
    Return an array containing the transform units of environment ``environment`` serialized to
    JSON.
    """
    try:
        requires_auth(request=request, allow_root=True, allow_any=True)
        return ok_200(orchestra.get_transform_units(environment), False)
    except Exception as e:
        map_exceptions(e)


@action('/transform/unit/environment/<environment>', methods=['POST'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_unit_post(request, environment):
    """
    Deploy some new transform units into environment ``environment``.
    """
    try:
        requires_auth(request=request, allow_root=True, role='admin_platform')
        data = get_request_json(request)
        orchestra.add_or_deploy_transform_units(environment, int(data['num_units']))
        return ok_200('Deployed %s transform units into environment "%s"' %
                      (data['num_units'], environment), False)
    except Exception as e:
        map_exceptions(e)


@action('/transform/unit/environment/<environment>', methods=['DELETE'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_unit_delete(request, environment):
    """
    Remove some transform units from environment ``environment``.
    """
    try:
        requires_auth(request=request, allow_root=True, role='admin_platform')
        data = get_request_json(request)
        numbers = orchestra.remove_transform_units(environment, int(data['num_units']), True)
        return ok_200('Removed %s (expected %s) transform units with number(s) %s from environment '
                      '"%s"' % (len(numbers), data['num_units'], numbers, environment), False)
    except Exception as e:
        map_exceptions(e)


@action('/transform/unit/environment/<environment>/number/<number>', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_unit_number_get(request, environment, number):
    """
    Return a transform unit serialized to JSON.
    """
    try:
        requires_auth(request=request, allow_root=True, allow_any=True)
        unit = orchestra.get_transform_unit(environment, number)
        if not unit:
            raise IndexError('Transform unit %s not found in environment %s.' %
                             (number, environment))
        return ok_200(unit, True)
    except Exception as e:
        map_exceptions(e)


@action('/transform/unit/environment/<environment>/number/<number>', methods=['DELETE'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_unit_number_delete(request, environment, number):
    """
    Remove transform unit number ``number`` from environment ``environment``.
    """
    try:
        requires_auth(request=request, allow_root=True, role='admin_platform')
        orchestra.remove_transform_unit(environment, number, True)
        return ok_200('The transform unit %s has been removed of environment %s.' %
                      (number, environment), False)
    except Exception as e:
        map_exceptions(e)


# Transformation tasks (encoding) ------------------------------------------------------------------

@action('/transform/queue', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_queue(request):
    """
    Return an array containing the transform queues serialized to JSON.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_transform_queues(), True)
    except Exception as e:
        map_exceptions(e)


@action('/transform/task/count', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_task_count(request):
    """
    Return transform tasks count.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_transform_tasks_count(), False)
    except Exception as e:
        map_exceptions(e)


@action('/transform/task/HEAD', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_task_head(request):
    """
    Return an array containing the transform tasks serialized as JSON.

    The transform tasks attributes are appended with the Celery's ``async result`` of the tasks.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_transform_tasks(), True)
    except Exception as e:
        map_exceptions(e)


@action('/transform/task', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_task_get(request):
    """
    Return an array containing the transform tasks serialized to JSON.

    The transform tasks attributes are appended with the Celery's ``async result`` of the tasks.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_transform_tasks(load_fields=True), True)
    except Exception as e:
        map_exceptions(e)


@action('/transform/task', methods=['POST'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_task_post(request):
    """
    Launch a transform task.

    Any user can launch a transform task using any media as input and any transform profile.
    This is linked to media and transform profile API methods access policies.

    The output media is registered to the database with the PENDING status and the ``parent_id``
    field is set to input media's ``id``. This permit to know relation between medias !

    The orchestrator will automatically add ``add_date`` to ``statistic``.

    .. note::

        Interesting enhancement would be to :

        * Schedule obs by specifying start time (...) ;
        * Handle the registration of tasks related to PENDING medias ;
    """
    try:
        auth_user = requires_auth(request=request, allow_any=True)
        data = get_request_json(request)
        if data['title']:  # Handle title-only metadata
            data['metadata'] = {'title': data['title']}
        task_id = orchestra.launch_transform_task(
            auth_user._id, data['media_in_id'], data['profile_id'], data['filename'],
            data['metadata'], data['queue'], '/transform/callback')
        return ok_200(task_id, True)
    except Exception as e:
        map_exceptions(e)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@action('/transform/task/id/<id>/HEAD', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_task_id_head(request, id):
    """
    Return a transform task serialized to JSON.

    The transform task attributes are appended with the Celery's ``async result`` of the task.
    """
    try:
        check_id(id)
        requires_auth(request=request, allow_any=True)
        task = orchestra.get_transform_task(specs={'_id': id})
        if not task:
            raise IndexError('No transform task with id %s.' % id)
        return ok_200(task, True)
    except Exception as e:
        map_exceptions(e)


@action('/transform/task/id/<id>', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_task_id_get(request, id):
    """
    Return a transform task serialized to JSON.

    The transform task attributes are appended with the Celery's ``async result`` of the task.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        check_id(id)
        requires_auth(request=request, allow_any=True)
        task = orchestra.get_transform_task(specs={'_id': id}, load_fields=True)
        if not task:
            raise IndexError('No transform task with id %s.' % id)
        return ok_200(task, True)
    except Exception as e:
        map_exceptions(e)


@action('/transform/task/id/<id>', methods=['DELETE'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_transform_task_id_delete(request, id):
    """
    Revoke a transform task.

    This method do not delete tasks from tasks database but set ``revoked`` attribute in tasks
    database and broadcast revoke request to transform units with Celery. If the task is actually
    running it will be canceled. The output media will be deleted.
    """
    try:
        check_id(id)
        auth_user = requires_auth(request=request, allow_any=True)
        task = orchestra.get_transform_task(specs={'_id': id})
        if not task:
            raise IndexError('No transform task with id %s.' % id)
        if auth_user._id != task.user_id:
            abort(403, 'You are not allowed to revoke transform task with id %s.' % id)
        orchestra.revoke_transform_task(task=task, terminate=True, remove=False, delete_media=True)
        return ok_200('The transform task "%s" has been revoked. Corresponding output media will be'
                      ' deleted.' % task._id, False)
    except Exception as e:
        map_exceptions(e)


# Publishing tasks ---------------------------------------------------------------------------------

@action('/publish/queue', methods=['GET'])
@action('/publisher/queue', methods=['GET'])
@action('/unpublish/queue', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_publish_queue(request):
    """
    Return an array containing the publish queues.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_publisher_queues(), True)
    except Exception as e:
        map_exceptions(e)


@action('/publish/task/count', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_publish_task_count(request):
    """
    Return publish tasks count.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_publish_tasks_count(), False)
    except Exception as e:
        map_exceptions(e)


@action('/publish/task/HEAD', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_publish_task_head(request):
    """
    Return an array containing the publish tasks serialized as JSON.

    The publish tasks attributes are appended with the Celery's ``async result`` of the tasks.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_publish_tasks(), True)
    except Exception as e:
        map_exceptions(e)


@action('/publish/task', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_publish_task_get(request):
    """
    Return an array containing the publish tasks serialized to JSON.

    The publish tasks attributes are appended with the Celery's ``async result`` of the tasks.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        requires_auth(request=request, allow_any=True)
        return ok_200(orchestra.get_publish_tasks(load_fields=True), True)
    except Exception as e:
        map_exceptions(e)


@action('/publish/task', methods=['POST'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_publish_task_post(request):
    """
    Launch a publish task.

    Any user can launch a publish task using any media as input.
    This is linked to media API methods access policy.

    The orchestrator will automatically add ``add_date`` to ``statistic``.

    .. note::

        Interesting enhancements would be to :

        * Schedule tasks by specifying start time (...)
        * Handle the registration of tasks related to PENDING medias
        * Permit to publish a media on more than one (1) publication queue
        * Permit to unpublish a media vbia a unpublish (broadcast) message
    """
    try:
        auth_user = requires_auth(request=request, allow_any=True)
        data = get_request_json(request)
        task_id = orchestra.launch_publish_task(auth_user._id, data['media_id'], data['queue'],
                                                '/publish/callback')
        return ok_200(task_id, True)
    except Exception as e:
        map_exceptions(e)


# FIXME why HEAD verb doesn't work (curl: (18) transfer closed with 263 bytes remaining to read) ?
@action('/publish/task/id/<id>/HEAD', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_publish_task_id_head(request, id):
    """
    Return a publish task serialized to JSON.

    The publish task attributes are appended with the Celery's ``async result`` of the task.
    """
    try:
        check_id(id)
        requires_auth(request=request, allow_any=True)
        task = orchestra.get_publish_task(specs={'_id': id})
        if not task:
            raise IndexError('No publish task with id %s.' % id)
        return ok_200(task, True)
    except Exception as e:
        map_exceptions(e)


@action('/publish/task/id/<id>', methods=['GET'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_publish_task_id_get(request, id):
    """
    Return a publish task serialized to JSON.

    The publish task attributes are appended with the Celery's ``async result`` of the task.

    All ``thing_id`` fields are replaced by corresponding ``thing``.
    For example ``user_id`` is replaced by ``user``'s data.
    """
    try:
        check_id(id)
        requires_auth(request=request, allow_any=True)
        task = orchestra.get_publish_task(specs={'_id': id}, load_fields=True)
        if not task:
            raise IndexError('No publish task with id %s.' % id)
        return ok_200(task, True)
    except Exception as e:
        map_exceptions(e)


@action('/publish/task/id/<id>', methods=['DELETE'])
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def api_publish_task_id_delete(request, id):
    """
    Revoke a publish task.

    This method do not delete tasks from tasks database but set ``revoked`` attribute in tasks
    database and broadcast revoke request to publisher units with Celery. If the task is actually
    running it will be canceled. The output publication media will be deleted.
    """
    try:
        check_id(id)
        auth_user = requires_auth(request=request, allow_any=True)
        task = orchestra.get_publish_task(specs={'_id': id})
        if not task:
            raise IndexError('No publish task with id %s.' % id)
        if auth_user._id != task.user_id:
            abort(403, 'You are not allowed to revoke publish task with id %s.' % id)
        orchestra.revoke_publish_task(task=task, terminate=True, remove=False)
        logging.info('here will be launched an unpublish task')
        #orchestra.launch_unpublish_task(auth_user._id, task, '/unpublish/callback')
        return ok_200('The publish task "%s" has been revoked. Corresponding media will be '
                      'unpublished from here.' % task._id, False)
    except Exception as e:
        map_exceptions(e)


# Workers (nodes) hooks ----------------------------------------------------------------------------

@action('/transform/callback', methods=['POST'])
@json_only()
def api_transform_task_hook(request):
    """
    This method is called by transform workers when they finish their work.

    If task is successful, the orchestrator will set media's status to READY.
    Else, the orchestrator will append ``error_details`` to ``statistic`` attribute of task.

    The media will be deleted if task failed (even the worker already take care of that).
    """
    try:
        requires_auth(request=request, allow_node=True)
        data = get_request_json(request)
        task_id, status = data['task_id'], data['status']
        logging.debug('task ' + task_id + ', status ' + status)
        orchestra.transform_callback(task_id, status)
        return ok_200('Your work is much appreciated, thanks !', False)
    except Exception as e:
        map_exceptions(e)


@action('/publish/callback', methods=['POST'])
@json_only()
def api_publish_task_hook(request):
    """
    This method is called by publisher workers when they finish their work.

    If task is successful, the orchestrator will update ``publish_uri`` attribute of task,
    set media's status to SUCCESS and update ``public_uris`` attribute.
    Else, the orchestrator will append ``error_details`` to ``statistic`` attribute of task.
    """
    try:
        requires_auth(request=request, allow_node=True)
        data = get_request_json(request)
        task_id = data['task_id']
        publish_uri = data['publish_uri'] if 'publish_uri' in data else None
        status = data['status']
        logging.debug('task ' + task_id + ', publish_uri ' + publish_uri + ', status ' + status)
        orchestra.publish_callback(task_id, publish_uri, status)
        return ok_200('Your work is much appreciated, thanks !', False)
    except Exception as e:
        map_exceptions(e)


# --------------------------------------------------------------------------------------------------

@action(route="/medias", template="medias/home.html", methods=['GET'])
@only_logged_user()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_medias(request):
    u"""
    Show the media assets home page.
    """
    return {}


@action(route="/medias/list", template="medias/list.html", methods=['GET'])
@only_logged_user()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_medias_list(request):
    u"""
    Show the media assets list page.
    """
    medias = response2dict(api_media_get(request), remove_underscore=True)
    return {'medias': medias, 'refresh_rate': 5}



@action(route="/medias/force_download/<id>",methods=['GET'])
@only_logged_user()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def get_medias(request, id):
    u"""
    Download a media
    """
    medias = api_media_id_get(request, id)
    uri = medias['value'].api_uri
    filename = medias['value'].filename

    return PlugItSendFile(uri, None, as_attachment=True, attachment_filename=filename)


@action(route="/transform/profiles", template="transform/profiles/home.html", methods=['GET'])
@only_logged_user()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_transform_profiles(request):
    u"""
    Show the transformation profiles home page.
    """
    encoders = response2dict(api_transform_profile_encoder(request), remove_underscore=True)
    return {'encoders': encoders}


@action(route="/transform/profiles/list", template="transform/profiles/list.html", methods=['GET'])
@only_logged_user()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_transform_profiles_list(request):
    u"""
    Show the transformation profiles list page.
    """
    profiles = response2dict(api_transform_profile_get(request), remove_underscore=True)
    return {'profiles': profiles, 'refresh_rate': 5}


@action(route="/transform/profiles/add", methods=['POST'])
@only_logged_user()
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_transform_profiles_add(request):
    u"""
    Add a transformation profile.
    """
    profile = response2dict(api_transform_profile_post(request), remove_underscore=True)
    return {'profile': profile}


@action(route="/transform/profiles/delete/<id>", methods=['GET'])
@only_logged_user()
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_transform_profiles_delete(request, id):
    u"""
    Delete a transformation profile.
    """
    msg = response2dict(api_transform_profile_id_delete(request, id), remove_underscore=True)
    return {'msg': msg}


@action(route="/transform/tasks", template="transform/tasks/home.html", methods=['GET'])
@only_logged_user()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_transform_tasks(request):
    u"""
    Show the transformation tasks home page.
    """
    medias = response2dict(api_media_head(request), remove_underscore=True)
    profiles = response2dict(api_transform_profile_get(request), remove_underscore=True)
    queues = response2dict(api_transform_queue(request), remove_underscore=True)
    return {'medias': medias, 'profiles': profiles, 'queues': queues}


@action(route="/transform/tasks/list", template="transform/tasks/list.html", methods=['GET'])
@only_logged_user()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_transform_tasks_list(request):
    u"""
    Show the transformation tasks list page.
    """
    tasks = response2dict(api_transform_task_get(request), remove_underscore=True)
    return {'tasks': tasks, 'refresh_rate': 5}


@action(route="/transform/tasks/launch", methods=['POST'])
@only_logged_user()
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_transform_tasks_launch(request):
    u"""
    Launch a transformation task.
    """
    task_id = response2dict(api_transform_task_post(request), remove_underscore=True)
    return {'task_id': task_id}


@action(route="/publisher/tasks", template="publisher/tasks/home.html", methods=['GET'])
@only_logged_user()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_publisher_tasks(request):
    u"""
    Show the publication tasks home page.
    """
    medias = response2dict(api_media_head(request), remove_underscore=True)
    queues = response2dict(api_publish_queue(request), remove_underscore=True)
    return {'medias': medias, 'queues': queues}


@action(route="/publisher/tasks/list", template="publisher/tasks/list.html", methods=['GET'])
@only_logged_user()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_publisher_tasks_list(request):
    u"""
    Show the publication tasks list page.
    """
    tasks = response2dict(api_publish_task_get(request), remove_underscore=True)
    return {'tasks': tasks, 'refresh_rate': 5}


@action(route="/publisher/tasks/launch", methods=['POST'])
@only_logged_user()
@json_only()
@user_info(props=['ebuio_admin', 'ebuio_member', 'first_name', 'last_name', 'username', 'email'])
def view_publisher_tasks_launch(request):
    u"""
    Launch a publication task.
    """
    task_id = response2dict(api_publish_task_post(request), remove_underscore=True)
    return {'task_id': task_id}
