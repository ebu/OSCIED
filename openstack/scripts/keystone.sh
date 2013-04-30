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
    xecho "Usage: $(basename $0) mode\n\tmode : { install, installData, uninstall, service, try }"
  fi
}

install()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) install"
  fi
  ok=$true

  user='keystone'
  getPass "$user" || xecho "Unable to get $user password"

  pecho 'Install and configure Keystone Identity Service'
  eval $install keystone python-keystone python-keystoneclient || xecho 'Unable to install Keystone'

  pecho 'Replace embedded sqlite database by MySQL'
  $udo rm /var/lib/keystone/keystone.db 2>/dev/null
  db="mysql://$user:$pass@$CONTROLLER_PRIVATE_IP/keystone?charset=utf8"

  pecho 'Configure Keystone'
  a=$KEYSTONE_CONF_FILE
  $udo cp $a $a.old
  setSetting $a $true 'admin_token' "$ADMIN_TOKEN" || xecho '1'
  setSetting $a $true 'connection'  "$db"          || xecho '2'

  service restart

  pecho 'Initialize the new Keystone Identity Service database'
  $udo keystone-manage db_sync || xecho 'Unable to initialize database'
}

installData()
{
  if ! which keystone > /dev/null; then
    xecho 'Keystone must be installed !'
  fi

  ok=$false
  if [ $# -eq 1 ]; then
    eval "data_$1"
  fi

  if [ $ok -eq $false ]; then
    mode='mode : {all, tenants, users, roles, usersRoles, services, endpoints, verify }'
    xecho "Usage: $(basename $0) installData mode\n\t$mode"
  fi
}

data_all()
{
  ok=$true
  tenants
  users
  roles
  usersRoles
  services
  endpoints
  verify
}

data_tenants()
{
  ok=$true
  pecho 'Create Keystone Tenants'
  savedIFS=$IFS
  IFS=';'
  while read tenant description
  do
    if echo "$tenant" | grep -q '#'; then
      continue
    fi
    mecho "Create Keystone's tenant $tenant"
    if ! tenantCreate "$tenant"; then
      xecho "Unable to create tenant $tenant"
    fi
  done < "$KEYSTONE_TENANTS_FILE"
  IFS=$savedIFS
}

data_users()
{
  ok=$true
  pecho 'Create Keystone Users'
  savedIFS=$IFS
  IFS=';'
  while read enabled name pass mail description
  do
    if echo "$enabled" | grep -q '#';   then continue; fi
    if echo "$enabled" | grep -q 'off'; then continue; fi
    mecho "Create Keystone's user $name"
    if ! userCreate "$name" "$pass" "$mail" "$description"; then
      xecho "Unable to create user $name"
    fi
  done < "$KEYSTONE_USERS_FILE"
  IFS=$savedIFS
}

data_roles()
{
  ok=$true
  pecho 'Create Keystone Roles'
  savedIFS=$IFS
  IFS=';'
  while read role description
  do
    if echo "$role" | grep -q '#'; then
      continue
    fi
    mecho "Create Keystone's role $role"
    if ! roleCreate "$role"; then
      xecho "Unable to create role $role"
    fi
  done < "$KEYSTONE_ROLES_FILE"
  IFS=$savedIFS
}

data_usersRoles()
{
  ok=$true
  pecho 'Assign Keystone Roles to Users'
  savedIFS=$IFS
  IFS=';'
  while read tenant user role comment
  do
    if echo "$tenant" | grep -q '#'; then
      continue
    fi
    mecho "Give role $role to user $user into tenant $tenant"
    getId 'tenant' "$tenant" || xecho 'Unable to get tenant id'; tenantId=$id
    getId 'user'   "$user"   || xecho 'Unable to get user id';   userId=$id
    getId 'role'   "$role"   || xecho 'Unable to get role id';   roleId=$id
    if ! userRoleAdd "$tenantId" "$userId" "$roleId"; then
      xecho "Unable to give role $role to user $user into tenant $tenant"
    fi
  done < "$KEYSTONE_USERS_ROLES_FILE"
  IFS=$savedIFS
}

data_services()
{
  ok=$true
  pecho 'Create Keystone Services'
  savedIFS=$IFS
  IFS=';'
  while read service type description
  do
    if echo "$service" | grep -q '#'; then
      continue
    fi
    mecho "Create Keystone's service $service"
    if ! serviceCreate "$service" "$type" "$description"; then
      xecho "Unable to create service $service"
    fi
  done < "$KEYSTONE_SERVICES_FILE"
  IFS=$savedIFS
}

data_endpoints()
{
  ok=$true
  pecho 'Create Keystone Endpoints'
  savedIFS=$IFS
  IFS=';'
  while read region service public internal admin
  do
    if echo "$region" | grep -q '#'; then
      continue
    fi
    mecho "Create Keystone's endpoint $region:$service"
    public="http://$CONTROLLER_PUBLIC_IP:$public"
    internal="http://$CONTROLLER_PRIVATE_IP:$internal"
    admin="http://$CONTROLLER_PRIVATE_IP:$admin"
    getId 'service' "$service" || xecho 'Unable to get service id'; serviceId=$id
    if ! endpointCreate "$region" "$serviceId" "$public" "$internal" "$admin"; then
      xecho "Unable to create endpoint $region:$service"
    fi
  done < "$KEYSTONE_ENDPOINTS_FILE"
  IFS=$savedIFS
}

data_verify()
{
  ok=$true
  pecho "Verify Keystone's insallation"
  getPass 'admin' || xecho 'Unable to get admin password'
  tokenGet 'admin' "$pass" || xecho 'Unable to get a token for admin user'
  tokenGet 'admin' "$pass" $TENANT_NAME || \
    xecho "Unable to get a token for admin user in tenant $TENANT_NAME"
  recho "No problem 'till now"
}


uninstall()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) uninstall"
  fi
  ok=$true

  pecho 'Uninstall Keystone Identity Service'
  eval $purge keystone python-keystone python-keystoneclient
  eval $autoremove
  $udo rm -rf /etc/keystone/ /var/lib/keystone/ /var/log/keystone/
}

service()
{
  if ! which keystone > /dev/null; then
    xecho 'Keystone must be installed !'
  fi

  if [ $# -ne 1 ]; then
    xecho "Usage: $(basename $0) service operation\n\toperation : { start, stop, restart, ... }"
  fi
  ok=$true

  op=$1
  eval $service keystone "$op" || xecho "Unable to $op keystone service"
}

try()
{
  if ! which keystone > /dev/null; then
    xecho 'Keystone must be installed !'
  fi
  ok=$true

  # mysqldump -u root -p keystone > keystone.sql

  getPass 'admin' || xecho 'Unable to get admin password'
  export OS_USERNAME=admin
  export OS_PASSWORD=$pass
  #export ADMIN_TOKEN=$ADMIN_TOKEN
  export SERVICE_TOKEN=$ADMIN_TOKEN
  export SERVICE_ENDPOINT=$CONTROLLER_ADMIN_URL
  export OS_AUTH_URL=$CONTROLLER_AUTHZ_URL
  getId user   'admin'      || exit 1; uId=$id
  getId tenant $TENANT_NAME || exit 1; tId=$id
  #env | sort | grep -v LS_COLOR
  #exit 0
  echo "Tenants";         keystone tenant-list
  echo "Users";           keystone user-list
  echo "Roles";           keystone role-list
  echo "Users Roles";     keystone user-role-list --user-id $uId --tenant-id $tId
  echo "Services";        keystone service-list
  echo "Endpoints";       keystone endpoint-list
  echo "EC2 Credentials"; keystone ec2-credentials-list --user-id $uId
}

main "$@"
