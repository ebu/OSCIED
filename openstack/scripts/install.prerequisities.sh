#!/usr/bin/env bash

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : CLOUD
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
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
# Retrieved from https://github.com/ebu/OSCIED

. ./common.sh

pecho 'Enable the Cloud Archive repository for Ubuntu'
release=$(cat /etc/lsb-release | grep DISTRIB_CODENAME | cut -d'=' -f2)
if [ "$release" = 'precise' ]; then
  deb='http://ubuntu-cloud.archive.canonical.com/ubuntu'
  $udo sh -c "echo 'deb $deb precise-updates/folsom main' > /etc/apt/sources.list.d/folsom.list"
  eval $install ubuntu-cloud-keyring || xecho 'Unable to install ubuntu cloud keyring'
else
  recho "Ubuntu Cloud Archive not necessary for release $release"
fi

pecho 'Enable OpenStack Ubuntu Testers repository for Ubuntu'
deb='http://ppa.launchpad.net/openstack-ubuntu-testing/folsom-trunk-testing/ubuntu'
$udo sh -c "echo 'deb $deb quantal main' > /etc/apt/sources.list.d/folsom-testing.list"
$udo apt-key adv --recv-keys --keyserver keyserver.ubuntu.com '81DCD8423B6F61A6' || \
 xecho 'Unable to receive gpg key'

eval $update
eval $upgrade
eval $install debconf-utils python-cliff python-greenlet python-mysqldb python-pyparsing \
  python-sqlalchemy || xecho 'Unable to install common prerequisities'

# http://serverfault.com/questions/252333/list-all-packages-from-a-repository-in-ubuntu-debian
#packages='ubuntu-cloud.archive.canonical.'
#packages+='com_ubuntu_dists_precise-updates_folsom_main_binary-amd64_Packages'
#cat /var/lib/apt/lists/$packages | grep Package

#Package: cinder-api
#Package: cinder-common
#Package: cinder-scheduler
#Package: cinder-volume
#Package: cliff-tablib
#Package: euca2ools
#Package: glance
#Package: glance-api
#Package: glance-client
#Package: glance-common
#Package: glance-registry
#Package: keystone
#Package: keystone-doc
#Package: libvirt-bin
#Package: libvirt-dev
#Package: libvirt-doc
#Package: libvirt0
#Package: libvirt0-dbg
#Package: nova-ajax-console-proxy
#Package: nova-api
#Package: nova-api-ec2
#Package: nova-api-metadata
#Package: nova-api-os-compute
#Package: nova-api-os-volume
#Package: nova-cert
#Package: nova-common
#Package: nova-compute
#Package: nova-compute-kvm
#Package: nova-compute-lxc
#Package: nova-compute-qemu
#Package: nova-compute-uml
#Package: nova-compute-xcp
#Package: nova-compute-xen
#Package: nova-console
#Package: nova-consoleauth
#Package: nova-doc
#Package: nova-network
#Package: nova-novncproxy
#Package: nova-objectstore
#Package: nova-scheduler
#Package: nova-vncproxy
#Package: nova-volume
#Package: nova-xcp-network
#Package: nova-xcp-plugins
#Package: nova-xvpvncproxy
#Package: novnc
#Package: openstack-dashboard
#Package: openstack-dashboard-ubuntu-theme
#Package: pep8
#Package: python-appconf
#Package: python-cinder
#Package: python-cinderclient
#Package: python-cliff
#Package: python-compressor
#Package: python-django
#Package: python-django-doc
#Package: python-django-horizon
#Package: python-django-openstack
#Package: python-django-openstack-auth
#Package: python-eventlet
#Package: python-glance
#Package: python-glance-doc
#Package: python-glanceclient
#Package: python-greenlet
#Package: python-greenlet-dbg
#Package: python-greenlet-dev
#Package: python-greenlet-doc
#Package: python-jsonschema
#Package: python-keystone
#Package: python-keystoneclient
#Package: python-libvirt
#Package: python-mock
#Package: python-mock-doc
#Package: python-nova
#Package: python-novaclient
#Package: python-novnc
#Package: python-openstack-auth
#Package: python-prettytable
#Package: python-quantum
#Package: python-quantumclient
#Package: python-setuptools-git
#Package: python-sqlalchemy
#Package: python-sqlalchemy-doc
#Package: python-sqlalchemy-ext
#Package: python-swift
#Package: python-swiftclient
#Package: python-tablib
#Package: python-warlock
#Package: python3-mock
#Package: python3-prettytable
#Package: python3-sqlalchemy
#Package: quantum-common
#Package: quantum-dhcp-agent
#Package: quantum-l3-agent
#Package: quantum-plugin-cisco
#Package: quantum-plugin-linuxbridge
#Package: quantum-plugin-linuxbridge-agent
#Package: quantum-plugin-metaplugin
#Package: quantum-plugin-nec
#Package: quantum-plugin-nicira
#Package: quantum-plugin-openvswitch
#Package: quantum-plugin-openvswitch-agent
#Package: quantum-plugin-ryu
#Package: quantum-plugin-ryu-agent
#Package: quantum-server
#Package: swift
#Package: swift-account
#Package: swift-container
#Package: swift-doc
#Package: swift-object
#Package: swift-plugin-s3
#Package: swift-proxy
#Package: websockify

