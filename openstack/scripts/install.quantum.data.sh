#!/bin/sh
#
# Quantum Networking
#
# Description: Create Virtual Networking for Quantum
#
# Designed for "Provider Router with Private Networks" Use-Case (http://goo.gl/JTt5n)
#
# Authors :
# Emilien Macchi / StackOps
# Endre Karlson / Bouvet ASA
#
# Inspired by DevStack script
#
# Support: openstack@lists.launchpad.net
# License: Apache Software License (ASL) 2.0

. ./common.sh

getPass 'admin' || xecho 'Unable to get admin password'
export OS_TENANT_NAME=$TENANT_NAME
export OS_USERNAME=admin
export OS_PASSWORD=$pass
#export ADMIN_TOKEN=$ADMIN_TOKEN
#export SERVICE_TOKEN=$ADMIN_TOKEN
#export SERVICE_ENDPOINT=$CONTROLLER_ADMIN_URL
export OS_AUTH_URL=$CONTROLLER_AUTHZ_URL

###########################
### Private Network #######
###########################
TENANT_NAME="$TENANT_NAME"
TENANT_NETWORK_NAME="$TENANT_NAME-net"
FIXED_RANGE="10.5.5.0/24"
NETWORK_GATEWAY="10.5.5.1"
###########################


##############################################################
### Public Network ###########################################
##############################################################

# Provider Router Informations
PROV_ROUTER_NAME="provider-router"

# Name of External Network (Don't change it)
EXT_NET_NAME="ext_net"

# External Network addressing
EXT_NET_CIDR="10.1.1.0/24"
EXT_NET_LEN=${EXT_NET_CIDR#*/}

# External bridge that we have configured into l3_agent.ini (Don't change it)
EXT_NET_BRIDGE=br-ex

# IP of external bridge (br-ex) :
EXT_GW_IP="10.1.1.47"

# IP of the Public Network Gateway (i.e.external router)
EXT_NET_GATEWAY="10.1.1.1"

# Floating IP range
POOL_FLOATING_START="10.1.1.10"
POOL_FLOATING_END="10.1.1.20"

###############################################################

# Function to get ID :
get_id () {
        echo `$@ | awk '/ id / { print $4 }'`
}


# Create the Tenant private network :
create_net() {
    local tenant_name="$1"
    local tenant_network_name="$2"
    local prov_router_name="$3"
    local fixed_range="$4"
    local network_gateway="$5"
    local tenant_id=$(keystone tenant-list | grep " $tenant_name " | awk '{print $2}')

    tenant_net_id=$(get_id quantum net-create --tenant_id $tenant_id $tenant_network_name)
    tenant_subnet_id=$(get_id quantum subnet-create --tenant_id $tenant_id --ip_version 4 $tenant_net_id $fixed_range --gateway $network_gateway)
    prov_router_id=$(get_id quantum router-create --tenant_id $tenant_id $prov_router_name)
    quantum router-interface-add $prov_router_id $tenant_subnet_id
}

# Create External Network :
create_ext_net() {
    local ext_net_name="$1"
    local ext_net_cidr="$2"
    local ext_net_gateway="$4"
    local pool_floating_start="$5"
    local pool_floating_end="$6"

    ext_net_id=$(get_id quantum net-create $ext_net_name -- --router:external=True)
    quantum subnet-create --ip_version 4 --allocation-pool start=$pool_floating_start,end=$pool_floating_end \
    --gateway $ext_net_gateway $ext_net_id $ext_net_cidr -- --enable_dhcp=False
}

# Connect the Tenant Virtual Router to External Network :
connect_providerrouter_to_externalnetwork() {
    local prov_router_name="$1"
    local ext_net_name="$2"

    router_id=$(get_id quantum router-show $prov_router_name)
    ext_net_id=$(get_id quantum net-show $ext_net_name)
    quantum router-gateway-set $router_id $ext_net_id
}


create_net $TENANT_NAME $TENANT_NETWORK_NAME $PROV_ROUTER_NAME $FIXED_RANGE $NETWORK_GATEWAY
create_ext_net $EXT_NET_NAME $EXT_NET_CIDR $EXT_NET_BRIDGE $EXT_NET_GATEWAY $POOL_FLOATING_START $POOL_FLOATING_END
connect_providerrouter_to_externalnetwork $PROV_ROUTER_NAME $EXT_NET_NAME

# Configure br-ex to reach public network :
$udo ip addr flush dev $EXT_NET_BRIDGE
$udo ip addr add $EXT_GW_IP/$EXT_NET_LEN dev $EXT_NET_BRIDGE
$udo ip link set $EXT_NET_BRIDGE up
