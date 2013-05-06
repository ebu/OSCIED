#!/usr/bin/env bash

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCENARIOS
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
# Retrieved from https://github.com/EBU-TI/OSCIED

osciedDemoDescription='Launch oscied demo setup (MaaS Cluster, Local, Amazon)'
osciedDemoScenario()
{
  cd "$CHARMS_DEPLOY_PATH/.." || xecho "Unable to find path $CHARMS_DEPLOY_PATH/.."
  cfg_maas="$CONFIG_JUJU_PATH/osciedDemo_maas.yaml"
  cfg_local="$CONFIG_JUJU_PATH/osciedDemo_local.yaml"
  cfg_amazon="$CONFIG_JUJU_PATH/osciedDemo_amazon.yaml"

  cp -f "$cfg_maas" "$CONFIG_GEN_CONFIG_FILE"

  yesOrNo $false "Deploy on MaaS Cluster"
  if [ $REPLY -eq $true ]; then
    osciedDemoScenario_maas
  fi
  yesOrNo $false "Deploy on Local Computer"
  if [ $REPLY -eq $true ]; then
    osciedDemoScenario_local
  fi
  yesOrNo $false "Deploy on Amazon"
  if [ $REPLY -eq $true ]; then
    osciedDemoScenario_amazon
  fi
}

osciedDemoScenario_maas()
{
  techo '1/3 Deploy services on private MaaS Cluster'

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
    juju deploy --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-orchestra || xecho '1'
    juju expose --environment 'maas' oscied-orchestra || xecho '2'
  fi

  id1=$(juju status --environment 'maas' oscied-orchestra | grep 'machine:' | cut -d':' -f2)
  if ! validateNumber "$id1"; then
    xecho "Unable to detect id of machine that runs Orchestra"
  fi

  pecho 'Deploy Web UI (1 instance)'
  mecho "Using user define Web UI configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    jitsu deploy-to "$id1" --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-webui || xecho '1'
    juju expose --environment 'maas' oscied-webui || xecho '2'
  fi

  pecho 'Deploy Storage (1 instance)'
  mecho "Using user define Storage configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju deploy --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-storage || xecho '1'
    juju expose --environment 'maas' oscied-storage || xecho '2'
  fi

  id2=$(juju status --environment 'maas' oscied-storage | grep 'machine:' | cut -d':' -f2)
  if ! validateNumber "$id2"; then
    xecho "Unable to detect id of machine that runs Storage"
  fi

  pecho 'Deploy Transform (1 instance)'
  mecho "Using user define Transform configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    jitsu deploy-to "$id2" --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-transform || xecho '1'
  fi

  pecho 'Deploy Publisher (1 instance)'
  mecho "Using user define Publisher configuration : $cfg_maas"
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    jitsu deploy-to "$id2" --environment 'maas' --config "$cfg_maas" \
      --repository=. local:$RELEASE/oscied-publisher || xecho '1'
    juju expose --environment 'maas' oscied-publisher || xecho '2'
  fi

  pecho 'Add-relation Storage <-> Transform'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation --environment 'maas' oscied-storage oscied-transform
  fi

  pecho 'Add-relation Storage <-> Publisher'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation --environment 'maas' oscied-storage oscied-publisher
  fi

  pecho 'Add-relation Storage <-> Orchestra'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation --environment 'maas' oscied-storage oscied-orchestra
  fi

  pecho 'Add-relation Storage <-> Web UI'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation --environment 'maas' oscied-storage oscied-webui
  fi

  pecho 'Add-relation Orchestra <-> Transform'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation --environment 'maas' oscied-orchestra:transform oscied-transform:transform
  fi

  pecho 'Add-relation Orchestra <-> Publisher'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation --environment 'maas' oscied-orchestra:publisher oscied-publisher:publisher
  fi

  pecho 'Add-relation Orchestra <-> Web UI'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju add-relation --environment 'maas' oscied-orchestra:api oscied-webui:api
  fi
}

osciedDemoScenario_local()
{
  techo "2/3 Deploy services (LXC containers) into David's Workstation at hepia"

  pecho 'Cleanup and bootstrap juju local environment'
  juju destroy-environment --environment 'local'
  juju bootstrap --environment 'local'

  mecho '[WARNING] Continue only when services deployed on the MaaS cluster are up and ready !'
  pause

  pecho 'Generate services configuration for local deployment'

  get_unit_config 'oscied-transform' '1' 'storage_ip'
  if [ ! "$REPLY" ]; then xecho 'Unable to detect storage internal IP address'; fi
  storage="s<STORAGE_IP<$REPLY<g"

  get_unit_config 'oscied-transform' '1' 'mongo_connection'
  if [ ! "$REPLY" ]; then xecho 'Unable to detect MongoDB connection'; fi
  mongo="s<MONGO<$REPLY<g"

  get_unit_config 'oscied-transform' '1' 'rabbit_connection'
  if [ ! "$REPLY" ]; then xecho 'Unable to detect RabbitMQ connection'; fi
  rabbit="s<RABBIT<$REPLY<g"

  sed "$storage;$mongo;$rabbit" < "$cfg_local.template" > "$cfg_local"

  pecho 'Deploy Transform (1 instance)'
  mecho "Using user define Transform configuration : $cfg_local"
  juju deploy --environment 'local' --config "$cfg_local" \
    --repository=charms/ local:$RELEASE/oscied-transform || xecho '1'

  pecho 'Deploy Publisher (1 instance)'
  mecho "Using user define Publisher configuration : $cfg_local"
  juju deploy --environment 'local' --config "$cfg_local" \
    --repository=charms/ local:$RELEASE/oscied-publisher || xecho '1'
  juju expose --environment 'local' oscied-publisher || xecho '2'
}

osciedDemoScenario_amazon()
{
  techo "3/3 Deploy services on Amazon"

  pecho 'Cleanup and bootstrap juju amazon environment'
  yesOrNo $false 'do it now'
  if [ $REPLY -eq $true ]; then
    juju destroy-environment --environment 'amazon'
    juju bootstrap --environment 'amazon'
  fi

  mecho '[WARNING] Continue only when services deployed on the MaaS cluster are up and ready !'
  pause

  pecho 'Gather services configuration for amazon deployment'

  yesOrNo $true 'Is Orchestra behind a NAT/FW'
  if [ $REPLY -eq $true ]; then
    default='129.194.185.47:5000'
    readLine "Please enter orchestra api public (NATed) socket [$default]"
    if [ ! "$CHOICE" ]; then CHOICE=$default; fi
  else
    CHOICE=''
  fi
  api_socket=$CHOICE
  api_nat="s<API_NAT_SOCKET<$CHOICE<g"

  yesOrNo $true 'Is Storage behind a NAT/FW'
  if [ $REPLY -eq $true ]; then
    default='129.194.185.47'
    readLine "Please enter storage public (NATed) IP address [$default]"
    if [ ! "$CHOICE" ]; then CHOICE=$default; fi
  else
    CHOICE=''
  fi
  storage_nat="s<STORAGE_NAT_IP<$CHOICE<g"

  pecho 'Generate services configuration for amazon deployment'

  get_unit_config 'oscied-transform' '1' 'storage_ip'
  if [ ! "$REPLY" ]; then xecho 'Unable to detect storage internal IP address'; fi
  storage="s<STORAGE_IP<$REPLY<g"

  get_unit_config 'oscied-transform' '1' 'mongo_connection'
  if [ ! "$REPLY" ]; then xecho 'Unable to detect MongoDB connection'; fi
  mongo="s<MONGO<$REPLY<g"

  get_unit_config 'oscied-transform' '1' 'rabbit_connection'
  if [ ! "$REPLY" ]; then xecho 'Unable to detect RabbitMQ connection'; fi
  rabbit="s<RABBIT<$REPLY<g"

  if [ "$api_nat" ]; then
    api_ip=$(echo $api_socket | cut -d':' -f1)
    mongo=$(echo $mongo | sed "s<@[^:]*:<@$api_ip:<")
    rabbit=$(echo $rabbit | sed "s<@[^:]*:<@$api_ip:<")
  fi

  sed "$api_nat;$storage;$storage_nat;$mongo;$rabbit" < "$cfg_amazon.template" > "$cfg_amazon"

  cat "$cfg_amazon"
  yesOrNo $true 'deploy with this configuration'
  if [ $REPLY -eq $true ]; then
    pecho 'Deploy Transform (1 instance)'
    mecho "Using user define Transform configuration : $cfg_amazon"
    juju deploy --environment 'amazon' --config "$cfg_amazon" \
      --repository=charms/ local:$RELEASE/oscied-transform oscied-transform-demo || xecho '1'

    pecho 'Deploy Publisher (1 instance)'
    mecho "Using user define Publisher configuration : $cfg_amazon"
    juju deploy --environment 'amazon' --config "$cfg_amazon" \
      --repository=charms/ local:$RELEASE/oscied-publisher oscied-publisher-demo || xecho '1'
    juju expose --environment 'amazon' oscied-publisher-demo || xecho '2'
  fi
}
