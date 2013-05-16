#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : STORAGE
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
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
# Retrieved from https://github.com/EBU-TI/OSCIED

import os
from charmhelpers import get_config, open_port, unit_get, relation_get, relation_list, relation_set
from shelltoolbox import apt_get_install, run
from lib.hooks_utils import logd, logm, logp, logr, logt, peer_i_am_leader

BASE_PATH = os.getcwd()
VOLUME_FLAG = os.path.join(BASE_PATH, 'volume_ok')

UNIT_ID = "TODO ${JUJU_UNIT_NAME##*/}"
PRIVATE_IP = unit_get('private-address')
VOLUME_NAME = "medias_volume_%s" % UNIT_ID

config = get_config()
VERBOSE = config['verbose']
REPLICA_COUNT = config['replica_count']


def hook_install():
    logt('Storage - install')
    apt_get_install('ntp', 'glusterfs-server', 'nfs-common')
    run('apt-get', '-y', 'upgrade')
    logp('Restart network time protocol service')
    run('service', 'ntp', 'restart')

    if REPLICA_COUNT == 1:
        logp('Create and start medias volume %s with 1 brick (no redudancy at all)' % VOLUME_NAME)
        run('gluster', 'volume', 'create', VOLUME_NAME, '%s:/exp1' % PRIVATE_IP)
        run('gluster', 'volume', 'start', VOLUME_NAME)
        run('gluster', 'volume', 'info')
        open(VOLUME_FLAG, 'w').close()
    else:
        logr("Waiting for %s peers to create and start medias volume %s" %
             (REPLICA_COUNT - 1, VOLUME_NAME))

    logp('Expose GlusterFS Server service')
    open_port(111, 'TCP')     # Is used for portmapper, and should have both TCP and UDP open
    open_port(24007, 'TCP')   # For the Gluster Daemon
    #open_port(24008, 'TCP')  # Infiniband management (optional unless you are using IB)
    open_port(24009, 'TCP')   # We have only 1 storage brick (24009-24009)
    #open_port(38465, 'TCP')  # For NFS (not used)
    #open_port(38466, 'TCP')  # For NFS (not used)
    #open_port(38467, 'TCP')  # For NFS (not used)


def hook_uninstall():
    logt('Storage - uninstall')
    hook_stop()
    run('apt-get', '-y', 'remove', '--purge', 'glusterfs-server', 'nfs-common')
    run('apt-get', '-y', 'autoremove')


def hook_start():
    logt('Storage - start')
    if not run('pgrep', 'glusterd'):
        run('service', 'glusterfs-server', 'start')


def hook_stop():
    logt('Storage - stop')
    if run('pgrep', 'glusterd'):
        run('service', 'glusterfs-server', 'stop')


def hook_storage_relation_joined():
    logt('Storage - storage relation joined')
    # Send file-system type, mount point & options only if volume is created and started
    if os.path.exists(VOLUME_FLAG):
        relation_set(fstype='glusterfs', mountpoint=VOLUME_NAME, options='')
    else:
        relation_set(fstype='', mountpoint='', options='')


def debug_peer_relation():
    if VERBOSE:
        logd('Peer relation settings:')
        logd(relation_get())
        logd('Peer relation members:')
        logd(relation_list())


def hook_peer_relation_joined():
    logt('Storage - peer relation joined')
    debug_peer_relation()
    if not peer_i_am_leader():
        logp('As slave, stop and delete my own volume %s' % VOLUME_NAME)
        try:
            run('gluster', 'volume', 'info', VOLUME_NAME)
            exist = True
        except:
            exist = False
        if exist:
            run('gluster', 'volume', 'stop', VOLUME_NAME)
            run('gluster', 'volume', 'delete', VOLUME_NAME)
            os.remove(VOLUME_FLAG)


def hook_peer_relation_changed():
    logt('Storage - peer relation changed')
    debug_peer_relation()

    # Get configuration from the relation
    peer_ip = relation_get('private-address')
    logm('Peer IP is %s' % peer_ip)
    if not peer_ip:
        logr('Waiting for complete setup')
        return

    # FIXME close previously opened ports if some bricks leaved ...
    logp('Open required ports')
    count = 1
    bricks = '%s:/exp1' % PRIVATE_IP
    for peer in relation_list():
        open_port(24009 + count, 'TCP')  # Open required
        peer_ip = relation_get('private-address', peer)
        bricks.append('%s:/exp1' % peer_ip)
        count += 1

    if peer_i_am_leader():
        logp('As leader, probe remote peer %s' % peer_ip)
        run('gluster', 'peer', 'probe', peer_ip)
        if len(bricks) < REPLICA_COUNT:
            logr('Waiting for %s peers to create and start medias volume %s' %
                 (REPLICA_COUNT-1, VOLUME_NAME))
        else:
            logp('Create and start medias volume %s with %s bricks' % (VOLUME_NAME, len(bricks)))
            logm('Bricks are %s' % bricks)
            run('gluster', 'volume', 'create', VOLUME_NAME, 'replica', REPLICA_COUNT, 'transport',
                'tcp', *bricks)
            run('gluster', 'volume', 'start', VOLUME_NAME)
            run('gluster', 'volume', 'info')
            open(VOLUME_FLAG, 'w').close()
        # FIXME handle addition of more peers when volume is already created and started !
        #gluster volume add-brick "$VOLUME_NAME" "$ip:/$BRICK_NAME" || \
        #  xecho 'Unable to add remote peer brick to medias volume' 4


def hook_peer_relation_broken():
    logt('Storage - peer relation broken')
    debug_peer_relation()
    logr('FIXME NOT IMPLEMENTED')
