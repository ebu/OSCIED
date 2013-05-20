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

import fcntl, os, re, select, shlex, subprocess, time
from celery import current_task
from celery.decorators import task
from Callback import Callback
from FFmpeg import get_media_duration
from Media import Media
from Storage import Storage
from TransformConfig import TransformConfig
from TransformProfile import TransformProfile
from User import User
from pyutils.pyutils import object2json, datetime_now, duration2secs


@task(name='Transform.transform_job')
def transform_job(user_json, media_in_json, media_out_json, profile_json, callback_json):

    try:
        # Avoid 'referenced before assignment'
        media_out = None
        encoder_out = ''
        request = current_task.request

        # Let's the task begin !
        start_date = datetime_now()
        start_time = time.time()
        print('%s Transform job started' % (request.id))

        # Read current configuration to translate files uri to local paths
        config = TransformConfig.read('config.json')
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
        media_in_path = Storage.media_path(config, media_in, False)
        if not media_in_path:
            raise NotImplementedError('Input media will not be readed from shared storage : %s' %
                                      media_in.uri)
        media_out_path = Storage.media_path(config, media_out, True)
        if not media_out_path:
            raise NotImplementedError('Output media will not be written to shared storage : %s' %
                                      media_out.uri)
        Storage.create_file_directory(media_out_path)

        # Get input media duration to be able to estimate ETA
        media_in_size = os.stat(media_in_path).st_size
        media_in_duration = get_media_duration(media_in_path)

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
            cmd = 'ffmpeg -y -i "%s" %s "%s"' % (
                media_in_path, profile.encoder_string, media_out_path)
            ffmpeg = subprocess.Popen(shlex.split(cmd), stderr=subprocess.PIPE, close_fds=True)

            # http://stackoverflow.com/questions/1388753/how-to-get-output-from-subprocess-popen
            fcntl.fcntl(ffmpeg.stderr.fileno(), fcntl.F_SETFL,
                        fcntl.fcntl(ffmpeg.stderr.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,)

            # frame= 2071 fps=  0 q=-1.0 size=   34623kB time=00:01:25.89 bitrate=3302.3kbits/s
            regex = re.compile("frame=\s*(?P<frame>\d+)" +
                               "\s+fps=\s*(?P<fps>\d+)" +
                               "\s+q=\s*(?P<q>\S+)" +
                               "\s+\S*size=\s*(?P<size>\S+)" +
                               "\s+time=\s*(?P<time>\S+)" +
                               "\s+bitrate=\s*(?P<bitrate>\S+)")

            while True:
                readeable = select.select([ffmpeg.stderr.fileno()], [], [])[0]
                if readeable:
                    chunk = ffmpeg.stderr.read()
                    if chunk == '':
                        break  # End of encoding reached
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
                time.sleep(1)  # FIXME put this number as parameter of the Transform charm (?)

            # FFmpeg output sanity check (yes, this is parsing)
            # video:78315kB audio:4876kB global headers:0kB muxing overhead 0.214781%
            match = re.search("\s+muxing overhead\s*(?P<overhead>\S+)", encoder_out)
            if not match:
                raise OSError('Unable to parse FFmpeg output, encoding probably failed')

            # Output media file sanity check
#            media_out_duration = get_media_duration(media_out_path)
#            if duration2secs(media_out_duration) / duration2secs(media_in_duration) > 1.5 or < 0.8:
#                salut

        # A REAL TRANSFORM : TRANSCODE WITH DASHCAST -----------------------------------------------
        elif profile.encoder_name == 'dashcast':
            raise NotImplementedError('FIXME Encoding with DashCast not yet implemented')

        # Here all seem okay -----------------------------------------------------------------------
        media_out_size = os.stat(media_out_path).st_size
        elapsed_time = time.time() - start_time
        print('%s Transform job successful' % (request.id))
        print('%s Callback: Ask to update output media %s' % (request.id, media_out.virtual_filename))
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
            name = media_out.virtual_filename
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
        result = callback.post(data_json)
        print('%s Code %s %s : %s' % (request.id, result.status_code, result.reason, result._content))
        raise
