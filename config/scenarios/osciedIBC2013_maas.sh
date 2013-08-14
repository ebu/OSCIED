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

osciedIBC2013_maasDescription='Launch IBC 2013 cluster setup (MaaS Cluster with 3 machines)'
osciedIBC2013_maasScenario()
{
  cd "$CHARMS_DEPLOY_PATH/.." || xecho "Unable to find path $CHARMS_DEPLOY_PATH/.."
  cfg_maas="$CONFIG_JUJU_PATH/osciedIBC2013_maas.yaml"

  cp -f "$cfg_maas" "$CONFIG_GEN_CONFIG_FILE"

  yesOrNo $false "Deploy on MaaS Cluster"
  if [ $REPLY -eq $true ]; then
    osciedIBC2013Scenario_maas
  fi
}

osciedIBC2013Scenario_maas()
{
  techo 'Deploy services on private MaaS Cluster'

  pecho 'Cleanup and bootstrap juju maas environment'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju destroy-environment -e 'maas'
    juju bootstrap -e 'maas'
  fi

  pecho 'Deploy Storage (2 instance without replication)'
  mecho "Using user define Storage configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju deploy -n 2 -e 'maas' --config "$cfg_maas" --repository=. local:$RELEASE/oscied-storage || xecho '1'
    juju expose -e 'maas' oscied-storage || xecho '2'
  fi

  # FIXME periodic check of juju status to wait until the storage service to be up and ready

  pecho 'Deploy Orchestra (1 instance)'
  mecho "Using user define Orchestra configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju deploy --to 0 -e 'maas' --config "$cfg_maas" --repository=. local:$RELEASE/oscied-orchestra || \
      xecho '1'
    juju expose -e 'maas' oscied-orchestra || xecho '2'
  fi

  # FIXME periodic check of juju status to wait until the orchestra service to be up and ready

  pecho 'Deploy Web UI (1 instance)'
  mecho "Using user define Web UI configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju deploy --to 0 -e 'maas' --config "$cfg_maas" --repository=. local:$RELEASE/oscied-webui || xecho '1'
    juju expose -e 'maas' oscied-webui || xecho '2'
  fi

  pecho 'Deploy Transform (2 instances)'
  mecho "Using user define Transform configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju deploy --to 1 -e 'maas' --config "$cfg_maas" --repository=. \
      local:$RELEASE/oscied-transform oscied-transform1 || xecho '1'
    juju deploy --to 2 -e 'maas' --config "$cfg_maas" --repository=. local:$RELEASE/oscied-transform oscied-transform2 \
      || xecho '2'
  fi

  # FIXME periodic check of juju status to wait until the publication service to be up and ready

  pecho 'Deploy Publisher (2 instances)'
  mecho "Using user define Publisher configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju deploy --to 1 -e 'maas' --config "$cfg_maas" --repository=. local:$RELEASE/oscied-publisher oscied-publisher1 \
      || xecho '1'
    juju deploy --to 2 -e 'maas' --config "$cfg_maas" --repository=. local:$RELEASE/oscied-publisher oscied-publisher2 \
      || xecho '2'
    juju expose -e 'maas' oscied-publisher1 || xecho '3'
    juju expose -e 'maas' oscied-publisher2 || xecho '4'
  fi

  pecho 'Disconnect all services [DEBUG PURPOSE ONLY] (with juju remove-relation)'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju remove-relation -e 'maas' oscied-storage oscied-orchestra
    juju remove-relation -e 'maas' oscied-storage oscied-webui
    juju remove-relation -e 'maas' oscied-storage oscied-transform1
    juju remove-relation -e 'maas' oscied-storage oscied-transform2
    juju remove-relation -e 'maas' oscied-storage oscied-publisher1
    juju remove-relation -e 'maas' oscied-storage oscied-publisher2
    juju remove-relation -e 'maas' oscied-orchestra:api oscied-webui:api
    juju remove-relation -e 'maas' oscied-orchestra:transform oscied-transform1:transform
    juju remove-relation -e 'maas' oscied-orchestra:transform oscied-transform2:transform
    juju remove-relation -e 'maas' oscied-orchestra:publisher oscied-publisher1:publisher
    juju remove-relation -e 'maas' oscied-orchestra:publisher oscied-publisher2:publisher
  fi

  pecho 'Connect all services together (with juju add-relation)'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'maas' oscied-storage oscied-orchestra
    juju add-relation -e 'maas' oscied-storage oscied-webui
    juju add-relation -e 'maas' oscied-storage oscied-transform1
    juju add-relation -e 'maas' oscied-storage oscied-transform2
    juju add-relation -e 'maas' oscied-storage oscied-publisher1
    juju add-relation -e 'maas' oscied-storage oscied-publisher2
    mecho 'now this is orchestra relation with the web user interface units'
    pause
    juju add-relation -e 'maas' oscied-orchestra:api oscied-webui:api
    mecho 'now this is orchestra relation with transformation units'
    pause
    juju add-relation -e 'maas' oscied-orchestra:transform oscied-transform1:transform
    juju add-relation -e 'maas' oscied-orchestra:transform oscied-transform2:transform
    mecho 'now this is orchestra relation with publication units'
    pause
    juju add-relation -e 'maas' oscied-orchestra:publisher oscied-publisher1:publisher
    juju add-relation -e 'maas' oscied-orchestra:publisher oscied-publisher2:publisher
  fi
}
