#!/usr/bin/env bash

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : CLOUD
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

{
  echo "OSCIED Setup Helper - $(date)"
  # FIXME this is hardcoded, a better solution ?
  cd nodes || { echo '[ERROR] nodes directory not found !' 1>&2; exit 1; }
  svn cleanup && svn update --username='oscied' --password='41nVGq07GmSgK9Ud' --non-interactive \
    --accept theirs-full
  sudo chown $UID:$UID . -R
  cd scripts && sh setup.sh "$@" || echo '[ERROR] Unable to execute setup.sh properly' 1>&2
} 2>&1 | tee setup.log
