#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**********************************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/ebu/OSCIED

import os, uuid
from OrchestraConfig import ORCHESTRA_CONFIG_TEST
from OsciedDBModel import OsciedDBModel
from pyutils.py_validation import valid_filename, valid_uuid


class Media(OsciedDBModel):

    STATUS = (u'PENDING', u'READY', u'DELETED')

    def __init__(self, user_id=None, parent_id=None, uri=None, public_uris=None, filename=None, metadata={},
                 status=u'PENDING', **kwargs):
        super(Media, self).__init__(**kwargs)
        self.user_id = user_id
        self.parent_id = parent_id
        self.uri = uri
        self.public_uris = public_uris or {}
        try:
            self.filename = unicode(filename).replace(u' ', u'_')
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
        >>> media.filename = u'test.mpd'
        >>> assert(media.is_dash)
        """
        return os.path.splitext(self.filename)[1].lower() == u'.mpd'

    def is_valid(self, raise_exception):
        if not super(Media, self).is_valid(raise_exception):
            return False
        if hasattr(self, u'user_id') and not valid_uuid(self.user_id, none_allowed=False):
            self._E(raise_exception, u'user_id is not a valid uuid string')
        # FIXME check use if loaded
        if hasattr(self, u'parent_id') and not valid_uuid(self.parent_id, none_allowed=True):
            self._E(raise_exception, u'parent_id is not a valid uuid string')
        # FIXME check parent if loaded
        # FIXME check uri
        # FIXME check public_uris
        if not valid_filename(self.filename):
            self._E(raise_exception, u'filename is not a valid file-name')
        # FIXME check metadata
        if not self.status in Media.STATUS:
            self._E(raise_exception, u'status is not in {0}'.format(self.__class__.STATUS))
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
        delattr(self, u'user_id')
        delattr(self, u'parent_id')

MEDIA_TEST = Media(unicode(uuid.uuid4()), unicode(uuid.uuid4()), None, None, u'tabby.mpg',
                   {u'title': u"Tabby's adventures §1", u'description': u'My cat drinking water'}, u'PENDING')
MEDIA_TEST.uri = ORCHESTRA_CONFIG_TEST.storage_medias_uri(MEDIA_TEST)
MEDIA_TEST.add_metadata(u'title', u'not authorized overwrite', False)
MEDIA_TEST.add_metadata(u'size', 4096, True)
