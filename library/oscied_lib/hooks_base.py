# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
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

from __future__ import absolute_import, division, print_function, unicode_literals

import os, pymongo.uri_parser, shutil, shlex, socket, time
from codecs import open
from pytoolbox.encoding import to_bytes
from pytoolbox.filesystem import chown, try_makedirs, try_remove
from pytoolbox.juju import CharmHooks

from .constants import DAEMON_GROUP, DAEMON_USER, LOCAL_CONFIG_FILENAME


class OsciedCharmHooks(CharmHooks):

    @property
    def paya_config_string(self):
        # Read the charm's config.yaml file and try to get the paya config string
        if hasattr(self.config, u'paya_config_string'):
            return self.config.paya_config_string
        return u''

    def __init__(self, metadata, default_config, default_os_env, local_config_filename, local_config_cls):
        super(OsciedCharmHooks, self).__init__(metadata, default_config, default_os_env)
        # Create the local configuration file if missing
        if not local_config_filename:
            local_config_filename = LOCAL_CONFIG_FILENAME
            local_config_cls().write(local_config_filename)
        self.local_config = local_config_cls.read(local_config_filename, store_filename=True, inspect_constructor=False)

    def generate_locales(self, locales):
        self.info(u'Generate locales if missing')
        self.cmd(u'locale-gen {0}'.format(u' '.join(locales)))
        self.cmd(u'dpkg-reconfigure locales')

    def install_packages(self, packages, ppas=None, upgrade=True, tries=3, delay_min=10, delay_max=20):
        self.info(u'Upgrade system and install prerequisites')
        retry_kwargs = {u'tries': tries, u'delay_min': delay_min, u'delay_max': delay_max}
        if ppas:
            for ppa in ppas:
                self.cmd(u'apt-add-repository -y {0}'.format(ppa), **retry_kwargs)
        self.cmd(u'apt-get -y update', **retry_kwargs)
        self.cmd(u'apt-get -y -f install', **retry_kwargs)  # May recover problems ...
        if upgrade:
            self.cmd(u'apt-get -y upgrade', **retry_kwargs)
        self.cmd(u'apt-get -y install {0}'.format(u' '.join(packages)), **retry_kwargs)

    def restart_ntp(self):
        self.info(u'Restart network time protocol service')
        self.cmd(u'service ntp restart')

    def start_paya(self, retry_count=15, retry_delay=1):
        if self.paya_config_string:
            config_list = shlex.split(to_bytes(self.paya_config_string))
            if screen_list(u'paya', log=self.debug, user=self.daemon_user) == []:            
                screen_launch(u'paya', [u'paya-monitor'] + config_list, user=self.daemon_user)
            for start_delay in xrange(retry_count):
                time.sleep(retry_delay)
                if screen_list(u'paya', log=self.debug, user=self.daemon_user) != []:
                    start_time = start_delay * retry_delay
                    self.remark(u'{0} successfully started in {1} seconds'.format(u'paya', start_time))
                    return
            raise RuntimeError(u'Monitor damon is not ready')
        else:
            self.remark(u'paya config string is not configured')

    def stop_paya(self):
        screen_kill(u'paya', log=self.debug, user=self.daemon_user)


class CharmHooks_Storage(OsciedCharmHooks):

    PACKAGES = (u'glusterfs-client', u'nfs-common')

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def storage_config_is_enabled(self):
        return self.config.storage_address and self.config.storage_fstype and self.config.storage_mountpoint

    @property
    def storage_is_mounted(self):
        return os.path.ismount(self.local_config.storage_path)

    # ------------------------------------------------------------------------------------------------------------------

    def storage_remount(self, address=None, fstype=None, mountpoint=None, options=u''):
        if self.storage_config_is_enabled:
            self.info(u'Override storage parameters with charm configuration')
            address = self.config.storage_address
            nat_address = self.config.storage_nat_address
            fstype = self.config.storage_fstype
            mountpoint = self.config.storage_mountpoint
            options = self.config.storage_options
        elif address and fstype and mountpoint:
            self.info(u'Use storage parameters from charm storage relation')
            nat_address = u''
        else:
            return
        if nat_address:
            self.info(u'Update hosts file to map storage internal address {0} to {1}'.format(address, nat_address))
            lines = filter(lambda l: nat_address not in l, open(self.local_config.hosts_file, u'r', u'utf-8'))
            lines += u'{0} {1}\n'.format(nat_address, address)
            open(self.local_config.hosts_file, u'w', u'utf-8').write(u''.join(lines))
        # Avoid unregistering and registering storage if it does not change ...
        if (address == self.local_config.storage_address and nat_address == self.local_config.storage_nat_address and
            fstype == self.local_config.storage_fstype and mountpoint == self.local_config.storage_mountpoint and
            options == self.local_config.storage_options):
            self.remark(u'Skip remount already mounted shared storage')
        else:
            self.storage_unregister()
            self.debug(u"Mount shared storage [{0}] {1}:{2} type {3} options '{4}' -> {5}".format(nat_address, address,
                       mountpoint, fstype, options, self.local_config.storage_path))
            try_makedirs(self.local_config.storage_path)
            # FIXME try X times, a better way to handle failure
            for i in xrange(self.local_config.storage_mount_max_retry):
                if self.storage_is_mounted:
                    break
                mount_address = u'{0}:/{1}'.format(nat_address or address, mountpoint)
                mount_path = self.local_config.storage_path
                if options:
                    self.cmd([u'mount', u'-t', fstype, u'-o', options, mount_address, mount_path])
                else:
                    self.cmd([u'mount', u'-t', fstype, mount_address, mount_path])
                time.sleep(self.local_config.storage_mount_sleep_delay)
            if self.storage_is_mounted:
                # FIXME update /etc/fstab (?)
                self.local_config.storage_address = address
                self.local_config.storage_nat_address = nat_address
                self.local_config.storage_fstype = fstype
                self.local_config.storage_mountpoint = mountpoint
                self.local_config.storage_options = options
                self.remark(u'Shared storage successfully registered')
                self.debug(u'Create directories in the shared storage and ensure it is owned by the right user')
                try_makedirs(self.local_config.storage_medias_path())
                try_makedirs(self.local_config.storage_uploads_path)
                chown(self.local_config.storage_path, DAEMON_USER, DAEMON_GROUP, recursive=True)
            else:
                raise IOError(to_bytes(u'Unable to mount shared storage'))

    def storage_unregister(self):
        self.info(u'Unregister shared storage')
        self.local_config.storage_address = u''
        self.local_config.storage_fstype = u''
        self.local_config.storage_mountpoint = u''
        self.local_config.storage_options = u''
        if self.storage_is_mounted:
            # FIXME update /etc/fstab (?)
            self.remark(u'Unmount shared storage (is mounted)')
            self.cmd([u'umount', self.local_config.storage_path])
        else:
            self.remark(u'Shared storage already unmounted')

    def storage_hook_bypass(self):
        if self.storage_config_is_enabled:
            raise RuntimeError(to_bytes(u'Shared storage is set in config, storage relation is disabled'))

    # ------------------------------------------------------------------------------------------------------------------

    def hook_storage_relation_joined(self):
        self.storage_hook_bypass()

    def hook_storage_relation_changed(self):
        self.storage_hook_bypass()
        address = socket.getfqdn(self.relation_get(u'private-address'))
        fstype = self.relation_get(u'fstype')
        mountpoint = self.relation_get(u'mountpoint')
        options = self.relation_get(u'options')
        self.debug(u'Storage address is {0}, fstype: {1}, mountpoint: {2}, options: {3}'.format(
                   address, fstype, mountpoint, options))
        if address and fstype and mountpoint:
            self.hook_stop()
            self.storage_remount(address, fstype, mountpoint, options)
            self.hook_start()
        else:
            self.remark(u'Waiting for complete setup')

    def hook_storage_relation_broken(self):
        self.storage_hook_bypass()
        self.hook_stop()
        self.storage_remount()


class CharmHooks_Subordinate(OsciedCharmHooks):

    PACKAGES = ()

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def rabbit_hostname(self):
        return u'{0}_{1}'.format(self.local_config.worker_name, self.public_address)

    @property
    def rabbit_queues(self):
        return u','.join([self.config.rabbit_queues, self.rabbit_hostname])

    @property
    def subordinate_config_is_enabled(self):
        return self.config.mongo_connection and self.config.rabbit_connection

    # ------------------------------------------------------------------------------------------------------------------

    def subordinate_register(self, mongo=None, rabbit=None):
        local_cfg = self.local_config
        if self.subordinate_config_is_enabled:
            self.info(u'Override subordinate parameters with charm configuration')
            mongo = self.config.mongo_connection
            rabbit = self.config.rabbit_connection
            socket = self.config.api_nat_socket
        elif mongo and rabbit:
            self.info(u'Use subordinate parameters from charm relation')
            socket = u''
        else:
            return
        self.info(u'Register the Orchestrator')
        local_cfg.api_nat_socket = socket
        try:
            infos = pymongo.uri_parser.parse_uri(mongo)
            assert len(infos[u'nodelist']) == 1
            infos.update({
                u'concurrency': self.config.concurrency, u'directory': self.directory,
                u'host': infos[u'nodelist'][0][0], u'port': infos[u'nodelist'][0][1],
                u'group': DAEMON_GROUP, u'name': local_cfg.worker_name, u'queues': self.rabbit_queues,
                u'rabbit': rabbit, u'user': DAEMON_USER
            })
            del infos[u'nodelist']
            self.info(u'{0}'.format(infos))
            for name in (u'concurrency', u'group', u'host', u'name', u'port', u'queues', u'rabbit', u'user'):
                assert infos[name], u'Info {0} is empty'.format(name)
        except:
            raise ValueError(to_bytes(u'Unable to parse MongoDB connection {0}'.format(mongo)))
        self.template2config(local_cfg.celery_init_template_file,    local_cfg.celery_init_file, {})
        self.template2config(local_cfg.celery_default_template_file, local_cfg.celery_default_file, infos)
        self.template2config(local_cfg.celery_config_template_file,  local_cfg.celery_config_file,  infos)
        os.chmod(local_cfg.celery_init_file, 755)
        self.cmd(u'update-rc.d {0} defaults'.format(local_cfg.worker_name))
        self.remark(u'Orchestrator successfully registered')

    def subordinate_unregister(self):
        self.info(u'Unregister the Orchestrator')
        self.local_config.api_nat_socket = u''
        try_remove(self.local_config.celery_config_file)
        self.cmd(u'update-rc.d -f {0} remove'.format(self.local_config.worker_name))

    def subordinate_hook_bypass(self):
        if self.subordinate_config_is_enabled:
            raise RuntimeError(to_bytes(u'Orchestrator is set in config, subordinate relation is disabled'))

    def start_celery_worker(self, retries=5, delay=2):
        worker_name = self.local_config.worker_name
        self.info(u'Start the {0} worker'.format(worker_name))

        self.info(u"Ensure that the worker's directory is owned by the right user")
        chown(self.directory, DAEMON_USER, DAEMON_GROUP, recursive=True)

        start_time = time.time()
        for start_delay in xrange(retries):
            if self.cmd(u'service {0} status'.format(worker_name), fail=False)[u'returncode'] == 0:
                delta_time = time.time() - start_time
                self.remark(u'Worker {0} successfully started in {1:0.1f} seconds'.format(worker_name, delta_time))
                return
            else:
                self.cmd(u'service {0} start'.format(worker_name))
                time.sleep(delay)
        # FIXME maybe the latest attempt was successful and we do not check ... hum
        raise RuntimeError(to_bytes(u'Worker {0} is not ready'.format(worker_name)))

    def stop_celery_worker(self):
        self.info(u'Stop the {0} worker'.format(self.local_config.worker_name))
        self.cmd(u'service {0} stop'.format(self.local_config.worker_name), fail=False)

    # ------------------------------------------------------------------------------------------------------------------

    def hook_subordinate_relation_joined(self):
        self.subordinate_hook_bypass()

    def hook_subordinate_relation_changed(self):
        self.subordinate_hook_bypass()
        address = socket.getfqdn(self.relation_get(u'private-address'))
        mongo = self.relation_get(u'mongo_connection')
        rabbit = self.relation_get(u'rabbit_connection')
        self.debug(u'Orchestra address is {0}, MongoDB is {1}, RabbitMQ is {2}'.format(address, mongo, rabbit))
        if address and mongo and rabbit:
            self.hook_stop()
            self.subordinate_register(mongo, rabbit)
            self.hook_start()
        else:
            self.remark(u'Waiting for complete setup')

    def hook_subordinate_relation_broken(self):
        self.subordinate_hook_bypass()
        self.hook_stop()
        self.subordinate_unregister()


class CharmHooks_Website(OsciedCharmHooks):

    PACKAGES = ()

    @property
    def proxy_ips_string(self):
        # Read the charm's config.yaml file proxy_ips option only if it does exist
        if hasattr(self.config, u'proxy_ips'):
            try:
                proxy_ips = self.config.proxy_ips.split(u',')
            except:
                proxy_ips = [self.config.proxy_ips]
        else:
            proxy_ips = []
        return u','.join(list(filter(None, self.local_config.proxy_ips + proxy_ips)))

    def hook_website_relation_joined(self):
        self.relation_set(port=u'80', hostname=self.cmd(u'hostname -f'))

    def hook_website_relation_changed(self):
        # Get configuration from the relation
        proxy_address = socket.getfqdn(self.relation_get(u'private-address'))
        self.info(u'Proxy address is {0}'.format(proxy_address))
        if not proxy_address:
            self.remark(u'Waiting for complete setup')
        elif not proxy_address in self.local_config.proxy_ips:
            self.info(u'Add {0} to allowed proxy IPs'.format(proxy_address))
            self.hook_stop()
            self.local_config.proxy_ips.append(proxy_address)
            self.save_local_config()
            self.hook_config_changed()
            self.hook_start()

    def hook_website_relation_departed(self):
        # Get configuration from the relation
        proxy_address = socket.getfqdn(self.relation_get(u'private-address'))
        if not proxy_address:
            self.remark(u'Waiting for complete setup')
        elif proxy_address in self.local_config.proxy_ips:
            self.info(u'Remove {0} from allowed proxy IPs'.format(proxy_address))
            self.hook_stop()
            self.local_config.proxy_ips.remove(proxy_address)
            self.save_local_config()
            self.hook_config_changed()
            self.hook_start()
