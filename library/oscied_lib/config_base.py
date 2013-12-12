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

import logging
from os.path import join, sep
from pytoolbox.serialization import JsoneableObject

from .constants import MEDIAS_PATH, UPLOADS_PATH


class CharmLocalConfig(JsoneableObject):

    def __init__(self, verbose=True):
        self.verbose = verbose

    def __repr__(self):
        return unicode(self.__dict__)

    @property
    def log_level(self):
        return logging.DEBUG if self.verbose else logging.INFO

    def reset(self):
        u"""
        Reset attributes to theirs default values.

        **Example usage**

        >>> config = CharmLocalConfig(verbose=True)
        >>> config._json_filename = u'my_file.json'
        >>> print(config.verbose)
        True
        >>> config.verbose = False
        >>> print(config.verbose)
        False
        >>> config.reset()
        >>> print(config.verbose)
        True
        >>> print(config._json_filename)
        my_file.json
        """
        self.__init__()


class CharmLocalConfig_Storage(CharmLocalConfig):

    def __init__(self, verbose=False, storage_address=u'', storage_nat_address=u'', storage_fstype=u'',
                 storage_mountpoint=u'', storage_options=u'', storage_path=u'/mnt/storage', storage_mount_max_retry=5,
                 storage_mount_sleep_delay=5, hosts_file=u'/etc/hosts', **kwargs):
        super(CharmLocalConfig_Storage, self).__init__(verbose=verbose)
        self.storage_address = storage_address
        self.storage_nat_address = storage_nat_address
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

        **Example usage**

        >>> import copy
        >>> from .models_test import MEDIA_TEST
        >>> media = copy.copy(MEDIA_TEST)
        >>> config = CharmLocalConfig_Storage()
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
            if getattr(media, u'user_id', None):
               raise ValueError(u"user_id not defined within media attributes (maybe you've got it with head=False)") 
            return join(self.storage_path, MEDIAS_PATH, media.user_id, media._id, media.filename)
        if media.uri and media.uri.startswith(uri):
            return join(self.storage_path, media.uri.replace(uri + sep, u'', 1))
        return None

    def storage_uri(self, path=None):
        u"""
        Returns storage URI.

        **Example usage**

        >>> config = CharmLocalConfig_Storage()
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

        **Example usage**

        >>> from .models_test import MEDIA_TEST
        >>> config = CharmLocalConfig_Storage()
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


class CharmLocalConfig_Subordinate(CharmLocalConfig):

    def __init__(self, verbose=False, api_nat_socket=u'',
                 celery_config_file=u'celeryconfig.py',
                 celery_config_template_file=u'templates/celeryconfig.py.template',
                 celery_default_template_file=u'templates/celeryd.default.template',
                 celery_init_template_file=u'templates/celeryd.init.template', **kwargs):
        super(CharmLocalConfig_Subordinate, self).__init__(verbose=verbose)
        self.api_nat_socket = api_nat_socket
        self.celery_config_file = celery_config_file
        self.celery_config_template_file = celery_config_template_file
        self.celery_default_template_file = celery_default_template_file
        self.celery_init_template_file = celery_init_template_file

    @property
    def worker_name(self):
        return self.__class__.__name__.lower().replace(u'localconfig', u'')

    @property
    def celery_default_file(self):
        return join(u'/etc/default', self.worker_name)

    @property
    def celery_init_file(self):
        return join(u'/etc/init.d', self.worker_name)
