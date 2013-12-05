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

from .config import (
    OrchestraLocalConfig, PublisherLocalConfig, StorageLocalConfig, TransformLocalConfig, WebuiLocalConfig)

ORCHESTRA_CONFIG_TEST = OrchestraLocalConfig(
    storage_address=u'127.0.0.1', storage_fstype=u'glusterfs', storage_mountpoint=u'medias_volume_0',
    api_url=u'http://127.0.0.1', root_secret=u'toto', node_secret=u'abcd', mongo_admin_connection=u'',
    mongo_node_connection=u'...', rabbit_connection=u'...')

PUBLISHER_CONFIG_TEST = PublisherLocalConfig(
    api_nat_socket=u'129.194.185.47', storage_address=u'10.1.1.2', storage_fstype=u'glusterfs',
    storage_mountpoint=u'medias_volume')

STORAGE_CONFIG_TEST = StorageLocalConfig(u'*', False)

TRANSFORM_CONFIG_TEST = TransformLocalConfig(
    api_nat_socket=u'129.194.185.47', storage_address=u'10.1.1.2', storage_fstype=u'glusterfs',
    storage_mountpoint=u'medias_volume')

WEBUI_CONFIG_TEST = WebuiLocalConfig(
    api_url=u'10.10.4.3', storage_address=u'10.1.1.2', storage_fstype=u'glusterfs',
    storage_mountpoint=u'medias_volume')
