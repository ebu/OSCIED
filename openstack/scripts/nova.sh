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
# Retrieved from https://github.com/EBU-TI/OSCIED

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
    xecho "Usage: $(basename $0) mode\n\tmode : { install, uninstall, service, try }"
  fi
}

install()
{
  ok=$false
  if [ $# -eq 1 ]; then
    eval "install_$1"
  fi

  if [ $ok -eq $false ]; then
    xecho "Usage: `basename $0` install mode\n\tmode : { standalone, controller, compute }"
  fi
}

install_standalone()
{
  ok=$true

  user='nova'
  getPass "$user" || xecho "Unable to get $user password"

  pecho 'Install and configure Nova Compute Service'
  eval $install nova-api nova-cert nova-common nova-compute nova-compute-kvm nova-doc \
    nova-consoleauth nova-scheduler nova-novncproxy novnc python-nova python-novaclient || \
    xecho 'Unable to install Nova Compute Service'

  pecho 'Replace embedded sqlite database by MySQL'
  $udo rm /var/lib/nova/nova.sqlite 2>/dev/null
  db="mysql://$user:$pass@$CONTROLLER_PRIVATE_IP/nova?charset=utf8"

  pecho 'Configure Nova API'
  a=$NOVA_API_PASTE_FILE
  $udo cp $a $a.old
  setSetting $a $true 'auth_host'         "$CONTROLLER_PRIVATE_IP" || xecho '1'
  setSetting $a $true 'admin_tenant_name' 'service'                || xecho '2'
  setSetting $a $true 'admin_user'        "$user"                  || xecho '3'
  setSetting $a $true 'admin_password'    "$pass"                  || xecho '4'

  user='quantum'
  getPass "$user" || xecho "Unable to get $user password"

  pecho 'Configure Nova on a Standalone'
  a=$NOVA_CONF_FILE
  $udo cp $a $a.old
  b="s:CONTROLLER_PUBLIC_IP:$CONTROLLER_PUBLIC_IP:g"
  c="s:CONTROLLER_PRIVATE_IP:$CONTROLLER_PRIVATE_IP:g"
  d="s:HOST_PUBLIC_IP:$HOST_PUBLIC_IP:g"
  e="s:HOST_PRIVATE_IP:$HOST_PRIVATE_IP:g"
  $udo sh -c "sed '$b;$c;$d;$e' '$NOVA_TEMPL_FILE' > '$a'"
  setSetting $a $true 'sql_connection'            "$db"          || xecho '1'
  setSetting $a $true 'rabbit_password'           "$RABBIT_PASS" || xecho '2'
  setSetting $a $true 'quantum_admin_tenant_name' 'service'      || xecho '3'
  setSetting $a $true 'quantum_admin_username'    "$user"        || xecho '4'
  setSetting $a $true 'quantum_admin_password'    "$pass"        || xecho '5'

  pecho 'Configure Nova Compute'
  a=$NOVA_COMPUTE_CONF_FILE
  $udo mv $a $a.old
  $udo cp $NOVA_COMPUTE_HACK_FILE $a

  service restart

  pecho 'Initialize the new Nova Compute Service database'
  $udo nova-manage db sync || exit 1

  service restart
}

uninstall()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) uninstall"
  fi
  ok=$true

  pecho 'Uninstall Nova Compute Service'
  eval $purge nova-* novnc python-nova*
  eval $autoremove
  $udo rm -rf /etc/nova/ /var/lib/nova/ /var/log/nova/
}

service()
{
  if ! which nova > /dev/null; then
    xecho 'Nova must be installed !'
  fi

  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) service operation\n\toperation : { start, stop, restart, ... }"
  fi
  ok=$true

  op=$1
  eval $service nova-api         "$op" || xecho "Unable to $op nova api service"
  eval $service nova-cert        "$op" || xecho "Unable to $op nova cert service"
  eval $service nova-compute     "$op" || xecho "Unable to $op nova compute service"
  eval $service nova-consoleauth "$op" || xecho "Unable to $op nova console auth service"
  #NOVA-VOLUME eval $service nova-volume      "$op" || xecho "Unable to $op nova volume service"
  eval $service nova-scheduler   "$op" || xecho "Unable to $op nova scheduler service"
}

try()
{
  if ! which nova > /dev/null; then
    xecho 'Nova must be installed !'
  fi

  ok=$false
  if [ $# -gt 1 ]; then
    eval "try_$1"
  fi

  if [ $ok -eq $false ]; then
    xecho "Usage: `basename $0` try mode\n\tmode : { nova, manage }"
  fi
}

try_nova()
{
  ok=$true

  # sh nova.sh try nova network create --label=yahoo --fixed_range_v4=10.10.10.0/24 \
  #   --bridge=br100 --dns1=8.8.8.8 --project_id=1c226c717e3d43e89415230e5e17c286
  # sh nova.sh try nova boot myUbuntu --image 9fbebc50-2376-4f6e-8492-a3048bc32ef9 --flavor 2

  getPass 'admin' || xecho 'Unable to get admin password'
  export OS_NO_CACHE=1 # fixes bug https://bugs.launchpad.net/python-novaclient/+bug/1020238
  export OS_TENANT_NAME=$TENANT_NAME
  export OS_USERNAME=admin
  export OS_PASSWORD=$pass
  #export ADMIN_TOKEN=$ADMIN_TOKEN
  #export SERVICE_TOKEN=$ADMIN_TOKEN
  #export SERVICE_ENDPOINT=$CONTROLLER_ADMIN_URL
  export OS_AUTH_URL=$CONTROLLER_AUTHZ_URL

  if [ $# -eq 0 ]; then
    echo "Hosts";         nova host-list
    echo "Hypervisors";   nova hypervisor-list
    echo "Images";        nova image-list
    echo "Servers";       nova list
    echo "Keypairs";      nova keypair-list
    echo "Networks";      nova network-list
    echo "Volumes";       nova volume-list
    echo "Volumes Types"; nova volume-type-list
    echo "Flavors";       nova flavor-list
    echo "Services";      $udo nova-manage service list
  #  echo "Quotas";         $udo nova-manage quota
  else
    nova --os-username=$OS_USERNAME --os-password=$OS_PASSWORD \
      --os-auth-url=$OS_AUTH_URL --os-tenant-name=$OS_TENANT_NAME "$@"
  fi
}

try_manage()
{
  ok=$true

  # sh nova.sh try nova network create --label=yahoo --fixed_range_v4=10.10.10.0/24 --bridge=br100 \
  #   --dns1=8.8.8.8 --project_id=1c226c717e3d43e89415230e5e17c286
  # sh nova.sh try nova boot myUbuntu --image 9fbebc50-2376-4f6e-8492-a3048bc32ef9 --flavor 2

  getPass 'admin' || xecho 'Unable to get admin password'
  export OS_NO_CACHE=1 # fixes bug https://bugs.launchpad.net/python-novaclient/+bug/1020238
  export ADMIN_TOKEN=$ADMIN_TOKEN
  export SERVICE_TOKEN=$ADMIN_TOKEN
  export SERVICE_ENDPOINT=$CONTROLLER_ADMIN_URL
  $udo nova-manage "$@"
}

main "$@"
