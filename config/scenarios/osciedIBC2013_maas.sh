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
    juju destroy-environment --environment 'maas'
    juju bootstrap --environment 'maas'
  fi

  pecho 'Deploy Orchestra (1 instance)'
  mecho "Using user define Orchestra configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    jitsu deploy-to 0 --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-orchestra orchestra || xecho '1'
    juju expose --environment 'maas' orchestra || xecho '2'
  fi

  pecho 'Deploy Web UI (1 instance)'
  mecho "Using user define Web UI configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    jitsu deploy-to 0 --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-webui webui || xecho '1'
    juju expose --environment 'maas' webui || xecho '2'
  fi

  pecho 'Deploy Storage (2 instance without replication)'
  mecho "Using user define Storage configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju deploy -n 2 --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-storage storage || xecho '1'
    juju expose --environment 'maas' storage || xecho '2'
  fi

  pecho 'Deploy Transform (2 instances)'
  mecho "Using user define Transform configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    jitsu deploy-to 1 --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-transform transform1 || xecho '1'
    jitsu deploy-to 2 --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-transform transform2 || xecho '2'
  fi

  pecho 'Deploy Publisher (2 instances)'
  mecho "Using user define Publisher configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    jitsu deploy-to 1 --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-publisher publisher1 || xecho '1'
    jitsu deploy-to 2 --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-publisher publisher2 || xecho '2'
    juju expose --environment 'maas' publisher1 || xecho '3'
    juju expose --environment 'maas' publisher2 || xecho '4'
  fi

  pecho 'Connect all services together (with juju add-relation)'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation --environment 'maas' storage orchestra
    juju add-relation --environment 'maas' storage webui
    juju add-relation --environment 'maas' storage transform1
    juju add-relation --environment 'maas' storage transform2
    juju add-relation --environment 'maas' storage publisher1
    juju add-relation --environment 'maas' storage publisher2
    juju add-relation --environment 'maas' orchestra:api webui:api
    juju add-relation --environment 'maas' orchestra:transform transform1:transform
    juju add-relation --environment 'maas' orchestra:transform transform2:transform
    juju add-relation --environment 'maas' orchestra:publisher publisher1:publisher
    juju add-relation --environment 'maas' orchestra:publisher publisher2:publisher
  fi
}
