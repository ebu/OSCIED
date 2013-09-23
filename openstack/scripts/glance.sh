#!/usr/bin/env bash

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : CLOUD
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

  user='glance'
  getPass "$user" || xecho "Unable to get $user password"

  pecho 'Install and configure Glance Image Service'
  eval $install glance glance-api glance-common python-glanceclient \
    glance-registry python-glance || xecho 'Unable to install Glance Image Service'

  pecho 'Replace embedded sqlite database by MySQL'
  $udo rm /var/lib/glance/glance.sqlite 2>/dev/null
  db="mysql://$user:$pass@$CONTROLLER_PRIVATE_IP/glance?charset=utf8"

  pecho 'Configure Glance API'
  a=$GLANCE_API_CONF_FILE
  $udo cp $a $a.old
  setSetting $a $true  'sql_connection'    "$db"                    || xecho '1'
  setSetting $a $true  'enable_v2_api'     'True'                   || xecho '2'
  setSetting $a $true  'notifier_strategy' 'rabbit'                 || xecho '3'
  setSetting $a $true  'rabbit_host'       "$CONTROLLER_PRIVATE_IP" || xecho '4'
  setSetting $a $true  'rabbit_password'   "$RABBIT_PASS"           || xecho '5'
  # FIXME todo swift related informations (if installed)
  setSetting $a $true  'auth_host'         "$CONTROLLER_PRIVATE_IP" || xecho '6'
  setSetting $a $true  'admin_tenant_name' 'service'                || xecho '7'
  setSetting $a $true  'admin_user'        "$user"                  || xecho '8'
  setSetting $a $true  'admin_password'    "$pass"                  || xecho '9'
  setSetting $a $true  'flavor'            'keystone'               || xecho '10'

  # FIXME and glance cache to speedup nodes !

  pecho 'Configure Glance Registry'
  a=$GLANCE_REGISTRY_CONF_FILE
  $udo cp $a $a.old
  setSetting $a $true  'sql_connection'    "$db"                    || xecho '1'
  setSetting $a $true  'auth_host'         "$CONTROLLER_PRIVATE_IP" || xecho '2'
  setSetting $a $true  'admin_tenant_name' 'service'                || xecho '3'
  setSetting $a $true  'admin_user'        "$user"                  || xecho '4'
  setSetting $a $true  'admin_password'    "$pass"                  || xecho '5'
  setSetting $a $true  'flavor'            'keystone'               || xecho '6'

  service restart

  pecho 'Initialize the new Glance Image Service database'
  $udo glance-manage db_sync || xecho 'Unable to initialize database'

  service restart
}

installData()
{
  if ! which glance > /dev/null; then
    xecho 'Glance must be installed !'
  fi

  ok=$false
  if [ $# -eq 1 ]; then
    eval "data_$1"
  fi

  if [ $ok -eq $false ]; then
    xecho "Usage: `basename $0` installData mode\n\tmode : { all, ubuntu_12_04_UEC, verify }"
  fi
}

data_all()
{
  ok=$true
  ubuntu_12_04_UEC
  verify
}

data_ubuntu_12_04_UEC()
{
  ok=$true
  pecho "Add Ubuntu 12.04 UEC image"
  getPass 'admin' || xecho 'Unable to get admin password'
  tar='ubuntu-12.04-server-cloudimg-amd64.tar.gz'
  imageCreateQcow2 'admin' "$pass" "$TENANT_NAME" $true 'Ubuntu 12.04 UEC' \
    'precise-server-cloudimg-amd64.img' \
    "http://uec-images.ubuntu.com/releases/precise/release/$tar" || exit 1
}

data_verify()
{
  ok=$true
  pecho "Verify Glance's insallation"
  #getPass 'admin' || xecho 'Unable to get admin password'
  #tar='http://smoser.brickies.net/ubuntu/ttylinux-uec/ttylinux-uec-amd64-12.1_2.6.35-22_1.tar.gz'
  #imageCreateAll 'admin' "$pass" "$TENANT_NAME" "$tar" || exit 1
  #recho "No problem 'till now"
  recho 'Verification skipped'
}

uninstall()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) uninstall"
  fi
  ok=$true

  pecho 'Uninstall Glance Image Service'
  eval $purge glance glance-api glance-common python-glanceclient glance-registry python-glance
  eval $autoremove
  $udo rm -rf /etc/glance/ /var/lib/glance/ /var/log/glance/
}

service()
{
  if ! which glance > /dev/null; then
    xecho 'Glance must be installed !'
  fi

  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) service operation\n\toperation : { start, stop, restart, ... }"
  fi
  ok=$true

  op=$1
  eval $service glance-api      "$op" || xecho "Unable to $op glance api service"
  eval $service glance-registry "$op" || xecho "Unable to $op glance registry service"
}

try()
{
  if ! which glance > /dev/null; then
    xecho 'Glance must be installed !'
  fi
  ok=$true

  getPass 'admin' || xecho 'Unable to get admin password'
  export OS_USERNAME=admin
  export OS_PASSWORD=$pass
  export ADMIN_TOKEN=$ADMIN_TOKEN
  export SERVICE_TOKEN=$ADMIN_TOKEN
  export SERVICE_ENDPOINT=$CONTROLLER_ADMIN_URL
  export OS_AUTH_URL=$CONTROLLER_AUTHZ_URL
  getId tenant $TENANT_NAME || exit 1; tId=$id
  echo "Images"; glance --os-tenant-id "$tId" image-list
}

main "$@"
