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

from oscied_config import (
    OrchestraLocalConfig, PublisherLocalConfig, StorageLocalConfig, TransformLocalConfig, WebuiLocalConfig)

ORCHESTRA_CONFIG_TEST = OrchestraLocalConfig(
    storage_address=u'127.0.0.1', storage_fstype=u'glusterfs', storage_mountpoint=u'medias_volume_0',
    api_url=u'http://127.0.0.1:5000', root_secret=u'toto', node_secret=u'abcd', mongo_admin_connection=u'',
    mongo_node_connection=u'...', rabbit_connection=u'...')

PUBLISHER_CONFIG_TEST = PublisherLocalConfig(
    api_nat_socket=u'129.194.185.47:5000', storage_address=u'10.1.1.2', storage_fstype=u'glusterfs',
    storage_mountpoint=u'medias_volume')

STORAGE_CONFIG_TEST = StorageLocalConfig(u'*', False)

TRANSFORM_CONFIG_TEST = TransformLocalConfig(
    api_nat_socket=u'129.194.185.47:5000', storage_address=u'10.1.1.2', storage_fstype=u'glusterfs',
    storage_mountpoint=u'medias_volume')

WEBUI_CONFIG_TEST = WebuiLocalConfig(
    api_url=u'10.10.4.3:5000', storage_address=u'10.1.1.2', storage_fstype=u'glusterfs',
    storage_mountpoint=u'medias_volume')
