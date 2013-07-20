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
from Storage import Storage
from pyutils.pyutils import object2json, datetime_now, get_size


def publish_job_test():

    RATIO_DELTA = 0.05  # Update status if at least 5% of progress
    TIME_DELTA = 0.01   # Update status if at least 1 second(s) elapsed

    try:
        # Avoid 'referenced before assignment'
        media_path = None
        publish_path = None

        # Let's the task begin !
        start_date = datetime_now()
        start_time = time.time()
        print('Publish job started')
        if False:
            media_path = '/home/famille/David/git/OSCIED/charms/oscied_lib/media_src/aaa/bbb/test.mp4'
            publish_path, publish_uri = '/home/famille/David/git/OSCIED/charms/oscied_lib/media_dst/aaa/bbb/test.mp4', 'http://medias/aaa/bbb/test.mp4'
        else:
            media_path = '/home/famille/David/git/OSCIED/charms/oscied_lib/media_src/aaa/ccc/test.mpd'
            publish_path, publish_uri = '/home/famille/David/git/OSCIED/charms/oscied_lib/media_dst/aaa/ccc/test.mpd', 'http://medias/aaa/ccc/test.mpd'
        media_root, publish_root = os.path.dirname(media_path), os.path.dirname(publish_path)
        media_size, publish_size = get_size(media_root), 0

        # Recursive copy of a media (directory of files or file) to the local path of the publisher
        for root, dirnames, filenames in os.walk(os.path.dirname(media_path)):
            print root, dirnames, filenames
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
                    except ZeroDivisionError:
                        ratio = 1.0
                    elapsed_time = time.time() - start_time
                    if ratio - prev_ratio > RATIO_DELTA and elapsed_time - prev_time > TIME_DELTA:
                        prev_ratio = ratio
                        prev_time = elapsed_time
                        eta_time = int(elapsed_time * (1 - ratio) / ratio) if ratio > 0 else 0
                        print(
                            {'state': 'PROGRESS', 'meta': {
                                'start_date': start_date,
                                'elapsed_time': elapsed_time,
                                'eta_time': eta_time,
                                'media_size': media_size,
                                'publish_size': publish_size,
                                'percent': int(100 * ratio)}})
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
        print('Publish job successful')
        print('Callback : Media published as %s' % publish_uri)
        print(object2json({'publish_uri': publish_uri, 'status': 'SUCCESS'}, False))
        return {'start_date': start_date,
                'elapsed_time': elapsed_time,
                'eta_time': 0,
                'media_size': media_size,
                'publish_size': publish_size,
                'percent': 100}

    except Exception as error:

        # Here something went wrong
        if publish_root:
            shutil.rmtree(publish_root, ignore_errors=True)
        print('Publish job failed')
        print('Callback : Something went wrong')
        print(object2json({'status': str(error)}, False))
        raise

publish_job_test()
