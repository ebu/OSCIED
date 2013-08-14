#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**********************************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/ebu/OSCIED

import os, re, shutil, time
from codecs import open
from kitchen.text.converters import to_bytes
from configobj import ConfigObj
from CharmHooks import DEFAULT_OS_ENV
from CharmHooks_Storage import CharmHooks_Storage
from OrchestraConfig import OrchestraConfig
from pyutils.py_filesystem import first_that_exist, try_makedirs
from pyutils.py_subprocess import rsync, screen_launch, screen_list, screen_kill


class OrchestraHooks(CharmHooks_Storage):

    PACKAGES = tuple(set(CharmHooks_Storage.PACKAGES +
                     (u'ffmpeg', u'ntp', u'x264', u'mongodb', u'rabbitmq-server')))
    JUJU_PACKAGES = (u'juju-core',)

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(OrchestraHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = OrchestraConfig.read(local_config_filename, store_filename=True)
        self.debug(u'My __dict__ is {0}'.format(self.__dict__))

    # ------------------------------------------------------------------------------------------------------------------

    def api_url(self, local=False):
        return u'http://{0}:5000'.format('127.0.0.1' if local else self.private_address)

    @property
    def mongo_admin_connection(self):
        return u'mongodb://admin:{0}@localhost:27017/orchestra'.format(self.config.mongo_admin_password)

    @property
    def mongo_nodes_connection(self):
        return u'mongodb://nodes:{0}@{1}:27017/celery'.format(self.config.mongo_nodes_password, self.private_address)

    @property
    def rabbit_connection(self):
        return u'amqp://nodes:{0}@{1}:5672/celery'.format(self.config.rabbit_password, self.private_address)

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
        self.cmd(u'rabbitmqctl add_user nodes "{0}"'.format(self.config.rabbit_password), fail=False)
        self.cmd(u'rabbitmqctl add_vhost celery', fail=False)
        self.cmd(u'rabbitmqctl set_permissions -p celery nodes ".*" ".*" ".*"', fail=False)
        users, vhosts = self.rabbit_users, self.rabbit_vhosts
        self.debug(u'RabbitMQ users: {0} vhosts: {1}'.format(users, vhosts))
        if u'guest' in users or u'nodes' not in users or u'/' in vhosts or u'celery' not in vhosts:
            raise RuntimeError(to_bytes(u'Unable to configure RabbitMQ'))

    # ------------------------------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info(u'Upgrade system and install prerequisites')
        self.cmd(u'apt-add-repository -y ppa:jon-severinsson/ffmpeg')
        self.cmd(u'apt-add-repository -y ppa:juju/stable')
        self.cmd(u'apt-get -y update', fail=False)
        self.cmd(u'apt-get -y upgrade')
        self.cmd(u'apt-get -y install {0}'.format(u' '.join(OrchestraHooks.PACKAGES)))
        self.cmd(u'apt-get -y install {0}'.format(u' '.join(OrchestraHooks.JUJU_PACKAGES)))
        self.info(u'Restart network time protocol service')
        self.cmd(u'service ntp restart')
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
        self.info(u'Expose RESTful API, MongoDB & RabbitMQ service')
        self.open_port(5000,  u'TCP')  # Orchestra RESTful API
        self.open_port(27017, u'TCP')  # MongoDB port mongod and mongos instances
        #self.open_port(27018, u'TCP') # MongoDB port when running with shardsvr setting
        #self.open_port(27019, u'TCP') # MongoDB port when running with configsvr setting
        #self.open_port(28017, u'TCP') # MongoDB port for the web status page. This is always +1000
        self.open_port(5672,  u'TCP')  # RabbitMQ service

    def hook_config_changed(self):
        self.info(u'Start MongoDB and RabbitMQ daemons')
        self.cmd(u'service mongodb start',         fail=False)
        self.cmd(u'service rabbitmq-server start', fail=False)

        self.info(u'Configure Secure Shell')
        rsync(self.local_config.ssh_template_path, self.local_config.ssh_config_path, recursive=True, log=self.debug)

        self.info(u'Configure JuJu Service Orchestrator')
        if not os.path.exists(self.local_config.juju_config_file):
            try_makedirs(os.path.dirname(self.local_config.juju_config_file))
            shutil.copy(self.local_config.juju_template_file, self.local_config.juju_config_file)

        self.info(u'Configure MongoDB Scalable NoSQL DB')
        with open(u'f.js', u'w', u'utf-8') as mongo_f:
            mongo_f.write(u"db.addUser('admin', '{0}', false);".format(self.config.mongo_admin_password))
        with open(u'g.js', u'w', u'utf-8') as mongo_g:
            mongo_g.write(u"db.addUser('nodes', '{0}', false);".format(self.config.mongo_nodes_password))
        self.cmd(u'mongo f.js')
        self.cmd(u'mongo orchestra f.js')
        self.cmd(u'mongo celery g.js')
        [os.remove(f) for f in (u'f.js', u'g.js')]

        config = ConfigObj(self.local_config.mongo_config_file)
        config[u'bind_ip'] = u'0.0.0.0'
        config[u'noauth'] = u'false'
        config[u'auth'] = u'true'
        self.debug(u'MongoDB configuration is: {0}'.format(config.__dict__))
        config.write()

        self.configure_rabbitmq()

        self.info(u'Configure Orchestra the Orchestrator')
        self.local_config.verbose = self.config.verbose
        self.local_config.api_url = self.api_url(local=False)
        self.local_config.root_secret = self.config.root_secret
        self.local_config.mongo_admin_connection = self.mongo_admin_connection
        self.local_config.mongo_nodes_connection = self.mongo_nodes_connection
        self.local_config.rabbit_connection = self.rabbit_connection
        infos = {
            u'rabbit': unicode(self.rabbit_connection),
            u'port': unicode(27017),
            u'username': u'nodes',
            u'password': unicode(self.config.mongo_nodes_password),
        }
        self.template2config(self.local_config.celery_template_file, self.local_config.celery_config_file, infos)
        self.remark(u'Orchestrator successfully configured')
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
            self.cmd(u'apt-get -y autoremove')
            #shutil.rmtree('$HOME/.juju $HOME/.ssh/id_rsa*
            shutil.rmtree(u'/etc/rabbitmq/',     ignore_errors=True)
            shutil.rmtree(u'/var/log/rabbitmq/', ignore_errors=True)
        self.local_config.reset()

    def hook_start(self):
        if not self.storage_is_mounted:
            self.remark(u'Do not start orchestra daemon : No shared storage')
        elif not os.path.exists(self.local_config.celery_config_file):
            self.remark(u'Do not start orchestra daemon : No celery configuration file')
        else:
            self.save_local_config()  # Update local configuration file for orchestra daemon
            # do not check status after all, orchestra can do it for us !
            self.cmd(u'service mongodb start',         fail=False)
            self.cmd(u'service rabbitmq-server start', fail=False)
            # FIXME this is not a good idea, but I have some trouble with precise release
            self.configure_rabbitmq()  # (see ticket #205 of my private TRAC ticket system)
            if screen_list(u'Orchestra', log=self.debug) == []:
                screen_launch(u'Orchestra', [u'python', u'orchestra.py'])
            for start_delay in range(15):
                time.sleep(1)
                if self.cmd(u'curl -s {0}'.format(self.api_url(local=True)), fail=False)[u'returncode'] == 0:
                    self.remark(u'Orchestra successfully started in {0} seconds'.format(start_delay))
                    return
            raise RuntimeError(to_bytes(u'Orchestra is not ready'))

    def hook_stop(self):
        screen_kill(u'Orchestra', log=self.debug)
        self.cmd(u'service rabbitmq-server stop', fail=False)
        self.cmd(u'service mongodb stop',         fail=False)

    def hook_api_relation_joined(self):
        self.relation_set(api_url=self.api_url(local=False))

    def hook_api_relation_changed(self):
        # Get configuration from the relation
        webui_address = self.relation_get(u'private-address')
        self.info(u'Web UI address is {0}'.format(webui_address))
        if not webui_address:
            self.remark(u'Waiting for complete setup')
            return
        # FIXME something to do (register unit ?)

    def hook_publisher_relation_joined(self):
        self.relation_set(mongo_connection=self.mongo_nodes_connection,
                          rabbit_connection=self.rabbit_connection)

    def hook_publisher_relation_changed(self):
        # Get configuration from the relation
        publisher_address = self.relation_get(u'private-address')
        self.info(u'Publisher address is {0}'.format(publisher_address))
        if not publisher_address:
            self.remark(u'Waiting for complete setup')
            return
        # FIXME something to do (register unit ?)

    def hook_transform_relation_joined(self):
        self.relation_set(mongo_connection=self.mongo_nodes_connection,
                          rabbit_connection=self.rabbit_connection)

    def hook_transform_relation_changed(self):
        # Get configuration from the relation
        transform_address = self.relation_get(u'private-address')
        self.info(u'Transform address is {0}'.format(transform_address))
        if not transform_address:
            self.remark(u'Waiting for complete setup')
            return
        # FIXME something to do (register unit ?)

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pyutils.py_unicode import configure_unicode
    configure_unicode()
    OrchestraHooks(first_that_exist(u'metadata.yaml',    u'../oscied-orchestra/metadata.yaml'),
                   first_that_exist(u'config.yaml',      u'../oscied-orchestra/config.yaml'),
                   first_that_exist(u'local_config.pkl', u'../oscied-orchestra/local_config.pkl'),
                   DEFAULT_OS_ENV).trigger()
