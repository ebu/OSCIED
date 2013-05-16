#!/usr/bin/env bash

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : CLOUD
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
# Retrieved from:
#   svn co https://claire-et-david.dyndns.org/prog/OSCIED

set -o nounset # will exit if an unitialized variable is used

# Prevent importing N times the following (like C++ .h : #ifndef ... #endif)
if ! cloudCommonImported 2>/dev/null; then

# Constants ========================================================================================

SCRIPTS_PATH=$(pwd)
BASE_PATH=$(dirname "$SCRIPTS_PATH")
FILES_PATH=$BASE_PATH'/files'
COMMON_FILES_PATH=$FILES_PATH'/common'
CONFIG_FILES_PATH=$FILES_PATH'/config'
NTP_CONF_FILE='/etc/ntp.conf'
NTP_HACK_FILE=$COMMON_FILES_PATH'/ntp.conf.hack'
NETWORK_CONF_FILE='/etc/network/interfaces'
SYSCTL_CONF_FILE='/etc/sysctl.conf'
LIBVIRTD_CONF_FILE='/etc/libvirt/libvirtd.conf'
LIBVIRTD_INIT_FILE='/etc/init/libvirt-bin.conf'
LIBVIRTD_DEF_FILE='/etc/default/libvirt-bin'
QEMU_CONF_FILE='/etc/libvirt/qemu.conf'
QEMU_PATCH_FILE=$COMMON_FILES_PATH'/qemu.conf.patch'
KEYSTONE_FILES_PATH=$CONFIG_FILES_PATH'/keystone'
KEYSTONE_TENANTS_FILE=$KEYSTONE_FILES_PATH'/tenants'
KEYSTONE_USERS_FILE=$KEYSTONE_FILES_PATH'/users'
KEYSTONE_ROLES_FILE=$KEYSTONE_FILES_PATH'/roles'
KEYSTONE_USERS_ROLES_FILE=$KEYSTONE_FILES_PATH'/usersRoles'
KEYSTONE_SERVICES_FILE=$KEYSTONE_FILES_PATH'/services'
KEYSTONE_ENDPOINTS_FILE=$KEYSTONE_FILES_PATH'/endpoints'
KEYSTONE_CONF_FILE='/etc/keystone/keystone.conf'
GLANCE_API_CONF_FILE='/etc/glance/glance-api.conf'
GLANCE_API_PASTE_FILE='/etc/glance/glance-api-paste.ini'
GLANCE_REGISTRY_CONF_FILE='/etc/glance/glance-registry.conf'
GLANCE_REGISTRY_PASTE_FILE='/etc/glance/glance-registry-paste.ini'
NOVA_FILES_PATH=$COMMON_FILES_PATH'/nova'
NOVA_CONF_FILE='/etc/nova/nova.conf'
NOVA_TEMPL_FILE=$NOVA_FILES_PATH'/nova.conf.template'
NOVA_API_PASTE_FILE='/etc/nova/api-paste.ini'
NOVA_API_HACK_FILE=$NOVA_FILES_PATH'/api-paste.ini.hack'
NOVA_COMPUTE_CONF_FILE='/etc/nova/nova-compute.conf'
NOVA_COMPUTE_HACK_FILE=$NOVA_FILES_PATH'/nova-compute.conf.hack'
QUANTUM_CONF_FILE='/etc/quantum/quantum.conf'
QUANTUM_PASTE_FILE='/etc/quantum/api-paste.ini'
QUANTUM_DHCP_CONF_FILE='/etc/quantum/dhcp_agent.ini'
QUANTUM_L3_CONF_FILE='/etc/quantum/l3_agent.ini'
QUANTUM_OVSWITCH_CONF_FILE='/etc/quantum/plugins/openvswitch/ovs_quantum_plugin.ini'
ISCSI_CONF_FILE='/etc/default/iscsitarget'
CINDER_FILES_PATH=$COMMON_FILES_PATH'/cinder'
CINDER_CONF_FILE='/etc/cinder/cinder.conf'
CINDER_APPEND_FILE=$CINDER_FILES_PATH'/cinder.conf.append'
CINDER_PASTE_FILE='/etc/cinder/api-paste.ini'
DASHBOARD_FILES_PATH=$COMMON_FILES_PATH'/dashboard'
DASHBOARD_CONF_FILE='/etc/openstack-dashboard/local_settings.py'
DASHBOARD_APPEND_FILE=$DASHBOARD_FILES_PATH'/local_settings.py.append'
QUANTUM_BUG_FILE='/usr/lib/python2.7/dist-packages/quantum/agent/linux/iptables_manager.py'

# Configuration ====================================================================================

host=$(hostname)
HOST_CONFIG_FILE=$(find "$FILES_PATH" -type f -name "$host.conf")
HOST_NETWORK_FILE=$(find "$FILES_PATH" -type f -name "$host.interfaces")

getInterface()
{
  if [ $# -ne 2 ]; then
    echo "[BUG] Usage: $(basename $0).getInterface type file" >&2
    exit 1
  fi
  content=$(sed 's:\n: :g' "$2")
  AZ='[A-Z ]*'
  REPLY_IFACE=$(expr match "$content" ".*START$AZ$1.*auto *\([a-z0-9:]*\).*END$AZ$1")
  REPLY_IP=$(expr match "$content" ".*START$AZ$1.*address *\([0-9\.]*\).*END$AZ$1.*")
  REPLY_MASK=$(expr match "$content" ".*START$AZ$1.*netmask *\([0-9\.]*\).*END$AZ$1.*")
  REPLY_GW=$(expr match "$content" ".*START$AZ$1.*gateway *\([0-9\.]*\).*END$AZ$1.*")
  if [ "$REPLY_IFACE" -a "$REPLY_IP" -a "$REPLY_MASK" ]
  then return 0
  else return 1
  fi
}

if [ ! -f "$HOST_CONFIG_FILE"  ]; then
  echo "Computer '$host' configuration file not found !" >&2
  exit 1
fi
if [ ! -f "$HOST_NETWORK_FILE" ]; then
  echo "Computer '$host' network file not found !" >&2
  exit 1
fi

if ! getInterface 'PUBLIC' "$HOST_NETWORK_FILE"; then
  echo 'Unable to detect public network interface' >&2
  exit 1
fi
HOST_PUBLIC_IFACE=$REPLY_IFACE
HOST_PUBLIC_IP=$REPLY_IP
HOST_PUBLIC_MASK=$REPLY_MASK
HOST_PUBLIC_GW=$REPLY_GW

if [ ! "$HOST_PUBLIC_GW" ]; then
  echo 'Unable to detect public network gateway' >&2
  exit 1
fi

if ! getInterface 'PRIVATE' "$HOST_NETWORK_FILE"; then
  echo 'Unable to detect private network interface' >&2
  exit 1
fi
HOST_PRIVATE_IFACE=$REPLY_IFACE
HOST_PRIVATE_IP=$REPLY_IP
HOST_PRIVATE_MASK=$REPLY_MASK

. "$HOST_CONFIG_FILE"

# FIXME a better way to handle urls ?
CONTROLLER_AUTHZ_URL="http://$CONTROLLER_PUBLIC_IP:5000/v2.0"
CONTROLLER_ADMIN_URL="http://$CONTROLLER_PRIVATE_IP:35357/v2.0"

# Utilities ========================================================================================

setSetting()
{
  if [ $# -ne 3 -a $# -ne 4 ]; then
    xecho "Usage: $(basename $0).setSetting file enabled name [value]"
  fi
  local toggle=''
  if [ $2 -eq $false ]; then toggle='#'; fi
  if [ $# -eq 3 ]; then
    $udo sed -i "s<[# ]*$3<$toggle$3<" "$1"
    $udo grep -q "$toggle$3" "$1" && return $true || return $false
  elif [ $# -eq 4 ]; then
    $udo sed -i "s<[# ]*$3 *= *.*<$toggle$3=$4<" "$1"
    $udo grep -q "$toggle$3=$4" "$1" && return $true || return $false
  fi
}

parseId()
{
  id="$(eval "$@" | grep ' id ')"
  id=$(expr match "$id" ".*\([0-9a-z]\{32\}\).*")
  if [ ! "$id" ]; then return $false; else return $true; fi
}

getId()
{
  if [ $# -ne 2 ]; then
    xecho "Usage: $(basename $0).getId category name"
  fi
  local a=$ADMIN_TOKEN
  local b=$CONTROLLER_ADMIN_URL
  id="$(keystone --token $a --endpoint $b ${1}-list | grep " $2 ")"
  id=$(expr match "$id" ".*\([0-9a-z]\{32\}\).*")
  if [ ! "$id" ]; then return $false; else return $true; fi
}

getPass()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0).getPass name"
  fi

  savedIFS=$IFS
  IFS=';'
  while read enabled name pass mail description
  do
    if [ "$name" = "$1" ]; then return $true; fi
  done < "$KEYSTONE_USERS_FILE"
  IFS=$savedIFS
  return $false
}

tenantCreate()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0).tenantCreate name"
  fi
  keystone --token $ADMIN_TOKEN --endpoint $CONTROLLER_ADMIN_URL \
    tenant-create --name "$1"
  getId 'tenant' "$1"
}

userCreate()
{
  if [ $# -ne 4 ]; then
    xecho "Usage: $(basename $0).userCreate name pass email description"
  fi
  # FIXME add user description
  keystone --token $ADMIN_TOKEN --endpoint $CONTROLLER_ADMIN_URL \
    user-create --name "$1" --pass="$2" --email="$3"
  getId 'user' "$1"
}

roleCreate()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0).roleCreate name"
  fi
  keystone --token $ADMIN_TOKEN --endpoint $CONTROLLER_ADMIN_URL \
    role-create --name "$1"
  getId 'role' "$1"
}

serviceCreate()
{
  if [ $# -ne 3 ]; then
    xecho "Usage: $(basename $0).serviceCreate name type description"
  fi
  # FIXME add service description
  keystone --token $ADMIN_TOKEN --endpoint $CONTROLLER_ADMIN_URL \
    service-create --name "$1" --type="$2"
  getId 'service' "$1"
}

endpointCreate()
{
  if [ $# -ne 5 ]; then
    xecho "Usage: $(basename $0).endpointCreate region serviceId publicUrl internalUrl adminUrl"
  fi
  keystone --token $ADMIN_TOKEN --endpoint $CONTROLLER_ADMIN_URL \
    endpoint-create --region "$1" --service-id=$2 \
    --publicurl=$3 --internalurl=$4 --adminurl=$5
}

userRoleAdd()
{
  if [ $# -ne 3 ]; then
    xecho "Usage: $(basename $0).userRoleAdd tenantId userId roleId"
  fi
  keystone --token $ADMIN_TOKEN --endpoint $CONTROLLER_ADMIN_URL \
    user-role-add --tenant-id=$1 --user-id=$2 --role-id=$3
}

tokenGet()
{
  if [ $# -eq 2 ]; then
    keystone --os-username="$1" --os-password="$2" \
      --os-auth-url=$CONTROLLER_ADMIN_URL token-get
  elif [ $# -eq 3 ]; then
    keystone --os-username="$1" --os-password="$2" --os-tenant-name="$3" \
      --os-auth-url=$CONTROLLER_ADMIN_URL token-get
  else
    xecho "Usage: $(basename $0).tokenGet username password [tenantName]"
  fi
}

imageCreateQcow2()
{
  if [ $# -ne 7 ]; then
    xecho "Usage: $(basename $0).imageCreateQcow2 username password tenantName public imageName imageFile imageUrl"
  fi

  archive=$(basename "$7")
  name=$(basename "$archive" .tar.gz)
  [ $4 -eq $true ] && public='--public' || public=''
  tmp=$(mktemp -d)
  cd $tmp || return $false
  wget -N "$7"
  tar -zxvf "$archive"
  [ ! -f "$6" ] && return $false
  id=$(glance --os-username="$1" --os-password="$2" --os-tenant-name="$3" \
    --os-auth-url=$CONTROLLER_AUTHZ_URL image-create \
    $public --name "$5" --container-format ovf --disk-format qcow2 < "$6")
  id=$(expr match "$id" ".*\([0-9a-z]\{8\}-[0-9a-z]\{4\}-[0-9a-z]\{4\}-[0-9a-z]\{4\}-[0-9a-z]\{12\}\).*")
  if [ ! "$id" ]; then return $false; else return $true; fi
}

imageCreateAll()
{
  if [ $# -ne 4 ]; then
    xecho "Usage: $(basename $0).imageCreateAll username password tenantName imageUrl"
  fi

  archive=$(basename "$4")
  name=$(basename "$archive" .tar.gz)
  mkdir /tmp/images 2>/dev/null
  cd /tmp/images || return $false
  wget -N "$4"
  tar -zxvf "$archive" || return $false
  imageCreateLinuxKernel  "$1" "$2" "$3" "${name}-vmlinuz" || return $false; kernelId=$id
  imageCreateLinuxRamdisk "$1" "$2" "$3" "${name}-loader"  || return $false; ramdiskId=$id
  imageCreateLinux "$1" "$2" "$3" "${name}.img" $kernelId $ramdiskId || return $false
}

imageCreateLinuxKernel()
{
  if [ $# -ne 4 ]; then
    xecho "Usage: $(basename $0).imageCreateLinuxKernel username password tenantName imagePath"
  fi
  id=$(glance --os-username="$1" --os-password="$2" --os-tenant-name="$3" \
    --os-auth-url=$CONTROLLER_AUTHZ_URL image-create \
    --name='tty-linux-kernel' --disk-format='aki' --container-format='aki' < "$4")
  id=$(expr match "$id" ".*\([0-9a-z]\{8\}-[0-9a-z]\{4\}-[0-9a-z]\{4\}-[0-9a-z]\{4\}-[0-9a-z]\{12\}\).*")
  if [ ! "$id" ]; then return $false; else return $true; fi
}

imageCreateLinuxRamdisk()
{
  if [ $# -ne 4 ]; then
    xecho "Usage: $(basename $0).imageCreateLinuxRamdisk username password tenantName imagePath"
  fi
  id=$(glance --os-username="$1" --os-password="$2" --os-tenant-name="$3" \
    --os-auth-url=$CONTROLLER_AUTHZ_URL image-create \
    --name='tty-linux-ramdisk' --disk-format='ari' --container-format='ari' < "$4")
  id=$(expr match "$id" ".*\([0-9a-z]\{8\}-[0-9a-z]\{4\}-[0-9a-z]\{4\}-[0-9a-z]\{4\}-[0-9a-z]\{12\}\).*")
  if [ ! "$id" ]; then return $false; else return $true; fi
}

imageCreateLinux()
{
  if [ $# -ne 6 ]; then
    xecho "Usage: $(basename $0).imageCreate username password tenantName imagePath kernelId ramdiskId"
  fi
  glance --os-username="$1" --os-password="$2" --os-tenant-name="$3" \
    --os-auth-url=$CONTROLLER_AUTHZ_URL image-create \
    --name='tty-linux' --disk-format='ami' --container-format='ami' \
    --property kernel_id=$5 --property ramdisk_id=$6 < "$4"
}

cloudCommonImported()
{
  echo > /dev/null
}
fi
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
