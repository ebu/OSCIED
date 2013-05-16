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

. ./common.sh

main()
{
  ok=$false
  if [ $# -gt 0 ]; then
    mode=$1
    shift # remove mode parameter
    eval "$mode" "$@"
  fi

  if [ $ok -eq $false ]; then
    xecho "Usage: $(basename $0) mode\n\tmode : { install, installData, uninstall, service, try }"
  fi
}

install()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) install"
  fi
  ok=$true

  which vgdisplay > /dev/null || xecho 'LVM must be installed !'
  $udo vgdisplay "$CINDER_VG" > /dev/null || xecho "LVM VG $CINDER_VG not found !"

  user='cinder'
  getPass "$user" || xecho "Unable to get $user password"

  pecho 'Install and configure Cinder Volume Service'
  eval $install linux-headers-generic # required to compile kernel modules
  eval $install cinder-common cinder-api cinder-scheduler cinder-volume iscsitarget \
    iscsitarget-dkms open-iscsi python-cinder python-cinderclient tgt \
    || xecho 'Unable to install Cinder Volume Service'

  pecho 'Replace embedded sqlite database by MySQL'
  $udo rm /var/lib/cinder/cinder.sqlite 2>/dev/null
  db="mysql://$user:$pass@$CONTROLLER_PRIVATE_IP/cinder?charset=utf8"

  pecho 'Configure iSCSI'
  a=$ISCSI_CONF_FILE
  $udo cp $a $a.old
  $udo sed -i 's/false/true/g' $a

  a=$CINDER_PASTE_FILE
  pecho "Configure Cinder (`basename $a`)"
  $udo cp $a $a.old
  setSetting $a $true 'service_host'      "$CONTROLLER_PUBLIC_IP"  || xecho '1'
  setSetting $a $true 'auth_host'         "$CONTROLLER_PRIVATE_IP" || xecho '2'
  setSetting $a $true 'admin_tenant_name' 'service'                || xecho '3'
  setSetting $a $true 'admin_user'        "$user"                  || xecho '4'
  setSetting $a $true 'admin_password'    "$pass"                  || xecho '5'

  a=$CINDER_CONF_FILE
  pecho "Configure Cinder (`basename $a`)"
  $udo cp $a $a.old
  if ! $udo grep -q 'PATCHED_BY_OSCIED' $a; then
    $udo sh -c "cat '$CINDER_APPEND_FILE' >> $a"
  fi
  setSetting $a $true 'rabbit_host'     "$CONTROLLER_PRIVATE_IP" || xecho '1'
  setSetting $a $true 'rabbit_password' "$RABBIT_PASS"           || xecho '2'
  setSetting $a $true 'sql_connection'  "$db"                    || xecho '3'
  setSetting $a $true 'iscsi_helper'    'ietadm'                 || xecho '4'
  setSetting $a $true 'volume_group'    "$CINDER_VG"             || xecho '5'

  service restart

  pecho 'Initialize the new Cinder Volume Service database'
  $udo cinder-manage db sync || xecho 'Unable to initialize database'

  service restart
}

installData()
{
  xecho 'NOT IMPLEMENTED'
  #FIXME : to check cinder setup, create & list
  try create --display_name test 1
}

uninstall()
{
  if ! which cinder > /dev/null; then
    xecho 'Cinder must be installed !'
  fi

  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) uninstall"
  fi
  ok=$true

  pecho 'Uninstall Cinder Volume Service'
  eval $purge cinder-common cinder-api cinder-scheduler cinder-volume iscsitarget \
    iscsitarget-dkms open-iscsi python-cinder python-cinderclient tgt
  eval $autoremove
  $udo rm -rf /etc/cinder/ /var/lib/cinder/ /var/log/cinder/
}

service()
{
  if ! which cinder > /dev/null; then
    xecho 'Cinder must be installed !'
  fi

  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) service operation\n\toperation : { start, stop, restart, ... }"
  fi
  ok=$true

  op=$1
  eval $service tgt              $op || xecho "Unable to $op tgt service"
  eval $service iscsitarget      $op || xecho "Unable to $op iscsitarget service"
  eval $service cinder-api       $op || xecho "Unable to $op cinder api service"
  eval $service cinder-volume    $op || xecho "Unable to $op cinder volume service"
  eval $service cinder-scheduler $op || xecho "Unable to $op cinder scheduler service"
}

try()
{
  if ! which cinder > /dev/null; then
    xecho 'Cinder must be installed !'
  fi
  ok=$true

  getPass 'admin' || xecho 'Unable to get admin password'
  export OS_TENANT_NAME=$TENANT_NAME
  export OS_USERNAME=admin
  export OS_PASSWORD=$pass
  export OS_AUTH_URL=$CONTROLLER_AUTHZ_URL
  echo "Volumes"; cinder list
  if [ $# -gt 0 ]; then
    cinder "$@"
  else
    yesOrNo 1 'create a new volume'
    if [ $REPLY -eq $true ]; then
      readLine 'Volume name';      name=$CHOICE
      readLine 'Volume size (GB)'; size=$CHOICE
      cinder create --display_name "$name" "$size"
    fi
  fi
}

main "$@"

