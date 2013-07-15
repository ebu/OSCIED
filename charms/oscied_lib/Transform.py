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
from Storage import Storage
from TransformConfig import TransformConfig
from TransformProfile import TransformProfile
from User import User
from pyutils.ffmpeg import get_media_duration, get_media_tracks
from pyutils.pyutils import object2json, datetime_now, duration2secs, make_async, read_async


@task(name='Transform.transform_job')
def transform_job(user_json, media_in_json, media_out_json, profile_json, callback_json):

    try:
        # Avoid 'referenced before assignment'
        callback = media_out = None
        encoder_out = ''
        request = current_task.request

        # Let's the task begin !
        start_date, start_time = datetime_now(), time.time()
        print('%s Transform job started' % (request.id))

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
        media_out_root = os.path.dirname(media_out_path)
        Storage.create_file_directory(media_out_path)

        # Get input media size, duration and frames to be able to estimate ETA
        media_in_size = os.stat(media_in_path).st_size
        media_in_duration = get_media_duration(media_in_path)
        try:
            media_in_frames = \
                int(get_media_tracks(media_in_path)['video']['0.0']['estimated_frames'])
        except:
            media_in_frames = None

        # NOT A REAL TRANSFORM : FILE COPY ---------------------------------------------------------
        if profile.encoder_name == 'copy':
            block_size = 1024 * 1024
            media_in_file = open(media_in_path, "rb")
            media_out_file = open(media_out_path, "wb")

            # Block-based media copy loop
            block_pos = 0
            while True:
                block = media_in_file.read(block_size)
                ratio = float(block_pos) / media_in_size
                elapsed_time = time.time() - start_time
                eta_time = int(elapsed_time * (1 - ratio) / ratio) if ratio > 0 else 0
                transform_job.update_state(
                    state="PROGRESS",
                    meta={'hostname': request.hostname,
                          'start_date': start_date,
                          'elapsed_time': elapsed_time,
                          'eta_time': eta_time,
                          'media_in_size': media_in_size,
                          'media_in_duration': media_in_duration,
                          'media_out_size': block_pos,
                          'percent': int(100 * ratio)})
                block_pos += block_size
                if block:
                    media_out_file.write(block)
                else:  # End of input media reached
                    break
            media_in_file.close()
            media_out_file.close()  # FIXME maybe a finally block for that

            # Output media file sanity check
            media_out_size = os.stat(media_out_path).st_size
            if media_out_size != media_in_size:
                raise IOError("Output media size does not match input (%s vs %s)" %
                              (media_in_size, media_out_size))

        # A REAL TRANSFORM : TRANSCODE WITH FFMPEG -------------------------------------------------
        elif profile.encoder_name == 'ffmpeg':
            # Create FFmpeg subprocess
            ffmpeg = Popen(shlex.split('ffmpeg -y -i "%s" %s "%s"' % (media_in_path,
                           profile.encoder_string, media_out_path)), stderr=PIPE, close_fds=True)
            make_async(ffmpeg.stderr)

            # frame= 2071 fps=  0 q=-1.0 size=   34623kB time=00:01:25.89 bitrate=3302.3kbits/s
            regex = re.compile(r'frame=\s*(?P<frame>\d+)\s+fps=\s*(?P<fps>\d+)\s+q=\s*(?P<q>\S+)'
                               r'\s+\S*size=\s*(?P<size>\S+)\s+time=\s*(?P<time>\S+)'
                               r'\s+bitrate=\s*(?P<bitrate>\S+)')

            while True:
                # Wait for data to become available
                select.select([ffmpeg.stderr], [], [])
                chunk = ffmpeg.stderr.read()
                encoder_out += chunk
                match = regex.match(chunk)
                if match:
                    stats = match.groupdict()
                    media_out_duration = stats['time']
                    ratio = duration2secs(media_out_duration) / duration2secs(media_in_duration)
                    elapsed_time = time.time() - start_time
                    eta_time = int(elapsed_time * (1 - ratio) / ratio) if ratio > 0 else 0
                    transform_job.update_state(
                        state="PROGRESS",
                        meta={'hostname': request.hostname,
                              'start_date': start_date,
                              'elapsed_time': elapsed_time,
                              'eta_time': eta_time,
                              'media_in_size': media_in_size,
                              'media_in_duration': media_in_duration,
                              'media_out_size': os.stat(media_out_path).st_size,
                              'media_out_duration': media_out_duration,
                              'percent': int(100 * ratio),
                              'encoding_frame': stats['frame'],
                              'encoding_fps': stats['fps'],
                              'encoding_bitrate': stats['bitrate'],
                              'encoding_quality': stats['q']})
                returncode = ffmpeg.poll()
                if returncode != None:
                    break

            # FFmpeg output sanity check
            if returncode != 0:
                raise OSError('FFmpeg return code is %s, encoding probably failed' % returncode)

            # Output media file sanity check
#            media_out_duration = get_media_duration(media_out_path)
#            if duration2secs(media_out_duration) / duration2secs(media_in_duration) > 1.5 or < 0.8:
#                salut

        # A REAL TRANSFORM : TRANSCODE WITH DASHCAST -----------------------------------------------
        elif profile.encoder_name == 'dashcast':
            # Create DashCast subprocess
            dashcast = Popen(shlex.split('DashCast -av "%s" %s -out "%s" -mpd "%s"' % (
                media_in_path, profile.encoder_string, media_out_root, media_out_path)),
                stdout=PIPE, close_fds=True)
            make_async(dashcast.stdout.fileno())

            # Read video frame 4903
            regex = re.compile(r'Read video frame (?P<frame>\d+)')

            while True:
                # Wait for data to become available
                select.select([dashcast.stdout.fileno()], [], [])
                chunk = read_async(dashcast.stdout)
                encoder_out += chunk
                match = regex.match(chunk)
                if match:
                    stats = match.groupdict()
                    media_out_frames = int(stats['frame'])
                    ratio = media_out_frames / media_in_frames
                    elapsed_time = time.time() - start_time
                    eta_time = int(elapsed_time * (1 - ratio) / ratio) if ratio > 0 else 0
                    transform_job.update_state(
                        state="PROGRESS",
                        meta={'hostname': request.hostname,
                              'start_date': start_date,
                              'elapsed_time': elapsed_time,
                              'eta_time': eta_time,
                              'media_in_size': media_in_size,
                              'media_in_duration': media_in_duration,
                              #'media_out_size': os.stat(media_out_path).st_size,
                              'percent': int(100 * ratio),
                              'encoding_frame': media_out_frames})
                returncode = dashcast.poll()
                if returncode != None:
                    break

            # DashCast output sanity check
            if returncode != 0:
                raise OSError('DashCast return code is %s, encoding probably failed' % returncode)

        # Here all seem okay -----------------------------------------------------------------------
        media_out_size = os.stat(media_out_path).st_size
        elapsed_time = time.time() - start_time
        print('%s Transform job successful' % (request.id))
        print('%s Callback: Ask to update output media %s' % (request.id, media_out.filename))
        data_json = object2json({'job_id': request.id, 'status': 'SUCCESS'}, False)
        result = callback.post(data_json)
        print(
            '%s Code %s %s : %s' % (request.id, result.status_code, result.reason, result._content))
        return {'hostname': request.hostname,
                'start_date': start_date,
                'elapsed_time': elapsed_time,
                'eta_time': 0,
                'media_in_size': media_in_size,
                'media_in_duration': media_in_duration,
                'media_out_size': media_out_size,
                'media_out_duration': get_media_duration(media_out_path),
                'percent': 100}

    except Exception as error:

        # Here something went wrong
        if media_out:
            name = media_out.filename
            try:
                Storage.delete_media(config, media_out)
            except:
                pass  # FIXME a good idea ?
        else:
            name = 'None'
        print('%s Transform job failed ' % (request.id))
        print('%s Callback : Ask to delete output media %s' % (request.id, name))
        data_json = object2json({
            'job_id': request.id,
            'status': 'ERROR\n%s\n\nOUTPUT\n%s' % (str(error), encoder_out,)}, False)
        if callback is None:
            print('%s [ERROR] Unable to callback orchestrator: %s' % (request.id, data_json))
        else:
            result = callback.post(data_json)
            print('%s Code %s %s : %s' %
                  (request.id, result.status_code, result.reason, result._content))
        raise
