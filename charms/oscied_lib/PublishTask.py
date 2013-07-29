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

from celery.result import AsyncResult
from Media import MEDIA_TEST
from OsciedDBModel import OsciedDBModel
from User import USER_TEST
from pyutils.py_validation import valid_uuid


class PublishTask(OsciedDBModel):

    def __init__(self, _id=None, user_id=None, media_id=None, publish_uri=None, statistic={},
                 revoked=False, status=u'UNKNOWN'):
        super(PublishTask, self).__init__(_id)
        self.user_id = user_id
        self.media_id = media_id
        self.publish_uri = publish_uri
        self.statistic = statistic
        self.revoked = revoked
        self.status = status

    def is_valid(self, raise_exception):
        if not valid_uuid(self._id, none_allowed=False):
            self._E(raise_exception, u'_id is not a valid uuid string')
        if hasattr(self, u'user_id') and not valid_uuid(self.user_id, none_allowed=False):
            self._E(raise_exception, u'user_id is not a valid uuid string')
        # FIXME check user if loaded
        if hasattr(self, u'media_id') and not valid_uuid(self.media_id, none_allowed=False):
            self._E(raise_exception, u'media_id is not a valid uuid string')
        # FIXME check media if loaded
        # FIXME check publish_uri
        # FIXME check statistic
        # FIXME check revoked
        # FIXME check status
        return True

    def add_statistic(self, key, value, overwrite):
        if overwrite or not key in self.statistic:
            self.statistic[key] = value

    def get_statistic(self, key):
        return self.statistic[key] if key in self.statistic else None

    def append_async_result(self):
        async_result = AsyncResult(self._id)
        if async_result:
            try:
                self.status = async_result.status
                try:
                    self.statistic.update(async_result.result)
                except:
                    self.statistic[u'error'] = unicode(async_result.result)
            except NotImplementedError:
                self.status = u'UNKNOWN'
        else:
            self.status = u'UNKNOWN'

    def load_fields(self, user, media):
        self.user = user
        self.media = media
        delattr(self, u'user_id')
        delattr(self, u'media_id')

PUBLISH_JOB_TEST = PublishTask(None, USER_TEST._id, MEDIA_TEST._id, u'http://amazon.com/salut.mpg')
