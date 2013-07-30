#!/usr/bin/env bash

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

oscied_install()
{
  echo 'Install OSCIED Library'
  echo '1/3 - Install Python modules prerequisites'
  apt-get -y install build-essential git-core python-dev python-pip
  echo '2/3 - Install Python module called pyutils'
  cd pyutils && ./setup.py develop || { echo 'Unable to install pyutils module' 1>&2; exit 2; }
  echo '3/3 - Install Python module called oscied_lib'
  cd .. && ./setup.py develop || { echo 'Unable to install oscied_lib module' 1>&2; exit 3; }
}

oscied_install 2>&1 > 'setup.log'
