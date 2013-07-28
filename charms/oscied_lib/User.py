#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARIE
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

import uuid
from passlib.hash import pbkdf2_sha512
from passlib.utils import consteq
from pyutils.py_serialization import json2object
from pyutils.py_validation import valid_email, valid_secret, valid_uuid


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

    @property
    def is_secret_hashed(self):
        return self.secret is not None and self.secret.startswith('$pbkdf2-sha512$')

    # FIXME test other fields
    def is_valid(self, raise_exception):
        if not valid_uuid(self._id, none_allowed=False):
            if raise_exception:
                raise TypeError(self.__class__.__name__ + ' : _id is not a valid uuid string')
            return False
        if not valid_email(self.mail):
            if raise_exception:
                raise TypeError(self.__class__.__name__ + ' : mail is not a valid email address')
            return False
        if not self.is_secret_hashed and not valid_secret(self.secret, True):
            if raise_exception:
                raise TypeError(self.__class__.__name__ +
                    ' : secret is not safe (8+ characters, upper/lower + numbers eg. StrongP6s)')
            return False
        return True

    def hash_secret(self, rounds=12000, salt=None, salt_size=16):
        u"""
        Hashes user's secret if it is not already hashed.

        **Example usage**:

        >>> from copy import copy
        >>> user = copy(USER_TEST)
        >>> user.is_secret_hashed
        False
        >>> len(user.secret)
        8
        >>> user.hash_secret()
        >>> user.is_secret_hashed
        True
        >>> len(user.secret)
        130
        >>> secret = user.secret
        >>> user.hash_secret()
        >>> assert(user.secret == secret)
        """
        if not self.is_secret_hashed:
            self.secret = pbkdf2_sha512.encrypt(
                self.secret, rounds=rounds, salt=salt, salt_size=salt_size)

    def verify_secret(self, secret):
        u"""
        Returns True if secret is equal to user's secret.

        **Example usage**:

        >>> from copy import copy
        >>> user = copy(USER_TEST)
        >>> user.verify_secret('bad_secret')
        False
        >>> user.verify_secret('Secr4taB')
        True
        >>> user.hash_secret()
        >>> user.verify_secret('bad_secret')
        False
        >>> user.verify_secret('Secr4taB')
        True
        """
        if self.is_secret_hashed:
            return pbkdf2_sha512.verify(secret, self.secret)
        return consteq(secret, self.secret)

    @staticmethod
    def load(json):
        u"""
        Returns a new user with attributes loaded from a source JSON string.

        **Example usage**:

        >>> from pyutils.py_serialization import object2json
        >>> user = User.load(object2json(USER_TEST, False))
        >>> assert(user.__dict__ == USER_TEST.__dict__)
        >>> assert(user.is_valid(False))
        """
        user = User(None, None, None, None, None)
        json2object(json, user)
        return user

USER_TEST = User(None, 'David', 'Fischer', 'david.fischer.ch@gmail.com', 'Secr4taB', True)

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Testing User with doctest')
    import doctest
    assert(doctest.testmod(verbose=False))
    print('OK')
