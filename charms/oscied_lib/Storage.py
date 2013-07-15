#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
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

import os, time
from pyutils.ffmpeg import get_media_duration
from pyutils.pyutils import try_makedirs


class Storage(object):

    @staticmethod
    def create_file_directory(file_path):
        return try_makedirs(os.path.dirname(file_path))

    @staticmethod
    def add_media(config, media):
        if not media.status in ('PENDING',):
            media_src_path = config.storage_medias_path(media, generate=False)
            if media_src_path:
                media_dst_path = config.storage_medias_path(media, generate=True)
                if media_dst_path != media_src_path:
                    # Generate media storage uri and move it to media storage path + set permissions
                    media.uri = config.storage_medias_uri(media)
                    Storage.create_file_directory(media_dst_path)
                    the_error = None
                    for i in range(1, 5):
                        try:
                            os.rename(media_src_path, media_dst_path)
                            # FIXME chown chmod
                            the_error = None
                            break
                        except OSError as error:
                            the_error = error
                            time.sleep(1)
                    if the_error:
                        raise IndexError('An error occured : %s (%s -> %s).' %
                                         (the_error, media_src_path, media_dst_path))
                try:
                    size = os.stat(media_dst_path).st_size
                except OSError:
                    raise ValueError('Unable to detect size of media %s.' % media_dst_path)
                duration = get_media_duration(media_dst_path)
                if duration is None:
                    raise ValueError('Unable to detect duration of media %s.' % media_dst_path)                        
                return (size, duration)
            else:
                raise NotImplementedError('FIXME Add of external URI not implemented.')
        return (0, None)

    @staticmethod
    def delete_media(config, media):
        media_path = config.storage_medias_path(media, generate=False)
        if media_path:
            try:
                os.remove(media_path)
            except:
                pass
        else:
            raise NotImplementedError('FIXME Delete of external uri not implemented.')
