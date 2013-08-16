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

from celery import states
from celery.result import AsyncResult
from OsciedDBModel import OsciedDBModel


class OsciedDBTask(OsciedDBModel):

    def __init__(self, _id=None, statistic={}, status=u'UNKNOWN'):
        super(OsciedDBTask, self).__init__(_id)
        self.statistic = statistic
        self.status = status

    def is_valid(self, raise_exception):
        if not super(OsciedDBTask, self).is_valid(raise_exception):
            return False
        # FIXME check statistic
        # FIXME check status
        return True

    def get_hostname(self):
        try:
            return AsyncResult(self._id).result['hostname']
        except:
            return None

    def add_statistic(self, key, value, overwrite):
        if overwrite or not key in self.statistic:
            self.statistic[key] = value

    def get_statistic(self, key):
        return self.statistic[key] if key in self.statistic else None

    def append_async_result(self):
        async_result = AsyncResult(self._id)
        if async_result:
            try:
                if self.status not in (states.REVOKED, 'REVOKING'):
                    self.status = async_result.status
                try:
                    self.statistic.update(async_result.result)
                except:
                    self.statistic[u'error'] = unicode(async_result.result)
            except NotImplementedError:
                self.status = u'UNKNOWN'
        else:
            self.status = u'UNKNOWN'
