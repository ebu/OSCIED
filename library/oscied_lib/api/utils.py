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

import os, uuid
from pytoolbox.encoding import csv_reader, to_bytes

from ..config_test import ORCHESTRA_CONFIG_TEST
from ..models import Media, User, TransformProfile
from .server import OrchestraAPICore


def get_test_api_core():
    u"""Return an instance of ``OrchestraAPICore`` initialized with current scenario's configuration."""
    orchestra = OrchestraAPICore(ORCHESTRA_CONFIG_TEST)
    init_api(orchestra, u'mock')
    print(u'There are {0} registered users.'.format(len(orchestra.get_users())))
    print(u'There are {0} available media assets.'.format(len(orchestra.get_medias())))
    print(u'There are {0} available transformation profiles.'.format(len(orchestra.get_transform_profiles())))
    print(u'There are {0} launched transformation tasks.'.format(len(orchestra.get_transform_tasks())))
    return orchestra


def init_api(api_core_or_client, api_init_csv_directory, flush=False, add_users=True, add_profiles=True,
             add_medias=True, add_tasks=True, backup_medias_in_remote=True):
    u"""
    Initialize an instance of ``OrchestraAPICore`` or use provided instance of ``OrchestraAPIClient`` to initialize a
    remote orchestration unit.
    """
    is_core = isinstance(api_core_or_client, OrchestraAPICore)
    orchestra = api_core_or_client if is_core else None
    api_client = api_core_or_client if not is_core else None
    is_standalone = not is_core or orchestra.is_standalone

    if flush:
        if is_core:
            orchestra.flush_db()
            # FIXME remove media files
        else:
            api_client.flush()
            api_client.remove_medias()

    add_users = add_users and is_standalone
    users, reader = [], csv_reader(os.path.join(api_init_csv_directory, u'users.csv'))
    for first_name, last_name, email, secret, admin_platform in reader:
        user = User(first_name, last_name, email, secret, admin_platform)
        users.append(user)
        if not add_users:
            continue
        print(u'Adding user {0}'.format(user.name))
        if is_core:
            orchestra.save_user(user, hash_secret=True)
        else:
            api_client.users.add(user)
    users = orchestra.get_users() if is_core and is_standalone else users# api_client.users.list()

    if add_profiles:
        i, reader = 0, csv_reader(os.path.join(api_init_csv_directory, u'tprofiles.csv'))
        for title, description, encoder_name, encoder_string in reader:
            user = users[i]
            profile = TransformProfile(title=title, description=description, encoder_name=encoder_name,
                                       encoder_string=encoder_string)
            print(u'Adding transformation profile {0} as user {1}'.format(profile.title, user.name))
            if is_core:
                orchestra.save_transform_profile(profile)
            else:
                api_client.auth = user
                api_client.transform_profiles.add(profile)
            i = (i + 1) % len(users)

    if add_medias:
        i, reader = 0, csv_reader(os.path.join(api_init_csv_directory, u'medias.csv'))
        for local_filename, filename, title in reader:
            local_filename = os.path.abspath(os.path.expanduser(local_filename))
            user = users[i]
            media = Media(user_id=user._id, filename=filename, metadata={u'title': title}, status=u'READY')
            if not os.path.exists(local_filename):
                print(u'Skip media asset {0}, file "{1}" Not found.'.format(media.metadata[u'title'], local_filename))
                continue
            print(u'Adding media asset {0} as user {1}'.format(media.metadata[u'title'], user.name))
            if is_core:
                #orchestra.config. bla bla -> get media.uri
                orchestra.save_media(media)
            else:
                api_client.auth = user
                media.uri = api_client.upload_media(local_filename, backup_in_remote=backup_medias_in_remote)
                api_client.medias.add(media)
            i = (i + 1) % len(users)

    if not is_core:
        return

    if add_tasks:
        reader = csv_reader(os.path.join(api_init_csv_directory, u'ttasks.csv'))
        for user_email, in_filename, profile_title, out_filename, out_title, send_email, queue in reader:
            user = orchestra.get_user({u'mail': user_email}) if is_standalone else User(_id=uuid.uuid4())
            if not user:
                raise IndexError(to_bytes(u'No user with e-mail address {0}.'.format(user_email)))
            for media in orchestra.get_medias():
                print(media.filename)
            media_in = orchestra.get_media({u'filename': in_filename})
            if not media_in:
                raise IndexError(to_bytes(u'No media asset with filename {0}.'.format(in_filename)))
            profile = orchestra.get_transform_profile({u'title': profile_title})
            if not profile:
                raise IndexError(to_bytes(u'No transformation profile with title {0}.'.format(profile_title)))
            print(u'Launching transformation task {0} with profile {1} as user {2}.'.format(
                  media_in.metadata[u'title'], profile.title, user.name))
            metadata = {u'title': out_title}
            orchestra.launch_transform_task(user._id, media_in._id, profile._id, out_filename, metadata, send_email,
                                            queue, u'/transform/callback')
