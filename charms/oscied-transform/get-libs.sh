#!/usr/bin/env bash

get_from_git()
{
  rm -rf ${1}* 2>/dev/null
  git clone --depth 0 $2 $1 || exit $3
  rm -rf $1/.git
  tar -cjf ${1}.tar.bz2 -C $1 .
  rm -rf $1
}

get_from_svn()
{
  rm -rf ${1}* 2>/dev/null
  svn export $2 $1 || exit $3
  tar -cjf ${1}.tar.bz2 -C $1 .
  rm -rf $1
}

#get_from_svn 'gpac'           'http://svn.code.sf.net/p/gpac/code/trunk/gpac/' 1
#get_from_git 'ffmpeg'         'git://source.ffmpeg.org/ffmpeg.git'             2
#get_from_svn 'openSVCDecoder' 'svn://svn.code.sf.net/p/opensvcdecoder/code/'   3
#get_from_git 'openHEVC'       'git://github.com/OpenHEVC/openHEVC.git'         4
#get_from_git 'x264'           'git://git.videolan.org/x264.git'                5

wget -N http://download.tsi.telecom-paristech.fr/gpac/latest_builds/linux64/gpac/gpac_0.5.1.DEV-r4944_amd64.deb
#wget -N http://download.tsi.telecom-paristech.fr/gpac/latest_builds/linux32/gpac/gpac_0.5.1.DEV-r4944_i386.deb
