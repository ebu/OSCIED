#! /usr/bin/env python
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
# Retrieved from:
#   svn co https://claire-et-david.dyndns.org/prog/OSCIED

import fcntl
import os
import re
import select
import shlex
import subprocess
import time


def get_media_duration(filename):
    cmd = 'ffmpeg -i "%s"' % (filename)
    pipe = subprocess.Popen(shlex.split(cmd), stderr=subprocess.PIPE, close_fds=True)
    duration = re.search('Duration: (?P<duration>\S+),', pipe.stderr.read())
    return None if not duration else duration.group('duration')


def encode(in_filename, out_filename, encoder_string, overwrite, sleep_time=1, callback=None):
    if os.path.exists(out_filename):
        if not overwrite:
            return False
        os.unlink(out_filename)
    cmd = 'ffmpeg -i "%s" ' + encoder_string + ' "%s"' % (in_filename, out_filename)
    pipe = subprocess.Popen(shlex.split(cmd), stderr=subprocess.PIPE, close_fds=True)

    # http://stackoverflow.com/questions/1388753/how-to-get-output-from-subprocess-popen
    fcntl.fcntl(pipe.stderr.fileno(), fcntl.F_SETFL,
                fcntl.fcntl(pipe.stderr.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,)

    # frame= 2071 fps=  0 q=-1.0 size=   34623kB time=00:01:25.89 bitrate=3302.3kbits/s
    regex = re.compile("frame=\s*(?P<frame>\d+)" +
                       "\s+fps=\s*(?P<fps>\d+)" +
                       "\s+q=\s*(?P<q>\S+)" +
                       "\s+\S*size=\s*(?P<size>\S+)" +
                       "\s+time=\s*(?P<time>\S+)" +
                       "\s+bitrate=\s*(?P<bitrate>\S+)")
    while True:
        readx = select.select([pipe.stderr.fileno()], [], [])[0]
        if readx:
            chunk = pipe.stderr.read()
            if chunk == '':
                break
            match = regex.match(chunk)
            if match and callback:
                callback(match.groupdict())
        time.sleep(sleep_time)
    return True

#def test_callback(dict):
#    print dict
#
#if __name__ == '__main__':
#    print FFmpeg.duration(movie)
#    FFmpeg.encode(movie, movie_out, '-acodec copy -vcodec copy', True, test_callback)
