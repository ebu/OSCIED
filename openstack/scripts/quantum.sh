#!/usr/bin/env bash

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : CLOUD
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

  user='quantum'
  getPass "$user" || xecho "Unable to get $user password"

  # quantum-plugin-openvswitch-agent <-> nova-compute
  pecho 'Install and configure Quantum Network Service'
  eval $install quantum-common quantum-server quantum-plugin-openvswitch \
    quantum-plugin-openvswitch-agent python-quantum python-quantumclient || \
    xecho 'Unable to install Quantum Network Service'

  pecho 'Replace embedded sqlite database by MySQL'
  $udo rm /var/lib/quantum/quantum.sqlite 2>/dev/null
  db="mysql://$user:$pass@$CONTROLLER_PRIVATE_IP/quantum?charset=utf8"

  pecho 'Configure Quantum Open vSwitch Agent'
  a=$QUANTUM_OVSWITCH_CONF_FILE
  $udo cp $a $a.old
  $udo sed -i 's/Default://g' $a
  setSetting $a $true 'sql_connection'      "$db"              || xecho '1' # Set sql connection
  setSetting $a $true 'enable_tunneling'    'True'             || xecho '2' # Enable tunnelling
  setSetting $a $true 'tenant_network_type' 'gre'              || xecho '3' # Mode tunneling
  setSetting $a $true 'tunnel_id_ranges'    '1:1000'           || xecho '4' # Set range of id's
  setSetting $a $true 'integration_bridge'  'br-int'           || xecho '5' # Set integration bridge
  setSetting $a $true 'tunnel_bridge'       'br-tun'           || xecho '6' # Set tunneling bridge
  setSetting $a $true 'local_ip'            "$HOST_PRIVATE_IP" || xecho '7' # Only if agent running

  a=$QUANTUM_CONF_FILE
  pecho "Configure Quantum ($(basename $a))"
  $udo cp $a $a.old
  plugin='quantum.plugins.openvswitch.ovs_quantum_plugin.OVSQuantumPluginV2'
  setSetting $a $true 'core_plugin'      "$plugin"                || xecho '1'
  setSetting $a $true 'auth_strategy'    'keystone'               || xecho '2'
  setSetting $a $true 'rabbit_host'      "$CONTROLLER_PRIVATE_IP" || xecho '3'
  setSetting $a $true 'rabbit_password'  "$RABBIT_PASS"           || xecho '4'

  a=$QUANTUM_PASTE_FILE
  pecho "Configure Quantum ($(basename $a))"
  $udo cp $a $a.old
  setSetting $a $true 'auth_host'         "$CONTROLLER_PRIVATE_IP" || xecho '1'
  setSetting $a $true 'admin_tenant_name' 'service'                || xecho '2'
  setSetting $a $true 'admin_user'        "$user"                  || xecho '3'
  setSetting $a $true 'admin_password'    "$pass"                  || xecho '4'

  eval $service quantum-server restart || xecho 'Unable to restart quantum server service'
  eval $service quantum-plugin-openvswitch-agent restart || \
    xecho 'Unable to restart quantum open-vSwitch agent'

  pecho 'Install and configure Quantum DHCP/L3 Agent'
  eval $install quantum-dhcp-agent quantum-l3-agent || \
    xecho 'Unable to install Quantum DHCP/L3 Agent'

  pecho 'Configure Quantum DHCP Agent'
  a=$QUANTUM_DHCP_CONF_FILE
  $udo cp $a $a.old
  setSetting $a $true 'use_namespaces' 'True' || xecho '1'

  pecho 'Configure Quantum Layer 3 Agent'
  a=$QUANTUM_L3_CONF_FILE
  $udo cp $a $a.old
  setSetting $a $true 'auth_url'          "$CONTROLLER_ADMIN_URL" || xecho '1'
  setSetting $a $true 'auth_region'       'RegionOne'             || xecho '2'
  setSetting $a $true 'admin_tenant_name' 'service'               || xecho '3'
  setSetting $a $true 'admin_user'        "$user"                 || xecho '4'
  setSetting $a $true 'admin_password'    "$pass"                 || xecho '5'
  setSetting $a $true 'metadata_ip'       "$CONTROLLER_PUBLIC_IP" || xecho '6'
  setSetting $a $true 'use_namespaces'    'True'                  || xecho '7'

  #pecho 'Initialize the new Quantum Network Service database'
  #$udo quantum-manage db_sync || xecho 'Unable to initialize database'

  g='https://github.com/mseknibilel/OpenStack-Folsom-Install-guide/blob/stable/GRE'
  pecho 'Fix a known bug of quantum (when using a single router)'
  cecho "URL : $g/Tricks%26Ideas/modify_iptables_manager.rst"
  $udo sed -i 's:/sbin/iptables:iptables:g' $QUANTUM_BUG_FILE

  service restart
}

uninstall()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) uninstall"
  fi
  ok=$true

  pecho 'Uninstall Quantum Network Service'
  eval $purge quantum-*
  eval $autoremove
  $udo rm -rf /etc/quantum/ /var/lib/quantum/ /var/log/quantum/
}

service()
{
  if ! which quantum > /dev/null; then
    xecho 'Quantum must be installed !'
  fi

  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) service operation\n\toperation : { start, stop, restart, ... }"
  fi
  ok=$true

  op=$1
  eval $service quantum-server     "$op" || xecho "Unable to $op quantum server service"
  eval $service quantum-dhcp-agent "$op" || xecho "Unable to $op quantum dhcp agent service"
  eval $service quantum-l3-agent   "$op" || xecho "Unable to $op quantum l3 agent service"
  eval $service quantum-plugin-openvswitch-agent "$op" || \
    xecho "Unable to $op quantum open-vSwitch agent"
}

try()
{
  if ! which quantum > /dev/null; then
    xecho 'Quantum must be installed !'
  fi
  ok=$true

  # sh nova.sh try nova network create --label=yahoo --fixed_range_v4=10.10.10.0/24 --bridge=br100 \
  #   --dns1=8.8.8.8 --project_id=1c226c717e3d43e89415230e5e17c286
  # sh nova.sh try nova boot myUbuntu --image 9fbebc50-2376-4f6e-8492-a3048bc32ef9 --flavor 2

  getPass 'admin' || xecho 'Unable to get admin password'
  export OS_TENANT_NAME=$TENANT_NAME
  export OS_USERNAME=admin
  export OS_PASSWORD=$pass
  #export ADMIN_TOKEN=$ADMIN_TOKEN
  #export SERVICE_TOKEN=$ADMIN_TOKEN
  #export SERVICE_ENDPOINT=$CONTROLLER_ADMIN_URL
  export OS_AUTH_URL=$CONTROLLER_AUTHZ_URL

  if [ $# -eq 0 ]; then
  #  echo "Hosts";         nova host-list
  #  echo "Hypervisors";   nova hypervisor-list
  #  echo "Images";        nova image-list
  #  echo "Servers";       nova list
  #  echo "Keypairs";      nova keypair-list
  echo oups
  else
    quantum --os-username=$OS_USERNAME --os-password=$OS_PASSWORD \
      --os-auth-url=$OS_AUTH_URL --os-tenant-name=$OS_TENANT_NAME "$@"
  fi
}

main "$@"
