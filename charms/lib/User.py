#! /usr/bin/env python
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARIE
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

import uuid
from Utilities import json2object, object2json, valid_mail, valid_secret, valid_uuid


class User(object):

    def __init__(self, _id, first_name, last_name, mail, secret, admin_platform=False):
        if not _id:
            _id = str(uuid.uuid4())
        self._id = _id
        self.first_name = first_name
        self.last_name = last_name
        self.mail = mail
        self.secret = secret
        self.admin_platform = True if str(admin_platform).lower() == 'true' else False

    @property
    def name(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        return 'anonymous'

    # FIXME test other fields
    def is_valid(self, raise_exception):
        if not valid_uuid(self._id, False):
            if raise_exception:
                raise TypeError(self.__class__.__name__ + ' : _id is not a valid uuid string')
            return False
        if not valid_mail(self.mail):
            if raise_exception:
                raise TypeError(self.__class__.__name__ + ' : mail is not a valid email address')
            return False
        if self.secret is not None and not valid_secret(self.secret):
            if raise_exception:
                raise TypeError(self.__class__.__name__ +
                    ' : secret is not safe (8+ characters, upper/lower + numbers eg. StrongP6s)')
            return False
        return True

    @staticmethod
    def load(json):
        user = User(None, None, None, None, None)
        json2object(json, user)
        return user

USER_TEST = User(None, 'David', 'Fischer', 'david.fischer.ch@gmail.com', 'Secr4taB', True)

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print object2json(USER_TEST, True)
    USER_TEST.is_valid(True)
    print str(User.load(object2json(USER_TEST, False)))
