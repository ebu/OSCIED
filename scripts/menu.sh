#!/usr/bin/env bash

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
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

. ./common.sh

RSYNC_UNIT_ID='0'  # FIXME temporary hack to avoid coding 10's lines of code

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

  get_root_secret;   ROOT_AUTH="root:$REPLY"
  get_node_secret;   NODE_AUTH="node:$REPLY"
  get_orchestra_url; ORCHESTRA_URL=$REPLY

  mkdir -p "$MEDIAS_PATH" 2>/dev/null

  listing=/tmp/$$.list
  tmpfile=/tmp/$$
  trap "rm -f '$listing' '$tmpfile' 2>/dev/null" INT TERM EXIT

  if [ "$operation_auto" ]; then
    ok=$false
    techo 'OSCIED General Operations [AUTO]'
    mecho "Operation is $operation_auto"
    eval $operation_auto "$@"
    if [ $ok -eq $false ]; then
      xecho "Unknown operation : $operation_auto"
    fi
  else
    # Initialize main menu
    while true
    do
      [ "$ORCHESTRA_URL" ] && a='' || a='[DISABLED] '
      $DIALOG --backtitle 'OSCIED General Operations' \
              --menu 'Please select an operation' 0 0 0 \
              install              'Download / update documents and tools'               \
              cleanup              'Cleanup configuration of charms (deploy path)'       \
              api_init_setup       "${a}Initialize demo setup with Orchestra API"        \
              rsync_orchestra      'Rsync local code to running Orchestra instance'      \
              rsync_publisher      'Rsync local code to running Publisher instance'      \
              rsync_storage        'Rsync local code to running Storage instance'        \
              rsync_transform      'Rsync local code to running Transform instance'      \
              rsync_webui          'Rsync local code to running Web UI instance' 2> $tmpfile

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

install()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) install"
  fi
  ok=$true

  autoInstall git-core git

  pecho 'Update submodules'
  cd "$BASE_PATH" || xecho "Unable to find path $BASE_PATH"
  git submodule init && git submodule update && git submodule status

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
  eval $install bzr rst2pdf texlive-latex-recommended texlive-latex-extra \
    texlive-fonts-recommended || xecho 'Unable to install packages'
  $udo pip install --upgrade coverage docutils nose pygments rednose sphinx sphinxcontrib-email \
    sphinxcontrib-googlechart sphinxcontrib-httpdomain || xecho 'Unable to install python packages'

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

  if [ -d 'juju-source' ]; then cd 'juju-source' && bzr merge && cd ..
  else bzr branch lp:juju 'juju-source'
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
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) cleanup"
  fi
  ok=$true

  cd "$CHARMS_DEPLOY_PATH" || xecho "Unable to find path $CHARMS_DEPLOY_PATH"
  git reset --hard  # Revert changes to modified files
  git clean -fd     # Remove all untracked files and directories
}

api_init_setup()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) api_init_setup"
  fi
  ok=$true

  [ "$ORCHESTRA_URL" ] || xecho 'No orchestrator found, this method is disabled'
  [ "$STORAGE_PRIVATE_IP" -a "$STORAGE_MOUNTPOINT" -a "$STORAGE_BRICK" ] || \
    xecho 'You must execute juju-menu.sh config first'

  pecho 'Flush database'
  yesOrNo $false "do you really want to flush orchestrator $ORCHESTRA_URL"
  if [ $REPLY -eq $false ]; then
    recho 'operation aborted by user'
    exit 0
  fi
  test_api 200 POST $ORCHESTRA_URL/flush "$ROOT_AUTH" ''

  pecho 'Add users'
  count=1
  savedIFS=$IFS
  IFS=';'
  while read fname lname mail secret aplatform
  do
    if [ ! "$fname" -o ! "$lname" -o ! "$mail" -o ! "$secret" -o ! "$aplatform" ]; then
      xecho "Line $count : Bad line format !"
    fi
    json_user "$fname" "$lname" "$mail" "$secret" "$aplatform"
    echo "$JSON"
    test_api 200 POST $ORCHESTRA_URL/user "$ROOT_AUTH" "$JSON"
    save_auth "user$count" "$mail:$secret"
    save_json "user$count" "$JSON"
    save_id   "user$count" "$ID"
    count=$((count+1))
  done < "$SCENARIO_API_USERS_FILE"
  IFS=$savedIFS

  get_auth 'user1'; user1_auth=$REPLY

  pecho 'Add medias'
  count=1
  savedIFS=$IFS
  IFS=';'
  while read uri vfilename title
  do
    if [ ! "$uri" -o ! "$vfilename" -o ! "$title" ]; then
      xecho "Line $count : Bad line format !"
    fi
    media="$MEDIAS_PATH/$uri"
    if [ ! -f "$media" ]; then
      recho "[WARNING] Unable to find media file $media"
      continue
    fi
    mecho "Uploading media $uri to uploads into shared storage unit ..."
    storage_upload_media "$media" || xecho "Unable to upload media"
    json_media "$REPLY" "$vfilename" "$title"
    echo "$JSON"
    test_api 200 POST $ORCHESTRA_URL/media "$user1_auth" "$JSON"
    save_json "media$count" "$JSON"
    save_id   "media$count" "$ID"
    count=$((count+1))
  done < "$SCENARIO_API_MEDIAS_FILE"
  IFS=$savedIFS

  pecho 'Add transform profiles'
  count=1
  savedIFS=$IFS
  IFS=';'
  while read title description encoder_name encoder_string
  do
    if [ ! "$title" -o ! "$description" -o ! "encoder_name" -o ! "$encoder_string" ]; then
      xecho "Line $count : Bad line format !"
    fi
    json_tprofile "$title" "$description" "$encoder_name" "$encoder_string"
    echo "$JSON"
    test_api 200 POST $ORCHESTRA_URL/transform/profile "$user1_auth" "$JSON"
    save_json "tprofile$count" "$JSON"
    save_id   "tprofile$count" "$ID"
    count=$((count+1))
  done < "$SCENARIO_API_TPROFILES_FILE"
  IFS=$savedIFS

  #pecho 'Add medias'
  #$udo mkdir -p /mnt/storage/medias /mnt/storage/uploads
  #$udo cp "$SCRIPTS_PATH/common.sh" /mnt/storage/uploads/tabby.mpg
  #test_api 200 POST $ORCHESTRA_URL/media "$admin_auth" "$media1_json"; save_id 'media1' "$ID"
}

rsync_helper()
{
  if [ $# -ne 2 ]; then
    xecho "Usage: $(basename $0).rsync_publisher charm id"
  fi

  chmod 600 "$ID_RSA" || xecho 'Unable to find id_rsa certificate'

  get_unit_public_url $true "$1" "$2"
  host="ubuntu@$REPLY"
  dest="/var/lib/juju/agents/unit-$1-$2/charm"
  ssh -i "$ID_RSA" "$host" -n "sudo chown 1000:1000 $dest -R"
  rsync -avhL --progress --delete -e "ssh -i '$ID_RSA'" --exclude=.git --exclude=config.json \
    --exclude=celeryconfig.py --exclude=*.pyc --exclude=local_config.pkl --exclude=charms \
    --exclude=ssh --exclude=environments.yaml --exclude=*.log "$CHARMS_PATH/$1/" "$host:$dest/"
  ssh -i "$ID_RSA" "$host" -n "sudo chown root:root $dest -R"
}

rsync_orchestra()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_orchestra"
  fi
  ok=$true

  rsync_helper 'oscied-orchestra' "$RSYNC_UNIT_ID"
}

rsync_publisher()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_publisher"
  fi
  ok=$true

  rsync_helper 'oscied-publisher' "$RSYNC_UNIT_ID"
}

rsync_storage()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_storage"
  fi
  ok=$true

  chmod 600 "$ID_RSA" || xecho 'Unable to find id_rsa certificate'

  rsync_helper 'oscied-storage' "$RSYNC_UNIT_ID"
}

rsync_transform()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_transform"
  fi
  ok=$true

  rsync_helper 'oscied-transform' "$RSYNC_UNIT_ID"
}

rsync_webui()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_webui"
  fi
  ok=$true

  chmod 600 "$ID_RSA" || xecho 'Unable to find id_rsa certificate'

  rsync_helper 'oscied-webui' "$RSYNC_UNIT_ID"

  get_unit_public_url $true 'oscied-webui' "$RSYNC_UNIT_ID"
  host="ubuntu@$REPLY"
  dest='/var/www'
  ssh -i "$ID_RSA" "$host" -n "sudo chown 1000:1000 $dest -R"
  rsync -avh --progress -e "ssh -i '$ID_RSA'" --exclude=.git --exclude=.htaccess \
    --exclude=application/config/config.php --exclude=application/config/database.php \
    --exclude=medias --exclude=uploads --exclude=orchestra_relation_ok --delete \
    "$CHARMS_PATH/oscied-webui/www/" "$host:$dest/"
  ssh -i "$ID_RSA" "$host" -n "sudo chown www-data:www-data $dest -R"
}

main "$@"
