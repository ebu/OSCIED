#! /usr/bin/env python
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012 OSCIED Team. All rights reserved.
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
# Retrieved from:
#   svn co https://claire-et-david.dyndns.org/prog/OSCIED

import os
import time
from FFmpeg import get_media_duration
from OrchestraConfig import ORCHESTRA_CONFIG_TEST


class Storage(object):

    @staticmethod
    def is_mounted(path):
        return os.path.ismount(path)

    @staticmethod
    def create_file_directory(file_path):
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))

    @staticmethod
    def media_path(config, media, generate):
        uri = config.storage_uri
        if not uri:
            return None
        if generate:
            return config.storage_path + '/medias/' + media.user_id + '/' + media._id
        if not media.uri or not media.uri.startswith(uri):
            return None
        return config.storage_path + media.uri.replace(uri, '', 1)

    @staticmethod
    def media_uri(config, media, generate):
        if not config.storage_uri:
            return None
        if generate:
            return config.storage_uri + '/medias/' + media.user_id + '/' + media._id
        return media.uri

    @staticmethod
    def publish_point(config, media):
        common = '/medias/' + media.user_id + '/' + media._id + '/' + media.virtual_filename
        return (config.publish_path + common, config.publish_uri + common)

    @staticmethod
    def add_media(config, media):
        if not media.status in ('PENDING',):
            media_src_path = Storage.media_path(config, media, False)  # get actual media path
            if media_src_path:
                media_dst_path = Storage.media_path(config, media, True)  # generate media storage path
                if media_dst_path != media_src_path:
                    # Generate media storage uri and move it to media storage path + set permissions
                    media.uri = Storage.media_uri(config, media, True)
                    Storage.create_file_directory(media_dst_path)
                    the_error = None
                    for i in range(1,5):
                        try:
                            os.rename(media_src_path, media_dst_path)
                            # FIXME chown chmod
                            the_error = None
                            break
                        except OSError as error:
                            the_error = error
                            time.sleep(1)
                    if the_error:
                        raise IndexError('An error occured : ' + the_error + '.')
                return (os.stat(media_dst_path).st_size, get_media_duration(media_dst_path))
            else:
                raise NotImplementedError('FIXME Add of external uri not implemented.')
        return (0, None)

    @staticmethod
    def delete_media(config, media):
        media_path = Storage.media_path(config, media, False)
        if media_path:
            try:
                os.remove(media_path)
            except:
                pass
        else:
            raise NotImplementedError('FIXME Delete of external uri not implemented.')

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':

    #print ORCHESTRA_CONFIG_TEST.storage_mounted
    assert ORCHESTRA_CONFIG_TEST.storage_uri == 'glusterfs://10.1.1.2/medias_volume'
    #assert ORCHESTRA_CONFIG_TEST.media_path('glusterfs://10.1.1.2/medias_volume/medias/test.mpg')
    #assert not ORCHESTRA_CONFIG_TEST.media_path('http://10.1.1.2/medias/test.mpg')


