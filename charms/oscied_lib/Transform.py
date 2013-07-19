#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : TRANSFORM
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

import os, re, select, shlex, time
from celery import current_task
from celery.decorators import task
from subprocess import Popen, PIPE
from Callback import Callback
from Media import Media
from TransformConfig import TransformConfig
from TransformProfile import TransformProfile
from User import User
from pyutils.ffmpeg import get_media_duration, get_media_tracks
from pyutils.filesystem import get_size, recursive_copy, try_makedirs
from pyutils.pyutils import object2json, datetime_now, duration2secs, make_async, read_async

# Read video frame 4903
DASHCAST_REGEX = re.compile(r'Read video frame (?P<frame>\d+)')

# frame= 2071 fps=  0 q=-1.0 size=   34623kB time=00:01:25.89 bitrate=3302.3kbits/s
FFMPEG_REGEX = re.compile(
    r'frame=\s*(?P<frame>\d+)\s+fps=\s*(?P<fps>\d+)\s+q=\s*(?P<q>\S+)\s+\S*size=\s*(?P<size>\S+)\s+'
    r'time=\s*(?P<time>\S+)\s+bitrate=\s*(?P<bitrate>\S+)')


@task(name='Transform.transform_task')
def transform_task(user_json, media_in_json, media_out_json, profile_json, callback_json):

    def copy_callback(start_date, elapsed_time, eta_time, src_size, dst_size, ratio):
        transform_task.update_state(state='PROGRESS', meta={
            'hostname': request.hostname, 'start_date': start_date, 'elapsed_time': elapsed_time,
            'eta_time': eta_time, 'media_in_size': src_size, 'media_out_size': dst_size,
            'percent': int(100 * ratio)})

    def transform_callback(status):
        data_json = object2json({'task_id': request.id, 'status': status}, False)
        if callback is None:
            print('%s [ERROR] Unable to callback orchestrator: %s' % (request.id, data_json))
        else:
            r = callback.post(data_json)
            print('%s Code %s %s : %s' % (request.id, r.status_code, r.reason, r._content))

    # ----------------------------------------------------------------------------------------------

    RATIO_DELTA = 0.01  # Update status if at least 1% of progress
    TIME_DELTA = 1      # Update status if at least 1 second(s) elapsed

    try:
        # Avoid 'referenced before assignment'
        callback, encoder_out = None, ''
        request = current_task.request

        # Let's the task begin !
        print('%s Transform task started' % request.id)

        # Read current configuration to translate files uri to local paths
        config = TransformConfig.read('local_config.pkl')
        print object2json(config, True)

        # Load and check task parameters
        user = User.load(user_json)
        media_in = Media.load(media_in_json)
        media_out = Media.load(media_out_json)
        profile = TransformProfile.load(profile_json)
        callback = Callback.load(callback_json)
        user.is_valid(True)
        media_in.is_valid(True)
        media_out.is_valid(True)
        profile.is_valid(True)
        callback.is_valid(True)

        # Update callback socket according to configuration
        if config.api_nat_socket and len(config.api_nat_socket) > 0:
            callback.replace_netloc(config.api_nat_socket)

        # Verify that media file can be accessed and create output path
        media_in_path = config.storage_medias_path(media_in, generate=False)
        if not media_in_path:
            raise NotImplementedError('Input media will not be readed from shared storage : %s' %
                                      media_in.uri)
        media_out_path = config.storage_medias_path(media_out, generate=True)
        if not media_out_path:
            raise NotImplementedError('Output media will not be written to shared storage : %s' %
                                      media_out.uri)
        media_in_root = os.path.dirname(media_in_path)
        media_out_root = os.path.dirname(media_out_path)
        try_makedirs(media_out_root)

        # Get input media duration and frames to be able to estimate ETA
        media_in_duration = get_media_duration(media_in_path)

        # NOT A REAL TRANSFORM : FILE COPY ---------------------------------------------------------
        if profile.encoder_name == 'copy':
            infos = recursive_copy(
                media_in_root, media_out_root, copy_callback, RATIO_DELTA, TIME_DELTA)
            media_out_tmp = media_in_path.replace(media_in_root, media_out_root)
            os.rename(media_out_tmp, media_out_path)
            start_date = infos['start_date']
            elapsed_time = infos['elapsed_time']
            media_in_size = infos['src_size']

        # A REAL TRANSFORM : TRANSCODE WITH FFMPEG -------------------------------------------------
        elif profile.encoder_name == 'ffmpeg':

            start_date, start_time = datetime_now(), time.time()
            prev_ratio = prev_time = 0

            # Get input media size to be able to estimate ETA
            media_in_size = get_size(media_in_root)

            # Create FFmpeg subprocess
            cmd = 'ffmpeg -y -i "%s" %s "%s"' % (
                media_in_path, profile.encoder_string, media_out_path)
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
                    media_out_duration = stats['time']
                    try:
                        ratio = duration2secs(media_out_duration) / duration2secs(media_in_duration)
                        ratio = 0.0 if ratio < 0.0 else 1.0 if ratio > 1.0 else ratio
                    except ZeroDivisionError:
                        ratio = 1.0
                    elapsed_time = time.time() - start_time
                    # Update status of task only if delta time or delta ratio is sufficient
                    if ratio - prev_ratio > RATIO_DELTA and elapsed_time - prev_time > TIME_DELTA:
                        prev_ratio, prev_time = ratio, elapsed_time
                        eta_time = int(elapsed_time * (1.0 - ratio) / ratio) if ratio > 0 else 0
                        transform_task.update_state(
                            state='PROGRESS',
                            meta={'hostname': request.hostname,
                                  'start_date': start_date,
                                  'elapsed_time': elapsed_time,
                                  'eta_time': eta_time,
                                  'media_in_size': media_in_size,
                                  'media_in_duration': media_in_duration,
                                  'media_out_size': get_size(media_out_root),
                                  'media_out_duration': media_out_duration,
                                  'percent': int(100 * ratio),
                                  'encoding_frame': stats['frame'],
                                  'encoding_fps': stats['fps'],
                                  'encoding_bitrate': stats['bitrate'],
                                  'encoding_quality': stats['q']})
                returncode = ffmpeg.poll()
                if returncode is not None:
                    break

            # FFmpeg output sanity check
            if returncode != 0:
                raise OSError('FFmpeg return code is %s, encoding probably failed.' % returncode)

            # Output media file sanity check
#            media_out_duration = get_media_duration(media_out_path)
#            if duration2secs(media_out_duration) / duration2secs(media_in_duration) > 1.5 or < 0.8:
#                salut

        # A REAL TRANSFORM : TRANSCODE WITH DASHCAST -----------------------------------------------
        elif profile.encoder_name == 'dashcast':

            start_date, start_time = datetime_now(), time.time()
            prev_ratio = prev_time = 0

            # Get input media size and frames to be able to estimate ETA
            media_in_size = get_size(media_in_root)
            try:
                media_in_frames = \
                    int(get_media_tracks(media_in_path)['video']['0.0']['estimated_frames'])
            except:
                media_in_frames = None

            # Create DashCast subprocess
            cmd = 'DashCast -av "%s" %s -out "%s" -mpd "%s"' % (
                media_in_path, profile.encoder_string, media_out_root, media_out.filename)
            print(cmd)
            dashcast = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE, close_fds=True)
            make_async(dashcast.stdout.fileno())
            make_async(dashcast.stderr.fileno())

            while True:
                # Wait for data to become available
                select.select([dashcast.stdout.fileno()], [], [])
                match = DASHCAST_REGEX.match(read_async(dashcast.stdout))
                if match:
                    stats = match.groupdict()
                    media_out_frames = int(stats['frame'])
                    try:
                        ratio = float(media_out_frames) / media_in_frames
                        ratio = 0.0 if ratio < 0.0 else 1.0 if ratio > 1.0 else ratio
                    except ZeroDivisionError:
                        ratio = 1.0
                    elapsed_time = time.time() - start_time
                    # Update status of task only if delta time or delta ratio is sufficient
                    if ratio - prev_ratio > RATIO_DELTA and elapsed_time - prev_time > TIME_DELTA:
                        prev_ratio, prev_time = ratio, elapsed_time
                        eta_time = int(elapsed_time * (1.0 - ratio) / ratio) if ratio > 0 else 0
                        transform_task.update_state(
                            state='PROGRESS',
                            meta={'hostname': request.hostname,
                                  'start_date': start_date,
                                  'elapsed_time': elapsed_time,
                                  'eta_time': eta_time,
                                  'media_in_size': media_in_size,
                                  'media_in_duration': media_in_duration,
                                  'media_out_size': get_size(media_out_root),
                                  'percent': int(100 * ratio),
                                  'encoding_frame': media_out_frames})
                returncode = dashcast.poll()
                if returncode is not None:
                    encoder_out = read_async(dashcast.stderr)
                    break

            # DashCast output sanity check
            if not os.path.exists(media_out_path):
                raise OSError('Output media not found, DashCast encoding probably failed.')
            if returncode != 0:
                raise OSError('DashCast return code is %s, encoding probably failed.' % returncode)
            # FIXME check duration too !

        # Here all seem okay -----------------------------------------------------------------------
        media_out_size = get_size(media_out_root)
        media_out_duration = get_media_duration(media_out_path)
        print('%s Transform task successful, output media %s' % (request.id, media_out.filename))
        transform_callback('SUCCESS')
        return {'hostname': request.hostname, 'start_date': start_date,
                'elapsed_time': elapsed_time, 'eta_time': 0, 'media_in_size': media_in_size,
                'media_in_duration': media_in_duration, 'media_out_size': media_out_size,
                'media_out_duration': media_out_duration, 'percent': 100}

    except Exception as error:

        # Here something went wrong
        print('%s Transform task failed ' % request.id)
        transform_callback('ERROR\n%s\n\nOUTPUT\n%s' % (str(error), encoder_out))
        raise
