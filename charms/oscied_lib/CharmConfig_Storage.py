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

from os.path import join, sep
from CharmConfig import CharmConfig

MEDIAS_PATH, UPLOADS_PATH = u'medias', u'uploads'


class CharmConfig_Storage(CharmConfig):

    def __init__(self, verbose=None, storage_address=u'', storage_fstype=u'', storage_mountpoint=u'',
                 storage_options=u'', storage_path=u'/mnt/storage', storage_mount_max_retry=5,
                 storage_mount_sleep_delay=5, hosts_file=u'/etc/hosts', **kwargs):
        super(CharmConfig_Storage, self).__init__(verbose=verbose)
        self.storage_address = storage_address
        self.storage_fstype = storage_fstype
        self.storage_mountpoint = storage_mountpoint
        self.storage_options = storage_options
        self.storage_path = storage_path
        self.storage_mount_max_retry = storage_mount_max_retry
        self.storage_mount_sleep_delay = storage_mount_sleep_delay
        self.hosts_file = hosts_file

    @property
    def storage_uploads_path(self):
        uri = self.storage_uri()
        if not uri:
            return None
        return join(self.storage_path, UPLOADS_PATH)

    def storage_medias_path(self, media=None, generate=True):
        u"""
        Returns storage path of a media stored into medias directory.

        **Example usage**:

        >>> import copy
        >>> from Media import MEDIA_TEST
        >>> media = copy.copy(MEDIA_TEST)
        >>> config = CharmConfig_Storage()
        >>> config.storage_address = u'10.1.1.2'
        >>> config.storage_fstype = u'glusterfs'
        >>> config.storage_mountpoint='medias_volume'
        >>> print(config.storage_medias_path())
        /mnt/storage/medias
        >>> media_uri = config.storage_medias_path(media=media)
        >>> print(media_uri)  # doctest: +ELLIPSIS
        /mnt/storage/medias/.../...
        >>> media.uri = media_uri
        >>> print(config.storage_medias_path(media=media))  # doctest: +ELLIPSIS
        /mnt/storage/medias/.../...
        """
        uri = self.storage_uri()
        if not uri:
            return None
        if media is None:
            return join(self.storage_path, MEDIAS_PATH)
        if generate:
            return join(self.storage_path, MEDIAS_PATH, media.user_id, media._id, media.filename)
        if media.uri and media.uri.startswith(uri):
            return join(self.storage_path, media.uri.replace(uri + sep, u'', 1))
        return None

    def storage_uri(self, path=None):
        u"""
        Returns storage URI.

        **Example usage**:

        >>> config = CharmConfig_Storage()
        >>> config.storage_address = u'10.1.1.2'
        >>> config.storage_fstype = u'glusterfs'
        >>> config.storage_mountpoint='medias_volume'
        >>> print(config.storage_uri())
        glusterfs://10.1.1.2/medias_volume
        >>> print(config.storage_uri(path=UPLOADS_PATH))
        glusterfs://10.1.1.2/medias_volume/uploads
        >>> config.storage_fstype = u''
        >>> print(config.storage_medias_uri())
        None
        >>> config.storage_fstype = 'nfs'
        >>> config.storage_address = u''
        >>> print(config.storage_medias_uri())
        None
        >>> config.storage_address = u'30.0.0.1'
        >>> print(config.storage_uri())
        nfs://30.0.0.1/medias_volume
        """
        if self.storage_fstype and self.storage_address and self.storage_mountpoint:
            path = (u'/{0}'.format(path) if path else u'')
            return u'{0}://{1}/{2}{3}'.format(self.storage_fstype, self.storage_address, self.storage_mountpoint, path)
        return None

    def storage_medias_uri(self, media=None):
        u"""
        Returns storage URI.

        **Example usage**:

        >>> from Media import MEDIA_TEST
        >>> config = CharmConfig_Storage()
        >>> config.storage_address = u'10.1.1.2'
        >>> config.storage_fstype = u'glusterfs'
        >>> config.storage_mountpoint = u'medias_volume'
        >>> print(config.storage_medias_uri())
        glusterfs://10.1.1.2/medias_volume/medias
        >>> print(config.storage_medias_uri(media=MEDIA_TEST))  # doctest: +ELLIPSIS
        glusterfs://10.1.1.2/medias_volume/medias/.../...
        """
        if media:
            return self.storage_uri(path=join(MEDIAS_PATH, media.user_id, media._id, media.filename))
        return self.storage_uri(path=MEDIAS_PATH)
