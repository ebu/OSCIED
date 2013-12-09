#!/usr/bin/env bash

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : David Fischer (david.fischer.ch@gmail.com)
#  Copyright       : Copyright (c) 2012-2013 EBU. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of EBU Technology & Innovation OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/ebu/OSCIED

xecho()
{
  echo "$1" 1>&2
  exit "$2"
}

oscied_install()
{
  base=$(cd "$(dirname "$0")"; pwd)

  echo 'Install OSCIED Library'

  echo '1/3 - Install Python modules prerequisites'
  apt-get -y update
  apt-get -y upgrade || xecho 'Unable to upgrade packages with apt-get' 1
  apt-get -y install build-essential git-core libyaml-dev libxml2-dev libxslt-dev libz-dev \
    python-dev python-kitchen python-pip || xecho 'Unable to install required packages with apt-get' 2

  echo '2/3 - Install Python requirements'
  cd "$base" && pip install -r REQUIREMENTS.txt || xecho 'Unable to install python requirements' 3

  echo '3/3 - Install Python module called oscied_lib'
  cd "$base" && ./setup.py develop || xecho 'Unable to install oscied_lib module' 4
}

oscied_install 2>&1 3>&1 > 'setup.log'
