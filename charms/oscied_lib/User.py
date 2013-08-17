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

from passlib.hash import pbkdf2_sha512
from passlib.utils import consteq
from OsciedDBModel import OsciedDBModel
from pyutils.py_validation import valid_email, valid_secret


class User(OsciedDBModel):

    def __init__(self, first_name=None, last_name=None, mail=None, secret=None, admin_platform=False, **kwargs):
        super(User, self).__init__(**kwargs)
        self.first_name = first_name
        self.last_name = last_name
        self.mail = mail
        self.secret = secret
        self.admin_platform = True if unicode(admin_platform).lower() == u'true' else False

    @property
    def name(self):
        if self.first_name and self.last_name:
            return u'{0} {1}'.format(self.first_name, self.last_name)
        return u'anonymous'

    @property
    def is_secret_hashed(self):
        return self.secret is not None and self.secret.startswith(u'$pbkdf2-sha512$')

    # FIXME test other fields
    def is_valid(self, raise_exception):
        if not super(User, self).is_valid(raise_exception):
            return False
        if not valid_email(self.mail):
            self._E(raise_exception, u'mail is not a valid email address')
        if not self.is_secret_hashed and not valid_secret(self.secret, True):
            self._E(raise_exception, u'secret is not safe (8+ characters, upper/lower + numbers eg. StrongP6s)')
        return True

    def hash_secret(self, rounds=12000, salt=None, salt_size=16):
        u"""
        Hashes user's secret if it is not already hashed.

        **Example usage**:

        >>> import copy
        >>> user = copy.copy(USER_TEST)
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

        >>> import copy
        >>> user = copy.copy(USER_TEST)
        >>> user.verify_secret(u'bad_secret')
        False
        >>> user.verify_secret(u'Secr4taB')
        True
        >>> user.hash_secret()
        >>> user.verify_secret(u'bad_secret')
        False
        >>> user.verify_secret(u'Secr4taB')
        True
        """
        if self.is_secret_hashed:
            return pbkdf2_sha512.verify(secret, self.secret)
        return consteq(secret, self.secret)

USER_TEST = User(u'David', u'Fischer', u'david.fischer.ch@gmail.com', u'Secr4taB', True)
