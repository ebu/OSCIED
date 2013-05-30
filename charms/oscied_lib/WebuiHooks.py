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

import os, shutil, string
from configobj import ConfigObj
from random import choice
from CharmHooks import DEFAULT_OS_ENV
from CharmHooks_Storage import CharmHooks_Storage
from CharmHooks_Website import CharmHooks_Website
from WebuiConfig import WebuiConfig
from pyutils.pyutils import chown, first_that_exist, rsync, try_makedirs


class WebuiHooks(CharmHooks_Storage, CharmHooks_Website):

    PACKAGES = tuple(set(CharmHooks_Storage.PACKAGES + CharmHooks_Website.PACKAGES +
                    ('mysql-server', 'apache2', 'php5', 'php5-cli', 'php5-curl', 'php5-gd',
                     'php5-mysql', 'libapache2-mod-auth-mysql', 'phpmyadmin', 'ntp')))
    FIX_PACKAGES = ('apache2.2-common', 'mysql-client-5.5', 'mysql-client-core-5.5', 'mysql-common',
                    'mysql-server', 'mysql-server-5.1', 'mysql-server-5.5', 'mysql-server-core-5.5')

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(WebuiHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = WebuiConfig.read(local_config_filename, store_filename=True)
        self.debug('My __dict__ is %s' % self.__dict__)

# ORCHESTRA_FLAG="$WWW_ROOT_PATH/orchestra_relation_ok"
# API_URL=$(config-get api_url)

    # ----------------------------------------------------------------------------------------------

# api_config_is_enabled()
# {
#   [ "$API_URL" ]
# }
# api_hook_bypass()
# {
#   if api_config_is_enabled; then
#     xecho 'Orchestrator is set in config, api relation is disabled' 1
#   fi
# }
# api_register()
# {
#   # Overrides api parameters with charm configuration
#   if api_config_is_enabled; then # if api options are set
#     api_url=$API_URL
#   # Or uses api parameters from charm api relation
#   elif [ $# -eq 1 ]; then # if function parameters are set
#     api_url=$1
#   elif [ $# -eq 0 ]; then
#     return
#   else
#     xecho "Usage: $(basename $0).api_register api_url"
#   fi
#   pecho 'Configure Web UI : Register the Orchestrator'
#   setSettingPHP $GENERAL_CONFIG_FILE 'config' 'orchestra_api_url' "$api_url" || xecho 'Config'
#   touch "$ORCHESTRA_FLAG" || xecho 'Unable to create flag'
# }
# api_unregister()
# {
#   pecho 'Configure Web UI : Unregister the Orchestrator'
#   setSettingPHP $GENERAL_CONFIG_FILE 'config' 'orchestra_api_url' '' || xecho 'Config'
#   rm -f "$ORCHESTRA_FLAG" 2>/dev/null
# }
# update_proxies()
# {
#   if [ $# -ne 2 ]; then
#     xecho "Usage: $(basename $0).update_proxies action ip"
#   fi
#   action=$1
#   ip=$2
#   PROXY_IPS=$(cat proxy_ips 2>/dev/null)
#   case "$action" in
#   'add' )
#     if ! echo $PROXY_IPS | grep -q "$ip"; then
#       [ "$PROXY_IPS" ] && PROXY_IPS="$PROXY_IPS,"
#       PROXY_IPS="$PROXY_IPS$ip"
#       echo $PROXY_IPS > proxy_ips
#       setSettingPHP $GENERAL_CONFIG_FILE 'config' 'proxy_ips' "$PROXY_IPS" || return $false
#     fi ;;
#   'remove' )
#     if echo $PROXY_IPS | grep -q "$ip"; then
#       sed -i "s<$ip,<<g;s<,$ip<<g;s<$ip<<g" proxy_ips
#       PROXY_IPS=$(cat proxy_ips)
#       setSettingPHP $GENERAL_CONFIG_FILE 'config' 'proxy_ips' "$PROXY_IPS" || return $false
#     fi ;;
#   'cleanup' )
#     if "$PROXY_IPS"; then
#       PROXY_IPS=''
#       echo '' > proxy_ips
#       setSettingPHP $GENERAL_CONFIG_FILE 'config' 'proxy_ips' "$PROXY_IPS" || return $false
#     fi ;;
#   * ) xecho "Unknown action : $action" ;;
#   esac
#   return $true
# }
# storage_remount()
# {
#   # ...
#   if storage_is_mounted; then
#     storage_migrate_path 'medias'  "$STORAGE_MEDIAS_PATH"  "$WWW_MEDIAS_PATH"  'root'     755 644
#     storage_migrate_path 'uploads' "$STORAGE_UPLOADS_PATH" "$WWW_UPLOADS_PATH" 'www-data' 755 644
#     # FIXME update /etc/fstab (?)
#     pecho 'Configure Web UI : Register shared storage'
#     # FIXME this is a little bit cheating with paths ;-)
#     storage_uri="$fstype://$ip/$mountpoint"
#     uploads_uri="$storage_uri/uploads/"
#     medias_uri="$storage_uri/medias/"
#     setSettingPHP $GENERAL_CONFIG_FILE 'config' 'uploads_uri' "$uploads_uri" || xecho 'Config' 2
#     setSettingPHP $GENERAL_CONFIG_FILE 'config' 'medias_uri'  "$medias_uri"  || xecho 'Config' 3
#   else
#     xecho 'Unable to mount shared storage' 4
#   fi
# }
# # Migrate a local Web UI path to shared storage only if necessary ----------------------------------
# storage_migrate_path()
# {
#   if [ $# -ne 6 ]; then
#     xecho "Usage: $(basename $0).storage_migrate_path name storage local owner dmod fmod"
#   fi
#   name=$1
#   storage=$2
#   local=$3
#   owner=$4
#   dmod=$5
#   fmod=$6
#   if [ ! -d "$storage" ]; then
#     pecho "Create $name path in storage"
#     mkdir -p "$storage" || xecho "Unable to create $name path" 1
#   else
#     recho "Storage $name path already created"
#   fi
#   if [ -d "$local" ]; then
#     mecho "Migrating files from Web UI $name path to $name path in storage ..."
#     rsync -a "$local/" "$storage/" || xecho "Unable to migrate $name files" 2
#     rm -rf "$local"
#   fi
#   if [ ! -h "$local" ]; then
#     pecho "Link Web UI $name path to $name path in storage"
#     ln -s "$storage" "$local" || xecho "Unable to create $name link" 3
#   fi
#   pecho "Ensure POSIX rights (owner=$owner:$owner mod=(d=$dmod,f=$fmod)) of $name path in storage"
#   chown "$owner:$owner" "$storage" -R || xecho "Unable to chown $storage" 4
#   find "$storage" -type d -exec chmod "$dmod" "$storage" \;
#   find "$storage" -type f -exec chmod "$fmod" "$storage" \;
# }

    # ----------------------------------------------------------------------------------------------

    def mysql_do(self, action=None, cli_input=None):
        command = ['mysql', '-uroot', '-p%s' % self.config.mysql_root_password]
        if action:
            command.extend(['-e', action])
        return self.cmd(command=command, cli_input=cli_input)

    @staticmethod
    def randpass(length):
        chars = string.letters + string.digits
        print ''.join([choice(chars) for i in range(length)])

    # ----------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info('Upgrade system and install prerequisites')
        self.cmd('apt-get -y update', fail=False)
        self.cmd('apt-get -y upgrade')
        try_makedirs('/etc/mysql')
        debconf = 'debconf-set-selections'
        mysql, myadmin = 'mysql-server mysql-server', 'phpmyadmin phpmyadmin'
        mysql_pass, myadmin_pass = self.config.mysql_root_password, self.config.mysql_my_password
        # Tip : http://ubuntuforums.org/showthread.php?t=981801
        self.cmd(debconf, input='%s/root_password select %s' % (mysql, mysql_pass))
        self.cmd(debconf, input='%s/root_password_again select %s' % (mysql, mysql_pass))
        # Tip : http://gercogandia.blogspot.ch/2012/11/automatic-unattended-install-of.html
        self.cmd(debconf, input='%s/app-password password %s' % (myadmin, myadmin_pass))
        self.cmd(debconf, input='%s/app-password-confirm password %s' % (myadmin, myadmin_pass))
        self.cmd(debconf, input='%s/mysql/admin-pass password %s' % (myadmin, mysql_pass))
        self.cmd(debconf, input='%s/mysql/app-pass password %s' % (myadmin, mysql_pass))
        self.cmd(debconf, input='%s/reconfigure-webserver multiselect apache2' % myadmin)
        self.cmd('apt-get -y install %s' % ' '.join(WebuiHooks.PACKAGES))
        self.info('Restart network time protocol service')
        self.cmd('service ntp restart')
        # Now MySQL will listen to incoming request of any source
        #sed -i 's/127.0.0.1/0.0.0.0/g' /etc/mysql/my.cnf
        # Fix ticket #57 : Keystone + MySQL = problems
        self.mysql_do("DROP USER ''@'localhost'; DROP USER ''@'$(hostname)';")
        self.mysql_do("GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;")
        self.mysql_do("SET PASSWORD FOR 'root'@'%' = PASSWORD('%s');" % mysql_pass)
        self.cmd('service mysql restart')

        self.info('Import Web User Interface database')
        self.mysql_do(cli_input=open(self.local_config.site_database_file).read())

        self.info('Create Web User Interface user')
        self.mysql_do("GRANT ALL ON webui.* TO 'webui'@'%' IDENTIFIED BY '%s';" %
                      self.config.mysql_user_pass)

        self.inf('Configure Apache2 + PHP')
        self.cmd('a2enmod rewrite')

        self.info('Copy Web User Interface')
        shutil.copy(self.local_config.site_template_file, self.local_config.sites_enabled_path)
        rsync('www/', self.local_config.www_root_path,
              archive=True, delete=True, exclude_vcs=True, recursive=True)

        self.info('Expose Apache 2 service')
        self.open_port(80, 'TCP')

        self.info('Configure Web User Interface')
        self.local_config.encryption_key = WebuiHooks.randpass(32)
        self.local_config.proxy_ips = self.config.proxy_ips  # FIXME like storage ips

        shutil.makedirs(self.local_config.mysql_temp_path)
        chown(self.local_config.mysql_temp_path, 'mysql', 'mysql')
        chown(self.local_config.www_root_path, 'www-data', 'www-data', recursive=True)

        # config php, mettre short opentags à "on"
        # lire les logs, problème MY_ my_ nom fichier

    def hook_config_changed(self):
        self.storage_remount()
        self.api_register()

        mysql_config = ConfigObj(self.local_config.mysql_config_file)
        mysql_config['tmpdir'] = self.local_config.mysql_temp_path
        mysql_config.write()

        self.template2config(self.local_config.general_template_file,
                             self.local_config.general_config_file, self.local_config.__dict__)

        self.template2config(self.local_config.database_template_file,
                             self.local_config.database_config_file, self.config.__dict__)

        self.template2config(self.local_config.htaccess_template_file,
                             self.local_config.htaccess_config_file, self.config.__dict__)

    def hook_uninstall(self):
        self.info('Uninstall prerequisities, unregister service and load default configuration')
        self.hook_stop()
        self.storage_unregister()
        self.cmd('apt-get -y remove --purge %s' % ' '.join(WebuiHooks.PACKAGES))
        self.cmd('apt-get -y remove --purge %s' % ' '.join(WebuiHooks.FIX_PACKAGES), fail=False)
        self.cmd('apt-get -y autoremove')
        shutil.rmtree('/etc/apache2/', ignore_errors=True)
        shutil.rmtree(self.local_config.www_root_path, ignore_errors=True)
        shutil.rmtree('/var/log/apache2/', ignore_errors=True)
        shutil.rmtree('/etc/mysql/', ignore_errors=True)
        shutil.rmtree('/var/lib/mysql/', ignore_errors=True)
        shutil.rmtree('/var/log/mysql/', ignore_errors=True)
        os.makedirs(self.local_config.www_root_path)
        self.local_config.reset(reset_publish_uri=False)

# hook_start()
# {
#   techo 'Web UI - start'
#   if ! storage_is_mounted; then
#     recho 'WARNING Do not start Web UI : No shared storage'
#   elif [ ! -f "$ORCHESTRA_FLAG" ]; then
#     recho 'WARNING Do not start Web UI : No Orchestrator API'
#   else
#     if ! service mysql status | grep -q 'running'; then
#       service mysql start || xecho 'Unable to start MySQL' 1
#     fi
#     service apache2 start || xecho 'Unable to start Apache 2' 2
#   fi
# }
# hook_stop()
# {
#   techo 'Web UI - stop'
#   service apache2 stop || xecho 'Unable to stop Apache 2' 1
#   if service mysql status | grep -q 'running'; then
#     service mysql stop || xecho 'Unable to stop MySQL' 2
#   fi
# }

    # def hook_start(self):
    #     if not self.storage_is_mounted:
    #         self.remark('Do not start publisher daemon : No shared storage')
    #     elif not os.path.exists(self.local_config.celery_config_file):
    #         self.remark('Do not start publisher daemon : No celery configuration file')
    #     elif len(self.rabbit_queues) == 0:
    #         self.remark('Do not start publisher daemon : No RabbitMQ queues declared')
    #     else:
    #         self.save_local_config()  # Update local configuration file for publisher daemon
    #         self.cmd('service apache2 start')
    #         if screen_list('Publisher', log=self.debug) == []:
    #             try:
    #                 screen_launch('Publisher',
    #                               ['celeryd', '--config', 'celeryconfig', '-Q', self.rabbit_queues])
    #             finally:
    #                 os.chdir('..')
    #         time.sleep(5)
    #         if screen_list('Publisher', log=self.debug) == []:
    #             raise RuntimeError('Publisher is not ready')
    #         else:
    #             self.remark('Publisher successfully started')

    # def hook_stop(self):
    #     screen_kill('Publisher', log=self.debug)
    #     self.cmd('service apache2 stop', fail=False)

# hook_api_relation_joined()
# {
#   techo 'Web UI - api relation joined'
#   api_hook_bypass
# }
# hook_api_relation_changed()
# {
#   techo 'Web UI - api relation changed'
#   api_hook_bypass
#   # Get configuration from the relation
#   ip=$(relation-get private-address)
#   api_url=$(relation-get api_url)
#   mecho "Orchestrator IP is $ip, API URL is $api_url"
#   if [ ! "$ip" -o ! "$api_url" ]; then
#     recho 'Waiting for complete setup'
#     exit 0
#   fi
#   hook_stop
#   api_register "$api_url"
#   hook_start
# }
# hook_api_relation_broken()
# {
#   techo 'Web UI - api relation broken'
#   api_hook_bypass
#   hook_stop
#   api_unregister
#}

# hook_website_relation_joined()
# {
#   techo 'Web UI - website relation joined'
#   # Send port & hostname
#   relation-set port=80 hostname=$(hostname -f)
# }
# hook_website_relation_changed()
# {
#   techo 'Web UI - website relation changed'
#   # Get configuration from the relation
#   proxy_ip=$(relation-get private-address)
#   mecho "Proxy IP is $proxy_ip"
#   if [ ! "$proxy_ip" ]; then
#     recho 'Waiting for complete setup'
#     exit 0
#   fi
#   hook_stop
#   pecho "Configure Web UI : Add $proxy_ip to allowed proxy IPs"
#   update_proxies add "$proxy_ip" || xecho 'Unable to add proxy'
#   hook_start
# }
# hook_website_relation_departed()
# {
#   techo 'Web UI - website relation departed'
#   # Get configuration from the relation
#   proxy_ip=$(relation-get private-address)
#   mecho "Proxy IP is $proxy_ip"
#   if [ ! "$proxy_ip" ]; then
#     recho 'Waiting for complete setup'
#     exit 0
#   fi
#   hook_stop
#   pecho "Configure Web UI : Remove $proxy_ip from allowed proxy IPs"
#   update_proxies remove "$proxy_ip" || xecho 'Unable to remove proxy'
#   hook_start
# }
# hook_website_relation_broken()
# {
#   techo 'Web UI - website relation broken'
#   # Get configuration from the relation
#   proxy_ip=$(relation-get private-address)
#   mecho "Proxy IP is $proxy_ip"
#   if [ ! "$proxy_ip" ]; then
#     recho 'Waiting for complete setup'
#     exit 0
#   fi
#   hook_stop
#   pecho "Configure Web UI : Remove $proxy_ip from allowed proxy IPs"
#   update_proxies remove "$proxy_ip" || xecho 'Unable to remove proxy'
#   # FIXME does relation broken means that no more proxies are linked to us ? if yes :
#   #pecho 'Configure Web UI : Cleanup allowed proxy IPs'
#   #update_proxies cleanup || xecho 'Unable to cleanup proxies'
#   hook_start
# }

if __name__ == '__main__':
    WebuiHooks(first_that_exist('metadata.yaml', '../oscied-webui/metadata.yaml'),
               first_that_exist('config.yaml', '../oscied-webui/config.yaml'),
               first_that_exist('local_config.pkl', '../oscied-webui/local_config.pkl'),
               DEFAULT_OS_ENV).trigger()
