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

import re
from CharmConfig import CharmConfig


class StorageConfig(CharmConfig):

    def __init__(self, allowed_ips=[], volume_flag=False, **kwargs):
        super(StorageConfig, self).__init__(**kwargs)
        self.allowed_ips = allowed_ips
        self.volume_flag = volume_flag
        self.volume_infos_regex = re.compile(
            r".*Volume Name:\s*(?P<name>\S+)\s+.*Type:\s*(?P<type>\S+)\s+.*"
            r"Status:\s*(?P<status>\S+)\s+.*Transport-type:\s*(?P<transport>\S+).*", re.DOTALL)

STORAGE_CONFIG_TEST = StorageConfig(u'*', False)

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pyutils.py_unicode import configure_unicode
    configure_unicode()
    print(u'Write default storage configuration')
    StorageConfig().write(u'../oscied-storage/local_config.pkl')
