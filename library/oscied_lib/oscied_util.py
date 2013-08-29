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

import os, requests, shutil, time
from kitchen.text.converters import to_bytes
from urlparse import urlparse, ParseResult
from pyutils.py_ffmpeg import get_media_duration
from pyutils.py_filesystem import get_size, try_makedirs
from pyutils.py_serialization import JsoneableObject


class Callback(JsoneableObject):
    def __init__(self, url=None, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password

    def is_valid(self, raise_exception):
        # FIXME check fields
        return True

    def replace_netloc(self, netloc):
        u"""
        Replace network location of the media URI.

        **Example usage**:

        >>> import copy
        >>> from oscied_util_test import CALLBACK_TEST
        >>> callback = copy.copy(CALLBACK_TEST)
        >>> callback.is_valid(True)
        True
        >>> print(callback.url)
        http://127.0.0.1:5000/media
        >>> callback.replace_netloc(u'129.194.185.47:5003')
        >>> print(callback.url)
        http://129.194.185.47:5003/media
        """
        url = urlparse(self.url)
        url = ParseResult(url.scheme, netloc, url.path, url.params, url.query, url.fragment)
        self.url = url.geturl()

    def post(self, data_json):
#       return requests.post(self.url, data_json, auth=(self.username, self.password))
        headers = {u'Content-type': u'application/json', u'Accept': u'text/plain'}
        return requests.post(self.url, headers=headers, data=data_json, auth=(self.username, self.password))


class Storage(object):

    @staticmethod
    def add_media(config, media):
        if not media.status in (u'PENDING',):
            media_src_path = config.storage_medias_path(media, generate=False)
            if media_src_path:
                media_dst_path = config.storage_medias_path(media, generate=True)
                if media_dst_path != media_src_path:
                    # Generate media storage uri and move it to media storage path + set permissions
                    media.uri = config.storage_medias_uri(media)
                    try_makedirs(os.path.dirname(media_dst_path))
                    the_error = None
                    for i in range(5):
                        try:
                            os.rename(media_src_path, media_dst_path)
                            # FIXME chown chmod
                            the_error = None
                            break
                        except OSError as error:
                            the_error = error
                            time.sleep(1)
                    if the_error:
                        raise IndexError(to_bytes(u'An error occured : {0} ({1} -> {2}).'.format(
                                         the_error, media_src_path, media_dst_path)))
                try:
                    size = get_size(os.path.dirname(media_dst_path))
                except OSError:
                    raise ValueError(to_bytes(u'Unable to detect size of media {0}.'.format(media_dst_path)))
                duration = get_media_duration(media_dst_path)
                if duration is None:
                    raise ValueError(to_bytes(u'Unable to detect duration of media {0}.'.format(media_dst_path)))
                return (size, duration)
            else:
                raise NotImplementedError(to_bytes(u'FIXME Add of external URI not implemented.'))
        return (0, None)

    @staticmethod
    def delete_media(config, media):
        media_path = config.storage_medias_path(media, generate=False)
        if media_path:
            shutil.rmtree(os.path.dirname(media_path), ignore_errors=True)
        else:
            raise NotImplementedError(to_bytes(u'FIXME Delete of external uri not implemented.'))
