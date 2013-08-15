#!/usr/bin/env bash

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCENARIOS
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

osciedEBUIO_amazonDescription='Launch oscied/ebuio (nano setup) on Amazon'
osciedEBUIO_amazonScenario()
{
  cd "$CHARMS_DEPLOY_PATH/.." || xecho "Unable to find path $CHARMS_DEPLOY_PATH/.."
  cfg="$CONFIG_JUJU_PATH/osciedEBUIO_amazon.yaml"
  cp -f "$cfg" "$CONFIG_GEN_CONFIG_FILE"

  techo '1/4 Cleanup and bootstrap JuJu environment'

  sudo juju destroy-environment -e 'amazon'
  sudo juju bootstrap -e 'amazon' -v

  techo '2/4 Deploy services on Amazon'

  pecho 'Deploy Orchestra (1 instance)'
  yesOrNo $true 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg" ]; then
      mecho "Using user define Orchestra configuration : $cfg"
      juju deploy -e 'amazon' --config "$cfg" --repository=. local:$RELEASE/oscied-orchestra || xecho '1'
    else
      mecho 'Using default Orchestra configuration'
      juju deploy -e 'amazon' --repository=. local:$RELEASE/oscied-orchestra || xecho '1'
    fi
    juju expose -e 'amazon' oscied-orchestra || xecho '2'
  fi

  pecho 'Deploy Storage (1 instance)'
  yesOrNo $true 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg" ]; then
      mecho "Using user define Storage configuration : $cfg"
      juju deploy -e 'amazon' --config "$cfg" --repository=. local:$RELEASE/oscied-storage || xecho '1'
    else
      mecho 'Using default Storage configuration'
      juju deploy -e 'amazon' --repository=. local:$RELEASE/oscied-storage || xecho '1'
    fi
    juju expose -e 'amazon' oscied-storage || xecho '2'
  fi

  pecho 'Deploy Transform (1 instance)'
  yesOrNo $true 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg" ]; then
      mecho "Using user define Transform configuration : $cfg"
      juju deploy --to 2 -e 'amazon' --config "$cfg" --repository=. local:$RELEASE/oscied-transform || xecho '1'
    else
      mecho 'Using default Transform configuration'
      juju deploy --to 2 -e 'amazon' --repository=. local:$RELEASE/oscied-transform || xecho '1'
    fi
  fi

  pecho 'Deploy Publisher (1 instance)'
  yesOrNo $true 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg" ]; then
      mecho "Using user define Publisher configuration : $cfg"
      juju deploy --to 2 -e 'amazon' --config "$cfg" --repository=. local:$RELEASE/oscied-publisher || xecho '1'
    else
      mecho 'Using default Publisher configuration'
      juju deploy --to 2 -e 'amazon' --repository=. local:$RELEASE/oscied-publisher || xecho '1'
    fi
    juju expose -e 'amazon' oscied-publisher || xecho '2'
  fi

  techo "3/4 Add relation between Storage and other services"

  pecho 'Add-relation Storage <-> Transform'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'amazon' oscied-storage oscied-transform
  fi

  pecho 'Add-relation Storage <-> Publisher'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'amazon' oscied-storage oscied-publisher
  fi

  pecho 'Add-relation Storage <-> Orchestra'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'amazon' oscied-storage oscied-orchestra
  fi

  techo "4/5 Add relation between Orchestra and other services"

  pecho 'Add-relation Orchestra <-> Transform'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'amazon' oscied-orchestra:transform oscied-transform:transform
  fi

  pecho 'Add-relation Orchestra <-> Publisher'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'amazon' oscied-orchestra:publisher oscied-publisher:publisher
  fi
}
