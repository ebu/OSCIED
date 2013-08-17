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

from CharmConfig_Storage import CharmConfig_Storage
from CharmConfig_Subordinate import CharmConfig_Subordinate


class TransformConfig(CharmConfig_Storage, CharmConfig_Subordinate):

    def __init__(self, **kwargs):
        super(TransformConfig, self).__init__(**kwargs)

TRANSFORM_CONFIG_TEST = TransformConfig(api_nat_socket=u'129.194.185.47:5000', storage_address=u'10.1.1.2',
                                        storage_fstype=u'glusterfs', storage_mountpoint=u'medias_volume')

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pyutils.py_unicode import configure_unicode
    configure_unicode()
    print(u'Test TransformConfig with doctest')
    import doctest
    assert(doctest.testmod(verbose=False))
    print(u'OK')
    print(u'Write default transform configuration')
    TransformConfig().write(u'../oscied-transform/local_config.pkl')
