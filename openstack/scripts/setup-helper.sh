#!/usr/bin/env bash

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : CLOUD
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

{
  echo "OSCIED Setup Helper - $(date)"
  # FIXME this is hardcoded, a better solution ?
  cd nodes || { echo '[ERROR] nodes directory not found !' 1>&2; exit 1; }
  svn cleanup && svn update --username='oscied' --password='41nVGq07GmSgK9Ud' --non-interactive \
    --accept theirs-full
  sudo chown $UID:$UID . -R
  cd scripts && sh setup.sh "$@" || echo '[ERROR] Unable to execute setup.sh properly' 1>&2
} 2>&1 | tee setup.log
