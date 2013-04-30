#!/usr/bin/env bash

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : ORCHESTRA
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
# Retrieved from:
#   svn co https://claire-et-david.dyndns.org/prog/OSCIED

set -o nounset # will exit if an unitialized variable is used

# Constants ========================================================================================

ECHO='juju-log' # Used by logicielsUbuntuUtils
RELEASE=$(lsb_release -cs)
JUJU_CHARMS_SVN='https://claire-et-david.dyndns.org/prog/OSCIED/components'

# Charms paths
BASE_PATH=$(pwd)

# Charms files
CONFIG_FILE="$BASE_PATH/config.json"
CELERY_TEMPL_FILE="$BASE_PATH/templates/celeryconfig.py.template"
CELERY_CONFIG_FILE="$BASE_PATH/celeryconfig.py"
JUJU_TEMPL_FILE="$BASE_PATH/templates/environments.yaml.template"
REPOS_CERTIF_FILE="$BASE_PATH/templates/99a9179b9106d19d4e1cca7a720b079a"

# Shared storage paths
STORAGE_ROOT_PATH='/mnt/storage'
STORAGE_MEDIAS_PATH="$STORAGE_ROOT_PATH/medias"
STORAGE_UPLOADS_PATH="$STORAGE_ROOT_PATH/uploads"

# JuJu, ssh & subversion paths
HOME_PATH='/root'
CHARMS_PATH="$HOME_PATH/charms"
PUBLISHER_PATH="$CHARMS_PATH/$RELEASE/oscied-publisher"
TRANSFORM_PATH="$CHARMS_PATH/$RELEASE/oscied-transform"
WEBUI_PATH="$CHARMS_PATH/$RELEASE/oscied-webui"
JUJU_STORAGE_PATH="$HOME_PATH/.juju/storage"
SVN_CERTIFS_PATH="$HOME_PATH/.subversion/auth/svn.ssl.server"

# JuJu, ssh & subversion files
CERTIF_FILE="$HOME_PATH/.ssh/id_rsa"
JUJU_ENVS_FILE="$HOME_PATH/.juju/environments.yaml"
SVN_SERVERS_FILE='/etc/subversion/servers'

# MongoDB configuration files
MONGO_CONFIG_FILE='/etc/mongodb.conf'

# Configuration ====================================================================================

if [ "$(config-get verbose)" = 'true' ] ; then
  VERBOSE=0     # true
  set -o xtrace # for verbose logging to juju debug-log
else
  VERBOSE=1 # false
fi

OWN_IP=$(unit-get private-address)
API_URL="http://$OWN_IP:5000"
API_LOCAL_URL="http://127.0.0.1:5000"
ROOT_SECRET=$(config-get root_secret)
NODES_SECRET=$(config-get nodes_secret)
REPOS_USER=$(config-get repositories_user)
REPOS_PASS=$(config-get repositories_pass)

WEBUI_REPO=$(config-get webui_repository)
TRANSFORM_REPO=$(config-get transform_repository)
PUBLISHER_REPO=$(config-get publisher_repository)

MONGO_ADMIN_PASSWORD=$(config-get mongo_admin_password)
MONGO_NODES_PASSWORD=$(config-get mongo_nodes_password)
RABBIT_PASSWORD=$(config-get rabbit_password)

STORAGE_IP=$(config-get storage_ip)
STORAGE_NAT_IP=$(config-get storage_nat_ip)
STORAGE_FSTYPE=$(config-get storage_fstype)
STORAGE_MOUNTPOINT=$(config-get storage_mountpoint)
STORAGE_OPTIONS=$(config-get storage_options)

mongo_admin_connection()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0).mongo_admin_connection IP"
  fi
  echo "mongodb://admin:$MONGO_ADMIN_PASSWORD@$1:27017/orchestra"
}

mongo_nodes_connection()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0).mongo_nodes_connection IP"
  fi
  echo "mongodb://nodes:$MONGO_NODES_PASSWORD@$1:27017/celery"
}

rabbit_connection()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0).rabbit_connection IP"
  fi
  echo "amqp://nodes:$RABBIT_PASSWORD@$1:5672/celery"
}

# Utilities ========================================================================================

storage_config_is_enabled()
{
  [ "$STORAGE_IP" -a "$STORAGE_FSTYPE" -a "$STORAGE_MOUNTPOINT" ]
}

storage_is_mounted()
{
  mount | grep -q "$STORAGE_ROOT_PATH"
}

storage_remount()
{
  # Overrides storage parameters with charm configuration
  if storage_config_is_enabled; then # if storage options are set
    ip=$STORAGE_IP
    nat_ip=$STORAGE_NAT_IP
    fstype=$STORAGE_FSTYPE
    mountpoint=$STORAGE_MOUNTPOINT
    options=$STORAGE_OPTIONS
  # Or uses storage parameters from charm storage relation
  elif [ $# -eq 4 ]; then # if function parameters are set
    ip=$1
    nat_ip=''
    fstype=$2
    mountpoint=$3
    options=$4
  elif [ $# -eq 0 ]; then
    return
  else
    xecho "Usage: $(basename $0).storage_remount ip fstype mountpoint options"
  fi

  if [ "$nat_ip" ]; then
    pecho "Update hosts file to map storage internal address $ip to $nat_ip"
    if grep -q "$ip" /etc/hosts; then
      sed -i "s<$nat_ip .*<$nat_ip $ip<" /etc/hosts
    else
      echo "$nat_ip $ip" >> /etc/hosts
    fi
  else
    nat_ip=$ip
  fi

  storage_umount

  r=$STORAGE_ROOT_PATH
  pecho "Mount shared storage [$nat_ip] $ip:$mountpoint type $fstype options '$options' -> $r"
  if [ ! -d "$STORAGE_ROOT_PATH" ]; then
    mkdir "$STORAGE_ROOT_PATH" || xecho "Unable to create shared storage path $STORAGE_ROOT_PATH" 1
  fi

  # FIXME try 5 times, a better way to handle failure
  for i in $(seq 1 5)
  do
    if storage_is_mounted; then
      break
    else
      if [ "$options" ]
      then mount -t "$fstype" -o "$options" "$nat_ip:$mountpoint" "$STORAGE_ROOT_PATH"
      else mount -t "$fstype"               "$nat_ip:$mountpoint" "$STORAGE_ROOT_PATH"
      fi
    fi
    sleep 5
  done

  if storage_is_mounted; then
    # FIXME update /etc/fstab (?)
    pecho 'Configure Orchestra : Register shared storage'
    setSettingJSON_STRING "$CONFIG_FILE" 'storage_ip'         "$ip"         || xecho 'Config' 2
    setSettingJSON_STRING "$CONFIG_FILE" 'storage_fstype'     "$fstype"     || xecho 'Config' 3
    setSettingJSON_STRING "$CONFIG_FILE" 'storage_mountpoint' "$mountpoint" || xecho 'Config' 4
    setSettingJSON_STRING "$CONFIG_FILE" 'storage_options'    "$options"    || xecho 'Config' 5
  else
    xecho 'Unable to mount shared storage' 6
  fi
}

storage_umount()
{
  pecho 'Configure Orchestra : Unregister shared storage'
  setSettingJSON_STRING "$CONFIG_FILE" 'storage_ip'         '' || xecho 'Config' 1
  setSettingJSON_STRING "$CONFIG_FILE" 'storage_fstype'     '' || xecho 'Config' 2
  setSettingJSON_STRING "$CONFIG_FILE" 'storage_mountpoint' '' || xecho 'Config' 3
  setSettingJSON_STRING "$CONFIG_FILE" 'storage_options'    '' || xecho 'Config' 4

  if storage_is_mounted; then
    # FIXME update /etc/fstab (?)
    pecho 'Unmount shared storage (is actually mounted)'
    umount "$STORAGE_ROOT_PATH" || xecho 'Unable to unmount shared storage' 5
    recho 'Shared storage successfully unmounted'
  else
    recho 'Shared storage already unmounted'
  fi
}

storage_hook_bypass()
{
  if storage_config_is_enabled; then
    xecho 'Shared storage is set in config, storage relation is disabled' 1
  fi
}

config_rabbitmq()
{
  pecho 'Configure RabbitMQ Message Broker'
  rabbitmqctl delete_user     guest
  rabbitmqctl delete_vhost    /
  rabbitmqctl add_user        nodes "$RABBIT_PASSWORD"
  rabbitmqctl add_vhost       celery
  rabbitmqctl set_permissions -p celery nodes ".*" ".*" ".*"
  if ! rabbitmqctl list_users | grep -q 'nodes'; then
    xecho 'Unable to add RabbitMQ user' 4
  fi
  if ! rabbitmqctl list_vhosts | grep -q 'celery'; then
    xecho 'Unable to add RabbitMQ vhost' 5
  fi
}

# HOOKS : Charm Setup ==============================================================================

hook_install()
{
  techo 'Orchestrator - install'

  # Fix memtest86+ : https://bugs.launchpad.net/ubuntu/+source/grub2/+bug/1069856
  #eval $purge grub-pc grub-common
  #eval $install grub-common grub-pc

  # I decidec to use the real ffmpeg, not the libav version :
  # http://blog.pkh.me/p/13-the-ffmpeg-libav-situation.html
  # http://doc.ubuntu-fr.org/ffmpeg
  apt-add-repository -y ppa:jon-severinsson/ffmpeg || xecho 'Unable to add FFmpeg repository' 1
  #apt-add-repository -y ppa:juju/pkgs || xecho 'Unable to add JuJu PPA repository' 2
  eval $update
  eval $upgrade

  pecho 'Install and configure Network Time Protocol'
  eval $install ntp || xecho 'Unable to install ntp' 3
  eval $service ntp restart || xecho 'Unable to restart ntp service' 4

  #pecho 'Checkout OSCIED charms locally'
  #eval $install subversion || xecho 'Unable to install packages' 5
  #setSettingBASH "$SVN_SERVERS_FILE" $true 'store-passwords'                    'yes' || exit 6
  #setSettingBASH "$SVN_SERVERS_FILE" $true 'store-plaintext-passwords'          'yes' || exit 7
  #setSettingBASH "$SVN_SERVERS_FILE" $true 'store-ssl-client-cert-pp'           'yes' || exit 8
  #setSettingBASH "$SVN_SERVERS_FILE" $true 'store-ssl-client-cert-pp-plaintext' 'yes' || exit 9
  #mkdir -p "$SVN_CERTIFS_PATH"; cp -f "$REPOS_CERTIF_FILE" "$SVN_CERTIFS_PATH/"
  #checkout "$WEBUI_REPO"     "$WEBUI_PATH"     "$REPOS_USER" "$REPOS_PASS" || exit 10
  #checkout "$TRANSFORM_REPO" "$TRANSFORM_PATH" "$REPOS_USER" "$REPOS_PASS" || exit 11
  #checkout "$PUBLISHER_REPO" "$PUBLISHER_PATH" "$REPOS_USER" "$REPOS_PASS" || exit 12

  pecho 'Install (the real) FFmpeg and x264'
  #pecho 'Install JuJu Cloud Orchestrator, (the real) FFmpeg and x264'
  #eval $install apt-cacher-ng charm-tools juju libzookeeper-java zookeeper ffmpeg x264 || \
  eval $install ffmpeg x264 || xecho 'Unable to install packages' 5

  pecho 'Install python, MongoDB Scalable NoSQL DB, RabbitMQ Message Broker and Gluster Filesystem'
  eval $install build-essential python-dev python python-pip git-core mongodb rabbitmq-server \
    glusterfs-client nfs-common || xecho 'Unable to install packages' 6

  pecho 'Install BSON, Celery Distrib. Task Queue, Flask Python Web Framework, PyMongo MongoDB API'
  pip install --upgrade bson celery flask ipaddr pymongo requests || \
    xecho 'Unable to install packages' 7

  pecho 'Expose RESTful API, MongoDB & RabbitMQ service'
  open-port 5000/tcp   # Orchestra RESTful API
  open-port 27017/tcp  # MongoDB portmongod and mongos instances
  #open-port 27018/tcp # MongoDB port when running with shardsvr setting
  #open-port 27019/tcp # MongoDB port when running with configsvr setting
  open-port 28017/tcp  # MongoDB port for the web status page. This is always +1000
  open-port 5672/tcp   # RabbitMQ service

  # FIXME this call is not necessary, but config-changed create an infinite loop, so WE call it
  hook_config_changed
}

hook_uninstall()
{
  techo 'Orchestrator - uninstall'

  hook_stop

  # fix rabbitmq-server package uninstall error
  mkdir /var/log/rabbitmq 2>/dev/null

  juju destroy-environment
  eval $purge apt-cacher-ng charm-tools juju libzookeeper-java lxc zookeeper
  eval $purge mongodb rabbitmq-server glusterfs-client nfs-common
  pip install uninstall bson flask celery
  eval $autoremove
  rm -rf $HOME/.juju $HOME/.ssh/id_rsa*
  rm -rf /etc/rabbitmq/ /var/log/rabbitmq/
}

hook_config_changed()
{
  techo 'Orchestrator - config changed'

  pecho 'Configure MongoDB Scalable NoSQL DB'

  echo "db.addUser('admin', '$MONGO_ADMIN_PASSWORD', false);" > f.js
  mongo f.js; mongo 'orchestra' f.js
  rm -f f.js

  echo "db.addUser('nodes', '$MONGO_NODES_PASSWORD', false);" > g.js
  mongo 'celery' g.js
  rm -f g.js

  setSettingBASH "$MONGO_CONFIG_FILE" $true 'bind_ip' '0.0.0.0' || xecho 'Config' 1
  setSettingBASH "$MONGO_CONFIG_FILE" $true 'noauth'  'false'   || xecho 'Config' 2
  setSettingBASH "$MONGO_CONFIG_FILE" $true 'auth'    'true'    || xecho 'Config' 3

  config_rabbitmq

  hook_stop

  pecho 'Configure Orchestra the Orchestrator'
  mongo=$(mongo_admin_connection 'localhost')
  rabbit=$(rabbit_connection 'localhost')
  mecho "MongoDB connection is $mongo, RabbitMQ connection is $rabbit"
  if [ ! "$mongo" -o ! "$rabbit" ]; then
    xecho 'Unable to detect MongoDB or RabbitMQ connection' 5
  fi
  setSettingJSON_BOOLEAN "$CONFIG_FILE" 'verbose'           "$VERBOSE"          || xecho 'Config' 6
  setSettingJSON_STRING  "$CONFIG_FILE" 'api_url'           "$API_URL"          || xecho 'Config' 7
  setSettingJSON_STRING  "$CONFIG_FILE" 'root_secret'       "$ROOT_SECRET"      || xecho 'Config' 8
  setSettingJSON_STRING  "$CONFIG_FILE" 'nodes_secret'      "$NODES_SECRET"     || xecho 'Config' 9
  setSettingJSON_STRING  "$CONFIG_FILE" 'mongo_connection'  "$mongo"            || xecho 'Config' 10
  setSettingJSON_STRING  "$CONFIG_FILE" 'rabbit_connection' "$rabbit"           || xecho 'Config' 11
  setSettingJSON_STRING  "$CONFIG_FILE" 'storage_path'     "$STORAGE_ROOT_PATH" || xecho 'Config' 12
  sed "s<RABBIT_CONNECTION<$rabbit<g;s<MONGO_PASSWORD<$MONGO_NODES_PASSWORD<g" \
    < "$CELERY_TEMPL_FILE" > "$CELERY_CONFIG_FILE" || xecho 'Config' 13

  storage_remount

  hook_start
  # FIXME infinite loop is used as config-changed hook !
}

# HOOKS : Charm Service ============================================================================

hook_start()
{
  techo 'Orchestrator - start'

  if ! storage_is_mounted; then
    recho 'WARNING: No shared storage, Orchestra may not start'
  fi

  # do not check status after all, orchestra can do it for us !
  service mongodb         start
  service rabbitmq-server start

  # FIXME this is not a good idea, but I have some trouble with precise release (see ticket #205)
  config_rabbitmq

  if ! curl -s "$API_LOCAL_URL" > /dev/null; then
    screen -dmS 'Orchestra' python orchestra.py
    sleep 5
    if ! curl -s "$API_LOCAL_URL" > /dev/null; then
      # FIXME mail to very important people
      recho 'Orchestra is not ready'
    else
      recho 'Orchestra successfully started'
    fi
  fi
}

hook_stop()
{
  techo 'Orchestrator - stop'

  if curl -s "$API_LOCAL_URL" > /dev/null; then
    screen -X -S 'Orchestra' quit || xecho 'Unable to stop Orchestra daemon' 1
  fi
  service rabbitmq-server stop || xecho 'Unable to stop RabbitMQ' 2
  if ! service mongodb status | grep -q 'stop'; then
    service mongodb stop || xecho 'Unable to stop MongoDB' 3
  fi
}

# HOOKS : Requires Storage =========================================================================

hook_storage_relation_joined()
{
  techo 'Orchestra - storage relation joined'

  storage_hook_bypass
}

hook_storage_relation_changed()
{
  techo 'Orchestra - storage relation changed'

  storage_hook_bypass

  # Get configuration from the relation
  ip=$(relation-get private-address)
  fstype=$(relation-get fstype)
  mountpoint=$(relation-get mountpoint)
  options=$(relation-get options)

  mecho "Storage IP is $ip, fstype: $fstype, mountpoint: $mountpoint, options: $options"
  if [ ! "$ip" -o ! "$fstype" -o ! "$mountpoint" ]; then
    recho 'Waiting for complete setup'
    exit 0
  fi

  hook_stop
  storage_remount "$ip" "$fstype" "$mountpoint" "$options"
  hook_start
}

hook_storage_relation_broken()
{
  techo 'Orchestra - storage relation broken'

  storage_hook_bypass

  hook_stop
  storage_umount
}

# HOOKS : Provides API =============================================================================

hook_api_relation_joined()
{
  techo 'Orchestrator - api relation joined'

  # Send Orchestra API URL
  relation-set "api_url=$API_URL"
}

hook_api_relation_changed()
{
  techo 'Orchestrator - api relation changed'

  # Get configuration from the relation
  webui_ip=$(relation-get private-address)

  mecho "Web UI IP is $webui_ip"
  if [ ! "$webui_ip" ]; then
    recho 'Waiting for complete setup'
    exit 0
  fi

  # FIXME something to do (register unit ?)
}

# HOOKS : Provides Publisher =======================================================================

hook_publisher_relation_joined()
{
  techo 'Orchestrator - publisher relation joined'

  # Send MongoDB & RabbitMQ connections
  mongo=$(mongo_nodes_connection "$OWN_IP")
  rabbit=$(rabbit_connection "$OWN_IP")
  mecho "MongoDB connection is $mongo, RabbitMQ connection is $rabbit"
  if [ ! "$mongo" -o ! "$rabbit" ]; then
    xecho 'Unable to detect MongoDB or RabbitMQ connection'
  fi
  relation-set "mongo_connection=$mongo" "rabbit_connection=$rabbit"
}

hook_publisher_relation_changed()
{
  techo 'Orchestrator - publisher relation changed'

  # Get configuration from the relation
  publisher_ip=$(relation-get private-address)

  mecho "Publisher IP is $publisher_ip"
  if [ ! "$publisher_ip" ]; then
    recho 'Waiting for complete setup'
    exit 0
  fi

  # FIXME something to do (register unit ?)
}

# HOOKS : Provides Transform Relation ==============================================================

hook_transform_relation_joined()
{
  techo 'Orchestrator - transform relation joined'

  # Send MongoDB & RabbitMQ connections
  mongo=$(mongo_nodes_connection "$OWN_IP")
  rabbit=$(rabbit_connection "$OWN_IP")
  mecho "MongoDB connection is $mongo, RabbitMQ connection is $rabbit"
  if [ ! "$mongo" -o ! "$rabbit" ]; then
    xecho 'Unable to detect MongoDB or RabbitMQ connection'
  fi
  relation-set "mongo_connection=$mongo" "rabbit_connection=$rabbit"
}

hook_transform_relation_changed()
{
  techo 'Orchestrator - transform relation changed'

  # Get configuration from the relation
  transform_ip=$(relation-get private-address)

  mecho "Transform IP is $transform_ip"
  if [ ! "$transform_ip" ]; then
    recho 'Waiting for complete setup'
    exit 0
  fi

  # FIXME something to do (register unit ?)
}
# START OF LOGICIELS UBUNTU UTILS (licencing : LogicielsUbuntu project's licence)
# Retrieved from:
#   git clone https://github.com/davidfischer-ch/logicielsUbuntu.git

# Prevent importing N times the following (like C++ .h : #ifndef ... #endif)
if ! logicielsUbuntuUtilsImported 2>/dev/null; then

# Colored echoes and yes/no question ===============================================================

true=0
false=1
true_auto=2
false_auto=3

if [ -t 0 ]; then
  TXT_BLD=$(tput bold)
  TXT_BLK=$(tput setaf 0)
  TXT_RED=$(tput setaf 1)
  TXT_GREEN=$(tput setaf 2)
  TXT_YLW=$(tput setaf 3)
  TXT_BLUE=$(tput setaf 4)
  TXT_PURPLE=$(tput setaf 5)
  TXT_CYAN=$(tput setaf 6)
  TXT_WHITE=$(tput setaf 7)
  TXT_RESET=$(tput sgr0)

  TECHO_COLOR=$TXT_GREEN
  PECHO_COLOR=$TXT_BLUE
  MECHO_COLOR=$TXT_YLW
  CECHO_COLOR=$TXT_YLW
  RECHO_COLOR=$TXT_PURPLE
  QECHO_COLOR=$TXT_CYAN
  XECHO_COLOR=$TXT_RED
else
  TXT_BLD=''
  TXT_BLK=''
  TXT_RED=''
  TXT_GREEN=''
  TXT_YLW=''
  TXT_BLUE=''
  TXT_PURPLE=''
  TXT_CYAN=''
  TXT_WHITE=''
  TXT_RESET=''

  TECHO_COLOR='[TITLE] '
  PECHO_COLOR='[PARAGRAPH] '
  MECHO_COLOR='[MESSAGE] '
  CECHO_COLOR='[CODE] '
  RECHO_COLOR='[REMARK] '
  QECHO_COLOR='[QUESTION] '
  XECHO_COLOR=''
fi

if echo "\n" | grep -q 'n'
then e_='-e'
else e_=''
fi

# By default output utility is the well known echo, but you can use juju-log with ECHO='juju-log'
echo=${ECHO:=echo}

# Disable echo extra parameter if output utility is not echo
[ "$echo" != 'echo' ] && e_=''

#if [ -z $DISPLAY ]
#then DIALOG=dialog
#else DIALOG=Xdialog
#fi
DIALOG=dialog

techo() { $echo $e_ "$TECHO_COLOR$TXT_BLD$1$TXT_RESET"; } # script title
pecho() { $echo $e_ "$PECHO_COLOR$1$TXT_RESET";         } # text title
mecho() { $echo $e_ "$MECHO_COLOR$1$TXT_RESET";         } # message (text)
cecho() { $echo $e_ "$CECHO_COLOR> $1$TXT_RESET";       } # message (code)
recho() { $echo $e_ "$RECHO_COLOR$1 !$TXT_RESET";       } # message (remark)
qecho() { $echo $e_ "$QECHO_COLOR$1 ?$TXT_RESET";       } # message (question)
becho() { $echo $e_ "$TXT_RESET$1";                     } # message (reset)

xecho() # message (error)
{
  [ $# -gt 1 ] && code=$2 || code=1
  $echo $e_ "${XECHO_COLOR}[ERROR] $1 (code $code)$TXT_RESET" >&2
  pause
  exit $code
}

pause() # menu pause
{
  [ ! -t 0 ] && return # skip if non interactive
  $echo $e_ 'press any key to continue ...'
  read ok </dev/tty
}

readLine() # menu read
{
  qecho "$1"
  read CHOICE </dev/tty
}

# use sudo only if we're not root & if available
if [ "$(id -u)" != '0' -a "$(which sudo)" != '' ]
then udo='sudo'
else udo=''
fi

service="$udo service"
if ! which service > /dev/null; then
  service() # replace missing 'service' binary !
  {
    if [ $# -ne 2 ]; then
      xecho "Usage: $(basename $0).service name argument"
    fi
    $udo /etc/init.d/$1 $2
  }
fi

if which apt-get > /dev/null; then
  installPack="$udo dpkg -i"
  install="$udo apt-get -fyq --force-yes install"
  buildDep="$udo apt-get -fyq --force-yes build-dep"
  update="$udo apt-get -fyq --force-yes update"
  upgrade="$udo apt-get -fyq --force-yes upgrade"
  distupgrade="$udo apt-get -fyq --force-yes dist-upgrade"
  remove="$udo apt-get -fyq --force-yes remove"
  autoremove="$udo apt-get -fyq --force-yes autoremove"
  purge="$udo apt-get -fyq --force-yes purge"
  key="$udo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys"
  packages="dpkg --get-selections"
elif which ipkg > /dev/null; then
  installPack="$udo ipkg install"
  install="$udo ipkg install"
  buildDep="xecho 'buildDep not implemented' #"
  update="$udo ipkg update"
  upgrade="$udo ipkg upgrade"
  distupgrade="$udo ipkg upgrade"
  remove="$udo ipkg remove"
  autoremove="xecho 'autoremove not implemented' #"
  purge="$udo ipkg remove"
  key="xecho 'key not implemented'"
  packages="xecho 'packages not implemented'"
else
  xecho 'Unable to find apt-get nor ipkg in your system'
fi

#if ! pushd . 2>/dev/null; then
#  recho 'pushd/popd as internal functions'
#  dirLifo=''
#  pushd()
#  {
#    if [ $# -ne 1 ]; then
#      xecho "Usage: $(basename $0).pushd path"
#    fi
#    dirLifo="$(pwd):$dirLifo"
#    cd "$1"
#  }
#  popd()
#  {
#    dir=$(echo $dirLifo | cut -d ':' -f1)
#    dirLifo=$(echo $dirLifo | cut -d ':' -f2-)
#    if [ "$dir" ]; then
#      cd "$dir"
#    else
#      xecho 'Paths LIFO is empty !'
#    fi
#  }
#else
#  recho 'pushd/popd as shell built-in'
#  popd
#fi

# unit-testing of the implementation !
#pushdTest()
#{
#  pushdUnitFailed="pushd/popd unit test failed !"
#  here=$(pwd)
#  pushd /media && echo $dirLifo
#  if [ "$(pwd)" != '/media' ]; then xecho "$pushdUnitFailed 1/5"; fi
#  cd /home
#  pushd /bin && echo $dirLifo
#  if [ "$(pwd)" != '/bin' ]; then xecho "$pushdUnitFailed 2/5"; fi
#  popd && echo $dirLifo
#  if [ "$(pwd)" != '/home' ]; then xecho "$pushdUnitFailed 3/5 $(pwd)"; fi
#  popd && echo $dirLifo
#  if [ "$(pwd)" != "$here" ]; then xecho "$pushdUnitFailed 4/5"; fi
#}

# Asks user to confirm an action (with yes or no) --------------------------------------------------
#> 0 (true value for if [ ]) if yes, 1 if no and (defaultChoice) by default
#1 : default (0 = yes / 1 = no)
#2 : question (automatically appended with [Y/n] ? / [y/N] ?)
yesOrNo()
{
  if [ $# -ne 2 ]; then
    xecho "Usage : yesOrNo default question\n\tdefault : 0=yes or 1=no 2='force yes' 3='force no'"
  fi

  local default="$1"
  local question="$2"
  case $default in
  "$true"       ) qecho "$question [Y/n]";;
  "$false"      ) qecho "$question [y/N]";;
  "$true_auto"  ) REPLY=$true;  return $true ;;
  "$false_auto" ) REPLY=$false; return $true ;;
  * ) xecho "Invalid default value : $default";;
  esac

  while true; do
    read REPLY </dev/tty
    case "$REPLY" in
    '' ) REPLY=$default ;;
    'y' | 'Y' ) REPLY=$true  ;;
    'n' | 'N' ) REPLY=$false ;;
    * ) REPLY='' ;;
    esac
    if [ "$REPLY" ]; then break; fi
    default='' # cancel default value
    recho "Please answer y for yes or n for no"
  done
}

# Utilities ========================================================================================

threadsCount()
{
  grep -c ^processor /proc/cpuinfo
}

# Checkout a subversion repository locally ---------------------------------------------------------
# TODO
checkout()
{
  [ $# -ne 4 ] && return $false

  rm -rf $2 2>/dev/null
  svn checkout --username=$3 --password=$4 --non-interactive --trust-server-cert $1 $2
}

# Generate a random password -----------------------------------------------------------------------
# size      : number of characters; defaults to 32
# special   : include special characters
# lowercase : convert any characters to lower case
# uppercase : convert any characters to upper case
randpass()
{
  [ $# -ne 4 ] && echo ''

  [ $2 -eq $true ] && chars='[:graph:]' || chars='[:alnum:]'
  [ $3 -eq $true ] && lower='[:upper:]' || lower='[:lower:]'
  [ $4 -eq $true ] && upper='[:lower:]' || upper='[:upper:]'
  cat /dev/urandom | tr -cd "$chars" | head -c $1 | \
    tr '[:upper:]' "$lower" | tr '[:lower:]' "$upper"
}

# Add a repository if it isn't yet listed in sources.list ------------------------------------------
# repositoryName   : the name (eg : virtualbox) of the repo.
# repositoryDebUrl : the debian URL (http://...) of the repo.
# repositoryKind   : the kind (contrib, ...) of the repo.
addAptRepo()
{
  if [ $# -ne 3 ]; then
    xecho 'Usage : addAptRepo repositoryName repositoryDebUrl repositoryKind'
  fi

  local release="$(lsb_release -cs)"
  if [ ! -f "/etc/apt/sources.list.d/$1.list" ]; then
    $udo sh -c "echo 'deb $2 $release $3' >> '/etc/apt/sources.list.d/$1.list'"
  fi
}

# Add a 'ppa' repository trying to fix TODO --------------------------------------------------------
# repositoryPpa : the PPA (eg : ppa:rabbitvcs/ppa) of the repo.
# repositoryName : the PPA name without ppa:/... TODO
addAptPpaRepo()
{
  if [ $# -ne 2 ]; then
    xecho 'Usage : addAptPpaRepo repositoryPpa repositoryName'
  fi

  local repositoryPpa="$1"
  local repositoryName="$2"

  local ok=$false
  local here="$(pwd)"
  local last="$(lsb_release -cs)"
  cd /etc/apt/sources.list.d
  $udo rm -rf *$repositoryName*
  $udo apt-add-repository -y $repositoryPpa
  repositoryFile=$(ls | grep $repositoryName)
  if [ ! "$repositoryFile" ]; then
    xecho "Unable to find $repositoryName's repository file"
  fi
  mecho "Repository file : $repositoryFile"
  for actual in "$last" 'quantal' 'precise' 'oneiric' 'maverick' 'lucid'
  do
    $udo sh -c "sed -i -e 's:$last:$actual:g' $repositoryFile"
    mecho "Checking if the $repositoryName's repository does exist for $actual ..."
    if $update 2>&1 | grep -q $repositoryName; then
      mecho "Hum, the $repositoryName's repository does not exist for $actual"
      recho "Ok, trying the next one"
    else
      ok=$true
      break
    fi
    last=$actual
  done
  cd "$here"
  if [ $ok -eq $true ]
  then mecho "Using the $repositoryName's repository for $actual"
  else xecho 'Unable to find a suitable repository !'
  fi
}

# Add a GPG key to the system ----------------------------------------------------------------------
# gpgKeyUrl : the URL (deb http://....asc) of the GPG key
addGpgKey()
{
  if [ $# -ne 1 ]; then
    xecho 'Usage : addGpgKey gpgKeyUrl'
  fi

  wget -q "$1" -O- | $udo apt-key add -
}

# Check if a package is installed ------------------------------------------------------------------
# packageName : name of the package to check
isInstalled()
{
  if [ $# -ne 1 ]; then
    xecho 'Usage : isInstalled packageName'
  fi

  if $packages | grep $1 | grep -v -q 'deinstall'
  then return $true
  else return $false
  fi
}

# Install a package if it isn't yet installed ------------------------------------------------------
# packageName : name of the package to install
# binaryName  : name of the binary to find
autoInstall()
{
  if [ $# -ne 2 ]; then
    xecho 'Usage : autoInstall packageName binaryName'
  fi

  local packageName="$1"
  local binaryName="$2"

  # install the package if missing
  if which "$binaryName" > /dev/null; then
    recho "Binary $binaryName of package $packageName founded, nothing to do"
  else
    recho "Binary $binaryName of package $packageName missing, installing it"
    eval $install $packageName || xecho "Unable to install package $packageName !"
  fi
}

# Install a package if it isn't yet installed ------------------------------------------------------
# libName : name of the package to install (library)
autoInstallLib()
{
  if [ $# -ne 1 ]; then
    xecho 'Usage : autoInstallLib libName'
  fi

  # install the libs package if missing
  if dpkg --get-selections | grep "$1" | grep -q install; then
    recho "Library $1 founded, nothing to do"
  else
    recho "Library $1 missing, installing it"
    eval $install $1
  fi
}

# Install a package (with a setup method) if it isn't yet installed --------------------------------
# setupName  : name of the (setup) method to execute
# binaryName : name of the binary to find
autoInstallSetup()
{
  if [ $# -ne 2 ]; then
    xecho 'Usage : autoInstallSetup setupName binaryName'
  fi

  local setupName="$1"
  local binaryName="$2"

  # install the package if missing
  if which "$binaryName" > /dev/null; then
    recho "Binary $binaryName of setup $setupName founded, nothing to do"
  else
    recho "Binary $binaryName of setup $setupName missing, installing it"
    $setupName
  fi
}

# Extract a debian package -------------------------------------------------------------------------
debianDepack()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) debianFilename"
  fi

  local name=$(basename "$1" .deb)
  dpkg-deb -x "$1" "$name"
  mkdir "$name/DEBIAN"
  dpkg-deb -e "$1" "$name/DEBIAN"
}

# Create a debian package of a folder --------------------------------------------------------------
debianRepack()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) debianPath"
  fi

  dpkg-deb -b "$1"
}

checkDepend()
{
  if [ $# -ne 1 ]; then
    xecho 'Usage : checkDepend binaryName methodName'
  fi

  if ! which "$1" > /dev/null; then
    xecho "Dependency : $2 depends of $1, unable to find $1"
  fi
}

validateNumber()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0).validateNumber input"
  fi
  [ "$1" -eq "$1" 2>/dev/null ]
}

# Get the Nth first digits of the IPv4 address of a network interface ------------------------------
#> The address, ex: 192.168.1.34 -> [3 digits] 192.168.1. [1 digit] 192.
# ethName : name of the network interface to get ...
# numberOfDigitsRequired : number of digits to return (1-4)
getInterfaceIPv4()
{
  if [ $# -ne 2 ]; then
    xecho 'Usage : getInterfaceIPv4 ethName numberOfDigitsRequired'
  fi

  local ethName="$1"
  local numberOfDigitsRequired="$2"

  # find the Nth first digits of the ip address of a certain network interface,
  # this method use regular expression to filter the output of ifconfig
  cmd=$(ifconfig $ethName)
  case "$numberOfDigitsRequired" in
  '1' ) REPLY=$(expr match "$cmd" '.*inet ad\+r:\([0-9]*\.\)[0-9]*\.[0-9]*\.[0-9]*');;
  '2' ) REPLY=$(expr match "$cmd" '.*inet ad\+r:\([0-9]*\.[0-9]*\.\)[0-9]*\.[0-9]*');;
  '3' ) REPLY=$(expr match "$cmd" '.*inet ad\+r:\([0-9]*\.[0-9]*\.[0-9]*\.\)[0-9]*');;
  '4' ) REPLY=$(expr match "$cmd" '.*inet ad\+r:\([0-9]*\.[0-9]*\.[0-9]*\.[0-9]*\)');;
  * ) xecho 'numberOfDigitsRequired must be between 1 and 4' ;;
  esac

  # FIXME : check du parsing !
}

# Get the name of the default network interface ----------------------------------------------------
getDefaultInterfaceName()
{
  local default="$(route | grep ^default)"
  REPLY=$(expr match "$default" '.* \(.*\)$')
  if [ ! "$REPLY" ]; then
    xecho '[BUG] Unable to detect default network interface'
  fi
}

validateIP()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0).validateIP ip"
  fi
  [ $(echo $1 | sed -n "/^[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*$/p") ]
}

validateMAC()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0).validateMAC mac"
  fi
  [ $(echo $1 | sed -n "/^\([0-9A-Za-z][0-9A-Za-z]:\)\{5\}[0-9A-Za-z][0-9A-Za-z]$/p") ]
}

# Set setting value of a 'JSON' configuration file -------------------------------------------------
# TODO parameters comment
setSettingJSON_STRING()
{
  if [ $# -ne 3 ]; then
    xecho "Usage: $(basename $0).setSettingJSON file name value"
  fi

  sed  -i "s<\"$2\" *: *\"[^\"]*\"<\"$2\": \"$3\"<g" "$1"
  grep -q "\"$2\": \"$3\"" "$1"
}

# Set setting value of a 'JSON' configuration file -------------------------------------------------
# TODO parameters comment
setSettingJSON_BOOLEAN()
{
  if [ $# -ne 3 ]; then
    xecho "Usage: $(basename $0).setSettingJSON file name value"
  fi

  [ $3 -eq $true ] && value='true' || value='false'
  sed  -i "s<\"$2\" *: *[a-zA-Z]*<\"$2\": $value<g" "$1"
  grep -q "\"$2\": $value" "$1"
}

# Set setting value of a 'BASH' configuration file -------------------------------------------------
# TODO parameters comment
setSettingBASH()
{
  if [ $# -ne 3 -a $# -ne 4 ]; then
    xecho "Usage: $(basename $0).setSettingBASH file enabled name [value]"
  fi

  local toggle=''
  if [ $2 -eq $false ]; then toggle='#'; fi
  if [ $# -eq 3 ]; then
    sed  -i "s<[# \t]*$3<$toggle$3<" "$1"
    grep -q "$toggle$3" "$1"
  elif [ $# -eq 4 ]; then
    sed  -i "s<[# \t]*$3[ \t]*=.*<$toggle$3=$4<" "$1"
    grep -q "$toggle$3=$4" "$1"
  fi
}

# Set setting value of a 'htaccess' file -----------------------------------------------------------
# TODO parameters comments
setSettingHTA()
{
  if [ $# -ne 3 -a $# -ne 4 ]; then
    xecho "Usage: $(basename $0).setSettingHTA file enabled name [value]"
  fi

  local toggle=''
  if [ $2 -eq $false ]; then toggle='#'; fi
  if [ $# -eq 3 ]; then
    sed  -i "s<[# \t]*$3<$toggle$3<" "$1"
    grep -q "$toggle$3" "$1"
  elif [ $# -eq 4 ]; then
    sed  -i "s<[# \t]*$3[ \t]*.*<$toggle$3 $4<" "$1"
    grep -q "$toggle$3 $4" "$1"
  fi
}

# Set setting value of a 'PHP' configuration file --------------------------------------------------
# TODO parameters comments
setSettingPHP()
{
  if   [ $# -eq 4 ]; then key="\$$2\['$3'\]";         value=$4
  elif [ $# -eq 5 ]; then key="\$$2\['$3'\]\['$4'\]"; value=$5
  else xecho "Usage: $(basename $0).setSettingPHP file variable (category) name value"
  fi

  sed  -i "s<$key = .*<$key = '$value';<" "$1"
  grep -q "$key = '$value';" "$1"
}

screenRunning()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0).screenRunning name"
  fi
  screen -list | awk '{print $1}' | grep -q "$1"
}

screenLaunch()
{
  if [ $# -lt 2 ]; then
    xecho "Usage: $(basename $0).screenLaunch name command"
  fi
  screen -dmS "$@"
}

screenKill()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0).screenKill name"
  fi
  screen -X -S "$1" kill
}

# http://freesoftware.zona-m.net/how-automatically-create-opendocument-invoices-without-openoffice

# Apply sed in a [Libre|Open] Office document ------------------------------------------------------
# oooSrcFilename : name of the source [Libre|Open] office file
# oooDstFilename : name of the destination [Libre|Open] office file
# paramsFilename : name of the params file (a couple of param value by line)
oooSed()
{
  if [ $# -ne 3 ]; then
    xecho 'Usage : oooSed oooSrcFilename oooDstFilename paramsFilename'
  fi

  local work_dir='/tmp/OOO_SED'
  local oooSrcFilename="$1"
  local oooDstFilename="$2"
  local paramsFilename="$3"

  mecho "Apply sed in a [Libre|Open] Office document"
  mecho "Source         : $oooSrcFilename"
  mecho "Destination    : $oooDstFilename"
  mecho "Sed parameters : $paramsFilename"

  rm -rf $work_dir
  mkdir  $work_dir
  # FIXME local filename instead of filename, + test behaviour !
  filename=$(basename $oooSrcFilename)
  filename=$(echo ${filename%.*})

  cp $oooSrcFilename $work_dir/my_template
  cp $paramsFilename $work_dir/my_data.sh

  # preparation
  cd     $work_dir
  mkdir  work
  mv     my_template work
  cd     work
  unzip  my_template > /dev/null
  rm     my_template

  # replace text strings
  local content="$(cat content.xml)"
  local styles="$(cat styles.xml)"

  # parse params list line by line to find
  #          param value
  while read param value
  do
    if [ "$read$param" ]; then
      echo "s#$param#$value#g"
      content=$(echo $content | sed "s#$param#$value#g")
      styles=$(echo $styles | sed "s#$param#$value#g")
    fi
  done < ../my_data.sh # redirect done before while loop

  rm -f content.xml
  echo "$content" > content.xml

  rm -f styles.xml
  echo "$styles" > styles.xml

  # zip everything, rename it as .od* file and clean up
  find . -type f -print0 | xargs -0 zip ../$filename > /dev/null
  cd ..
  mv ${filename}.zip $oooDstFilename
  cd ..
  rm -rf $work_dir
}

# http://dag.wieers.com/home-made/unoconv/

# Convert a [Libre|Open] office document to a PDF with unoconv -------------------------------------
# oooSrcFilename : name of the [Libre|Open] office document to convert
oooToPdf()
{
  if [ $# -ne 3 ]; then
    xecho 'Usage : oooToPdf oooSrcFilename'
  fi

  unoconv -v --format pdf $1
}

logicielsUbuntuUtilsImported()
{
  echo > /dev/null
}
fi

# END OF LOGICIELS UBUNTU UTILS
