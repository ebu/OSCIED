#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
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
# Retrieved from https://github.com/ebu/OSCIED

from OsciedDBModel import OsciedDBModel
from pyutils.py_validation import valid_uuid

ENCODERS_NAMES = (u'copy', u'ffmpeg', u'dashcast')


class TransformProfile(OsciedDBModel):

    def __init__(self, _id=None, title=None, description=None, encoder_name=None,
                 encoder_string=None):
        super(TransformProfile, self).__init__(_id)
        self.title = title
        self.description = description
        self.encoder_name = encoder_name
        self.encoder_string = encoder_string

    @property
    def is_dash(self):
        u"""
        >>> import copy
        >>> profile = copy.copy(TRANSFORM_PROFILE_TEST)
        >>> assert(not profile.is_dash)
        >>> profile.encoder_name = u'dashcast'
        >>> assert(profile.is_dash)
        """
        return self.encoder_name in (u'dashcast',)

    # FIXME test other fields
    def is_valid(self, raise_exception):
        if not valid_uuid(self._id, none_allowed=False):
            self._E(raise_exception, u'_id is not a valid uuid string')
        if not self.title or not self.title.strip():
            self._E(raise_exception, u'title is required')
        if not self.encoder_name in ENCODERS_NAMES:
            self._E(raise_exception, u'encoder_name is not a valid encoder')
        return True

TRANSFORM_PROFILE_TEST = TransformProfile(None, u'HD 1080p', u'MP4 H.264 1080p, audio copy',
                                          u'ffmpeg', u'-c:a copy ...')
