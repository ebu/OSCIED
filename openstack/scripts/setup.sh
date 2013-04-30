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

pecho 'Detected network configuration :'
cecho "Public iface  : $HOST_PUBLIC_IFACE $HOST_PUBLIC_IP $HOST_PUBLIC_MASK $HOST_PUBLIC_GW"
cecho "Private iface : $HOST_PRIVATE_IFACE $HOST_PRIVATE_IP $HOST_PRIVATE_MASK"

main()
{
  ok=$false
  if [ $# -gt 0 ]; then
    mode=$1
    shift # remove mode parameter
    eval "$mode" "$@"
  fi

  if [ $ok -eq $false ]; then
    n1="\n    "
    n2="\t: "
    m='{ bootstrap, startup, standalone, controller, compute, uninstall, service }'
    a="${n1}bootstrap${n2}Enable automatic setup on boot"
    b="${n1}startup${n2}Keep system up-to-date on boot"
    c="${n1}standalone${n2}Install an OpenStack Standalone (all-in-one)"
    d="${n1}controller${n2}Install an OpenStack Controller"
    e="${n1}compute${n2}Install an OpenStack Compute Node"
    f="${n1}uninstall${n2}Uninstall OpenStack components"
    g="${n1}service${n2}Run OpenStack components services init script"
    xecho "Usage: $(basename $0) mode\n\tmode : $m\n$a$b$c$d$e$f$g"
  fi
}

bootstrap()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) bootstrap"
  fi
  ok=$true

  ./configure.bootstrap.sh
}

startup()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) startup"
  fi
  ok=$true

  ./configure.startup.sh
}

standalone()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) standalone"
  fi
  ok=$true

  #./configure.network.sh              || exit 1
  ./install.prerequisities.sh          || exit 1
  ./rabbitmq.sh     install            || exit 1
  ./mysql.sh        install            || exit 1
  ./keystone.sh     install            || exit 1
  ./keystone.sh     installData all    || exit 1
  ./glance.sh       install            || exit 1
  ./glance.sh       installData all    || exit 1
  ./cinder.sh       install            || exit 1
  ./kvm.sh          install            || exit 1
  ./open-vswitch.sh install            || exit 1
  ./quantum.sh      install standalone || exit 1
# ./cinder.sh       installData        || exit 1
# ./swift.sh        install standalone || exit 1
  ./nova.sh         install standalone || exit 1
  ./dashboard.sh    install            || exit 1
}

controller()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) controller"
  fi
  ok=$true

  ./configure.network.sh               || exit 1
  ./install.prerequisities.sh          || exit 1
  ./rabbitmq.sh     install            || exit 1
  ./mysql.sh        install            || exit 1
  ./keystone.sh     install            || exit 1
  ./keystone.sh     installData all    || exit 1
  ./glance.sh       install            || exit 1
  ./glance.sh       installData all    || exit 1
# ./open-vswitch.sh install            || exit 1
# ./quantum.sh      install controller || exit 1
  ./cinder.sh       install            || exit 1
# ./cinder.sh       installData        || exit 1
# ./swift.sh        install controller || exit 1
  ./nova.sh         install controller || exit 1
  ./dashboard.sh    install            || exit 1
}

compute()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) compute"
  fi
  ok=$true

  ./configure.network.sh              || exit 1
  ./install.prerequisities.sh         || exit 1
# ./open-vswitch.sh install           || exit 1
# ./quantum.sh      install compute   || exit 1
  ./kvm.sh          install           || exit 1
  ./nova.sh         install compute   || exit 1
}

uninstall()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) uninstall"
  fi
  ok=$true

  ./mysql.sh        uninstall
  ./rabbitmq.sh     uninstall
  ./cinder.sh       uninstall
  ./dashboard.sh    uninstall
  ./glance.sh       uninstall
  ./keystone.sh     uninstall
  ./nova.sh         uninstall
  #./swift.sh        uninstall
  ./quantum.sh      uninstall
  ./open-vswitch.sh uninstall
  ./kvm.sh          uninstall
}

service()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) service operation\n\toperation : { start, stop, restart, ... }"
  fi
  ok=$true

  # FIXME If a component is not installed = error
  op=$1
  ./mysql.sh        service "$op" || exit 1
  ./rabbitmq.sh     service "$op" || exit 1
  ./cinder.sh       service "$op" || exit 1
  ./dashboard.sh    service "$op" || exit 1
  ./glance.sh       service "$op" || exit 1
  ./keystone.sh     service "$op" || exit 1
  ./nova.sh         service "$op" || exit 1
  #./swift.sh        service "$op" || exit 1
  ./quantum.sh      service "$op" || exit 1
  ./open-vswitch.sh service "$op" || exit 1
  ./kvm.sh          service "$op" || exit 1
}

main "$@"
