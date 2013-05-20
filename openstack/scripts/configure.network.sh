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

pecho 'Configuring Network Interfaces'
a=$NETWORK_CONF_FILE
$udo mv $a $a.old
$udo cp "$HOST_NETWORK_FILE" $a
eval $service networking restart || xecho 'Unable to restart networking service'

$udo ifup $HOST_PUBLIC_IFACE
$udo ifup $HOST_PRIVATE_IFACE

pecho 'Enable IP Forwarding'
setSetting $SYSCTL_CONF_FILE $true 'net.ipv4.ip_forward' '1' || xecho '1'
$udo sysctl net.ipv4.ip_forward=1

pecho 'Install Network Utilities'
eval $install vlan bridge-utils || xecho 'Unable to install network utilities'

pecho 'Install and configure Network Time Protocol'
eval $install ntp || xecho 'Unable to install ntp'
$udo cp -f "$NTP_HACK_FILE" "$NTP_CONF_FILE" # FIXME node cfg is different
eval $service ntp restart || xecho 'Unable to restart ntp service'

exit 0 # FIXME bridge for flat
if $udo grep -q $NETWORK_BR_IFACE $NETWORK_CONF_FILE; then

  pecho "Setup network bridge interface $NETWORK_BR_IFACE"

  pecho 'Create VM Networking Bridge'
  $udo brctl addbr $NETWORK_BR_IFACE
  # FIXME restart maybe not needed
  eval $service networking restart || xecho 'Unable to restart networking service'

  $udo ifup $NETWORK_BR_IFACE
fi

# FIXME TODO FOR QUANTUM VLAN

#eval $install bridge-utils vlan || xecho 'Unable to install network utilities'
#pecho 'Load 8021q module to support VLAN'
#$udo modprobe 8021q
