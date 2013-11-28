#!/usr/bin/env bash

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
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

. ./logicielsUbuntuUtils.inc

# Constants ============================================================================================================

RELEASE='raring'  # Update this according to your needs

SCRIPTS_PATH=$(pwd)
BASE_PATH=$(dirname "$SCRIPTS_PATH")
CHARMS_PATH="$BASE_PATH/charms"
CHARMS_DEPLOY_PATH="$BASE_PATH/deploy/$RELEASE"
DOCS_PATH="$BASE_PATH/docs"
LIBRARY_PATH="$BASE_PATH/library"
MEDIAS_PATH="$BASE_PATH/medias"
SCENARIOS_PATH="$BASE_PATH/scenarios"

# Symbolic link to current configuration's path
SCENARIO_CURRENT_PATH="$SCENARIOS_PATH/current"
SCENARIO_GEN_UNITS_FILE="$SCENARIO_CURRENT_PATH/units.list"

# Orchestra related configuration (e.g. initial setup)
SCENARIO_API_USERS_FILE="$SCENARIO_CURRENT_PATH/users.csv"
SCENARIO_API_MEDIAS_FILE="$SCENARIO_CURRENT_PATH/medias.csv"
SCENARIO_API_TPROFILES_FILE="$SCENARIO_CURRENT_PATH/tprofiles.csv"

# JuJu related configuration (e.g. environments)
SCENARIO_JUJU_ID_RSA="$SCENARIO_CURRENT_PATH/id_rsa"
SCENARIO_JUJU_ID_RSA_PUB="$SCENARIO_CURRENT_PATH/id_rsa.pub"
SCENARIO_JUJU_ENVS_FILE="$SCENARIO_CURRENT_PATH/environments.yaml"
SCENARIO_JUJU_LOG_FILE="$SCENARIO_CURRENT_PATH/juju-debug.log"

# System configuration (e.g. certificates + juju configuration)
ID_RSA="$HOME/.ssh/id_rsa"
ID_RSA_PUB="$HOME/.ssh/id_rsa.pub"
JUJU_PATH="$HOME/.juju"
JUJU_STORAGE_PATH="$JUJU_PATH/local/"
JUJU_ENVS_FILE="$JUJU_PATH/environments.yaml"


# Utilities ============================================================================================================

_check_juju()
{
  if which juju > /dev/null; then
    echo ''
  elif [ $# -gt 0 ]; then
    echo '[DISABLED] '
  else
    xecho 'JuJu must be installed, this method is disabled'
  fi
}

_config_helper()
{
  _check_juju

  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) _config_helper"
  fi
  ok=$true

  content=''
  count=1
  last_name=''
  juju status 2>/dev/null > $tmpfile
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
  done < $tmpfile

  if [ "$content" ]; then
    echo $e_ "$content" > "$SCENARIO_GEN_UNITS_FILE"
    recho "Charms's units public URLs listing file updated"
  else
    xecho "Unable to detect charms's units public URLs"
  fi
}

_deploy_helper()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0)._deploy_helper scenario"
  fi
  scenario=$1

  techo "Deploy scenario $scenario"

  pecho 'Update symlink to current scenario'
  rm -f "$SCENARIO_CURRENT_PATH" 2>/dev/null
  ln -s "$scenario" "$SCENARIO_CURRENT_PATH" || xecho 'Unable to update symlink'

  pecho 'Initialize JuJu orchestrator configuration'
  if [ -f "$ID_RSA" ]; then
    suffix=$(md5sum "$ID_RSA" | cut -d' ' -f1)
    mecho "Backup certificate $ID_RSA into ${ID_RSA}_$suffix"
    cp -f "$ID_RSA"     "${ID_RSA}_$suffix"     || xecho 'Unable to backup certificate file (1/2)'
    cp -f "$ID_RSA_PUB" "${ID_RSA_PUB}_$suffix" || xecho 'Unable to backup certificate file (2/2)'
  fi
  if [ ! -f "$SCENARIO_JUJU_ID_RSA" ]; then
    recho 'It is strongly advised to create a certificate per scenario'
    yesOrNo $default 'generate it now'
    if [ $REPLY -eq $true ]; then
      ssh-keygen -t rsa -b 2048 -f "$SCENARIO_JUJU_ID_RSA"
    fi
  fi
  if [ -f "$SCENARIO_JUJU_ID_RSA" ]; then
    mecho "Using scenario's certificate file : $SCENARIO_JUJU_ID_RSA"
    # And make scenario's certificate the default
    cp -f "$SCENARIO_JUJU_ID_RSA"     "$ID_RSA"     || xecho 'Unable to copy certificate file (1/2)'
    cp -f "$SCENARIO_JUJU_ID_RSA_PUB" "$ID_RSA_PUB" || xecho 'Unable to copy certificate file (2/2)'
  fi
  # Fix ERROR SSH forwarding error: Agent admitted failure to sign using the key.
  ssh-add "$ID_RSA"

  # FIXME and what about *.pem stuff ?
  mkdir -p "$JUJU_PATH" "$JUJU_STORAGE_PATH" 2>/dev/null
  # Backup any already existing environments file (magic stuff) !
  if [ -f "$JUJU_ENVS_FILE" ]; then
    suffix=$(md5sum "$JUJU_ENVS_FILE" | cut -d' ' -f1)
    cp -f "$JUJU_ENVS_FILE" "${JUJU_ENVS_FILE}_$suffix" || xecho 'Unable to backup environments file'
  fi
  if [ -f "$SCENARIO_JUJU_ENVS_FILE" ]; then
    mecho "Using scenario's environments file : $SCENARIO_JUJU_ENVS_FILE"
  else
    if [ ! -f "$JUJU_ENVS_FILE" ]; then
      mecho 'Using juju to generate default environments file'
      juju generate-config || xecho "Unable to generate juju's environments file"
    fi
    mv "$JUJU_ENVS_FILE" "$SCENARIO_JUJU_ENVS_FILE"
  fi

  mecho 'An editor will be opened with the juju environments file.'
  mecho 'You must ensure that this file is filled with required values.'
  mecho 'For example, verify or set your amazon credentials ...'
  pause
  editor "$SCENARIO_JUJU_ENVS_FILE"
  cp "$SCENARIO_JUJU_ENVS_FILE" "$JUJU_ENVS_FILE" || xecho 'Unable to copy environments file'

  $udo ufw disable # Fix master thesis ticket #80 - Juju stuck in pending when using LXC

  pecho "Copy JuJu environments file & SSH keys to Orchestra charm's deployment path"
  cp -f "$ID_RSA"         "$CHARMS_DEPLOY_PATH/oscied-orchestra/ssh/"
  cp -f "$ID_RSA_PUB"     "$CHARMS_DEPLOY_PATH/oscied-orchestra/ssh/"
  cp -f "$JUJU_ENVS_FILE" "$CHARMS_DEPLOY_PATH/oscied-orchestra/juju/"
  find "$JUJU_PATH" -mindepth 1 -maxdepth 1 -type f -name '*.pem' \
    -exec sudo chown $USER:$USER {} \; \
    -exec cp -f {} "$CHARMS_DEPLOY_PATH/oscied-orchestra/juju/" \;

  pecho "Execute script of scenario $scenario"
  python "$scenario/scenario.py" -m "$(dirname "$CHARMS_DEPLOY_PATH")" -r "$RELEASE"
}

_overwrite_helper()
{
  if [ $# -ne 2 ]; then
    xecho "Usage: $(basename $0)._overwrite_helper source destination"
  fi

  mkdir -p "$CHARMS_DEPLOY_PATH/$2" 2>/dev/null
  rsync -rtvh -LH --delete --progress --exclude='.git' --exclude='*.log' --exclude='*.pyc' \
    --exclude='celeryconfig.py' --exclude='build' --exclude='dist' --exclude='cover' \
    --exclude='*.egg-info' "$CHARMS_PATH/$1/" "$CHARMS_DEPLOY_PATH/$2/" || \
    xecho "Unable to overwrite $2 charm"
}

_rsync_helper()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0)._rsync_helper charm"
  fi

  chmod 600 "$ID_RSA" || xecho 'Unable to find id_rsa certificate'

  _config_helper

  # Initialize rsync menu
  unitsList=$(cat "$SCENARIO_GEN_UNITS_FILE" | grep "$1" | sort | sed 's:=: :g;s:\n: :g')

  # Rsync menu
  while true
  do
    $DIALOG --backtitle 'OSCIED Operations with JuJu > Rsync source-code to a Unit' \
            --menu 'Please select a unit' 0 0 0 \
            $unitsList 2> $tmpfile

    retval=$?
    unit=$(cat $tmpfile)
    [ $retval -ne 0 -o ! "$unit" ] && break
    number=$(echo $unit | cut -d'/' -f2)
    [ ! "$number" ] && xecho 'Unable to detect unit number'
    _get_unit_public_url $true "$1" "$number"
    host="ubuntu@$REPLY"
    dest="/var/lib/juju/agents/unit-$1-$number/charm"
    ssh -i "$ID_RSA" "$host" -n "sudo chown 1000:1000 $dest -R"
    rsync --rsync-path='sudo rsync' -avhL --progress --delete -e "ssh -i '$ID_RSA'" --exclude=.git \
      --exclude='build' --exclude='cover' --exclude='dist' --exclude=config.json \
      --exclude=celeryconfig.py --exclude=*.pyc --exclude=local_config.pkl --exclude=charms \
      --exclude=ssh --exclude=environments.yaml --exclude=*.log "$CHARMS_PATH/$1/" "$host:$dest/"
    ssh -i "$ID_RSA" "$host" -n "sudo chown root:root $dest -R"

    if [ "$1" = 'oscied-webui' ]; then
      dest='/var/www'
      ssh -i "$ID_RSA" "$host" -n "sudo chown 1000:1000 $dest -R"
      rsync -avh --progress -e "ssh -i '$ID_RSA'" --exclude=.git --exclude=.htaccess \
        --exclude=application/config/config.php --exclude=application/config/database.php --exclude=medias \
        --exclude=uploads --exclude=orchestra_relation_ok --delete "$CHARMS_PATH/oscied-webui/www/" "$host:$dest/"
      ssh -i "$ID_RSA" "$host" -n "sudo chown www-data:www-data $dest -R"
    fi

    yesOrNo $false "Ask juju to retry setup of $unit"
    if [ $REPLY -eq $true ]; then
      juju resolved --retry "$unit"
    fi
    yesOrNo $false "SSH to unit $unit"
    if [ $REPLY -eq $true ]; then
      juju ssh "$unit"
    fi
    [ $retval -eq 0 ] && pause
  done
  REPLY=$number
}


# Parse charm's units URLs listing file to get specific URLs -----------------------------------------------------------

_get_units_dialog_listing()
{
  REPLY=$(cat "$SCENARIO_GEN_UNITS_FILE" | sort | sed 's:=: :g;s:\n: :g')
  [ ! $REPLY ] && xecho 'Unable to generate units listing for dialog'
}

_get_services_dialog_listing()
{
  REPLY=$(cat "$SCENARIO_GEN_UNITS_FILE" | sort | sed 's:/[0-9]*=: :g;s:\n: :g' | uniq)
  [ ! $REPLY ] && xecho 'Unable to generate services listing for dialog'
}

_get_unit_public_url()
{
  if [ $# -gt 3 ]; then
    xecho "Usage: $(basename $0).get_unit_public_url fail name (number)"
  fi
  fail=$1
  name=$2

  [ $# -eq 3 ] && number=$3 || number='.*'
  if [ -f "$SCENARIO_GEN_UNITS_FILE" ]; then
    url=$(cat "$SCENARIO_GEN_UNITS_FILE" | grep -m 1 "^$name/$number=" | cut -d '=' -f2)
  else
    url='127.0.0.1'
  fi
  [ ! "$url" -a $fail -eq $true ] && xecho "Unable to detect unit $1 public URL !"
  REPLY="$url"
}

# Main menu ============================================================================================================

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

  autoInstall dialog dialog

  mkdir -p "$MEDIAS_PATH" 2>/dev/null

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
    techo 'OSCIED Menu [AUTO]'
    mecho "Operation is $operation_auto"
    eval $operation_auto "$@"
    if [ $ok -eq $false ]; then
      xecho "Unknown operation : $operation_auto"
    fi
  else
    # Initialize main menu
    while true
    do
      a=$(_check_juju 'non mais allô quoi !')
      $DIALOG --backtitle 'OSCIED Menu' \
              --menu 'Please select an operation' 0 0 0 \
              install          'Download / update documents and tools'          \
              cleanup          'Cleanup *.pyc compiled python, deploy path'     \
              deploy           "${a}Launch a deployment scenario"               \
              status           "${a}Display juju status"                        \
              log              "${a}Launch juju debug log in a screen"          \
              browse_webui     "Launch a browser to browse the Web UI"          \
              rsync_orchestra  'Rsync local code to running Orchestra instance' \
              rsync_publisher  'Rsync local code to running Publisher instance' \
              rsync_storage    'Rsync local code to running Storage instance'   \
              rsync_transform  'Rsync local code to running Transform instance' \
              rsync_webui      'Rsync local code to running Web UI instance'    \
              unit_ssh         "${a}Access to units with secure shell"          \
              unit_add         "${a}Add a new unit to a running service"        \
              unit_remove      "${a}Remove an unit from a running service"      \
              destroy          "${a}Destroy a deployed environment" 2> $tmpfile

      retval=$?
      operation=$(cat $tmpfile)

      # Main menu exit door
      [ $retval -ne 0 -o ! "$operation" ] && break

      techo "Execute operation $operation"
      eval $operation

      # Main menu pause
      [ $retval -eq 0 ] && pause
    done
  fi
}

# Operations -----------------------------------------------------------------------------------------------------------

install()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) install"
  fi
  ok=$true

  autoInstall git-core git

  pecho 'Update submodules'
  cd "$BASE_PATH" || xecho "Unable to find path $BASE_PATH"
  git submodule update --init && git submodule status

  pecho 'Install OSCIED Library with prerequisities (takes some time)'
  cd "$LIBRARY_PATH" || xecho "Unable to find path $LIBRARY_PATH"
  $udo "./setup.sh"  || xecho 'Unable to install OSCIED Library'

  pecho 'Install prerequisites'
  addAptPpaRepo ppa:juju/stable juju || xecho 'Unable to add juju PPA repository'
  eval $install --reinstall juju-core juju-local || xecho 'Unable to install JuJu orchestrator'

  pecho 'Fixes #7 - https://github.com/ebu/OSCIED/issues/7'
  $udo sed -i 's:#!/usr/bin/python3.*:#!/usr/bin/python3 -Es:' /usr/bin/lxc-ls
}

cleanup()
{
  rm -rf "$CHARMS_DEPLOY_PATH"
  find "$LIBRARY_PATH" -type d -name 'build'      -exec $udo rm -rf {} 2>/dev/null \;
  find "$LIBRARY_PATH" -type d -name 'dist'       -exec $udo rm -rf {} 2>/dev/null \;
  find "$LIBRARY_PATH" -type d -name "*.egg-info" -exec $udo rm -rf {} 2>/dev/null \;
  find "$LIBRARY_PATH" -type f -name "*.egg"      -exec $udo rm -rf {} 2>/dev/null \;
  find "$BASE_PATH"    -type f -name "*.pyc"      -exec rm -f {} \;
}

deploy()
{
  _check_juju

  if [ $# -eq 1 ]; then
    scenario_auto=$1
  elif [ $# -eq 0 ]; then
    scenario_auto=''
  else
    xecho "Usage: $(basename $0) deploy [scenario]"
  fi
  ok=$true

  [ "$scenario_auto" ] && default=$true_auto || default=$true

  pecho "Download encoders packages into Transform charm's path"
  recho 'This step is required the 1st time or when you want to upgrade them'
  yesOrNo $default 'do it now'
  if [ $REPLY -eq $true ]; then
    path="$CHARMS_PATH/oscied-transform/"
    cd "$path" || xecho "Unable to find path $path"
    ./get-libs.sh || xecho 'Something went wrong'
  fi

  pecho 'Overwrite charms in deployment path'
  recho 'This step is required the 1st time or when the code is modified'
  yesOrNo $default 'do it now'
  if [ $REPLY -eq $true ]; then
    _overwrite_helper 'oscied-orchestra' 'oscied-orchestra'
    _overwrite_helper 'oscied-publisher' 'oscied-publisher'
    _overwrite_helper 'oscied-storage'   'oscied-storage'
    _overwrite_helper 'oscied-transform' 'oscied-transform'
    _overwrite_helper 'oscied-webui'     'oscied-webui'
    _overwrite_helper 'oscied-storage'   "oscied-orchestra/charms/$RELEASE/oscied-storage"
    _overwrite_helper 'oscied-transform' "oscied-orchestra/charms/$RELEASE/oscied-transform"
    _overwrite_helper 'oscied-publisher' "oscied-orchestra/charms/$RELEASE/oscied-publisher"
    _overwrite_helper 'oscied-webui'     "oscied-orchestra/charms/$RELEASE/oscied-webui"
  fi

  cd "$SCENARIOS_PATH" || xecho "Unable to find path $SCENARIOS_PATH"

  if [ "$scenario_auto" ]; then
    techo 'OSCIED Main Menu > Deployment Scenarios [AUTO]'
    _deploy_helper "$scenario_auto"
  else
    pecho 'Initialize scenarios menu'
    current=$(readlink "$SCENARIO_CURRENT_PATH" 2>/dev/null)
    find . -type f -name 'scenario.py' | sort > $listing
    scenariosList=''
    while read scenario
    do
      name=$(dirname "$scenario" | sed 's:\./::')
      description=$(grep 'description = ' "$scenario" | cut -d'=' -f2 | sed "s: *'::g;s: :_:g")
      if [ "$current" -a "$current" = "$name" ]; then
        description="[CURRENT]_$description"
      fi
      scenariosList="$scenariosList$name $description "
    done < $listing
    # Scenarios menu
    pause
    while true
    do
      $DIALOG --backtitle 'OSCIED Main Menu > Deployment Scenarios' \
              --menu 'Please select a deployment scenario' 0 0 0 \
              $scenariosList 2> $tmpfile

      retval=$?
      scenario=$(cat $tmpfile)
      [ $retval -ne 0 -o ! "$scenario" ] && break
      _deploy_helper "$scenario"
      [ $retval -eq 0 ] && pause
    done
  fi
}

status()
{
  _check_juju

  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) status"
  fi
  ok=$true

  techo 'Status of default environment'; juju status
  techo 'Status of amazon environment';  juju status --environment amazon
  techo 'Status of local environment';   juju status --environment local
  techo 'Status of maas environment';    juju status --environment maas
}

log()
{
  _check_juju

  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) log"
  fi
  ok=$true

  screen -dmS juju-log juju debug-log > "$SCENARIO_JUJU_LOG_FILE"
}

browse_webui()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) browse_webui"
  fi
  ok=$true

  _config_helper

  _get_unit_public_url $true 'oscied-webui'
  xdg-open "http://$REPLY"
}

rsync_orchestra()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_orchestra"
  fi
  ok=$true

  _rsync_helper 'oscied-orchestra'
}

rsync_publisher()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_publisher"
  fi
  ok=$true

  _rsync_helper 'oscied-publisher'
}

rsync_storage()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_storage"
  fi
  ok=$true

  chmod 600 "$ID_RSA" || xecho 'Unable to find id_rsa certificate'

  _rsync_helper 'oscied-storage'
}

rsync_transform()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_transform"
  fi
  ok=$true

  _rsync_helper 'oscied-transform'
}

rsync_webui()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_webui"
  fi
  ok=$true

  chmod 600 "$ID_RSA" || xecho 'Unable to find id_rsa certificate'

  _rsync_helper 'oscied-webui'
}

unit_ssh()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) unit_ssh"
  fi
  ok=$true

  _config_helper

  # Initialize remote menu
  unitsList=$(cat "$SCENARIO_GEN_UNITS_FILE" | sort | sed 's:=: :g;s:\n: :g')

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

  _config_helper

  # Initialize add unit menu
  _get_services_dialog_listing
  $DIALOG --backtitle 'OSCIED Operations with JuJu > Scale-up a Service' \
          --menu 'Please select a service' 0 0 0 $REPLY 2> $tmpfile

  retval=$?
  service=$(cat $tmpfile)
  if [ $retval -ne 0 -o ! "$service" ]; then
    recho 'Operation aborted by user'
  else
    juju add-unit "$service"
  fi
}

unit_remove()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) unit_remove"
  fi
  ok=$true

  _config_helper

  # Initialize remove unit menu
  _get_units_dialog_listing
  $DIALOG --backtitle 'OSCIED Operations with JuJu > Scale-down a Service' \
          --menu 'Please select an unit' 0 0 0 $REPLY 2> $tmpfile

  retval=$?
  unit=$(cat $tmpfile)
  if [ $retval -ne 0 -o ! "$unit" ]; then
    recho 'Operation aborted by user'
  else
    if juju remove-unit "$unit"; then
      cat "$SCENARIO_GEN_UNITS_FILE" | grep -v "$1=.*" > $tmpfile
      mv $tmpfile "$SCENARIO_GEN_UNITS_FILE"
    fi
  fi
}

destroy()
{
  _check_juju

  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) destroy"
  fi
  ok=$true

  # Environments menu
  while true
  do
    $DIALOG --backtitle 'OSCIED Menu > Destroy Environment' \
            --menu 'Please select an environment' 0 0 0 \
            'amazon' '-' 'local' '-' 'maas' '-' 2> $tmpfile

    retval=$?
    environment=$(cat $tmpfile)
    [ $retval -ne 0 -o ! "$environment" ] && break
    juju destroy-environment --environment "$environment"
  done
}

main "$@"
