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

osciedLocalDescription='Launch oscied (minimal setup) locally (LXC provider)'
osciedLocalScenario()
{
  cd "$CHARMS_DEPLOY_PATH/.." || xecho "Unable to find path $CHARMS_DEPLOY_PATH/.."
  cfg="$CONFIG_JUJU_PATH/osciedLocal.yaml"
  cp -f "$cfg" "$CONFIG_GEN_CONFIG_FILE"

  techo '1/5 Cleanup and bootstrap juju environment'

  juju destroy-environment -e 'local'
  juju bootstrap -e 'local'

  techo '2/5 Deploy services on this computer'

  pecho 'Deploy Orchestra (1 instance)'
  yesOrNo $true 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg" ]; then
      mecho "Using user define Orchestra configuration : $cfg"
      juju deploy -e 'local' --config "$cfg" --repository=. local:$RELEASE/oscied-orchestra || xecho '1'
    else
      mecho 'Using default Orchestra configuration'
      juju deploy -e 'local' --repository=. local:$RELEASE/oscied-orchestra || xecho '1'
    fi
    juju expose -e 'local' oscied-orchestra || xecho '2'
  fi

  pecho 'Deploy Web UI (1 instance)'
  yesOrNo $true 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg" ]; then
      mecho "Using user define Web UI configuration : $cfg"
      juju deploy -e 'local' --config "$cfg" --repository=. local:$RELEASE/oscied-webui || xecho '1'
    else
      mecho 'Using default Web UI configuration'
      juju deploy -e 'local' --repository=. local:$RELEASE/oscied-webui || xecho '1'
    fi
    juju expose -e 'local' oscied-webui || xecho '2'
  fi

  pecho 'Deploy Storage (1 instance)'
  yesOrNo $true 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg" ]; then
      mecho "Using user define Storage configuration : $cfg"
      juju deploy -e 'local' --config "$cfg" --repository=. local:$RELEASE/oscied-storage || xecho '1'
    else
      mecho 'Using default Storage configuration'
      juju deploy -e 'local' --repository=. local:$RELEASE/oscied-storage || xecho '1'
    fi
    juju expose -e 'local' oscied-storage || xecho '2'
  fi

  pecho 'Deploy Transform (1 instance)'
  yesOrNo $true 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg" ]; then
      mecho "Using user define Transform configuration : $cfg"
      juju deploy -e 'local' --config "$cfg" --repository=. local:$RELEASE/oscied-transform || xecho '1'
    else
      mecho 'Using default Transform configuration'
      juju deploy -e 'local' --repository=. local:$RELEASE/oscied-transform || xecho '1'
    fi
  fi

  pecho 'Deploy Publisher (1 instance)'
  yesOrNo $true 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg" ]; then
      mecho "Using user define Publisher configuration : $cfg"
      juju deploy -e 'local' --config "$cfg" --repository=. local:$RELEASE/oscied-publisher || xecho '1'
    else
      mecho 'Using default Publisher configuration'
      juju deploy -e 'local' --repository=. local:$RELEASE/oscied-publisher || xecho '1'
    fi
    juju expose -e 'local' oscied-publisher || xecho '2'
  fi

  pecho 'Deploy haproxy (1 instance)'
  yesOrNo $false 'deploy it now'
  if [ $REPLY -eq $true ]; then
    juju deploy -e 'local' cs:precise/haproxy || xecho '2'
    juju expose -e 'local' haproxy || xecho '3'
  fi

  techo "3/5 Add relation between Storage and other services"

  pecho 'Add-relation Storage <-> Transform'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'local' oscied-storage oscied-transform
  fi

  pecho 'Add-relation Storage <-> Publisher'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'local' oscied-storage oscied-publisher
  fi

  pecho 'Add-relation Storage <-> Orchestra'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'local' oscied-storage oscied-orchestra
  fi

  pecho 'Add-relation Storage <-> Web UI'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'local' oscied-storage oscied-webui
  fi

  techo "4/5 Add relation between Orchestra and other services"

  pecho 'Add-relation Orchestra <-> Transform'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'local' oscied-orchestra:transform oscied-transform:transform
  fi

  pecho 'Add-relation Orchestra <-> Publisher'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'local' oscied-orchestra:publisher oscied-publisher:publisher
  fi

  pecho 'Add-relation Orchestra <-> Web UI'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'local' oscied-orchestra:api oscied-webui:api
  fi

  techo '5/5 Add relation between Web UI and HA Proxy'

  pecho 'Add-relation haproxy <-> Web UI'
  yesOrNo $false 'add it now'
  if [ $REPLY -eq $true ]; then
    juju unexpose -e 'local' oscied-webui
    juju add-relation -e 'local' haproxy oscied-webui
  fi
}
