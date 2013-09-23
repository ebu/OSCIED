#!/usr/bin/env bash

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : CLOUD
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

. ./common.sh

# Must be done before (boostrap of the bootstrap)
# sudo apt-get install subversion
# svn co https://claire-et-david.dyndns.org/prog/OSCIED/components/cloud/nodes \
#   --username=oscied --password=####

pecho "Configure passwordless sudo for user $USER"
nopasswd="$USER ALL=(ALL) NOPASSWD: ALL"
if ! $udo grep -q "$nopasswd" /etc/sudoers
then $udo sh -c "echo '$nopasswd' >> /etc/sudoers"
else recho 'sudoers already modified'
fi

pecho 'Bootstrap : Add automatic call to setup script'
if [ ! -e $HOME/setup.sh ]
then ln -s $(pwd)/setup-helper.sh $HOME/setup.sh
else recho 'symlink to setup.sh already created'
fi
if ! $udo grep -q 'setup.sh' /etc/rc.local; then
  boot="su $USER -c 'cd $HOME \&\& sh setup.sh startup' \&\n&"
  $udo sed -i "s:^exit 0:$boot:" /etc/rc.local
else
  recho 'call to setup script already added'
fi
$udo chmod +x /etc/rc.local

pecho 'Upgrade the system'
eval $update
eval $upgrade
eval $distupgrade
eval $autoremove

pecho 'Configure the bootloader'
# Fix ticket #42 : Sometimes grub doesn't start default "option" automatically.
fail='GRUB_RECORDFAIL_TIMEOUT=2'
if ! grep -q "$fail" /etc/default/grub; then
  $udo sed -i "s:GRUB_TIMEOUT=.*:GRUB_TIMEOUT=2:" /etc/default/grub
  $udo sh -c "echo '$fail' >> /etc/default/grub"
  $udo update-grub
else
  recho 'bootloader already modified'
fi

pecho 'Install some tools'
#sudo grep fr /usr/share/i18n/SUPPORTED
$udo locale-gen fr_CH.UTF-8
eval $install linux-headers-generic openssh-server

recho 'Job done'
