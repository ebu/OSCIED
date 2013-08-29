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
              config           "${a}Update units public URL listing file"       \
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

  pecho 'Import logicielsUbuntu'
  if ! which lu-importUtils > /dev/null; then
    cd "$TOOLS_PATH/logicielsUbuntu" || xecho "Unable to find path $TOOLS_PATH/logicielsUbuntu"
    sh ./logicielsUbuntuExports || xecho 'Unable to export logicielsUbuntu'
    recho 'Please restart this script once from a new terminal'
    recho 'or after having executed the following:'
    cecho 'source ~/.bashrc'
    pause
    exit 0
  else
    cd "$SCRIPTS_PATH" || xecho "Unable to find path $SCRIPTS_PATH"
    lu-importUtils .   || xecho 'Unable to import utilities of logicielsUbuntu'
  fi

  cd "$LIBRARY_PATH" || xecho "Unable to find path $LIBRARY_PATH"
  $udo "./setup.sh"  || xecho 'Unable to install OSCIED Library'

  pecho 'Install prerequisites'
  eval $install bzr default-jre imagemagick rst2pdf texlive-latex-recommended texlive-latex-extra \
    texlive-fonts-recommended || xecho 'Unable to install packages'
  $udo pip install --upgrade sphinx sphinxcontrib-email sphinxcontrib-googlechart sphinxcontrib-httpdomain || \
    xecho 'Unable to install sphinx python packages'
  $udo easy_install rednose || xecho 'Unable to install rednose python package' # NEVER install it with pip ;-)

  pecho 'Download references'
  cd "$REFERENCES_PATH"|| xecho "Unable to find path $REFERENCES_PATH"
  openstack='http://docs.openstack.org'
  wget -N $openstack/trunk/openstack-compute/install/apt/openstack-install-guide-apt-trunk.pdf
  wget -N $openstack/api/openstack-compute/programmer/openstackapi-programming.pdf
  wget -N $openstack/folsom/openstack-compute/admin/bk-compute-adminguide-folsom.pdf
  wget -N $openstack/folsom/openstack-network/admin/bk-quantum-admin-guide-folsom.pdf
  wget -N $openstack/folsom/openstack-object-storage/admin/os-objectstorage-adminguide-folsom.pdf

  pecho 'Download tools'

  cd "$TOOLS_PATH"|| xecho "Unable to find path $TOOLS_PATH"
  clonezilla='http://switch.dl.sourceforge.net/project/clonezilla'
  wget -N $clonezilla/clonezilla_live_stable/2.1.1-25/clonezilla-live-2.1.1-25-amd64.zip

  if [ -d 'juju-core-source' ]; then cd 'juju-core-source' && bzr merge && cd ..
  else bzr branch lp:juju-core 'juju-core-source'
  fi

  addAptPpaRepo ppa:juju/stable juju || xecho 'Unable to add juju PPA repository'
  eval $install --reinstall juju-core juju-local || xecho 'Unable to install JuJu orchestrator'

  #cat \
  # /var/lib/apt/lists/ppa.launchpad.net_juju_pkgs_ubuntu_dists_quantal_main_binary-amd64_Packages \
  # | grep Package
  #Package: python-txzookeeper
  #Package: ...

  plantuml=http://downloads.sourceforge.net/project/plantuml
  wget -N $plantuml/plantuml.jar
  wget -N $plantuml/PlantUML%20Language%20Reference%20Guide.pdf

  if cd "$TOOLS_PATH/rabbitmq-tutorials"; then
    readLine 'Please enter local RabbitMQ guest user password [default=guest]'
    [ "$CHOICE" ] && pass=$CHOICE || pass='guest'
    a='amqp://.*localhost/'
    b="amqp://guest:$pass@localhost/"
    find . -type f -exec sed -i "s#$a#$b#g" {} \;
    git status
  else
    recho 'Unable to find RabbitMQ tutorials path'
  fi

  pecho 'Fixes bitbucket.org/birkenfeld/sphinx/pull-request/98/fixes-typeerror-raised-from/diff'
  $udo find /usr/local/lib/ -type f -name latex.py -path "*/sphinx/writers/*" -exec \
    sed -i 's:letter.translate(tex_escape_map)):unicode(letter).translate(tex_escape_map)):g' {} \;

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

  pecho 'Overwrite charms in deployment path'
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
    lu-importUtils "$CHARMS_DEPLOY_PATH"
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

config()
{
  _check_juju

  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) config"
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
  [ ! "$REPLY" ] && return

  _get_unit_public_url $true 'oscied-webui' "$REPLY"
  host="ubuntu@$REPLY"
  dest='/var/www'
  ssh -i "$ID_RSA" "$host" -n "sudo chown 1000:1000 $dest -R"
  rsync -avh --progress -e "ssh -i '$ID_RSA'" --exclude=.git --exclude=.htaccess \
    --exclude=application/config/config.php --exclude=application/config/database.php --exclude=medias \
    --exclude=uploads --exclude=orchestra_relation_ok --delete "$CHARMS_PATH/oscied-webui/www/" "$host:$dest/"
  ssh -i "$ID_RSA" "$host" -n "sudo chown www-data:www-data $dest -R"
}

unit_ssh()
{
  _check_juju

  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) unit_ssh"
  fi
  ok=$true

  yesOrNo $true 'Update units listing'
  [ $REPLY -eq $true ] && config

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
  _check_juju

  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) unit_add"
  fi
  ok=$true

  yesOrNo $true 'Update units listing'
  [ $REPLY -eq $true ] && config

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
  _check_juju

  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) unit_remove"
  fi
  ok=$true

  yesOrNo $true 'Update units listing'
  [ $REPLY -eq $true ] && config

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
