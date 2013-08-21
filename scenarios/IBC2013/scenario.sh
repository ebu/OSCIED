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

osciedIBC2013Description='Launch IBC 2013 demo setup (MaaS Cluster with 3 machines // Amazon)'
osciedIBC2013Scenario()
{
  cd "$CHARMS_DEPLOY_PATH/.." || xecho "Unable to find path $CHARMS_DEPLOY_PATH/.."
  cfg_amazon="$CONFIG_JUJU_PATH/osciedIBC2013_amazon.yaml"
  cfg_maas="$CONFIG_JUJU_PATH/osciedIBC2013_maas.yaml"
  mecho "Using user define Publisher configuration : $cfg_maas"

  cp -f "$cfg_amazon" "$CONFIG_GEN_CONFIG_FILE"
  cp -f "$cfg_maas"   "$CONFIG_GEN_CONFIG_FILE"

  yesOrNo $false "Deploy on MaaS Cluster"
  if [ $REPLY -eq $true ]; then
    osciedIBC2013Scenario_maas
  fi

  yesOrNo $false "Deploy on Amazon"
  if [ $REPLY -eq $true ]; then
    osciedIBC2013Scenario_amazon
  fi
}

osciedIBC2013Scenario_maas()
{
  techo '1/2 Deploy services on private MaaS Cluster'

  pecho 'Cleanup and bootstrap juju maas environment'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    sudo juju destroy-environment -e 'maas'
    sudo juju bootstrap -e 'maas' -v
  fi

  pecho 'Deploy Storage (2 instance without replication)'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju deploy -n 2 -e 'maas' --config "$cfg_maas" --repository=. local:$RELEASE/oscied-storage || xecho '1'
    juju expose -e 'maas' oscied-storage || xecho '2'
  fi

  # FIXME periodic check of juju status to wait until the storage service to be up and ready

  pecho 'Deploy Orchestra (1 instance)'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju deploy --to 0 -e 'maas' --config "$cfg_maas" --repository=. local:$RELEASE/oscied-orchestra || \
      xecho '1'
    juju expose -e 'maas' oscied-orchestra || xecho '2'
  fi

  # FIXME periodic check of juju status to wait until the orchestra service to be up and ready

  pecho 'Deploy Web UI (1 instance)'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju deploy --to 0 -e 'maas' --config "$cfg_maas" --repository=. local:$RELEASE/oscied-webui || xecho '1'
    juju expose -e 'maas' oscied-webui || xecho '2'
  fi

  pecho 'Deploy Transform (2 instances)'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju deploy --to 1 -e 'maas' --config "$cfg_maas" --repository=. \
      local:$RELEASE/oscied-transform oscied-transform1 || xecho '1'
    juju deploy --to 2 -e 'maas' --config "$cfg_maas" --repository=. local:$RELEASE/oscied-transform oscied-transform2 \
      || xecho '2'
  fi

  # FIXME periodic check of juju status to wait until the publication service to be up and ready

  pecho 'Deploy Publisher (2 instances)'
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

osciedIBC2013Scenario_amazon()
{
  techo "2/2 Deploy services on Amazon"

  tm='instance-type=t1.micro'
  mm='instance-type=m1.medium'

  pecho 'Cleanup and bootstrap juju amazon environment'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    sudo juju destroy-environment -e 'amazon'
    sudo juju bootstrap -e 'amazon' -v
  fi

  pecho 'Deploy Orchestra (1 instance)'
  yesOrNo $false 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg_amazon" ]; then
      mecho "Using user define Orchestra configuration : $cfg_amazon"
      juju deploy -e 'amazon' --config "$cfg_amazon" --repository=. local:$RELEASE/oscied-orchestra || xecho '1'
    else
      mecho 'Using default Orchestra configuration'
      juju deploy -e 'amazon' --repository=. local:$RELEASE/oscied-orchestra || xecho '1'
    fi
    juju expose -e 'amazon' oscied-orchestra || xecho '2'
  fi

  pecho 'Deploy Storage (1 instance)'
  yesOrNo $false 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg_amazon" ]; then
      mecho "Using user define Storage configuration : $cfg_amazon"
#      juju deploy -e 'amazon' --config "$cfg_amazon" --constraints "arch=amd64 cpu-cores=2 mem=1G" --repository=. \
      juju deploy -e 'amazon' --config "$cfg_amazon" --repository=. local:$RELEASE/oscied-storage || xecho '1'
    else
      mecho 'Using default Storage configuration'
      juju deploy -e 'amazon' --repository=. local:$RELEASE/oscied-storage || xecho '1'
    fi
    juju expose -e 'amazon' oscied-storage || xecho '2'
  fi

  pecho 'Deploy Web UI (1 instance)'
  yesOrNo $false 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg_amazon" ]; then
      mecho "Using user define Web UI configuration : $cfg_amazon"
      juju deploy --to 1 -e 'amazon' --config "$cfg_amazon" --repository=. local:$RELEASE/oscied-webui || xecho '1'
    else
      mecho 'Using default Web UI configuration'
      juju deploy --to 1 -e 'amazon' --repository=. local:$RELEASE/oscied-webui || xecho '1'
    fi
    juju expose -e 'amazon' oscied-webui || xecho '2'
  fi

  pecho 'Deploy Transform (1 instance)'
  yesOrNo $false 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg_amazon" ]; then
      mecho "Using user define Transform configuration : $cfg_amazon"
      juju deploy --to 2 -e 'amazon' --config "$cfg_amazon" --repository=. local:$RELEASE/oscied-transform || xecho '1'
    else
      mecho 'Using default Transform configuration'
      juju deploy --to 2 -e 'amazon' --repository=. local:$RELEASE/oscied-transform || xecho '1'
    fi
  fi

  pecho 'Deploy Publisher (1 instance)'
  yesOrNo $false 'deploy it now'
  if [ $REPLY -eq $true ]; then
    if [ -f "$cfg_amazon" ]; then
      mecho "Using user define Publisher configuration : $cfg_amazon"
      juju deploy --to 2 -e 'amazon' --config "$cfg_amazon" --repository=. local:$RELEASE/oscied-publisher || xecho '1'
    else
      mecho 'Using default Publisher configuration'
      juju deploy --to 2 -e 'amazon' --repository=. local:$RELEASE/oscied-publisher || xecho '1'
    fi
    juju expose -e 'amazon' oscied-publisher || xecho '2'
  fi

  pecho 'Deploy haproxy (1 instance)'
  yesOrNo $false 'deploy it now'
  if [ $REPLY -eq $true ]; then
    juju deploy -e 'amazon' cs:precise/haproxy || xecho '2'
    juju expose -e 'amazon' haproxy || xecho '3'
  fi

  techo "3/5 Add relation between Storage and other services"

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

  pecho 'Add-relation Storage <-> Web UI'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'amazon' oscied-storage oscied-webui
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

  pecho 'Add-relation Orchestra <-> Web UI'
  yesOrNo $true 'add it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation -e 'amazon' oscied-orchestra:api oscied-webui:api
  fi

  techo '5/5 Add relation between Web UI and HA Proxy'

  pecho 'Add-relation haproxy <-> Web UI'
  yesOrNo $false 'add it now'
  if [ $REPLY -eq $true ]; then
    juju unexpose -e 'amazon' oscied-webui
    juju add-relation -e 'amazon' haproxy oscied-webui
  fi
}
