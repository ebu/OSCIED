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
