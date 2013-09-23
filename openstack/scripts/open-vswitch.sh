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
    xecho "Usage: $(basename $0) mode\n\tmode : { install, uninstall, services }"
  fi
}

install()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) install"
  fi
  ok=$true

  pecho 'Install and configure Open vSwitch'
  eval $install linux-headers-generic # required to compile kernel modules
  eval $install openvswitch-switch openvswitch-datapath-dkms
  eval $service openvswitch-switch start || xecho 'Unable to start Open vSwitch'

  pecho 'Create quantum open-vSwitch agent required OVS bridge br-int'
  $udo ovs-vsctl add-br br-int || xecho 'Unable to create bridge br-int'

  # FIXME todo a network watchdog -> fallback in case of necessity !

  pecho 'Create quantum l3 agent required OVS bridge br-ex'
  $udo ovs-vsctl add-br br-ex || xecho 'Unable to create bridge br-ex'
  $udo ovs-vsctl br-set-external-id br-ex bridge-id br-ex || xecho 'TODO'
  $udo ovs-vsctl add-port br-ex $HOST_PUBLIC_IFACE || \
    xecho "Unable to attach br-ex to $HOST_PUBLIC_IFACE"

  pecho "Enable bridge br-ex and reset interface $HOST_PUBLIC_IFACE"
  $udo ifconfig br-ex up
  $udo ifconfig br-ex $HOST_PUBLIC_IP netmask $HOST_PUBLIC_MASK
  $udo ifconfig $HOST_PUBLIC_IFACE 0
  $udo route add default gw $HOST_PUBLIC_GW dev br-ex

  pecho 'Update network interfaces configuration'
  if ! grep -q 'br-ex' $NETWORK_CONF_FILE; then
    a=$NETWORK_CONF_FILE
    n=$HOST_PUBLIC_IFACE
    $udo cp $a $a.old
    b='auto PUBLIC_IFACE'
    c='iface PUBLIC_IFACE inet manual'
    d='pre-up ip link set \$IFACE up'
    e='post-down ip link set \$IFACE down'
    f='auto br-ex'
    $udo sed -i "s:auto $n:$b\n$c\n$d\n$e\n\n$f:;s:$n:br-ex:g;s:PUBLIC_IFACE:$n:g" $a
  else
    recho 'Network interfaces configuration already updated'
  fi

  service restart
}

uninstall()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) uninstall"
  fi
  ok=$true

  # FIXME avoid breaking network (insert old network config + ifconfig)
  pecho 'Uninstall Open vSwitch'
  eval $purge openvswitch-switch openvswitch-datapath-dkms
  eval $autoremove
  $udo rm -rf /etc/openvswitch* /var/log/openvswitch/
  $udo cp -f "$HOST_NETWORK_FILE" $NETWORK_CONF_FILE
  $udo ifconfig br-ex down
  $udo ifconfig $HOST_PUBLIC_IFACE $HOST_PUBLIC_IP netmask $HOST_PUBLIC_MASK
  $udo route add default gw $HOST_PUBLIC_GW
  eval $service networking restart
}

service()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) service operation\n\toperation : { start, stop, restart, ... }"
  fi
  ok=$true

  op=$1
  eval $service networking "$op" || xecho "Unable to $op networking service"
}

main "$@"
