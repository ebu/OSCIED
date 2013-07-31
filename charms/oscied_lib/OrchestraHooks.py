#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
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

import os, re, shutil, time
from configobj import ConfigObj
from CharmHooks import DEFAULT_OS_ENV
from CharmHooks_Storage import CharmHooks_Storage
from OrchestraConfig import OrchestraConfig
from pyutils.filesystem import first_that_exist, try_makedirs
from pyutils.pyutils import rsync, screen_launch, screen_list, screen_kill


class OrchestraHooks(CharmHooks_Storage):

    PACKAGES = tuple(set(CharmHooks_Storage.PACKAGES +
                     ('ffmpeg', 'ntp', 'x264', 'mongodb', 'rabbitmq-server')))
    JUJU_PACKAGES = ('juju', 'juju-jitsu')

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(OrchestraHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = OrchestraConfig.read(local_config_filename, store_filename=True)
        self.debug('My __dict__ is %s' % self.__dict__)

    # ----------------------------------------------------------------------------------------------

    @property
    def api_standalone(self):
        return self.config.plugit_api_url is None or not self.config.plugit_api_url.strip()

    @property
    def api_filename(self):
        return 'orchestra.py' if self.api_standalone else 'server.py'

    @property
    def api_url(self):
        return 'http://{0}:5000{1}'.format(self.private_address, '' if self.api_standalone else '/action')

    @property
    def api_local_url(self):
        return 'http://127.0.0.1:5000{0}'.format('' if self.api_standalone else '/action')

    @property
    def mongo_admin_connection(self):
        return 'mongodb://admin:%s@localhost:27017/orchestra' % self.config.mongo_admin_password

    @property
    def mongo_nodes_connection(self):
        return 'mongodb://nodes:%s@%s:27017/celery' % \
            (self.config.mongo_nodes_password, self.private_address)

    @property
    def rabbit_connection(self):
        return 'amqp://nodes:%s@%s:5672/celery' % \
            (self.config.rabbit_password, self.private_address)

    @property
    def rabbit_users(self):
        stdout = self.cmd('rabbitmqctl list_users', fail=False)['stdout']
        return re.findall('^([a-z]+)\s+.*$', stdout, re.MULTILINE)

    @property
    def rabbit_vhosts(self):
        stdout = self.cmd('rabbitmqctl list_vhosts', fail=False)['stdout']
        return re.findall('^([a-z]+)$', stdout, re.MULTILINE)

    # ----------------------------------------------------------------------------------------------

    def configure_rabbitmq(self):
        self.info('Configure RabbitMQ Message Broker')
        self.cmd('rabbitmqctl delete_user guest', fail=False)
        self.cmd('rabbitmqctl delete_vhost /', fail=False)
        self.cmd('rabbitmqctl add_user nodes "%s"' % self.config.rabbit_password, fail=False)
        self.cmd('rabbitmqctl add_vhost celery', fail=False)
        self.cmd('rabbitmqctl set_permissions -p celery nodes ".*" ".*" ".*"', fail=False)
        users = self.rabbit_users
        vhosts = self.rabbit_vhosts
        self.debug('RabbitMQ users: %s vhosts: %s' % (users, vhosts))
        if 'guest' in users or 'nodes' not in users or '/' in vhosts or 'celery' not in vhosts:
            raise RuntimeError('Unable to configure RabbitMQ')

    # ----------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info('Upgrade system and install prerequisites')
        self.cmd('apt-add-repository -y ppa:jon-severinsson/ffmpeg')
        self.cmd('apt-add-repository -y ppa:juju/pkgs')
        self.cmd('apt-get -y update', fail=False)
        self.cmd('apt-get -y upgrade')
        self.cmd('apt-get -y install %s' % ' '.join(OrchestraHooks.PACKAGES))
        self.cmd('apt-get -y install %s' % ' '.join(OrchestraHooks.JUJU_PACKAGES))
        self.info('Restart network time protocol service')
        self.cmd('service ntp restart')
        #pecho 'Checkout OSCIED charms locally'
        #eval $install subversion || xecho 'Unable to install packages' 5
        #setSettingBASH "$SVN_SERVERS_FILE" $true 'store-passwords'           'yes' || exit 6
        #setSettingBASH "$SVN_SERVERS_FILE" $true 'store-plaintext-passwords' 'yes' || exit 7
        #setSettingBASH "$SVN_SERVERS_FILE" $true 'store-ssl-client-cert-pp'  'yes' || exit 8
        #setSettingBASH "$SVN_SERVERS_FILE" $true 'store-ssl-client-cert-pp-plaintext' 'yes' || x 9
        #mkdir -p "$SVN_CERTIFS_PATH"; cp -f "$REPOS_CERTIF_FILE" "$SVN_CERTIFS_PATH/"
        #checkout "$WEBUI_REPO"     "$WEBUI_PATH"     "$REPOS_USER" "$REPOS_PASS" || exit 10
        #checkout "$TRANSFORM_REPO" "$TRANSFORM_PATH" "$REPOS_USER" "$REPOS_PASS" || exit 11
        #checkout "$PUBLISHER_REPO" "$PUBLISHER_PATH" "$REPOS_USER" "$REPOS_PASS" || exit 12
        self.info('Expose RESTful API, MongoDB & RabbitMQ service')
        self.open_port(5000, 'TCP')   # Orchestra RESTful API
        self.open_port(27017, 'TCP')  # MongoDB port mongod and mongos instances
        #self.open_port(27018, 'TCP') # MongoDB port when running with shardsvr setting
        #self.open_port(27019, 'TCP') # MongoDB port when running with configsvr setting
        #self.open_port(28017, 'TCP') # MongoDB port for the web status page. This is always +1000
        self.open_port(5672, 'TCP')   # RabbitMQ service

    def hook_config_changed(self):
        self.info('Configure Secure Shell')
        rsync(self.local_config.ssh_template_path, self.local_config.ssh_config_path,
              recursive=True, log=self.debug)

        self.info('Configure JuJu Service Orchestrator')
        if not os.path.exists(self.local_config.juju_config_file):
            try_makedirs(os.path.dirname(self.local_config.juju_config_file))
            shutil.copy(self.local_config.juju_template_file, self.local_config.juju_config_file)

        self.info('Configure MongoDB Scalable NoSQL DB')
        with open('f.js', 'w') as mongo_f:
            mongo_f.write("db.addUser('admin', '%s', false);" % self.config.mongo_admin_password)
        with open('g.js', 'w') as mongo_g:
            mongo_g.write("db.addUser('nodes', '%s', false);" % self.config.mongo_nodes_password)
        self.cmd('mongo f.js')
        self.cmd('mongo orchestra f.js')
        self.cmd('mongo celery g.js')
        [os.remove(f) for f in ('f.js', 'g.js')]

        config = ConfigObj(self.local_config.mongo_config_file)
        config['bind_ip'] = '0.0.0.0'
        config['noauth'] = 'false'
        config['auth'] = 'true'
        self.debug('MongoDB configuration is: %s' % config.__dict__)
        config.write()

        self.configure_rabbitmq()

        self.info('Configure Orchestra the Orchestrator')
        self.local_config.verbose = self.config.verbose
        self.local_config.api_url = self.api_url
        self.local_config.root_secret = self.config.root_secret
        self.local_config.mongo_admin_connection = self.mongo_admin_connection
        self.local_config.mongo_nodes_connection = self.mongo_nodes_connection
        self.local_config.rabbit_connection = self.rabbit_connection
        infos = {
            'rabbit': str(self.rabbit_connection),
            'port': str(27017),
            'username': 'nodes',
            'password': str(self.config.mongo_nodes_password),
        }
        self.template2config(self.local_config.celery_template_file,
                             self.local_config.celery_config_file, infos)
        self.local_config.plugit_api_url = self.plugit_api_url
        self.remark('Orchestrator successfully configured')
        self.storage_remount()

    def hook_uninstall(self):
        self.info('Uninstall prerequisities, unregister service and load default configuration')
        self.hook_stop()
        try_makedirs('/var/log/rabbitmq')  # Fix rabbitmq-server package uninstall error
        #self.cmd('juju destroy-environment')
        #self.cmd('... --purge apt-cacher-ng charm-tools juju libzookeeper-java lxc zookeeper')
        self.storage_unregister()
        self.cmd('apt-get -y remove --purge %s' % ' '.join(OrchestraHooks.PACKAGES))
        self.cmd('apt-get -y autoremove')
        #shutil.rmtree('$HOME/.juju $HOME/.ssh/id_rsa*
        shutil.rmtree('/etc/rabbitmq/',     ignore_errors=True)
        shutil.rmtree('/var/log/rabbitmq/', ignore_errors=True)
        self.local_config.reset()

    def hook_start(self):
        if not self.storage_is_mounted:
            self.remark('Do not start orchestra daemon : No shared storage')
        elif not os.path.exists(self.local_config.celery_config_file):
            self.remark('Do not start orchestra daemon : No celery configuration file')
        else:
            self.save_local_config()  # Update local configuration file for orchestra daemon
            # do not check status after all, orchestra can do it for us !
            self.cmd('service mongodb start',         fail=False)
            self.cmd('service rabbitmq-server start', fail=False)
            # FIXME this is not a good idea, but I have some trouble with precise release
            self.configure_rabbitmq()  # (see ticket #205 of my private TRAC ticket system)
            if screen_list('Orchestra', log=self.debug) == []:
                self.info('Start in {0} mode'.format('standalone' if self.api_standalone else 'PlugIt'))
                screen_launch('Orchestra', ['python', self.api_filename])
            time.sleep(10)
            #if screen_list('Orchestra', log=self.debug) == [] or
            if self.cmd('curl -s {0}'.format(self.api_local_url), fail=False)['returncode'] != 0:
                raise RuntimeError('Orchestra is not ready')
            else:
                self.remark('Orchestra successfully started')

    def hook_stop(self):
        screen_kill('Orchestra', log=self.debug)
        self.cmd('service rabbitmq-server stop', fail=False)
        self.cmd('service mongodb stop',         fail=False)

    def hook_api_relation_joined(self):
        self.relation_set(api_url=self.api_url)

    def hook_api_relation_changed(self):
        # Get configuration from the relation
        webui_address = self.relation_get('private-address')
        self.info('Web UI address is %s' % webui_address)
        if not webui_address:
            self.remark('Waiting for complete setup')
            return
        # FIXME something to do (register unit ?)

    def hook_publisher_relation_joined(self):
        self.relation_set(mongo_connection=self.mongo_nodes_connection,
                          rabbit_connection=self.rabbit_connection)

    def hook_publisher_relation_changed(self):
        # Get configuration from the relation
        publisher_address = self.relation_get('private-address')
        self.info('Publisher address is %s' % publisher_address)
        if not publisher_address:
            self.remark('Waiting for complete setup')
            return
        # FIXME something to do (register unit ?)

    def hook_transform_relation_joined(self):
        self.relation_set(mongo_connection=self.mongo_nodes_connection,
                          rabbit_connection=self.rabbit_connection)

    def hook_transform_relation_changed(self):
        # Get configuration from the relation
        transform_address = self.relation_get('private-address')
        self.info('Transform address is %s' % transform_address)
        if not transform_address:
            self.remark('Waiting for complete setup')
            return
        # FIXME something to do (register unit ?)

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    OrchestraHooks(first_that_exist('metadata.yaml',    '../oscied-orchestra/metadata.yaml'),
                   first_that_exist('config.yaml',      '../oscied-orchestra/config.yaml'),
                   first_that_exist('local_config.pkl', '../oscied-orchestra/local_config.pkl'),
                   DEFAULT_OS_ENV).trigger()
