# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
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

import os, re, select, shlex, time
from celery import current_task, states
from celery.decorators import task
#from celery.signals import celeryd_after_setup, worker_shutdown
from kitchen.text.converters import to_bytes
from subprocess import Popen, PIPE
from oscied_config import TransformLocalConfig
from oscied_models import Media, TransformProfile
from oscied_util import Callback
from pyutils.py_datetime import datetime_now, duration2secs
from pyutils.py_ffmpeg import get_media_duration, get_media_tracks
from pyutils.py_filesystem import get_size, recursive_copy, try_makedirs
from pyutils.py_serialization import object2json
from pyutils.py_subprocess import make_async, read_async
from pyutils.py_unicode import configure_unicode

configure_unicode()

# Read video frame 4903
DASHCAST_REGEX = re.compile(r'Read video frame (?P<frame>\d+)')

# frame= 2071 fps=  0 q=-1.0 size=   34623kB time=00:01:25.89 bitrate=3302.3kbits/s
FFMPEG_REGEX = re.compile(
    r'frame=\s*(?P<frame>\d+)\s+fps=\s*(?P<fps>\d+)\s+q=\s*(?P<q>\S+)\s+\S*size=\s*(?P<size>\S+)\s+'
    r'time=\s*(?P<time>\S+)\s+bitrate=\s*(?P<bitrate>\S+)')


#@celeryd_after_setup.connect
#def setup_direct_queue(sender, instance, **kwargs):
#    queue_name = sender   # sender is the hostname of the worker
#    instance.app.amqp.queues.select_add(queue_name)
#@worker_shutdown.connect
#def test(**kwargs):
#    print(kwargs)


@task(name=u'TransformWorker.transform_task')
def transform_task(media_in_json, media_out_json, profile_json, callback_json):

    def copy_callback(start_date, elapsed_time, eta_time, src_size, dst_size, ratio):
        transform_task.update_state(state=u'PROGRESS', meta={
            u'hostname': request.hostname, 'start_date': start_date, u'elapsed_time': elapsed_time,
            u'eta_time': eta_time, u'media_in_size': src_size, u'media_out_size': dst_size,
            u'percent': int(100 * ratio)})

    def transform_callback(status):
        data_json = object2json({u'task_id': request.id, u'status': status}, include_properties=False)
        if callback is None:
            print(u'{0} [ERROR] Unable to callback orchestrator: {1}'.format(request.id, data_json))
        else:
            r = callback.post(data_json)
            print(u'{0} Code {1} {2} : {3}'.format(request.id, r.status_code, r.reason, r._content))

    # ------------------------------------------------------------------------------------------------------------------

    RATIO_DELTA, TIME_DELTA = 0.01, 1  # Update status if at least 1% of progress and 1 second elapsed.
    MAX_TIME_DELTA = 5                 # Also ensure status update every 5 seconds.
    DASHCAST_TIMEOUT_TIME = 10

    try:
        # Avoid 'referenced before assignment'
        callback, encoder_out, request = None, u'', current_task.request

        # Let's the task begin !
        print(u'{0} Transformation task started'.format(request.id))

        # Read current configuration to translate files uri to local paths
        local_config = TransformLocalConfig.read(u'local_config.pkl')
        print(object2json(local_config, include_properties=True))

        # Load and check task parameters
        callback = Callback.from_json(callback_json, inspect_constructor=True)
        callback.is_valid(True)

        # Update callback socket according to configuration
        if local_config.api_nat_socket and len(local_config.api_nat_socket) > 0:
            callback.replace_netloc(local_config.api_nat_socket)

        media_in = Media.from_json(media_in_json, inspect_constructor=True)
        media_out = Media.from_json(media_out_json, inspect_constructor=True)
        profile = TransformProfile.from_json(profile_json, inspect_constructor=True)
        media_in.is_valid(True)
        media_out.is_valid(True)
        profile.is_valid(True)

        # Verify that media file can be accessed and create output path
        media_in_path = local_config.storage_medias_path(media_in, generate=False)
        if not media_in_path:
            raise NotImplementedError(to_bytes(u'Input media will not be readed from shared storage : {0}'.format(
                                      media_in.uri)))
        media_out_path = local_config.storage_medias_path(media_out, generate=True)
        if not media_out_path:
            raise NotImplementedError(to_bytes(u'Output media will not be written to shared storage : {0}'.format(
                                      media_out.uri)))
        media_in_root = os.path.dirname(media_in_path)
        media_out_root = os.path.dirname(media_out_path)
        try_makedirs(media_out_root)

        # Get input media duration and frames to be able to estimate ETA
        media_in_duration = get_media_duration(media_in_path)

        # NOT A REAL TRANSFORM : FILE COPY -----------------------------------------------------------------------------
        if profile.encoder_name == u'copy':
            infos = recursive_copy(media_in_root, media_out_root, copy_callback, RATIO_DELTA, TIME_DELTA)
            media_out_tmp = media_in_path.replace(media_in_root, media_out_root)
            os.rename(media_out_tmp, media_out_path)
            start_date = infos[u'start_date']
            elapsed_time = infos[u'elapsed_time']
            media_in_size = infos[u'src_size']

        # A REAL TRANSFORM : TRANSCODE WITH FFMPEG ---------------------------------------------------------------------
        elif profile.encoder_name == u'ffmpeg':

            start_date, start_time = datetime_now(), time.time()
            prev_ratio = prev_time = 0

            # Get input media size to be able to estimate ETA
            media_in_size = get_size(media_in_root)

            # Create FFmpeg subprocess
            cmd = u'ffmpeg -y -i "{0}" {1} "{2}"'.format(media_in_path, profile.encoder_string, media_out_path)
            print(cmd)
            ffmpeg = Popen(shlex.split(cmd), stderr=PIPE, close_fds=True)
            make_async(ffmpeg.stderr)

            while True:
                # Wait for data to become available
                select.select([ffmpeg.stderr], [], [])
                chunk = ffmpeg.stderr.read()
                encoder_out += chunk
                match = FFMPEG_REGEX.match(chunk)
                if match:
                    stats = match.groupdict()
                    media_out_duration = stats[u'time']
                    try:
                        ratio = duration2secs(media_out_duration) / duration2secs(media_in_duration)
                        ratio = 0.0 if ratio < 0.0 else 1.0 if ratio > 1.0 else ratio
                    except ZeroDivisionError:
                        ratio = 1.0
                    elapsed_time = time.time() - start_time
                    delta_time = elapsed_time - prev_time
                    if (ratio - prev_ratio > RATIO_DELTA and delta_time > TIME_DELTA) or delta_time > MAX_TIME_DELTA:
                        prev_ratio, prev_time = ratio, elapsed_time
                        eta_time = int(elapsed_time * (1.0 - ratio) / ratio) if ratio > 0 else 0
                        transform_task.update_state(
                            state=u'PROGRESS',
                            meta={u'hostname': request.hostname,
                                  u'start_date': start_date,
                                  u'elapsed_time': elapsed_time,
                                  u'eta_time': eta_time,
                                  u'media_in_size': media_in_size,
                                  u'media_in_duration': media_in_duration,
                                  u'media_out_size': get_size(media_out_root),
                                  u'media_out_duration': media_out_duration,
                                  u'percent': int(100 * ratio),
                                  u'encoding_frame': stats[u'frame'],
                                  u'encoding_fps': stats[u'fps'],
                                  u'encoding_bitrate': stats[u'bitrate'],
                                  u'encoding_quality': stats[u'q']})
                returncode = ffmpeg.poll()
                if returncode is not None:
                    break

            # FFmpeg output sanity check
            if returncode != 0:
                raise OSError(to_bytes(u'FFmpeg return code is {0}, encoding probably failed.'.format(returncode)))

            # Output media file sanity check
#            media_out_duration = get_media_duration(media_out_path)
#            if duration2secs(media_out_duration) / duration2secs(media_in_duration) > 1.5 or < 0.8:
#                salut

        # A REAL TRANSFORM : TRANSCODE WITH DASHCAST -------------------------------------------------------------------
        elif profile.encoder_name == u'dashcast':

            start_date, start_time = datetime_now(), time.time()
            prev_ratio = prev_time = 0

            # Get input media size and frames to be able to estimate ETA
            media_in_size = get_size(media_in_root)
            try:
                media_in_frames = int(get_media_tracks(media_in_path)[u'video'][u'0:0'][u'estimated_frames'])
                media_out_frames = 0
            except:
                raise ValueError(to_bytes(u'Unable to estimate # frames of input media'))

            # Create DashCast subprocess
            cmd = u'DashCast -av "{0}" {1} -out "{2}" -mpd "{3}"'.format(
                media_in_path, profile.encoder_string, media_out_root, media_out.filename)
            print(cmd)
            dashcast = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, close_fds=True)
            make_async(dashcast.stdout.fileno())
            make_async(dashcast.stderr.fileno())

            while True:
                # Wait for data to become available
                select.select([dashcast.stdout.fileno()], [], [])
                stdout, stderr = read_async(dashcast.stdout), read_async(dashcast.stderr)
                match = DASHCAST_REGEX.match(stdout)
                if match:
                    stats = match.groupdict()
                    media_out_frames = int(stats[u'frame'])
                    try:
                        ratio = float(media_out_frames) / media_in_frames
                        ratio = 0.0 if ratio < 0.0 else 1.0 if ratio > 1.0 else ratio
                    except ZeroDivisionError:
                        ratio = 1.0
                    elapsed_time = time.time() - start_time
                    delta_time = elapsed_time - prev_time
                    if (ratio - prev_ratio > RATIO_DELTA and delta_time > TIME_DELTA) or delta_time > MAX_TIME_DELTA:
                        prev_ratio, prev_time = ratio, elapsed_time
                        eta_time = int(elapsed_time * (1.0 - ratio) / ratio) if ratio > 0 else 0
                        transform_task.update_state(
                            state=u'PROGRESS',
                            meta={u'hostname': request.hostname,
                                  u'start_date': start_date,
                                  u'elapsed_time': elapsed_time,
                                  u'eta_time': eta_time,
                                  u'media_in_size': media_in_size,
                                  u'media_in_duration': media_in_duration,
                                  u'media_out_size': get_size(media_out_root),
                                  u'percent': int(100 * ratio),
                                  u'encoding_frame': media_out_frames})
                returncode = dashcast.poll()
                if returncode is not None:
                    encoder_out = u'stdout: {0}\nstderr: {1}'.format(stdout, stderr)
                    break
                if media_out_frames == 0 and elapsed_time > DASHCAST_TIMEOUT_TIME:
                    encoder_out = u'stdout: {0}\nstderr: {1}'.format(stdout, stderr)
                    raise OSError(to_bytes(u'DashCast does not output frame number, encoding probably failed.'))

            # DashCast output sanity check
            if not os.path.exists(media_out_path):
                raise OSError(to_bytes(u'Output media not found, DashCast encoding probably failed.'))
            if returncode != 0:
                raise OSError(to_bytes(u'DashCast return code is {0}, encoding probably failed.'.format(returncode)))
            # FIXME check duration too !

        # Here all seem okay -------------------------------------------------------------------------------------------
        media_out_size = get_size(media_out_root)
        media_out_duration = get_media_duration(media_out_path)
        print(u'{0} Transformation task successful, output media {1}'.format(request.id, media_out.filename))
        transform_callback(states.SUCCESS)
        return {u'hostname': request.hostname, u'start_date': start_date, u'elapsed_time': elapsed_time,
                u'eta_time': 0, u'media_in_size': media_in_size, u'media_in_duration': media_in_duration,
                u'media_out_size': media_out_size, u'media_out_duration': media_out_duration, u'percent': 100}

    except Exception as error:

        # Here something went wrong
        print(u'{0} Transformation task failed '.format(request.id))
        transform_callback(u'ERROR\n{0}\n\nOUTPUT\n{1}'.format(unicode(error), encoder_out))
        raise
