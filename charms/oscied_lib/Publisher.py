#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : PUBLISHER
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

import time, os, shutil
from celery import current_task
from celery.decorators import task
from Callback import Callback
from Media import Media
from PublisherConfig import PublisherConfig
from Storage import Storage
from User import User
from pyutils.filesystem import get_size
from pyutils.pyutils import object2json, datetime_now


@task(name='Publisher.publish_job')
def publish_job(user_json, media_json, callback_json):

    RATIO_DELTA = 0.01  # Update status if at least 1% of progress
    TIME_DELTA = 1      # Update status if at least 1 second(s) elapsed

    try:
        # Avoid 'referenced before assignment'
        callback = media_path = publish_path = publish_root = None
        request = current_task.request

        # Let's the task begin !
        start_date, start_time = datetime_now(), time.time()
        print('%s Publish job started' % (request.id))

        # Read current configuration to translate files uri to local paths
        config = PublisherConfig.read('local_config.pkl')
        print object2json(config, True)

        # Load and check task parameters
        user = User.load(user_json)
        media = Media.load(media_json)
        callback = Callback.load(callback_json)
        user.is_valid(True)
        media.is_valid(True)
        callback.is_valid(True)

        # Update callback socket according to configuration
        if config.api_nat_socket and len(config.api_nat_socket) > 0:
            callback.replace_netloc(config.api_nat_socket)

        # Verify that media file can be accessed
        media_path = config.storage_medias_path(media, generate=False)
        if not media_path:
            raise NotImplementedError('Media will not be readed from shared storage : %s' %
                                      media.uri)
        publish_path, publish_uri = config.publish_point(media)
        media_root, publish_root = os.path.dirname(media_path), os.path.dirname(publish_path)
        media_size, publish_size = get_size(media_root), 0

        # Recursive copy of a media (directory of files or file) to the local path of the publisher
        for root, dirnames, filenames in os.walk(media_root):
            for filename in filenames:
                dst_root = root.replace(media_root, publish_root)
                src_path = os.path.join(root, filename)
                dst_path = os.path.join(dst_root, filename)

                # Initialize block-based copy
                Storage.create_file_directory(dst_path)
                block_size = 1024 * 1024
                src_file = open(src_path, 'rb')
                dst_file = open(dst_path, 'wb')

                # Block-based copy loop
                block_pos = prev_ratio = prev_time = 0
                while True:
                    block = src_file.read(block_size)
                    try:
                        ratio = float(publish_size) / media_size
                        ratio = 0.0 if ratio < 0.0 else 1.0 if ratio > 1.0 else ratio
                    except ZeroDivisionError:
                        ratio = 1.0
                    elapsed_time = time.time() - start_time
                    # Update status of job only if delta time or delta ratio is sufficient
                    if ratio - prev_ratio > RATIO_DELTA and elapsed_time - prev_time > TIME_DELTA:
                        prev_ratio = ratio
                        prev_time = elapsed_time
                        eta_time = int(elapsed_time * (1.0 - ratio) / ratio) if ratio > 0 else 0
                        publish_job.update_state(
                            state='PROGRESS',
                            meta={'hostname': request.hostname,
                                  'start_date': start_date,
                                  'elapsed_time': elapsed_time,
                                  'eta_time': eta_time,
                                  'media_size': media_size,
                                  'publish_size': publish_size,
                                  'percent': int(100 * ratio)})
                    block_length = len(block)
                    block_pos += block_length
                    publish_size += block_length
                    if not block:
                        break  # End of input media reached
                    dst_file.write(block)
                src_file.close()
                dst_file.close()  # FIXME maybe a finally block for that

        # Output media file sanity check
        publish_size = get_size(publish_root)
        if publish_size != media_size:
            raise IOError('Output media size does not match input (%s vs %s)' %
                          (media_size, publish_size))

        # Here all seem okay
        elapsed_time = time.time() - start_time
        print('%s Publish job successful' % (request.id))
        print('%s Callback : Media published as %s' % (request.id, publish_uri))
        data_json = object2json(
            {'job_id': request.id, 'publish_uri': publish_uri, 'status': 'SUCCESS'}, False)
        result = callback.post(data_json)
        print('%s Code %s %s : %s' % (request.id, result.status_code, result.reason, result._content))
        return {'hostname': request.hostname,
                'start_date': start_date,
                'elapsed_time': elapsed_time,
                'eta_time': 0,
                'media_size': media_size,
                'publish_size': publish_size,
                'percent': 100}

    except Exception as error:

        # Here something went wrong
        if publish_root:
            shutil.rmtree(publish_root, ignore_errors=True)
        print('%s Publish job failed ' % (request.id))
        print('%s Callback : Something went wrong' % (request.id))
        data_json = object2json({'job_id': request.id, 'status': str(error)}, False)
        if callback is None:
            print('%s [ERROR] Unable to callback orchestrator: %s' % (request.id, data_json))
        else:
            result = callback.post(data_json)
            print('%s Code %s %s : %s' %
                  (request.id, result.status_code, result.reason, result._content))
        raise
