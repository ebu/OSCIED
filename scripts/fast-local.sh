#!/usr/bin/env bash

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012 OSCIED Team. All rights reserved.
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
# Retrieved from https://github.com/EBU-TI/OSCIED

. ./common.sh

techo 'Temporary utility to speed-up testing of charms'

# Simple helper to speed-up LXC containers
yesOrNo $false 'Mount a ramdisk of 3GB for LXC VMs (Max. 3 VMs)'
if [ $REPLY -eq $true ]; then
  $udo umount /var/lib/lxc 2>/dev/null
  $udo mount -t tmpfs -o size=3072M tmpfs /var/lib/lxc
fi

yesOrNo $true 'Download Ubuntu cloud image to LXC cache'
if [ $REPLY -eq $true ]; then
  cd "$TOOLS_PATH" || xecho "Unable to find path $TOOLS_PATH"
  cloud_host='https://cloud-images.ubuntu.com'
  cloud_list_url="$cloud_host/query/$RELEASE/server/released-dl.current.txt"
  lxc_cache='/var/cache/lxc/cloud-raring'
  wget -N "$cloud_list_url"
  cloud_image_url="$cloud_host/$(cat $(basename $cloud_list_url) | grep amd64 | cut -f6)"
  wget -N "$cloud_image_url"
  $udo mkdir -p "$lxc_cache" 2>/dev/null
  $udo cp -a "$(basename $cloud_image_url)" "$lxc_cache/"
fi

lu-importUtils ../charms/
sh juju-menu.sh overwrite
sh juju-menu.sh
