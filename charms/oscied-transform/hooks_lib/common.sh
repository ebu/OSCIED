#!/usr/bin/env bash

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : TRANSFORM
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

# Charms paths
BASE_PATH=$(pwd)

# Charms files
CONFIG_FILE="$BASE_PATH/config.json"
CELERY_TEMPL_FILE="$BASE_PATH/templates/celeryconfig.py.template"
CELERY_CONFIG_FILE="$BASE_PATH/celeryconfig.py"

# Shared storage paths
STORAGE_ROOT_PATH='/mnt/storage'
STORAGE_MEDIAS_PATH="$STORAGE_ROOT_PATH/medias"
STORAGE_UPLOADS_PATH="$STORAGE_ROOT_PATH/uploads"

# Configuration ====================================================================================

if [ "$(config-get verbose)" = 'true' ] ; then
  VERBOSE=0     # true
  set -o xtrace # for verbose logging to juju debug-log
else
  VERBOSE=1 # false
fi

PUBLIC_ADDRESS=$(unit-get public-address)
THE_CONCURRENCY=$(config-get concurrency)
RABBIT_QUEUES="$(config-get rabbit_queues),$PUBLIC_ADDRESS"

MONGO_CONNECTION=$(config-get mongo_connection)
RABBIT_CONNECTION=$(config-get rabbit_connection)
API_NAT_SOCKET=$(config-get api_nat_socket)

STORAGE_IP=$(config-get storage_ip)
STORAGE_NAT_IP=$(config-get storage_nat_ip)
STORAGE_FSTYPE=$(config-get storage_fstype)
STORAGE_MOUNTPOINT=$(config-get storage_mountpoint)
STORAGE_OPTIONS=$(config-get storage_options)

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
    pecho 'Configure Transform : Register shared storage'
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
  pecho 'Configure Transform : Unregister shared storage'
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

transform_config_is_enabled()
{
  [ "$MONGO_CONNECTION" -a "$RABBIT_CONNECTION" ]
}

transform_hook_bypass()
{
  if transform_config_is_enabled; then
    xecho 'Orchestrator is set in config, transform relation is disabled' 1
  fi
}

transform_register()
{
  # Overrides transform parameters with charm configuration
  if transform_config_is_enabled; then # if transform options are set
    mongo=$MONGO_CONNECTION
    rabbit=$RABBIT_CONNECTION
    socket=$API_NAT_SOCKET
  # Or uses transform parameters from charm transform relation
  elif [ $# -eq 2 ]; then # if function parameters are set
    mongo=$1
    rabbit=$2
    socket=''
  elif [ $# -eq 0 ]; then
    return
  else
    xecho "Usage: $(basename $0).transform_register mongo rabbit"
  fi

  pecho 'Configure Transform : Register the Orchestrator'
  setSettingJSON_STRING "$CONFIG_FILE" 'mongo_connection'  "$mongo"  || xecho 'Config' 1
  setSettingJSON_STRING "$CONFIG_FILE" 'rabbit_connection' "$rabbit" || xecho 'Config' 2
  setSettingJSON_STRING "$CONFIG_FILE" 'api_nat_socket'    "$socket" || xecho 'Config' 3

  host=$(expr match "$mongo" '.*mongodb://[^:]*:[^@]*@\([^:]*\):[0-9]*/[a-z]*.*')
  port=$(expr match "$mongo" '.*mongodb://[^:]*:[^@]*@[^:]*:\([0-9]*\)/[a-z]*.*')
  user=$(expr match "$mongo" '.*mongodb://\([^:]*\):[^@]*@[^:]*:[0-9]*/[a-z]*.*')
  password=$(expr match "$mongo" '.*mongodb://[^:]*:\([^@]*\)@[^:]*:[0-9]*/[a-z]*.*')
  database=$(expr match "$mongo" '.*mongodb://[^:]*:[^@]*@[^:]*:[0-9]*/\([a-z]*\).*')
  mecho "MongoDB host=$host, port=$port, user=$user, password=$password, database=$database"
  if [ ! "$host" -o ! "$port" -o ! "$user" -o ! "$password" -o ! "$database" ]; then
    xecho 'Unable to parse MongoDB connection' 3
  fi

  a="s<RABBIT_CONNECTION<$rabbit<g"
  b="s<MONGO_HOST<$host<g"
  c="s<MONGO_PORT<$port<g"
  d="s<MONGO_USER<$user<g"
  e="s<MONGO_PASSWORD<$password<g"
  f="s<MONGO_DATABASE<$database<g"
  g="s<THE_CONCURRENCY<$THE_CONCURRENCY<g"
  sed "$a;$b;$c;$d;$e;$f;$g" "$CELERY_TEMPL_FILE" > "$CELERY_CONFIG_FILE" || xecho 'Config' 4
  recho "Orchestrator successfully registered, it's time to wake-up"
}

transform_unregister()
{
  pecho 'Configure Transform : Unregister the Orchestrator'
  setSettingJSON_STRING "$CONFIG_FILE" 'mongodb_connection'  '' || xecho 'Config' 1
  setSettingJSON_STRING "$CONFIG_FILE" 'rabbitmq_connection' '' || xecho 'Config' 2
  setSettingJSON_STRING "$CONFIG_FILE" 'api_nat_socket'      '' || xecho 'Config' 3
  rm -f "$CELERY_CONFIG_FILE"
  recho 'Orchestrator successfully unregistered'
}

# HOOKS : Charm Setup ==============================================================================

hook_install()
{
  techo 'Transform - install'

  # I decidec to use the real ffmpeg, not the libav version :
  # http://blog.pkh.me/p/13-the-ffmpeg-libav-situation.html
  # http://doc.ubuntu-fr.org/ffmpeg
  apt-add-repository -y ppa:jon-severinsson/ffmpeg

  eval $update
  eval $upgrade

  pecho 'Install and configure Network Time Protocol'
  eval $install ntp || xecho 'Unable to install ntp' 1
  eval $service ntp restart || xecho 'Unable to restart ntp service' 2

  pecho 'Install python, (the real) FFmpeg, x264 and Gluster Fileystem'
  eval $install ffmpeg x264 python python-dev python-pip glusterfs-client nfs-common || \
    xecho 'Unable to install packages' 3

  pecho 'Install DashCash dependencies'
  eval $install libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libavdevice-dev \
    libavcodec-extra-53 zlib1g-dev || xecho 'Unable to install packages' 4

  pecho 'Install BSON Binary JSON, Celery Distributed Task Queue, MongoDB API and Requests'
  pip install --upgrade bson celery ipaddr passlib pymongo requests || \
    xecho 'Unable to install packages' 5

  pecho 'Install GPAC/DashCast'
  lib='gpac'
  tar="$lib.tar.bz2"
  rm -rf $lib 2>/dev/null; mkdir $lib; tar -xjf $tar -C $lib
  cd $lib || xecho "Unable to find directory $lib" 6
  ./configure; make -j$(threadsCount) && make install || xecho 'Unable to compile GPAC/DashCast' 7
  cd ..; rm -rf $lib

  # FIXME this call is not necessary, but config-changed may create an infinite loop, so WE call it
  hook_config_changed
}

hook_uninstall()
{
  techo 'Transform - uninstall'

  hook_stop
  eval $purge ffmpeg x264 glusterfs-client nfs-common
  pip install uninstall bson celery
  eval $autoremove
}

hook_config_changed()
{
  techo 'Transform - config changed'

  hook_stop
  pecho 'Configure Transform : Set verbose, messaging queues and storage path'
  setSettingJSON_STRING  "$CONFIG_FILE" 'public_address' "$PUBLIC_ADDRESS"    || xecho 'Config' 1
  setSettingJSON_BOOLEAN "$CONFIG_FILE" 'verbose'        "$VERBOSE"           || xecho 'Config' 2
  setSettingJSON_STRING  "$CONFIG_FILE" 'rabbit_queues'  "$RABBIT_QUEUES"     || xecho 'Config' 3
  setSettingJSON_STRING  "$CONFIG_FILE" 'storage_path'   "$STORAGE_ROOT_PATH" || xecho 'Config' 4
  storage_remount
  transform_register
  hook_start
  # FIXME infinite loop is used as config-changed hook !
}

# HOOKS : Charm Service ============================================================================

hook_start()
{
  techo 'Transform - start'

  if ! storage_is_mounted; then
    recho 'WARNING Do not start Transform daemon : No shared storage'
  elif [ ! -f "$CELERY_CONFIG_FILE" ]; then
    recho 'WARNING Do not start Transform daemon : No Celery configuration file'
  elif [ ! "$RABBIT_QUEUES" ]; then
    recho 'WARNING Do not start Transform daemon : No RabbitMQ queue(s) declared'
  else
    if ! screenRunning 'Transform'; then
      cd "$BASE_PATH" || xecho "Unable to find path $BASE_PATH"
      screenLaunch 'Transform' celeryd --config 'celeryconfig' -Q "$RABBIT_QUEUES" || \
        xecho 'Unable to start Transform daemon' 1
    fi
    sleep 5
    if ! screenRunning 'Transform'; then
      xecho 'Transform is not ready' 2
    else
      recho 'Transform successfully started'
    fi
  fi
}

hook_stop()
{
  techo 'Transform - stop'

  if screenRunning 'Transform'; then
    screenKill 'Transform' || xecho 'Unable to stop Transform daemon'
  fi
}

# HOOKS : Requires Storage =========================================================================

hook_storage_relation_joined()
{
  techo 'Transform - storage relation joined'
  storage_hook_bypass
}

hook_storage_relation_changed()
{
  techo 'Transform - storage relation changed'
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
  techo 'Transform - storage relation broken'
  storage_hook_bypass

  hook_stop
  storage_umount
}

# HOOKS : Requires Transform =======================================================================

hook_transform_relation_joined()
{
  techo 'Transform - transform relation joined'
  transform_hook_bypass
}

hook_transform_relation_changed()
{
  techo 'Transform - transform relation changed'
  transform_hook_bypass

  # Get configuration from the relation
  orchestra_ip=$(relation-get private-address)
  mongo=$(relation-get mongo_connection)
  rabbit=$(relation-get rabbit_connection)
  mecho "Orchestra IP is $orchestra_ip, MongoDB is $mongo, RabbitMQ is $rabbit"
  if [ ! "$orchestra_ip" -o ! "$mongo" -o ! "$rabbit" ]; then
    recho 'Waiting for complete setup'
    exit 0
  fi
  hook_stop
  transform_register "$mongo" "$rabbit"
  hook_start
}

hook_transform_relation_broken()
{
  techo 'Transform - transform relation broken'
  transform_hook_bypass

  hook_stop
  transform_unregister
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
