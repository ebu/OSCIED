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

from CharmHooks import CharmHooks


class CharmHooks_Website(CharmHooks):

    PACKAGES = ()

    def __init__(self, metadata, default_config, default_os_env):
        super(CharmHooks_Website, self).__init__(metadata, default_config, default_os_env)
        self.local_config = None  # Must be set by derived class

    # ----------------------------------------------------------------------------------------------

    @property
    def proxy_ips_string(self):
        try:
            proxy_ips = self.config.proxy_ips.split(',')
        except:
            proxy_ips = []
        return ','.join(list(filter(None, self.local_config.proxy_ips + proxy_ips)))

    # ----------------------------------------------------------------------------------------------

    def hook_website_relation_joined(self):
        self.relation_set(port='80', hostname=self.cmd('hostname -f'))

    def hook_website_relation_changed(self):
        # Get configuration from the relation
        proxy_address = self.relation_get('private-address')
        self.info('Proxy address is %s' % proxy_address)
        if not proxy_address:
            self.remark('Waiting for complete setup')
            return
        if not proxy_address in self.local_config.proxy_ips:
            self.info('Add %s to allowed proxy IPs' % proxy_address)
            self.hook_stop()
            self.local_config.proxy_ips.append(proxy_address)
            self.save_local_config()
            self.hook_config_changed()
            self.hook_start()

    def hook_website_relation_departed(self):
        # Get configuration from the relation
        proxy_address = self.relation_get('private-address')
        if not proxy_address:
            self.remark('Waiting for complete setup')
            return
        if proxy_address in self.local_config.proxy_ips:
            self.info('Remove %s from allowed proxy IPs' % proxy_address)
            self.hook_stop()
            self.local_config.proxy_ips.remove(proxy_address)
            self.save_local_config()
            self.hook_config_changed()
            self.hook_start()

    def hook_website_relation_broken(self):
        self.info('Cleanup allowed proxy IPs')
        self.hook_stop()
        self.local_config.proxy_ips = []
        self.hook_config_changed()
        self.hook_start()
