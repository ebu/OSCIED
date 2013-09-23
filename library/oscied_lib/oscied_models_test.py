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

import uuid
from oscied_config_test import ORCHESTRA_CONFIG_TEST
from oscied_models import Media, User, TransformProfile, PublisherTask, TransformTask


MEDIA_TEST = Media(user_id=unicode(uuid.uuid4()), parent_id=unicode(uuid.uuid4()), filename=u'tabby.mpg',
                   metadata={u'title': u"Tabby's adventures §1", u'description': u'My cat drinking water'},
                   status=Media.PENDING)
MEDIA_TEST.uri = ORCHESTRA_CONFIG_TEST.storage_medias_uri(MEDIA_TEST)
MEDIA_TEST.add_metadata(u'title', u'not authorized overwrite', False)
MEDIA_TEST.add_metadata(u'size', 4096, True)
USER_TEST = User(first_name=u'David', last_name=u'Fischer', mail=u'david.fischer.ch@gmail.com', secret=u'Secr4taB',
                 admin_platform=True)

TRANSFORM_PROFILE_TEST = TransformProfile(title=u'HD 1080p', description=u'MP4 H.264 1080p, audio copy',
                                          encoder_name=u'ffmpeg', encoder_string=u'-c:a copy ...')

PUBLISH_JOB_TEST = PublisherTask(user_id=USER_TEST._id, media_id=MEDIA_TEST._id,
                                 publish_uri=u'http://amazon.com/salut.mpg')

TRANSFORM_JOB_TEST = TransformTask(user_id=USER_TEST._id, media_in_id=MEDIA_TEST._id, media_out_id=MEDIA_TEST._id,
                                   profile_id=TRANSFORM_PROFILE_TEST._id)
