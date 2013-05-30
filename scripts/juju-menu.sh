#!/usr/bin/env bash

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
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

. ./common.sh

main()
{
  if [ $# -gt 0 ]; then
    operation_auto="$1"
    shift
  elif [ $# -eq 0 ]; then
    operation_auto=''
  else
    xecho "Usage: $(basename $0) (nothing) -or- operation [parameters]"
  fi

  if ! which juju > /dev/null; then
    xecho 'JuJu must be installed'
  fi

  autoInstall dialog dialog

  listing=/tmp/$$.list
  tmpfile=/tmp/$$
  jujulog='/usr/local/bin/juju-log'
  openport='/usr/local/bin/open-port'
  cget='/usr/local/bin/config-get'
  rget='/usr/local/bin/relation-get'
  uget='/usr/local/bin/unit-get'
  trap "rm -f '$listing' '$tmpfile' '$jujulog' '$openport' '$cget' '$rget' '$uget' 2>/dev/null" \
    INT TERM EXIT

  if [ "$operation_auto" ]; then
    ok=$false
    techo 'OSCIED Operations with JuJu [AUTO]'
    mecho "Operation is $operation_auto"
    eval $operation_auto "$@"
    if [ $ok -eq $false ]; then
      xecho "Unknown operation : $operation_auto"
    fi
  else
    # Initialize main menu
    while true
    do
      $DIALOG --backtitle 'OSCIED Operations with JuJu' \
              --menu 'Please select an operation' 0 0 0 \
              overwrite       'Overwrite charms in deployment path'      \
              deploy          'Launch a deployment scenario'             \
              destroy         'Destroy a deployed environment'           \
              standalone      'Play with a charm locally (yes, really)'  \
              status          'Display juju status'                      \
              status_svg      'Display juju status as a SVG graphic'     \
              log             'Launch juju debug log in a screen'        \
              config          'Update units public url listing file'     \
              unit_ssh        'Access to units with secure shell'        \
              unit_add        'Add a new unit to a running service'      \
              unit_remove     'Remove an unit from a running service'    \
              service_destroy 'Destroy a running service'  2> $tmpfile

      retval=$?
      operation=$(cat $tmpfile)
      [ $retval -ne 0 -o ! "$operation" ] && break
      techo "Execute operation $operation"
      eval $operation
      [ $retval -eq 0 ] && pause
    done
  fi
}

overwrite()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) overwrite"
  fi
  ok=$true

  overwrite_helper 'oscied-orchestra' || xecho 'Unable to overwrite Orchestra charm'
  overwrite_helper 'oscied-publisher' || xecho 'Unable to overwrite Publisher charm'
  overwrite_helper 'oscied-storage'   || xecho 'Unable to overwrite Storage charm'
  overwrite_helper 'oscied-transform' || xecho 'Unable to overwrite Transform charm'
  overwrite_helper 'oscied-webui'     || xecho 'Unable to overwrite Web UI charm'
  lu-importUtils "$CHARMS_DEPLOY_PATH"
}

overwrite_helper()
{
  [ $# -ne 1 ] && xecho 'OUPS !'
  mkdir -p "$CHARMS_DEPLOY_PATH" 2>/dev/null
  rm   -rf "$CHARMS_DEPLOY_PATH/$1" 2>/dev/null
  rsync -rtvh -LH --delete --progress --exclude='.git' --exclude='*.log' --exclude='*.pyc' \
    --exclude='celeryconfig.py' --exclude='build' --exclude='dist' --exclude='*.egg-info' \
    "$CHARMS_PATH/$1/" "$CHARMS_DEPLOY_PATH/$1/"
}

deploy()
{
  if [ $# -eq 1 ]; then
    scenario_auto=$1
  elif [ $# -eq 0 ]; then
    scenario_auto=''
  else
    xecho "Usage: $(basename $0) deploy [scenario]"
  fi
  ok=$true

  pecho 'Initialize JuJu orchestrator configuration'
  if [ ! -f $HOME/.ssh/id_rsa ]; then ssh-keygen -t rsa; fi # FIXME better trick
  ssh-add # Fix ERROR SSH forwarding error: Agent admitted failure to sign using the key.
  mkdir -p "$JUJU_STORAGE_PATH" 2>/dev/null
  if [ -f "$CONFIG_JUJU_ENVS_FILE" ]; then
    mecho "Using user defined environment : $CONFIG_JUJU_ENVS_FILE"
    cp "$CONFIG_JUJU_ENVS_FILE" "$JUJU_ENVS_FILE" || \
      xecho "Unable to copy juju's configuration file"
  else
    mecho 'Using default template to generate environment'
    sed "s:RELEASE:$RELEASE:g;s:STORAGE_PATH:$JUJU_STORAGE_PATH:g" "$CONFIG_JUJU_TEMPL_FILE" > \
      "$JUJU_ENVS_FILE" || xecho "Unable to generate juju's configuration file"
  fi
  $udo ufw disable # Fix master thesis ticket #80 - Juju stuck in pending when using LXC

  cd "$CONFIG_SCENARIOS_PATH" || xecho "Unable to find path $CONFIG_SCENARIOS_PATH"

  # Initialize scenarios menu
  find . -type f -name '*.sh' | sort > $listing
  scenariosList=''
  while read scenario
  do
    . "$scenario" # Include scenario source
    name=$(basename "$scenario" .sh)
    description=$(eval "echo \${${name}Description} | sed 's: :_:g'")
    scenariosList="$scenariosList$name $description "
  done < $listing

  if [ "$scenario_auto" ]; then
    techo 'OSCIED Operations with JuJu > Deployment Scenarios [AUTO]'
    mecho "Scenario is $scenario_auto"
    eval "${scenario_auto}Scenario"
  else
    # Scenarios menu
    while true
    do
      $DIALOG --backtitle 'OSCIED Operations with JuJu > Deployment Scenarios' \
              --menu 'Please select a deployment scenario' 0 0 0 \
              $scenariosList 2> $tmpfile

      retval=$?
      scenario=$(cat $tmpfile)
      [ $retval -ne 0 -o ! "$scenario" ] && break
      eval "${scenario}Scenario"
      [ $retval -eq 0 ] && pause
    done
  fi
}

destroy()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) destroy"
  fi
  ok=$true

  # Environments menu
  while true
  do
    $DIALOG --backtitle 'OSCIED Operations with JuJu > Destroy Environment' \
            --menu 'Please select an environment' 0 0 0 \
            'amazon' '-' 'local' '-' 'maas' '-' 2> $tmpfile

    retval=$?
    environment=$(cat $tmpfile)
    [ $retval -ne 0 -o ! "$environment" ] && break
    juju destroy-environment --environment "$environment"
  done
}

standalone()
{
  if [ $# -eq 2 ]; then
    charm_auto=$1
    hook_auto=$2
  elif [ $# -eq 0 ]; then
    charm_auto=''
    hook_auto=''
  else
    xecho "Usage: $(basename $0) standalone [charm hook]"
  fi
  ok=$true

  cd "$CHARMS_DEPLOY_PATH" || xecho "Unable to find path $CHARMS_DEPLOY_PATH"

  find .

  if [ "$charm_auto" -a "$hook_auto" ]; then
    techo 'OSCIED Operations with JuJu > Charms Standalone [AUTO]'
    mecho "Charm is $charm_auto, hook is $hook_auto"
    standalone_execute_hook "$CHARMS_DEPLOY_PATH/$charm_auto" "$hook_auto"
  else
    # Initialize charms menu
    find . -mindepth 1 -maxdepth 1 -type d | sort > $listing
    charmsList=''
    while read charm
    do
      charmsList="$charmsList$charm - "
    done < $listing

    # Charms menu
    while true
    do
      $DIALOG --backtitle 'OSCIED Operations with JuJu > Charms Standalone' \
              --menu 'Please select a charm' 0 0 0 \
              $charmsList 2> $tmpfile

      retval=$?
      charm="$CHARMS_DEPLOY_PATH/$(cat $tmpfile)"
      [ $retval -ne 0 -o ! "$charm" ] && break
      cd "$charm" || xecho "Unable to find path $charm"

      # Initialize hooks menu
      find 'hooks' -mindepth 1 -maxdepth 1 -type f | sort > $listing
      hooksList=''
      while read hook
      do
        hooksList="$hooksList$hook - "
      done < $listing

      # Hooks menu
      while true
      do
        name=$(basename $charm)
        $DIALOG --backtitle "OSCIED Operations with JuJu > Charms Standalone > Charm $name" \
                --menu 'Please select a hook' 0 0 0 \
                $hooksList 2> $tmpfile

        retval=$?
        hook=$(cat $tmpfile)
        [ $retval -ne 0 -o ! "$hook" ] && break
        standalone_execute_hook "$charm" "$hook"
        [ $retval -eq 0 ] && pause
      done

      # Charms menu pause
      [ $retval -eq 0 ] && pause
    done
  fi
}

standalone_execute_hook()
{
  [ $# -ne 2 ] && xecho 'OUPS !'

  pecho 'Install juju-log & open-port tricks'
  if ! getInterfaceIPv4 "$NETWORK_IFACE" '4'; then
    xecho "Unable to detect network interface $NETWORK_IFACE IP address"
  fi
  ip=$REPLY
  $udo sh -c "cp -f $CONFIG_JUJU_FILES_PATH/juju-log      $jujulog;  chmod 777 $jujulog"
  $udo sh -c "cp -f $CONFIG_JUJU_FILES_PATH/open-port     $openport; chmod 777 $openport"
  $udo sh -c "cp -f $CONFIG_JUJU_FILES_PATH/something-get $cget;     chmod 777 $cget"
  $udo sh -c "cp -f $CONFIG_JUJU_FILES_PATH/something-get $rget;     chmod 777 $rget"
  $udo sh -c "cp -f $CONFIG_JUJU_FILES_PATH/something-get $uget;     chmod 777 $uget"
  $udo sh -c "cp -f $CONFIG_JUJU_FILES_PATH/something-get.list /tmp/;"
  $udo sh -c "sed -i 's:127.0.0.1:$ip:g' /tmp/something-get.list"
  pecho "Execute hook script $2"
  cd "$1"  || xecho "Unable to find path $1"
  $udo $2  || xecho 'Hook is unsucessful'
  recho 'Hook successful'
}

status()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) status"
  fi
  ok=$true

  techo 'Status of default environment'; juju status
  techo 'Status of amazon environment';  juju status --environment amazon
  techo 'Status of local environment';   juju status --environment local
  techo 'Status of maas environment';    juju status --environment maas
}

status_svg()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) status_svg"
  fi
  ok=$true

  cd $HOME
  e='--environment'
  f='--format'
  techo 'Status of default environment'; juju status $f svg --output default_status.svg
  techo 'Status of amazon environment';  juju status $e amazon $f svg --output amazon_status.svg
  techo 'Status of local environment';   juju status $e local  $f svg --output local_status.svg
  techo 'Status of maas environment';    juju status $e maas   $f svg --output maas_status.svg
  eog *_status.svg
}

log()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) log"
  fi
  ok=$true

  screen -dmS juju-log juju debug-log
}

config()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) config"
  fi
  ok=$true

  content=''
  count=1
  last_name=''
  orchestra=''
  juju status 2>/dev/null | \
  {
    while read line
    do
      name=$(expr match "$line" '.*\(oscied-.*/[0-9]*\):.*')
      address=$(expr match "$line" '.*public-address: *\([^ ]*\) *')
      [ "$name" ] && last_name=$name
      if [ "$address" -a "$last_name" ]; then
        mecho "$last_name -> $address"
        [ "$content" ] && content="$content\n"
        content="$content$last_name=$address"
        last_name=''
      fi
      count=$((count+1))

      if echo $name | grep -q 'oscied-orchestra'; then
        orchestra=$name
      fi
    done

    if [ "$content" ]; then
      echo $e_ "$content" > "$CONFIG_GEN_UNITS_FILE"
      recho "Charms's units public URLs listing file updated"
    else
      xecho "Unable to detect charms's units public URLs"
    fi

    if [ "$orchestra" ]; then
      pecho "Auto-detect storage internal IP address by parsing $orchestra unit configuration"
      number=$(expr match "$orchestra" '.*/\([0-9]*\)')
      get_unit_config 'oscied-orchestra' "$number" 'storage_address'
      if [ ! "$REPLY" ]; then
        xecho 'Unable to detect storage internal IP address'
      else
        mecho "Updating common.sh with detected storage internal IP = $REPLY"
        sed -i "s#STORAGE_PRIVATE_IP=.*#STORAGE_PRIVATE_IP='$REPLY'#" "$SCRIPTS_PATH/common.sh"
      fi
      get_unit_config 'oscied-orchestra' "$number" 'storage_mountpoint'
      if [ ! "$REPLY" ]; then
        xecho 'Unable to detect storage mountpoint'
      else
        number=$(expr match "$REPLY" '.*_\([0-9]*\)')
        brick="/exp$number"
        mecho "Updating common.sh with detected storage mountpoint = $REPLY and brick = $brick"
        sed -i -e "s#STORAGE_MOUNTPOINT=.*#STORAGE_MOUNTPOINT='$REPLY'#" \
               -e "s#STORAGE_BRICK=.*#STORAGE_BRICK='$brick'#" "$SCRIPTS_PATH/common.sh"
      fi
    else
      recho 'Unable to detect orchestrator unit name'
    fi
  }
}

unit_ssh()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) unit_ssh"
  fi
  ok=$true

  yesOrNo $true 'Update units listing'
  [ $REPLY -eq $true ] && config

  # Initialize remote menu
  unitsList=$(cat "$CONFIG_GEN_UNITS_FILE" | sort | sed 's:=: :g;s:\n: :g')

  # Remote menu
  while true
  do
    $DIALOG --backtitle 'OSCIED Operations with JuJu > Remote Access to Units' \
            --menu 'Please select a unit' 0 0 0 \
            $unitsList 2> $tmpfile

    retval=$?
    unit=$(cat $tmpfile)
    [ $retval -ne 0 -o ! "$unit" ] && break
    juju ssh "$unit"
    [ $retval -eq 0 ] && pause
  done
}

unit_add()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) unit_add"
  fi
  ok=$true

  yesOrNo $true 'Update units listing'
  [ $REPLY -eq $true ] && config

  # Initialize add unit menu
  get_services_dialog_listing
  $DIALOG --backtitle 'OSCIED Operations with JuJu > Scale-up a Service' \
          --menu 'Please select a service' 0 0 0 $REPLY 2> $tmpfile

  retval=$?
  service=$(cat $tmpfile)
  if [ $retval -ne 0 -o ! "$service" ]; then
    recho 'Operation aborted by user'
  else
    juju_unit_add "$service"
  fi
}

unit_remove()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) unit_remove"
  fi
  ok=$true

  yesOrNo $true 'Update units listing'
  [ $REPLY -eq $true ] && config

  # Initialize remove unit menu
  get_units_dialog_listing
  $DIALOG --backtitle 'OSCIED Operations with JuJu > Scale-down a Service' \
          --menu 'Please select an unit' 0 0 0 $REPLY 2> $tmpfile

  retval=$?
  unit=$(cat $tmpfile)
  if [ $retval -ne 0 -o ! "$unit" ]; then
    recho 'Operation aborted by user'
  else
    juju_unit_remove "$unit"
  fi
}

main "$@"
