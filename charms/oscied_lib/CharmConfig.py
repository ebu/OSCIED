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

import logging
from pyutils.py_serialization import PickleableObject


class CharmConfig(PickleableObject):

    def __init__(self, verbose=True):
        self.verbose = verbose

    def __repr__(self):
        return str(self.__dict__)

    @property
    def log_level(self):
        return logging.DEBUG if self.verbose else logging.INFO

    def reset(self):
        u"""
        Reset attributes to theirs default values.

        **Example usage**:

        >>> config = CharmConfig(verbose=True)
        >>> config._pickle_filename = 'my_file.pkl'
        >>> print(config.verbose)
        True
        >>> config.verbose = False
        >>> print(config.verbose)
        False
        >>> config.reset()
        >>> print(config.verbose)
        True
        >>> print(config._pickle_filename)
        my_file.pkl
        """
        self.__init__()

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Test CharmConfig with doctest')
    import doctest
    assert(doctest.testmod(verbose=False))
    print('OK')
