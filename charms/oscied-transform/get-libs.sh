#!/usr/bin/env bash

get_gpac()
{
  rm -rf gpac* 2>/dev/null
  svn export http://svn.code.sf.net/p/gpac/code/trunk/gpac/ || exit 1
  tar -cjf gpac.tar.bz2 -C gpac .
  rm -rf gpac
}

get_openSVCDecoder()
{
  rm -rf openSVCDecoder* 2>/dev/null
  svn export svn://svn.code.sf.net/p/opensvcdecoder/code/ openSVCDecoder || exit 2
  tar -cjf openSVCDecoder.tar.bz2 -C openSVCDecoder .
  rm -rf openSVCDecoder
}

get_openHEVC()
{
  rm -rf openHEVC* 2>/dev/null
  git clone --depth 0 git://github.com/OpenHEVC/openHEVC.git || exit 3
  rm -rf openHEVC/.git
  tar -cjf openHEVC.tar.bz2 -C openHEVC .
  rm -rf openHEVC
}

get_x264()
{
  rm -rf x264* 2>/dev/null
  git clone --depth 0 git://git.videolan.org/x264.git || exit 4
  rm -rf x264/.git
  tar -cjf x264.tar.bz2 -C x264 .
  rm -rf x264
  #git init
  #git remote add origin git://git.videolan.org/x264.git
  #git fetch origin 9e941d1fabb2de4b15f169057a07dc395307d2ce
  #git reset --hard FETCH_HEAD
}

get_gpac
get_openSVCDecoder
get_openHEVC
get_x264
