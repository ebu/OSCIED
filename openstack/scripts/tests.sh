# MY TRIALS/TESTS WITH QUANTUM

# nova-network XOR quantum
# http://docs.openstack.org/folsom/openstack-network/admin/content/nova_with_quantum.html

# Quantum L3 agent cannot ping directly, must use :
# -> ip netns exec qrouter... ip addr list
# -> ip netns exec qrouter... ping <fixed_ip>
# http://docs.openstack.org/trunk/openstack-network/admin/content/install_quantum-l3.html

# Common security group workflow
# http://docs.openstack.org/trunk/openstack-network/admin/content/securitygroup_workflow.html

. ./common.sh

getId tenant $TENANT_NAME || xecho '1'; tId=$id
parseId sh quantum.sh try net-create    --tenant-id $tId demoNet              || xecho '2'; nId=$id
parseId sh quantum.sh try subnet-create --tenant-id $tId demoNet 50.50.1.0/24 || xecho '3'; sId=$id
parseId sh quantum.sh try router-create --tenant-id $tId demoRouter           || xecho '4'; rId=$id
sh quantum.sh try router-interface-add $rId $sId || exit 1

exit 0
sh quantum.sh try net-create --tenant-id 4e2c131ac12946658fffe984feb5ce0e sharednet1 --shared \
  --provider:network_type flat --provider:physical_network physnet1

nid=

sh quantum.sh try subnet-create --tenant-id $tid sharednet1 192.168.1.0/24

sid=

sh nova.sh try nova boot --image 'Ubuntu 12.04 UEC' --flavor 1 --nic net-id=$nid vmS
