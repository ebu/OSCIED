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
import re
from lib.CharmHooks import CharmHooks
from shelltoolbox import apt_get_install


class StorageHooks(CharmHooks):

    def __init__(self, default_config):
        super(StorageHooks, self).__init__(default_config)
        self.volume_flag = os.path.join(os.getcwd(), 'volume_ok')

    @property
    def brick(self):
        return '%s:/exp1' % self.private_address

    @property
    def volume(self):
        return 'medias_volume_%s' % self.id

    @property
    def volumes(self):
        return re.findall('Name:\s*(\S*)', self.cmd('gluster volume info')['stdout'])

    # ----------------------------------------------------------------------------------------------

    def peer_probe(self, peer_address, fail=True):
        return self.cmd('gluster peer probe %s' % peer_address)

    def volume_create(self, volume=None, bricks=None, replica=None, fail=True):
        if volume is None:
            volume = self.volume
        if bricks is None:
            bricks = [self.brick]
        if replica is None:
            replica = self.replica_count
        if replica % len(bricks) != 0:
            raise ValueError('Cannot create a replica=%s volume with %s bricks' %
                             (replica, len(bricks)))
        extra = (' ' if replica == 1 else ' replica %s transport tcp ' % replica) + ' '.join(bricks)
        return self.cmd('gluster volume create %s%s' % (volume, extra), fail=fail)

    def volume_do(self, action, volume=None, input=None, cli_input=None, fail=True):
        if volume is None:
            volume = self.volume
        return self.cmd('gluster volume %s %s' % (action, volume), input=input, cli_input=cli_input,
                        fail=fail)

    # ----------------------------------------------------------------------------------------------

    def hook_install(self):
        self.info('Install prerequisities')
        apt_get_install('ntp', 'glusterfs-server', 'nfs-common')
        self.info('Upgrade packages')
        self.cmd('apt-get -y upgrade')
        self.info('Restart network time protocol service')
        self.cmd('service ntp restart')

        if self.replica_count == 1:
            for volume in self.volumes:
                self.info('Remove previously created medias volume %s' % volume)
                self.volume_do('delete', volume=volume, cli_input='y\n')
            self.info('Create and start medias volume %s with 1 brick (no redundancy at all)' %
                      self.volume)
            self.volume_create()
            print(self.volume_do('info')['stdout'])
            open(self.volume_flag, 'w').close()
        else:
            self.remark("Waiting for %s peers to create and start medias volume %s" %
                        (self.replica_count - 1, self.volume))
            os.remove(self.volume_flag)

        self.info('Expose GlusterFS Server service')
        self.open_port(111, 'TCP')     # Is used for portmapper, and should have both TCP and UDP open
        self.open_port(24007, 'TCP')   # For the Gluster Daemon
        #open_port(24008, 'TCP')  # Infiniband management (optional unless you are using IB)
        self.open_port(24009, 'TCP')   # We have only 1 storage brick (24009-24009)
        #open_port(38465, 'TCP')  # For NFS (not used)
        #open_port(38466, 'TCP')  # For NFS (not used)
        #open_port(38467, 'TCP')  # For NFS (not used)

    def hook_uninstall(self):
        self.hook_stop()
        self.cmd('apt-get -y remove --purge glusterfs-server nfs-common')
        self.cmd('apt-get -y autoremove')

    def hook_start(self):
        if self.cmd('pgrep glusterd', fail=False)['returncode'] != 0:
            self.cmd('service glusterfs-server start')

    def hook_stop(self):
        if self.cmd('pgrep glusterd', fail=False)['returncode'] == 0:
            self.cmd('service glusterfs-server stop')

    def hook_storage_relation_joined(self):
        # Send file-system type, mount point & options only if volume is created and started
        if os.path.exists(self.volume_flag):
            self.relation_set(fstype='glusterfs', mountpoint=self.volume, options='')
        else:
            self.relation_set(fstype='', mountpoint='', options='')

    def debug_peer_relation(self):
        if self.verbose:
            self.debug('Peer relation settings:'); self.debug(self.relation_get())
            self.debug('Peer relation members:');  self.debug(self.relation_list())

    def hook_peer_relation_joined(self):
        self.debug_peer_relation()
        if not self.peer_i_am_leader():
            self.info('As slave, stop and delete my own volume %s' % self.volume)
            if self.volume_exist():
                self.volume_do('stop', cli_input='y\n')
                self.volume_do('delete', cli_input='y\n')
                os.remove(self.volume_flag)

    def hook_peer_relation_changed(self):
        self.debug_peer_relation()

        # Get configuration from the relation
        peer_address = self.relation_get('private-address')
        self.info('Peer address is %s' % peer_address)
        if not peer_address:
            self.remark('Waiting for complete setup')
            return

        # FIXME close previously opened ports if some bricks leaved ...
        self.info('Open required ports')
        count = 1
        bricks = [self.brick]
        for peer in self.relation_list():
            self.open_port(24009 + count, 'TCP')  # Open required
            peer_address = self.relation_get('private-address', peer)
            bricks.append('%s:/exp1' % peer_address)
            count += 1

        if self.peer_i_am_leader():
            self.info('As leader, probe remote peer %s' % peer_address)
            self.peer_probe(peer_address)
            if len(bricks) < self.replica_count:
                self.remark('Waiting for %s peers to create and start medias volume %s' %
                            (self.replica_count - 1, self.volume))
            else:
                self.info('Create and start medias volume %s with %s bricks' %
                          (self.volume, len(bricks)))
                self.info('Bricks are %s' % bricks)
                self.volume_create(bricks=bricks)
                self.volume_do('start')
                print(self.volume_do('info')['stdout'])
                open(self.volume_flag, 'w').close()
            # FIXME handle addition of more peers when volume is already created and started !
            #gluster volume add-brick "$VOLUME_NAME" "$ip:/$BRICK_NAME" || \
            #  xecho 'Unable to add remote peer brick to medias volume' 4

    def hook_peer_relation_broken(self):
        self.debug_peer_relation()
        self.remark('FIXME NOT IMPLEMENTED')

if __name__ == '__main__':
    StorageHooks('config.yaml').trigger()
