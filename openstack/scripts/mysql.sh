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

  pecho 'Install and configure MySQL'
  sql='mysql-server mysql-server' # Tip : http://ubuntuforums.org/showthread.php?t=981801
  echo "$sql/root_password select $MYSQL_ROOT_PASS"       | $udo debconf-set-selections
  echo "$sql/root_password_again select $MYSQL_ROOT_PASS" | $udo debconf-set-selections
  $udo mkdir /etc/mysql 2>/dev/null
  eval $install mysql-server || xecho 'Unable to install MySQL'

  # Now MySQL will listen to incoming request of any source
  recho 'FIXME security (listen to private network only ?)'
  $udo sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/my.cnf

  root=$MYSQL_ROOT_PASS

  # Fix ticket #57 : Keystone + MySQL = problems
  mysql -uroot -p"$root" -e "DROP USER ''@'localhost'; DROP USER ''@'$(hostname)';"
  mysql -uroot -p"$root" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;"
  mysql -uroot -p"$root" -e "SET PASSWORD FOR 'root'@'%' = PASSWORD('$MYSQL_ROOT_PASS');"

  service restart

  pecho 'Create Cinder Volume Service database & user'
  user='cinder'
  getPass "$user" || xecho "Unable to get $user password"
  mysql -u root -p"$root" -e "CREATE DATABASE cinder;"
  mysql -u root -p"$root" -e "GRANT ALL ON cinder.* TO '$user'@'%' IDENTIFIED BY '$pass';"

  pecho 'Create Dashboard Service database & user'
  user='dashboard'
  getPass "$user" || xecho "Unable to get $user password"
  mysql -u root -p"$root" -e "CREATE DATABASE dashboard;"
  mysql -u root -p"$root" -e "GRANT ALL ON dashboard.* TO '$user'@'%' IDENTIFIED BY '$pass';"

  pecho 'Create Glance Image Service database & user'
  user='glance'
  getPass "$user" || xecho "Unable to get $user password"
  mysql -u root -p"$root" -e "CREATE DATABASE glance;"
  mysql -u root -p"$root" -e "GRANT ALL ON glance.* TO '$user'@'%' IDENTIFIED BY '$pass';"

  pecho 'Create Keystone Identity Service database & user'
  user='keystone'
  getPass "$user" || xecho "Unable to get $user password"
  mysql -u root -p"$root" -e 'CREATE DATABASE keystone;'
  mysql -u root -p"$root" -e "GRANT ALL ON keystone.* TO '$user'@'%' IDENTIFIED BY '$pass';"

  pecho 'Create Nova Compute Service database & user'
  user='nova'
  getPass "$user" || xecho "Unable to get $user password"
  mysql -uroot -p"$root" -e 'CREATE DATABASE nova;'
  mysql -uroot -p"$root" -e "GRANT ALL PRIVILEGES ON nova.* TO '$user'@'%' IDENTIFIED BY '$pass';"

  pecho 'Create Quantum Network Service database & user'
  user='quantum'
  getPass "$user" || xecho "Unable to get $user password"
  mysql -u root -p"$root" -e "CREATE DATABASE quantum;"
  mysql -u root -p"$root" -e "GRANT ALL ON quantum.* TO '$user'@'%' IDENTIFIED BY '$pass';"
}

uninstall()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) uninstall"
  fi
  ok=$true

  pecho 'Uninstall MySQL'
  eval $purge mysql-client-5.5 mysql-client-core-5.5 mysql-common mysql-server mysql-server-5.1 \
    mysql-server-5.5 mysql-server-core-5.5
  eval $autoremove
  $udo rm -rf /etc/mysql/ /var/lib/mysql/ /var/log/mysql/
}

service()
{
  if ! which mysql > /dev/null; then
    xecho 'MySQL must be installed !'
  fi

  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) service operation\n\toperation : { start, stop, restart, ... }"
  fi
  ok=$true

  op=$1
  eval $service mysql "$op" || xecho "Unable to $op MySQL service"
}

main "$@"
