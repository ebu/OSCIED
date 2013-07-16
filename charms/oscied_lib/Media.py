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

import os, uuid
from OrchestraConfig import ORCHESTRA_CONFIG_TEST
from pyutils.pyutils import json2object, object2json, valid_filename, valid_uuid


class Media(object):

    STATUS = ('PENDING', 'READY', 'PUBLISHED', 'DELETED')

    def __init__(self, _id, user_id, parent_id, uri, public_uris, filename, metadata, status):
        if not _id:
            _id = str(uuid.uuid4())
        self._id = _id
        self.user_id = user_id
        self.parent_id = parent_id
        self.uri = uri
        self.public_uris = public_uris
        try:
            self.filename = str(filename).replace(' ', '_')
        except:
            self.filename = None
        self.metadata = metadata
        self.status = status

    @property
    def is_dash(self):
        u"""
        Returns True if the media's filename point to a MPEG-DASH MPD.

        **Example usage**:

        >>> import copy
        >>> media = copy.copy(MEDIA_TEST)
        >>> assert(not media.is_dash)
        >>> media.filename = 'test.mpd'
        >>> assert(media.is_dash)
        """
        return os.path.splitext(self.filename)[1].lower() == '.mpd'

    def is_valid(self, raise_exception):
        if not valid_uuid(self._id, none_allowed=False):
            if raise_exception:
                raise TypeError(self.__class__.__name__ + ' : _id is not a valid uuid string')
            return False
        if hasattr(self, 'user_id') and not valid_uuid(self.user_id, none_allowed=False):
            if raise_exception:
                raise TypeError(self.__class__.__name__ + ' : user_id is not a valid uuid string')
            return False
        # FIXME check use if loaded
        if hasattr(self, 'parent_id') and not valid_uuid(self.parent_id, none_allowed=True):
            if raise_exception:
                raise TypeError(self.__class__.__name__ + ' : parent_id is not a valid uuid string')
            return False
        # FIXME check parent if loaded
        # FIXME check uri
        # FIXME check public_uris
        if not valid_filename(self.filename):
            if raise_exception:
                raise TypeError(self.__class__.__name__ + ' : filename is not a valid file-name')
            return False
        # FIXME check metadata
        if not self.status in Media.STATUS:
            if raise_exception:
                raise TypeError(self.__class__.__name__ + ' : status is not a valid status string')
            return False
        return True

    def add_metadata(self, key, value, overwrite):
        if overwrite or not key in self.metadata:
            self.metadata[key] = value

    def get_metadata(self, key):
        return self.metadata[key] if key in self.metadata else None

    #def detect_codecs(self, storage_path):
    #''' Update media's metadata based on file's attribute '''

    def load_fields(self, user, parent):
        self.user = user
        self.parent = parent
        delattr(self, 'user_id')
        delattr(self, 'parent_id')

    @staticmethod
    def load(json):
        media = Media(None, None, None, None, None, None, None, None)
        json2object(json, media)
        return media

MEDIA_TEST = Media(None, str(uuid.uuid4()), str(uuid.uuid4()), None, None, 'tabby.mpg',
                   {'title': "Tabby's adventures §1", 'description': 'My cat drinking water'},
                   'PENDING')
MEDIA_TEST.uri = ORCHESTRA_CONFIG_TEST.storage_medias_uri(MEDIA_TEST)
MEDIA_TEST.add_metadata('title', 'not authorized overwrite', False)
MEDIA_TEST.add_metadata('size', 4096, True)

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print object2json(MEDIA_TEST, True)
    MEDIA_TEST.is_valid(True)
    print str(Media.load(object2json(MEDIA_TEST, False)))
    print('Testing Media with doctest')
    import doctest
    assert(doctest.testmod(verbose=False))
    print('OK')
