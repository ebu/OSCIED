#!/usr/bin/env python
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

import os, re, shutil, socket, time
from codecs import open
from configobj import ConfigObj
from os.path import abspath, dirname, exists, join
from pytoolbox.encoding import to_bytes
from pytoolbox.filesystem import chown, first_that_exist, try_makedirs, try_symlink
from pytoolbox.juju import CONFIG_FILENAME, METADATA_FILENAME, DEFAULT_OS_ENV
from pytoolbox.subprocess import rsync

from .api import VERSION
from .config import OrchestraLocalConfig
from .constants import DAEMON_GROUP, DAEMON_USER, LOCAL_CONFIG_FILENAME
from .hooks_base import CharmHooks_Storage


class OrchestraHooks(CharmHooks_Storage):

    PPAS = (u'ppa:jon-severinsson/ffmpeg', u'ppa:juju/stable')
    PACKAGES = tuple(set(CharmHooks_Storage.PACKAGES + (u'apache2', u'ffmpeg', u'libapache2-mod-wsgi', u'mongodb',
                     u'ntp', u'rabbitmq-server', u'x264')))
    FIX_PACKAGES = (u'apache2.2-common',)
    JUJU_PACKAGES = (u'juju-core',)

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(OrchestraHooks, self).__init__(metadata, default_config, default_os_env, local_config_filename,
                                             OrchestraLocalConfig)
        self.rsync_kwargs = {
            u'archive': True, u'delete': True, u'exclude_vcs': True, u'makedest': True, u'recursive': True,
            u'extra_args': [u'--copy-links'], u'log': self.log
        }

    def save_local_config(self):
        u"""Save or update local configuration in charm's and api's path and ensure that is owned by the right user."""
        super(OrchestraHooks, self).save_local_config()
        self.local_config.write(self.local_config.site_local_config_file, makedirs=True)
        chown(self.local_config.site_local_config_file, DAEMON_USER, DAEMON_GROUP)

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def api_alias(self):
        return u'api/{0}'.format(VERSION)

    def api_url(self, local=False):
        return u'http://{0}:80/{1}'.format(u'127.0.0.1' if local else self.private_address, self.api_alias)

    @property
    def mongo_admin_connection(self):
        return u'mongodb://admin:{0}@localhost:27017/orchestra'.format(self.config.mongo_admin_password)

    @property
    def mongo_node_connection(self):
        return u'mongodb://node:{0}@{1}:27017/celery'.format(self.config.mongo_node_password, self.private_address)

    @property
    def rabbit_connection(self):
        return u'amqp://node:{0}@{1}:5672/celery'.format(self.config.rabbit_password, self.private_address)

    @property
    def rabbit_users(self):
        stdout = self.cmd(u'rabbitmqctl list_users', fail=False)[u'stdout']
        return re.findall(u'^([a-z]+)\s+.*$', stdout, re.MULTILINE)

    @property
    def rabbit_vhosts(self):
        stdout = self.cmd(u'rabbitmqctl list_vhosts', fail=False)[u'stdout']
        return re.findall(u'^([a-z]+)$', stdout, re.MULTILINE)

    # ------------------------------------------------------------------------------------------------------------------

    def configure_rabbitmq(self):
        self.info(u'Configure RabbitMQ Message Broker')
        self.cmd(u'rabbitmqctl delete_user guest', fail=False)
        self.cmd(u'rabbitmqctl delete_vhost /', fail=False)
        self.cmd(u'rabbitmqctl add_user node "{0}"'.format(self.config.rabbit_password), fail=False)
        self.cmd(u'rabbitmqctl add_vhost celery', fail=False)
        self.cmd(u'rabbitmqctl set_permissions -p celery node ".*" ".*" ".*"', fail=False)
        users, vhosts = self.rabbit_users, self.rabbit_vhosts
        self.debug(u'RabbitMQ users: {0} vhosts: {1}'.format(users, vhosts))
        if u'guest' in users or u'node' not in users or u'/' in vhosts or u'celery' not in vhosts:
            raise RuntimeError(to_bytes(u'Unable to configure RabbitMQ'))

    # ------------------------------------------------------------------------------------------------------------------

    def hook_install(self):
        local_cfg = self.local_config

        self.hook_uninstall()
        self.generate_locales((u'fr_CH.UTF-8',))
        self.install_packages(OrchestraHooks.PACKAGES + OrchestraHooks.JUJU_PACKAGES, ppas=OrchestraHooks.PPAS)
        self.restart_ntp()
        self.info(u'Copy Orchestra and the local charms repository of OSCIED')
        rsync(local_cfg.api_path, local_cfg.site_directory, **self.rsync_kwargs)
        chown(local_cfg.site_directory, DAEMON_USER, DAEMON_GROUP, recursive=True)
        self.info(u'Expose RESTful API, MongoDB & RabbitMQ service')
        self.open_port(80,    u'TCP')  # Orchestra RESTful API
        self.open_port(27017, u'TCP')  # MongoDB port mongod and mongos instances
        #self.open_port(27018, u'TCP') # MongoDB port when running with shardsvr setting
        #self.open_port(27019, u'TCP') # MongoDB port when running with configsvr setting
        #self.open_port(28017, u'TCP') # MongoDB port for the web status page. This is always +1000
        self.open_port(5672,  u'TCP')  # RabbitMQ service

    def hook_config_changed(self):
        cfg, local_cfg = self.config, self.local_config

        self.info(u'Start MongoDB and RabbitMQ daemons')
        self.cmd(u'service mongodb start',         fail=False)
        self.cmd(u'service rabbitmq-server start', fail=False)

        self.info(u'Configure JuJu Service Orchestrator')
        juju_config_path = dirname(local_cfg.juju_config_file)
        rsync(local_cfg.juju_template_path, juju_config_path, **self.rsync_kwargs)
        chown(juju_config_path, DAEMON_USER, DAEMON_GROUP, recursive=True)

        self.info(u'Configure Secure Shell')
        rsync(local_cfg.ssh_template_path, local_cfg.ssh_config_path, **self.rsync_kwargs)
        chown(local_cfg.ssh_config_path, DAEMON_USER, DAEMON_GROUP, recursive=True)

        self.info(u'Configure Apache 2')
        self.template2config(local_cfg.htaccess_template_file, local_cfg.htaccess_config_file, {})
        self.template2config(local_cfg.site_template_file, join(local_cfg.sites_available_path, self.name_slug), {
            u'alias': self.api_alias, u'directory': local_cfg.site_directory, u'domain': self.public_address,
            u'wsgi': local_cfg.api_wsgi
        })
        self.cmd(u'a2dissite default')
        self.cmd(u'a2ensite {0}'.format(self.name_slug))

        self.info(u'Configure MongoDB Scalable NoSQL DB')
        with open(u'f.js', u'w', u'utf-8') as mongo_f:
            mongo_f.write(u"db.addUser('admin', '{0}', false);".format(cfg.mongo_admin_password))
        with open(u'g.js', u'w', u'utf-8') as mongo_g:
            mongo_g.write(u"db.addUser('node', '{0}', false);".format(cfg.mongo_node_password))
        self.cmd(u'mongo f.js')
        self.cmd(u'mongo orchestra f.js')
        self.cmd(u'mongo celery g.js')
        [os.remove(f) for f in (u'f.js', u'g.js')]

        mongo_config = ConfigObj(local_cfg.mongo_config_file)
        mongo_config[u'bind_ip'] = u'0.0.0.0'
        mongo_config[u'noauth'] = u'false'
        mongo_config[u'auth'] = u'true'
        mongo_config.write()

        self.configure_rabbitmq()

        if cfg.plugit_api_url:
            self.info(u'Configure PlugIt server')
            infos = {
                u'api_url': cfg.plugit_api_url, u'debug': cfg.verbose, u'base_url': cfg.plugit_base_url,
                u'allowed_networks': u'", "'.join(cfg.plugit_allowed_networks.split(u','))
            }
            self.template2config(local_cfg.plugit_template_file, local_cfg.plugit_config_file, infos)

        self.info(u'Configure Orchestra the Orchestrator')
        local_cfg.verbose = cfg.verbose
        local_cfg.api_url = self.api_url(local=False)
        local_cfg.charms_release = cfg.charms_release
        local_cfg.node_secret = cfg.node_secret
        local_cfg.root_secret = cfg.root_secret
        local_cfg.mongo_admin_connection = self.mongo_admin_connection
        local_cfg.mongo_node_connection = self.mongo_node_connection
        local_cfg.rabbit_connection = self.rabbit_connection
        infos = {
            u'rabbit': unicode(self.rabbit_connection),
            u'port': unicode(27017),
            u'username': u'node',
            u'password': unicode(cfg.mongo_node_password),
        }
        self.template2config(local_cfg.celery_template_file, local_cfg.celery_config_file, infos)
        local_cfg.email_server = cfg.email_server
        local_cfg.email_tls = cfg.email_tls
        local_cfg.email_address = cfg.email_address
        local_cfg.email_username = cfg.email_username
        local_cfg.email_password = cfg.email_password
        local_cfg.plugit_api_url = cfg.plugit_api_url
        self.remark(u'Orchestrator successfully configured')

        self.info(u'Symlink charms default directory to directory for release {0}'.format(cfg.charms_release))
        try_symlink(abspath(local_cfg.charms_default_path), abspath(local_cfg.charms_release_path))

        self.info(u'Ensure that the Apache sites directory is owned by the right user')
        chown(local_cfg.sites_directory, DAEMON_USER, DAEMON_GROUP, recursive=True)

        self.storage_remount()

    def hook_uninstall(self):
        self.info(u'Uninstall prerequisities, unregister service and load default configuration')
        self.hook_stop()
        try_makedirs(u'/var/log/rabbitmq')  # Fix rabbitmq-server package uninstall error
        #self.cmd('juju destroy-environment')
        #self.cmd('... --purge apt-cacher-ng charm-tools juju libzookeeper-java lxc zookeeper')
        self.storage_unregister()
        if self.config.cleanup:
            self.cmd(u'apt-get -y remove --purge {0}'.format(u' '.join(OrchestraHooks.PACKAGES)))
            self.cmd(u'apt-get -y remove --purge {0}'.format(u' '.join(OrchestraHooks.FIX_PACKAGES)), fail=False)
            self.cmd(u'apt-get -y autoremove')
            #shutil.rmtree('$HOME/.juju $HOME/.ssh/id_rsa*
            shutil.rmtree(u'/etc/apache2/',      ignore_errors=True)
            shutil.rmtree(u'/var/log/apache2/',  ignore_errors=True)
            shutil.rmtree(u'/etc/rabbitmq/',     ignore_errors=True)
            shutil.rmtree(u'/var/log/rabbitmq/', ignore_errors=True)
            shutil.rmtree(self.local_config.site_directory, ignore_errors=True)
        self.local_config.reset()

    def hook_start(self):
        if not self.storage_is_mounted:
            self.remark(u'Do not start orchestra daemon : No shared storage')
        elif not exists(self.local_config.celery_config_file):
            self.remark(u'Do not start orchestra daemon : No celery configuration file')
        else:
            self.save_local_config()  # Update local configuration file for orchestra daemon
            self.start_paya()  # Start paya monitoring (if paya_config_string set in config.yaml)

            # do not check status after all, orchestra can do it for us !
            self.cmd(u'service mongodb start',         fail=False)
            self.cmd(u'service rabbitmq-server start', fail=False)
            # FIXME this is not a good idea, but I have some trouble with precise release
            self.configure_rabbitmq()  # (see ticket #205 of my private TRAC ticket system)
            self.cmd(u'service apache2 start')
            for start_delay in xrange(15):
                time.sleep(1)
                if self.cmd(u'curl -s {0}'.format(self.api_url(local=True)), fail=False)[u'returncode'] == 0:
                    self.remark(u'Orchestra successfully started in {0} seconds'.format(start_delay))
                    return
            raise RuntimeError(to_bytes(u'Orchestra is not ready'))

    def hook_stop(self):
        self.cmd(u'service apache2 stop',         fail=False)
        self.cmd(u'service rabbitmq-server stop', fail=False)
        self.cmd(u'service mongodb stop',         fail=False)
        self.stop_paya()

    def hook_api_relation_joined(self):
        self.relation_set(api_url=self.api_url(local=False))

    def hook_api_relation_changed(self):
        # Get configuration from the relation
        webui_address = socket.getfqdn(self.relation_get(u'private-address'))
        self.info(u'Web UI address is {0}'.format(webui_address))
        if not webui_address:
            self.remark(u'Waiting for complete setup')
            return
        # FIXME something to do (register unit ?)

    def hook_publisher_relation_joined(self):
        self.relation_set(mongo_connection=self.mongo_node_connection, rabbit_connection=self.rabbit_connection)

    def hook_publisher_relation_changed(self):
        # Get configuration from the relation
        publisher_address = socket.getfqdn(self.relation_get(u'private-address'))
        self.info(u'Publisher address is {0}'.format(publisher_address))
        if not publisher_address:
            self.remark(u'Waiting for complete setup')
            return
        # FIXME something to do (register unit ?)

    def hook_transform_relation_joined(self):
        self.relation_set(mongo_connection=self.mongo_node_connection, rabbit_connection=self.rabbit_connection)

    def hook_transform_relation_changed(self):
        # Get configuration from the relation
        transform_address = socket.getfqdn(self.relation_get(u'private-address'))
        self.info(u'Transform address is {0}'.format(transform_address))
        if not transform_address:
            self.remark(u'Waiting for complete setup')
            return
        # FIXME something to do (register unit ?)

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pytoolbox.encoding import configure_unicode
    configure_unicode()
    orchestra_path = abspath(join(dirname(__file__), u'../../charms/oscied-orchestra'))
    OrchestraHooks(first_that_exist(METADATA_FILENAME,     join(orchestra_path, METADATA_FILENAME)),
                   first_that_exist(CONFIG_FILENAME,       join(orchestra_path, CONFIG_FILENAME)),
                   first_that_exist(LOCAL_CONFIG_FILENAME, join(orchestra_path, LOCAL_CONFIG_FILENAME)),
                   DEFAULT_OS_ENV).trigger()
