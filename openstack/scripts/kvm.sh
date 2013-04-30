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
    xecho "Usage: $(basename $0) mode\n\tmode : { install, uninstall, service }"
  fi
}

install()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) install"
  fi
  ok=$true

  pecho 'Install and configure KVM hypervisor'
  eval $install kvm libvirt-bin pm-utils || xecho 'Unable to install hypervisor'
  if ! $udo grep -q 'PATCHED_BY_OSCIED' $QEMU_CONF_FILE; then
    if ! $udo grep -q '/dev/net/tun' $QEMU_CONF_FILE; then
      $udo patch -c $QEMU_CONF_FILE "$QEMU_PATCH_FILE" || xecho 'Unable to configure hypervisor'
    else
      # FIXME better check
      recho 'Hypervisor configuration seem OK'
    fi
  else
    recho 'Hypervisor configuration already updated'
  fi

  pecho 'Check if KVM virtualization is supported'
  autoInstall cpu-checker kvm-ok
  if ! kvm-ok > /dev/null; then
    xecho 'Hardware virtualization support is required'
  fi

  pecho 'Load KVM virtualization kernel module'
  $udo modprobe kvm
  $udo modprobe kvm-intel
  if ! lsmod | grep -q 'kvm'; then
    xecho 'Unable to load KVM kernel module'
  fi

  pecho 'Disable default virtual bridge'
  $udo virsh net-destroy  default
  $udo virsh net-undefine default

  pecho 'Allow live migration'
  a=$LIBVIRTD_CONF_FILE
  $udo cp $a $a.old
  setSetting $a $true 'listen_tls' '0'      || xecho '1'
  setSetting $a $true 'listen_tcp' '1'      || xecho '2'
  setSetting $a $true 'auth_tcp'   "'none'" || xecho '3'

  a=$LIBVIRTD_INIT_FILE
  $udo cp $a $a.old
  setSetting $a $true 'env libvirtd_opts' '"-d -l"' || xecho '4'

  a=$LIBVIRTD_DEF_FILE
  $udo cp $a $a.old
  setSetting $a $true 'libvirtd_opts' '"-d -l"' || xecho '4'

  service restart
}

uninstall()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) uninstall"
  fi
  ok=$true

  pecho 'Uninstall KVM hypervisor'
  eval $purge kvm libvirt-bin
  eval $autoremove
  $udo rm -rf /etc/kvm/ /etc/libvirt/ /var/log/libvirt/
}

service()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) service operation\n\toperation : { start, stop, restart, ... }"
  fi
  ok=$true

  op=$1
  eval $service libvirt-bin "$op" || xecho "Unable to $op hypervisor service"
}

main "$@"
