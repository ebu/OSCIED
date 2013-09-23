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

  user='dashboard'
  getPass "$user" || xecho "Unable to get $user password"

  pecho 'Install and configure OpenStack Dashboard'
  $udo mkdir -p /var/log/apache2 2>/dev/null # fixes bug apache2 restart failed
  eval $install memcached libapache2-mod-wsgi openstack-dashboard || \
    xecho 'Unable to install OpenStack Dashboard'

  eval $remove openstack-dashboard-ubuntu-theme || \
    xecho 'Unable to remove OpenStack Dashboard Ubuntu theme'

  pecho 'Replace embedded cache backend by memcached'
  # FIXME todo

  pecho 'Configure OpenStack Dashboard'
  a=$DASHBOARD_CONF_FILE
  if ! $udo grep -q 'PATCHED_BY_OSCIED' $a; then
    $udo cp $a $a.old
    b="s:CONTROLLER_PRIVATE_IP:$CONTROLLER_PRIVATE_IP:g"
    c="s:DASH_USER:$user:g"
    d="s:DASH_PASSWORD:$pass:g"
    $udo sh -c "sed '$b;$c;$d' '$DASHBOARD_APPEND_FILE' >> '$a'"
  else
    # FIXME not keep in sync if something changed ...
    recho 'dashboard configuration already done'
  fi

  service restart
}

uninstall()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) uninstall"
  fi
  ok=$true

  pecho 'Uninstall OpenStack Dashboard'
  eval $purge memcached libapache2-mod-wsgi openstack-dashboard apache2
  eval $autoremove
  $udo rm -rf /etc/openstack-dashboard/ /var/log/apache2/ #+ memcached
}

service()
{
  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) service operation\n\toperation : { start, stop, restart, ... }"
  fi
  ok=$true

  op=$1
  eval $service apache2 "$op" || xecho "Unable to $op dashboard service"
}

main "$@"
