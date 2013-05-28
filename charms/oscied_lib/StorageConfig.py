#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
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
# Retrieved from https://github.com/EBU-TI/OSCIED

import re
from pyutils.pyutils import PickleableObject


class StorageConfig(PickleableObject):

    def __init__(self, allowed_ips='', volume_flag=False):
        self.allowed_ips = allowed_ips
        self.volume_flag = volume_flag
        self.volume_infos_regex = re.compile(
            r".*Volume Name:\s*(?P<name>\S+)\s+.*Type:\s*(?P<type>\S+)\s+.*"
            r"Status:\s*(?P<status>\S+)\s+.*Transport-type:\s*(?P<transport>\S+).*", re.DOTALL)

    def __repr__(self):
        return str(self.__dict__)

    def reset(self):
        self.allowed_ips = ''
        self.volume_flag = False

STORAGE_CONFIG_TEST = StorageConfig('*', False)

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Write default storage configuration')
    StorageConfig().write('../oscied-storage/local_config.pkl')
