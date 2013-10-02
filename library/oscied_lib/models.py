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

from __future__ import absolute_import

import os, re
from passlib.hash import pbkdf2_sha512
from passlib.utils import consteq
from .pytoolbox.encoding import to_bytes
from .pytoolbox.serialization import dict2object
from .pytoolbox.mongo import Model, TaskModel
from .pytoolbox.validation import valid_email, valid_filename, valid_secret, valid_uuid

ENCODERS_NAMES = (u'copy', u'ffmpeg', u'dashcast')


# ----------------------------------------------------------------------------------------------------------------------

class Media(Model):

    ALL_STATUS = PENDING, READY, DELETED = u'PENDING', u'READY', u'DELETED'

    def __init__(self, user=None, user_id=None, parent=None, parent_id=None, uri=None, public_uris=None, filename=None,
                 metadata=None, status=PENDING, _id=None):
        super(Media, self).__init__(_id)
        self.user = dict2object(User, user, inspect_constructor=True) if isinstance(user, dict) else user
        if user is None:  # User attribute overrides user_id
            self.user_id = user_id
            del self.user
        self.parent = dict2object(Media, parent, inspect_constructor=True) if isinstance(parent, dict) else parent
        if parent is None:  # Parent attribute overrides parent_id
            self.parent_id = parent_id
            del self.parent
        self.uri = uri
        self.public_uris = public_uris or {}
        try:
            self.filename = unicode(filename).replace(u' ', u'_')
        except:
            self.filename = None
        self.metadata = metadata or {}
        self.status = status

    @property
    def is_dash(self):
        u"""
        Returns True if the media's filename point to a MPEG-DASH MPD.

        **Example usage**

        >>> import copy
        >>> from .models_test import MEDIA_TEST
        >>> media = copy.copy(MEDIA_TEST)
        >>> assert(not media.is_dash)
        >>> media.filename = u'test.mpd'
        >>> assert(media.is_dash)
        """
        return os.path.splitext(self.filename)[1].lower() == u'.mpd'

    def is_valid(self, raise_exception):
        if not super(Media, self).is_valid(raise_exception):
            return False
        # FIXME check user XOR user_id ...
        if (hasattr(self, u'user') and self.user is not None and
            (not isinstance(self.user, User) or not self.user.is_valid(False))):
            self._E(raise_exception, u'user is not a valid instance of user')
        if hasattr(self, u'user_id') and not valid_uuid(self.user_id, none_allowed=False):
            self._E(raise_exception, u'user_id is not a valid uuid string')
        if (hasattr(self, u'parent') and self.parent is not None and
            (not isinstance(self.parent, Media) or not self.parent.is_valid(False))):
            self._E(raise_exception, u'parent is not a valid instance of media')
        if hasattr(self, u'parent_id') and not valid_uuid(self.parent_id, none_allowed=True):
            self._E(raise_exception, u'parent_id is not a valid uuid string')
        # FIXME check uri
        # FIXME check public_uris
        if not valid_filename(self.filename):
            self._E(raise_exception, u'filename is not a valid file-name')
        # FIXME check metadata
        if not self.status in Media.ALL_STATUS:
            self._E(raise_exception, u'status is not in {0}'.format(Media.ALL_STATUS))
        return True

    def add_metadata(self, key, value, overwrite):
        if overwrite or not key in self.metadata:
            self.metadata[key] = value

    def get_metadata(self, key):
        return self.metadata[key] if key in self.metadata else None

    #def detect_codecs(self, storage_path):
    #''' Update media's metadata based on file's attribute '''

    def load_fields(self, user, parent):
        self.user = user
        self.parent = parent
        del self.user_id
        del self.parent_id


class User(Model):

    def __init__(self, first_name=None, last_name=None, mail=None, secret=None, admin_platform=False, _id=None):
        super(User, self).__init__(_id)
        self.first_name = first_name
        self.last_name = last_name
        self.mail = mail
        self.secret = secret
        self.admin_platform = (unicode(admin_platform).lower() == u'true')

    @property
    def credentials(self):
        return (self.mail, self.secret)

    @property
    def name(self):
        if self.first_name and self.last_name:
            return u'{0} {1}'.format(self.first_name, self.last_name)
        return u'anonymous'

    @property
    def is_secret_hashed(self):
        return self.secret is not None and self.secret.startswith(u'$pbkdf2-sha512$')

    def is_valid(self, raise_exception):
        if not super(User, self).is_valid(raise_exception):
            return False
        # FIXME check first_name
        # FIXME check last_name
        if not valid_email(self.mail):
            self._E(raise_exception, u'mail is not a valid email address')
        if not self.is_secret_hashed and not valid_secret(self.secret, True):
            self._E(raise_exception, u'secret is not safe (8+ characters, upper/lower + numbers eg. StrongP6s)')
        # FIXME check admin_platform
        return True

    def hash_secret(self, rounds=12000, salt=None, salt_size=16):
        u"""
        Hashes user's secret if it is not already hashed.

        **Example usage**

        >>> import copy
        >>> from .models_test import USER_TEST
        >>> user = copy.copy(USER_TEST)
        >>> user.is_secret_hashed
        False
        >>> len(user.secret)
        8
        >>> user.hash_secret()
        >>> user.is_secret_hashed
        True
        >>> len(user.secret)
        130
        >>> secret = user.secret
        >>> user.hash_secret()
        >>> assert(user.secret == secret)
        """
        if not self.is_secret_hashed:
            self.secret = pbkdf2_sha512.encrypt(
                self.secret, rounds=rounds, salt=salt, salt_size=salt_size)

    def verify_secret(self, secret):
        u"""
        Returns True if secret is equal to user's secret.

        **Example usage**

        >>> import copy
        >>> from .models_test import USER_TEST
        >>> user = copy.copy(USER_TEST)
        >>> user.verify_secret(u'bad_secret')
        False
        >>> user.verify_secret(u'Secr4taB')
        True
        >>> user.hash_secret()
        >>> user.verify_secret(u'bad_secret')
        False
        >>> user.verify_secret(u'Secr4taB')
        True
        """
        if self.is_secret_hashed:
            return pbkdf2_sha512.verify(secret, self.secret)
        return consteq(secret, self.secret)


class TransformProfile(Model):

    def __init__(self, title=None, description=None, encoder_name=None, encoder_string=None, _id=None):
        super(TransformProfile, self).__init__(_id)
        self.title = title
        self.description = description
        self.encoder_name = encoder_name
        self.encoder_string = encoder_string

    @property
    def is_dash(self):
        u"""
        >>> import copy
        >>> from .models_test import TRANSFORM_PROFILE_TEST
        >>> profile = copy.copy(TRANSFORM_PROFILE_TEST)
        >>> assert(not profile.is_dash)
        >>> profile.encoder_name = u'dashcast'
        >>> assert(profile.is_dash)
        """
        return self.encoder_name == u'dashcast'

    @property
    def dash_options(self):
        return self.encoder_string.split(u'/')[0].strip() if self.is_dash else None

    @property
    def dash_config(self):
        if not self.is_dash:
            return None
        try:
            return self.encoder_string.split(u'/')[1].strip().replace(u' ', u'\n')
        except:
            return u''

    def output_filename(self, input_filename, suffix=None):
        u"""
        >>> p = TransformProfile(title=u'test', encoder_name=u'copy')
        >>> print(p.output_filename(u'my_media.mkv'))
        my_media.mkv
        >>> print(p.output_filename(u'my_media.ts', suffix=u'_xyz'))
        my_media_xyz.ts
        >>> p.encoder_name = u'ffmpeg'
        >>> p.encoder_string = u"-r 25 -c:v libx264 -vf scale='trunc(oh*a/2)*2:min(480\,iw)' -acodec aac -f mp4"
        >>> print(p.output_filename(u'my_media.avi'))
        my_media.mp4
        >>> p.encoder_string = u'-acodec copy -vcodec copy'
        >>> print(p.output_filename(u'my_media.mov'))
        my_media.mov
        >>> p.encoder_name = u'dashcast'
        >>> print(p.output_filename(u'my_media.mp4', suffix=u' dash'))
        my_media dash.mpd
        """
        filename, extension = os.path.splitext(input_filename)
        if self.encoder_name == u'dashcast':
            extension = u'.mpd'
        elif self.encoder_name == u'ffmpeg':
            match = re.search(u'-f (?P<extension>\S+)', self.encoder_string)
            if match:
                extension = u'.' + match.groupdict()['extension']
        return u'{0}{1}{2}'.format(filename, suffix or u'', extension)

    # FIXME test other fields
    def is_valid(self, raise_exception):
        u"""
        >>> p = TransformProfile(title=u'test', encoder_name=u'ffmpeg')
        >>> print(p.dash_options)
        None
        >>> print(p.dash_config)
        None
        >>> p.encoder_name = u'dashcast'
        >>> p.encoder_string = u'--seg-dur 1000 --frag-dur 200 / [v1] type=video width=960 height=540 bitrate=1536000 [v2] type=video width=640 height=360 bitrate=819200 [v3] type=video width=480 height=270 bitrate=512000 [v4] type=video width=160 height=90 bitrate=256000 [a1] type=audio bitrate=98304'
        >>> print(p.dash_options)
        --seg-dur 1000 --frag-dur 200
        >>> print(p.dash_config)
        [v1]
        type=video
        width=960
        height=540
        bitrate=1536000
        [v2]
        type=video
        width=640
        height=360
        bitrate=819200
        [v3]
        type=video
        width=480
        height=270
        bitrate=512000
        [v4]
        type=video
        width=160
        height=90
        bitrate=256000
        [a1]
        type=audio
        bitrate=98304
        """
        if not valid_uuid(self._id, none_allowed=False):
            self._E(raise_exception, u'_id is not a valid uuid string')
        if not self.title or not self.title.strip():
            self._E(raise_exception, u'title is required')
        if not self.description or not self.title.strip():
            self._E(raise_exception, u'description is required')
        if not self.encoder_name in ENCODERS_NAMES:
            self._E(raise_exception, u'encoder_name is not a valid encoder')
        return True


# ----------------------------------------------------------------------------------------------------------------------

class PublisherTask(TaskModel):

    def __init__(self, user=None, user_id=None, media=None, media_id=None, publish_uri=None, revoke_task_id=None,
                 send_email=False, _id=None, statistic=None, status=TaskModel.UNKNOWN):
        super(PublisherTask, self).__init__(_id, statistic, status)
        self.user = dict2object(User, user, inspect_constructor=True) if isinstance(user, dict) else user
        if user is None:  # User attribute overrides user_id
            self.user_id = user_id
            del self.user
        self.media = dict2object(Media, media, inspect_constructor=True) if isinstance(media, dict) else media
        if media is None:  # Media attribute overrides media_id
            self.media_id = media_id
            del self.media
        self.publish_uri = publish_uri
        self.revoke_task_id = revoke_task_id
        self.send_email = send_email

    def is_valid(self, raise_exception):
        if not super(PublisherTask, self).is_valid(raise_exception):
            return False
        if (hasattr(self, u'user') and self.user is not None and
            (not isinstance(self.user, User) or not self.user.is_valid(False))):
            self._E(raise_exception, u'user is not a valid instance of user')
        if hasattr(self, u'user_id') and not valid_uuid(self.user_id, none_allowed=False):
            self._E(raise_exception, u'user_id is not a valid uuid string')
        if (hasattr(self, u'media') and self.media is not None and
            (not isinstance(self.media, Media) or not self.media.is_valid(False))):
            self._E(raise_exception, u'media is not a valid instance of media')
        if hasattr(self, u'media_id') and not valid_uuid(self.media_id, none_allowed=False):
            self._E(raise_exception, u'media_id is not a valid uuid string')
        # FIXME check publish_uri
        if not valid_uuid(self.revoke_task_id, none_allowed=True):
            self._E(raise_exception, u'revoke_task_id is not a valid uuid string')
        # FIXME check send_email
        return True

    def load_fields(self, user, media):
        self.user = user
        self.media = media
        del self.user_id
        del self.media_id


class TransformTask(TaskModel):

    def __init__(self, user=None, user_id=None, media_in=None, media_in_id=None, media_out=None, media_out_id=None,
                 profile=None, profile_id=None, send_email=False, _id=None, statistic=None,
                 status=TaskModel.UNKNOWN):
        super(TransformTask, self).__init__(_id, statistic, status)
        self.user = dict2object(User, user, inspect_constructor=True) if isinstance(user, dict) else user
        if user is None:  # User attribute overrides user_id
            self.user_id = user_id
            del self.user
        self.media_in = dict2object(Media, media_in, True) if isinstance(media_in, dict) else media_in
        if media_in is None:  # Media_in attribute overrides media_in_id
            self.media_in_id = media_in_id
            del self.media_in
        self.media_out = dict2object(Media, media_out, True) if isinstance(media_out, dict) else media_out
        if media_out is None:  # Media_out attribute overrides media_out_id
            self.media_out_id = media_out_id
            del self.media_out
        self.profile = dict2object(TransformProfile, profile, True) if isinstance(profile, dict) else profile
        if profile is None:  # Profile attribute overrides profile_id
            self.profile_id = profile_id
            del self.profile
        self.send_email = send_email

    def is_valid(self, raise_exception):
        if not super(TransformTask, self).is_valid(raise_exception):
            return False
        if (hasattr(self, u'user') and self.user is not None and
            (not isinstance(self.user, User) or not self.user.is_valid(False))):
            self._E(raise_exception, u'user is not a valid instance of user')
        if hasattr(self, u'user_id') and not valid_uuid(self.user_id, none_allowed=False):
            self._E(raise_exception, u'user_id is not a valid uuid string')
        if (hasattr(self, u'media_in') and self.media_in is not None and
            (not isinstance(self.media_in, Media) or not self.media_in.is_valid(False))):
            self._E(raise_exception, u'media_in is not a valid instance of media')
        if hasattr(self, u'media_in_id') and not valid_uuid(self.media_in_id, none_allowed=False):
            self._E(raise_exception, u'media_in_id is not a valid uuid string')
        if (hasattr(self, u'media_out') and self.media_out is not None and
            (not isinstance(self.media_out, Media) or not self.media_out.is_valid(False))):
            self._E(raise_exception, u'media_out is not a valid instance of media')
        if hasattr(self, u'media_out_id') and not valid_uuid(self.media_out_id, none_allowed=False):
            self._E(raise_exception, u'media_out_id is not a valid uuid string')
        if (hasattr(self, u'profile') and self.profile is not None and
            (not isinstance(self.profile, TransformProfile) or not self.profile.is_valid(False))):
            self._E(raise_exception, u'profile is not a valid instance of transformation profile')
        if hasattr(self, u'profile_id') and not valid_uuid(self.profile_id, none_allowed=False):
            self._E(raise_exception, u'profile_id is not a valid uuid string')
        # FIXME check send_email
        return True

    def load_fields(self, user, media_in, media_out, profile):
        self.user = user
        self.media_in = media_in
        self.media_out = media_out
        self.profile = profile
        del self.user_id
        del self.media_in_id
        del self.media_out_id
        del self.profile_id

    @staticmethod
    def validate_task(media_in, profile, media_out):
        if media_in.status != Media.READY:
            raise NotImplementedError(to_bytes(u"Cannot launch the task, input media asset's status is {0}.".format(
                                      media_in.status)))
        if media_in.is_dash and profile.encoder_name != u'copy':
            raise NotImplementedError(to_bytes(u'Cannot launch the task, input media asset is MPEG-DASH content and enc'
                                      'oder is not copy.'))
        if profile.is_dash and not media_out.is_dash:
            raise ValueError(to_bytes(u'Cannot launch the task, output media asset is not a MPD but task is based on a '
                             'MPEG-DASH encoder called {0}.'.format(profile.encoder_name)))
        if not profile.is_dash and media_out.is_dash:
            raise ValueError(to_bytes(u'Cannot launch the task, output media asset is a MPD but task is not based on a '
                             'MPEG-DASH encoder called {0}.'.format(profile.encoder_name)))
