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

import time, os
from celery import current_task
from celery.decorators import task
from Callback import Callback
from Media import Media
from PublisherConfig import PublisherConfig
from Storage import Storage
from User import User
from pyutils.pyutils import object2json, datetime_now


@task(name='Publisher.publish_job')
def publish_job(user_json, media_json, callback_json):

    RATIO_DELTA = 0.05  # Update status if at least 5% of progress
    TIME_DELTA = 1      # Update status if at least 1 second(s) elapsed

    try:
        # Avoid 'referenced before assignment'
        callback = None
        media_path = None
        publish_path = None
        request = current_task.request

        # Let's the task begin !
        start_date = datetime_now()
        start_time = time.time()
        print('%s Publish job started' % (request.id))

        # Read current configuration to translate files uri to local paths
        config = PublisherConfig.read('../local_config.pkl')
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

        # Verify that media file can be accessed and create output path
        media_path = Storage.media_path(config, media, False)
        if not media_path:
            raise NotImplementedError('Media will not be readed from shared storage : %s' %
                                      media.uri)
        (publish_path, publish_uri) = Storage.publish_point(config, media)
        Storage.create_file_directory(publish_path)

        # Initialize block-based copy
        block_size = 1024 * 1024
        media_file = open(media_path, "rb")
        publish_file = open(publish_path, "wb")
        media_size = os.stat(media_path).st_size

        # Block-based copy loop
        block_pos = 0
        prev_ratio = 0
        prev_time = 0
        while True:
            block = media_file.read(block_size)
            ratio = float(block_pos) / media_size
            elapsed_time = time.time() - start_time
            if ratio - prev_ratio > RATIO_DELTA and elapsed_time - prev_time > TIME_DELTA:
                prev_ratio = ratio
                prev_time = elapsed_time
                eta_time = int(elapsed_time * (1 - ratio) / ratio) if ratio > 0 else 0
                publish_job.update_state(
                    state="PROGRESS",
                    meta={'hostname': request.hostname,
                          'start_date': start_date,
                          'elapsed_time': elapsed_time,
                          'eta_time': eta_time,
                          'media_size': media_size,
                          'publish_size': block_pos,
                          'percent': int(100 * ratio)})
            block_pos += len(block)
            if not block:
                break  # End of input media reached
            publish_file.write(block)
        media_file.close()
        publish_file.close()  # FIXME maybe a finally block for that

        # Output media file sanity check
        publish_size = os.stat(publish_path).st_size
        if publish_size != media_size:
            raise IOError(
                "Output media size does not match input (%s vs %s)" %
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
        if publish_path:
            os.remove(publish_path)
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
