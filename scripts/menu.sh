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

main()
{
  if [ $# -gt 0 ]; then
    operation_auto="$1"
    shift
  elif [ $# -eq 0 ]; then
    operation_auto=''
  else
    xecho "Usage: $(basename $0) (nothing) -or- operation [parameters]"
  fi

  autoInstall dialog dialog

  get_root_secret;   ROOT_AUTH="root:$REPLY"
  get_node_secret;   NODE_AUTH="node:$REPLY"
  get_orchestra_url; ORCHESTRA_URL=$REPLY

  mkdir -p "$MEDIAS_PATH" 2>/dev/null

  listing=/tmp/$$.list
  tmpfile=/tmp/$$
  trap "rm -f '$listing' '$tmpfile' 2>/dev/null" INT TERM EXIT

  if [ "$operation_auto" ]; then
    ok=$false
    techo 'OSCIED General Operations [AUTO]'
    mecho "Operation is $operation_auto"
    eval $operation_auto "$@"
    if [ $ok -eq $false ]; then
      xecho "Unknown operation : $operation_auto"
    fi
  else
    # Initialize main menu
    while true
    do
      $DIALOG --backtitle 'OSCIED General Operations' \
              --menu 'Please select an operation' 0 0 0 \
              install              'Download / update documents and tools'           \
              cleanup              'Cleanup configuration of charms (deploy path)'   \
              revup                "Increment all charm's revision (+1)"             \
              api_init_setup       'Initialize demo setup with Orchestra API'        \
              api_launch_transform 'Launch a transform job with Orchestra API'       \
              api_revoke_transform 'Revoke a transform job with Orchestra API'       \
              api_launch_publish   'Launch a publish job with Orchestra API'         \
              api_revoke_publish   'Revoke a publish job with Orchestra API'         \
              api_test_all         'Test the whole methods of Orchestra API'         \
              api_get_all          'Get listings of all things with Orchestra API'   \
              webui_test_common    'Test some functions of Web UI hooks'             \
              rsync_orchestra      'Rsync local code to running Orchestra instance'  \
              rsync_publisher      'Rsync local code to running Publisher instance'  \
              rsync_transform      'Rsync local code to running Transform instance'  \
              rsync_webui          'Rsync local code to running Web UI instance' 2> $tmpfile

      retval=$?
      operation=$(cat $tmpfile)

      # Main menu exit door
      [ $retval -ne 0 -o ! "$operation" ] && break

      techo "Execute operation $operation"
      eval $operation

      # Main menu pause
      [ $retval -eq 0 ] && pause
    done
  fi
}

install()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) install"
  fi
  ok=$true

  pecho 'Update submodules'
  cd "$BASE_PATH" || xecho "Unable to find path $BASE_PATH"
  git submodule foreach git pull

  pecho 'Import logicielsUbuntu'
  if ! which lu-importUtils > /dev/null; then
    cd "$TOOLS_PATH/logicielsUbuntu" || xecho "Unable to find path $TOOLS_PATH/logicielsUbuntu"
    sh logicielsUbuntuExports
    recho 'Please restart this script once from a new terminal'
    recho 'or after having executed the following:'
    cecho 'source ~/.bashrc'
    pause
    exit 0
  else
    cd "$SCRIPTS_PATH" || xecho "Unable to find path $SCRIPTS_PATH"
    lu-importUtils . || xecho 'Unable to import utilities of logicielsUbuntu'
  fi

  pecho 'Install prerequisites'
  eval $install bzr git-core python-pip rst2pdf texlive-latex-recommended \
    texlive-latex-extra texlive-fonts-recommended || xecho 'Unable to install prerequisites'

  pecho 'Update sublime text configuration'
  find "$SUBLIME_PATH" -type f -exec sed -i "s:BASE_PATH:$BASE_PATH:g" {} \;

  pecho 'Download references'
  cd "$REFERENCES_PATH"|| xecho "Unable to find path $REFERENCES_PATH"
  openstack='http://docs.openstack.org'
  wget -N $openstack/trunk/openstack-compute/install/apt/openstack-install-guide-apt-trunk.pdf
  wget -N $openstack/cli/quick-start/content/cli-guide.pdf
  wget -N $openstack/api/openstack-compute/programmer/openstackapi-programming.pdf
  wget -N $openstack/folsom/openstack-compute/admin/bk-compute-adminguide-folsom.pdf
  wget -N $openstack/folsom/openstack-network/admin/bk-quantum-admin-guide-folsom.pdf
  wget -N $openstack/folsom/openstack-object-storage/admin/os-objectstorage-adminguide-folsom.pdf

  pecho 'Download tools'

  cd "$TOOLS_PATH"|| xecho "Unable to find path $TOOLS_PATH"
  clonezilla='http://switch.dl.sourceforge.net/project/clonezilla'
  wget -N $clonezilla/clonezilla_live_stable/2.1.1-25/clonezilla-live-2.1.1-25-amd64.zip

  if [ -d 'juju-source' ]; then cd 'juju-source' && bzr merge && cd ..
  else bzr branch lp:juju 'juju-source'
  fi

  addAptPpaRepo ppa:juju/pkgs juju || xecho 'Unable to add juju PPA repository'
  eval $install --reinstall lxc apt-cacher-ng libzookeeper-java zookeeper juju juju-jitsu \
    charm-tools || xecho 'Unable to install JuJu orchestrator'

  #cat \
  # /var/lib/apt/lists/ppa.launchpad.net_juju_pkgs_ubuntu_dists_quantal_main_binary-amd64_Packages \
  # | grep Package
  #Package: python-txzookeeper
  #Package: ...

  plantuml=http://downloads.sourceforge.net/project/plantuml
  wget -N $plantuml/plantuml.jar
  wget -N $plantuml/PlantUML%20Language%20Reference%20Guide.pdf

  if cd "$TOOLS_PATH/rabbitmq-tutorials"; then
    readLine 'Please enter local RabbitMQ guest user password [default=guest]'
    [ "$CHOICE" ] && pass=$CHOICE || pass='guest'
    a='amqp://.*localhost/'
    b="amqp://guest:$pass@localhost/"
    find . -type f -exec sed -i "s#$a#$b#g" {} \;
    git status
  else
    recho 'Unable to find RabbitMQ tutorials path'
  fi

  pecho 'Fix https://github.com/martinkou/bson/issues/19, bson not installed'
  $udo pip install --upgrade docutils pygments sphinx sphinxcontrib-email \
    sphinxcontrib-googlechart sphinxcontrib-httpdomain flask celery pymongo requests

  pecho 'Fix https://bitbucket.org/birkenfeld/sphinx/pull-request/98/fixes-typeerror-raised-from/diff'
  $udo find /usr/local/lib/ -type f -name latex.py -path "*/sphinx/writers/*" -exec \
    sed -i 's:letter.translate(tex_escape_map)):unicode(letter).translate(tex_escape_map)):g' {} \;

  pecho 'Fixes #7 - https://github.com/EBU-TI/OSCIED/issues/7'
  $udo sed -i 's:#!/usr/bin/python3.*:#!/usr/bin/python3 -Es:' /usr/bin/lxc-ls
}

cleanup()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) cleanup"
  fi
  ok=$true

  cd "$CHARMS_DEPLOY_PATH" || xecho "Unable to find path $CHARMS_DEPLOY_PATH"
  git reset --hard  # Revert changes to modified files
  git clean -fd     # Remove all untracked files and directories
}

revup()
{
  if [ $# -eq 0 ]; then
    xecho "Usage: $(basename $0) revup"
  fi
  ok=$true

  cd "$CHARMS_PATH" || xecho "Unable to find path $CHARMS_PATH"
  find . -maxdepth 2 -type f -path "*/oscied-*/*" -name revision | while read revision
  do
    value=$(cat "$revision")
    echo $((value+1)) > "$revision"
    mecho "$(basename $(dirname $(dirname $revision))) is not at revision $(cat $revision)"
  done
}

api_init_setup()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) api_init_setup"
  fi
  ok=$true

  pecho 'Flush database'
  yesOrNo $false "do you really want to flush orchestrator $ORCHESTRA_URL"
  if [ $REPLY -eq $false ]; then
    recho 'operation aborted by user'
    exit 0
  fi
  test_api 200 POST $ORCHESTRA_URL/flush "$ROOT_AUTH" ''

  pecho 'Add users'
  count=1
  savedIFS=$IFS
  IFS=';'
  while read fname lname mail secret aplatform
  do
    if [ ! "$fname" -o ! "$lname" -o ! "$mail" -o ! "$secret" -o ! "$aplatform" ]; then
      xecho "Line $count : Bad line format !"
    fi
    json_user "$fname" "$lname" "$mail" "$secret" "$aplatform"
    echo "$JSON"
    test_api 200 POST $ORCHESTRA_URL/user "$ROOT_AUTH" "$JSON"
    save_auth "user$count" "$mail:$secret"
    save_json "user$count" "$JSON"
    save_id   "user$count" "$ID"
    count=$((count+1))
  done < "$CONFIG_API_USERS_FILE"
  IFS=$savedIFS

  get_auth 'user1'; user1_auth=$REPLY

  pecho 'Add medias'
  count=1
  savedIFS=$IFS
  IFS=';'
  while read uri vfilename title
  do
    if [ ! "$uri" -o ! "$vfilename" -o ! "$title" ]; then
      xecho "Line $count : Bad line format !"
    fi
    media="$MEDIAS_PATH/$uri"
    if [ ! -f "$media" ]; then
      recho "[WARNING] Unable to find media file $media"
      continue
    fi
    mecho "Uploading media $uri to uploads into shared storage unit ..."
    storage_upload_media "$media" || xecho "Unable to upload media"
    json_media "$REPLY" "$vfilename" "$title"
    echo "$JSON"
    test_api 200 POST $ORCHESTRA_URL/media "$user1_auth" "$JSON"
    save_json "media$count" "$JSON"
    save_id   "media$count" "$ID"
    count=$((count+1))
  done < "$CONFIG_API_MEDIAS_FILE"
  IFS=$savedIFS

  pecho 'Add transform profiles'
  count=1
  savedIFS=$IFS
  IFS=';'
  while read title description encoder_string
  do
    if [ ! "$title" -o ! "$description" -o ! "$encoder_string" ]; then
      xecho "Line $count : Bad line format !"
    fi
    json_tprofile "$title" "$description" "$encoder_string"
    echo "$JSON"
    test_api 200 POST $ORCHESTRA_URL/transform/profile "$user1_auth" "$JSON"
    save_json "tprofile$count" "$JSON"
    save_id   "tprofile$count" "$ID"
    count=$((count+1))
  done < "$CONFIG_API_TPROFILES_FILE"
  IFS=$savedIFS

  #pecho 'Add medias'
  #$udo mkdir -p /mnt/storage/medias /mnt/storage/uploads
  #$udo cp "$SCRIPTS_PATH/common.sh" /mnt/storage/uploads/tabby.mpg
  #test_api 200 POST $ORCHESTRA_URL/media "$admin_auth" "$media1_json"; save_id 'media1' "$ID"

}

api_launch_transform()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) api_launch_transform"
  fi
  ok=$true

  pecho 'Gather required authorizations and IDs'
  get_auth 'user1';     user1_auth=$REPLY
  get_id   'media1';    media1_id=$REPLY
  get_id   'tprofile2'; tprofile1_id=$REPLY

  pecho 'Launch a transform job'
  json_tjob "$media1_id" "$tprofile1_id" "tabby2.mpg" 'transcoded media1' 'transform_private' 'high'
  echo "$JSON"
  test_api 200 POST $ORCHESTRA_URL/transform/job "$user1_auth" "$JSON"
  save_id 'tjob1' "$ID"
  get_id  'tjob1'
  echo $REPLY
}

api_revoke_transform()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) api_revoke_transform"
  fi
  ok=$true

  pecho 'Gather required authorizations and IDs'
  get_auth 'user1'; user1_auth=$REPLY
  get_id   'tjob1'; tjob1_id=$REPLY

  pecho 'Revoke a transform job'
  test_api 200 DELETE $ORCHESTRA_URL/transform/job/id/$tjob1_id "$user1_auth" ''
}

api_launch_publish()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) api_launch_publish"
  fi
  ok=$true

  pecho 'Gather required authorizations and IDs'
  get_auth 'user1';  user1_auth=$REPLY
  get_id   'media1'; media1_id=$REPLY

  pecho 'Launch a publish job'
  json_pjob "$media1_id" 'publisher_private' 'high'
  echo "$JSON"
  test_api 200 POST $ORCHESTRA_URL/publish/job "$user1_auth" "$JSON"
  save_id 'pjob1' "$ID"
  get_id  'pjob1'
  echo $REPLY
}

api_revoke_publish()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) api_revoke_pubish"
  fi
  ok=$true

  pecho 'Gather required authorizations and IDs'
  get_auth 'user1'; user1_auth=$REPLY
  get_id   'pjob1'; pjob1_id=$REPLY

  pecho 'Revoke a publish job'
  test_api 200 DELETE $ORCHESTRA_URL/publish/job/id/$pjob1_id "$user1_auth" ''
}

api_test_all()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) api_test_all"
  fi
  ok=$true

  cd "$CHARMS_PATH/oscied-orchestra/lib" || \
    xecho "Unable to find path $CHARMS_PATH/oscied-orchestra/lib"

  techo '1/4 Test source code'

  test_code Callback.py
  test_code Media.py
  test_code OrchestraConfig.py
  test_code PublisherConfig.py
  test_code TransformConfig.py
  test_code TransformProfile.py
  test_code User.py
  test_code Utilities.py

  techo '2/4 Initialize Orchestra database'

  api_init_setup

  techo '3/4 Gather required authorizations and IDs'

  get_auth 'user1';     user1_auth=$REPLY
  get_id   'user1';     user1_id=$REPLY
  get_json 'user1';     user1_json=$REPLY
  get_auth 'user2';     user2_auth=$REPLY
  get_id   'user2';     user2_id=$REPLY
  get_json 'user2';     user2_json=$REPLY
  get_auth 'user3';     user3_auth=$REPLY
  get_id   'user3';     user3_id=$REPLY
  get_json 'user3';     user3_json=$REPLY
  #get_id   'media1';    media1_id=$REPLY
  #get_json 'media1';    media1_json=$REPLY
  get_id   'tprofile1'; tprofile1_id=$REPLY
  get_json 'tprofile1'; tprofile1_json=$REPLY

  techo '4/4 Test Orchestra API'
  api_test_main
  api_test_user
  #api_test_media
  #api_test_tprofile
  #api_test_tjob
  mecho 'Unit test passed (Orchestrator API OK)'
}

api_test_main()
{
  pecho 'Test main API'
  test_api 401 POST $ORCHESTRA_URL/flush ''            ''
  test_api 401 POST $ORCHESTRA_URL/flush "$BAD_AUTH"   ''
  test_api 403 POST $ORCHESTRA_URL/flush "$user2_auth" ''
  test_api 200 GET  $ORCHESTRA_URL       ''            ''
  test_api 200 GET  $ORCHESTRA_URL/index ''            ''
  test_api 200 GET  $ORCHESTRA_URL       "$BAD_AUTH"   ''
  test_api 200 GET  $ORCHESTRA_URL/index "$BAD_AUTH"   ''
  test_api 200 GET  $ORCHESTRA_URL       "$ROOT_AUTH"  ''
  test_api 200 GET  $ORCHESTRA_URL/index "$ROOT_AUTH"  ''
  test_api 200 GET  $ORCHESTRA_URL       "$NODE_AUTH"  ''
  test_api 200 GET  $ORCHESTRA_URL/index "$NODE_AUTH"  ''
  test_api 200 GET  $ORCHESTRA_URL       "$user1_auth" ''
  test_api 200 GET  $ORCHESTRA_URL/index "$user1_auth" ''
  test_api 200 GET  $ORCHESTRA_URL       "$user2_auth" ''
  test_api 200 GET  $ORCHESTRA_URL/index "$user2_auth" ''
}

api_test_user()
{
  pecho 'Test user API'
  mecho 'We cannot double post an user'
  test_api 400 POST $ORCHESTRA_URL/user "$ROOT_AUTH" "$user1_json"
  mecho 'Anonymous can get nothing except one'
  test_api 200 GET $ORCHESTRA_URL                   '' ''
  test_api 200 GET $ORCHESTRA_URL/index             '' ''
  test_api 401 GET $ORCHESTRA_URL/user/login        '' ''
  test_api 401 GET $ORCHESTRA_URL/user/count        '' ''
  test_api 401 GET $ORCHESTRA_URL/user              '' ''
  test_api 401 GET $ORCHESTRA_URL/user/id/$user1_id '' ''
  mecho 'Charlie can get nothing except one'
  test_api 200 GET $ORCHESTRA_URL                   "$BAD_AUTH" ''
  test_api 200 GET $ORCHESTRA_URL/index             "$BAD_AUTH" ''
  test_api 401 GET $ORCHESTRA_URL/user/login        "$BAD_AUTH" ''
  test_api 401 GET $ORCHESTRA_URL/user/count        "$BAD_AUTH" ''
  test_api 401 GET $ORCHESTRA_URL/user              "$BAD_AUTH" ''
  test_api 401 GET $ORCHESTRA_URL/user/id/$user1_id "$BAD_AUTH" ''
  mecho 'Root can get a lot of things'
  test_api 200 GET $ORCHESTRA_URL                   "$ROOT_AUTH" ''
  test_api 200 GET $ORCHESTRA_URL/index             "$ROOT_AUTH" ''
  test_api 403 GET $ORCHESTRA_URL/user/login        "$ROOT_AUTH" ''
  test_api 200 GET $ORCHESTRA_URL/user/count        "$ROOT_AUTH" ''
  test_api 200 GET $ORCHESTRA_URL/user              "$ROOT_AUTH" ''
  test_api 200 GET $ORCHESTRA_URL/user/id/$user1_id "$ROOT_AUTH" ''
  test_api 415 GET $ORCHESTRA_URL/user/id/salut     "$ROOT_AUTH" ''
  mecho 'Node can get nothing except one'
  test_api 200 GET $ORCHESTRA_URL                   "$NODE_AUTH" ''
  test_api 200 GET $ORCHESTRA_URL/index             "$NODE_AUTH" ''
  test_api 403 GET $ORCHESTRA_URL/user/login        "$NODE_AUTH" ''
  test_api 403 GET $ORCHESTRA_URL/user/count        "$NODE_AUTH" ''
  test_api 403 GET $ORCHESTRA_URL/user              "$NODE_AUTH" ''
  test_api 403 GET $ORCHESTRA_URL/user/id/$user1_id "$NODE_AUTH" ''
  test_api 415 GET $ORCHESTRA_URL/user/id/salut     "$NODE_AUTH" ''
  mecho 'Admin can get a lot of things'
  test_api 200 GET $ORCHESTRA_URL                   "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/index             "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/user/login        "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/user/count        "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/user              "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/user/id/$user1_id "$user1_auth" ''
  test_api 415 GET $ORCHESTRA_URL/user/id/salut     "$user1_auth" ''
  mecho 'Simple user can get lesser things'
  test_api 200 GET $ORCHESTRA_URL                   "$user2_auth" ''
  test_api 200 GET $ORCHESTRA_URL/index             "$user2_auth" ''
  test_api 200 GET $ORCHESTRA_URL/user/login        "$user2_auth" ''
  test_api 200 GET $ORCHESTRA_URL/user/count        "$user2_auth" ''
  test_api 403 GET $ORCHESTRA_URL/user              "$user2_auth" ''
  test_api 200 GET $ORCHESTRA_URL/user/id/$user1_id "$user2_auth" ''
  test_api 415 GET $ORCHESTRA_URL/user/id/salut     "$user2_auth" ''
  mecho 'Admin can modify users (and it should work as expected)'
  test_api 200 PATCH $ORCHESTRA_URL/user/id/$user3_id "$user1_auth" \
    '{"first_name":"the", "last_name":"test"}'
  test_api 200 PATCH $ORCHESTRA_URL/user/id/$user3_id "$user1_auth" \
    '{"mail":"t@t.com", "secret": "salutMe3"}'
  test_api 200 GET   $ORCHESTRA_URL/user/login        't@t.com:salutMec3' ''
  test_api 200 PATCH $ORCHESTRA_URL/user/id/$user3_id "$user1_auth"   "$user3_json"
  test_api 200 GET   $ORCHESTRA_URL/user/login        "$user3_auth"   ''
  mecho 'Admin can add/remove admin_platform role to users'
  test_api 200 PATCH $ORCHESTRA_URL/user/id/$user2_id "$user1_auth" '{"admin_platform":true}'
  test_api 200 GET   $ORCHESTRA_URL/user              "$user2_auth" ''
  test_api 200 PATCH $ORCHESTRA_URL/user/id/$user2_id "$user1_auth" '{"admin_platform":false}'
  test_api 403 GET   $ORCHESTRA_URL/user              "$user2_auth" ''
  mecho 'Simple user cannot kill another, itself yes, but not 2x (Chuck Norris can)'
  test_api 403 DELETE $ORCHESTRA_URL/user/id/$user1_id "$user3_auth" ''
  test_api 200 DELETE $ORCHESTRA_URL/user/id/$user2_id "$user2_auth" ''
  test_api 401 DELETE $ORCHESTRA_URL/user/id/$user2_id "$user2_auth" ''
  test_api 401 GET    $ORCHESTRA_URL/user/login        "$user2_auth" ''
  test_api 200 POST   $ORCHESTRA_URL/user              "$user1_auth" "$user2_json"
  save_id 'user2' "$ID"
  test_api 200 GET    $ORCHESTRA_URL/user/login        "$user2_auth" ''
}

api_test_media()
{
  pecho 'Test media API'
  test_api 200 POST   $ORCHESTRA_URL/media               "$user1_auth" "$media1_json"; media1_id=$ID
  test_api 400 POST   $ORCHESTRA_URL/media               "$user1_auth" "$media1_json"
  test_api 200 GET    $ORCHESTRA_URL/media/count         "$user2_auth" ''
  test_api 200 GET    $ORCHESTRA_URL/media               "$user2_auth" ''
  test_api 403 PATCH  $ORCHESTRA_URL/media/id/$media1_id "$user2_auth" "$media1b_json"
  test_api 200 PATCH  $ORCHESTRA_URL/media/id/$media1_id "$user1_auth" "$media1b_json"
  test_api 200 GET    $ORCHESTRA_URL/media/id/$media1_id "$user2_auth" ''
  test_api 403 DELETE $ORCHESTRA_URL/media/id/$media1_id "$user2_auth" ''
  test_api 200 DELETE $ORCHESTRA_URL/media/id/$media1_id "$user1_auth" ''
  test_api 200 POST   $ORCHESTRA_URL/media               "$user1_auth" "$media1_json"; media1_id=$ID
}

api_test_tprofile()
{
  pecho 'Test transform profile API'
  mecho 'We cannot double post a profile'
  test_api 400 POST $ORCHESTRA_URL/transform/profile "$user1_auth" "$tprofile1_json"
  mecho 'Anonymous can get nothing'
  test_api 401 GET $ORCHESTRA_URL/transform/profile/count            '' ''
  test_api 401 GET $ORCHESTRA_URL/transform/profile                  '' ''
  test_api 401 GET $ORCHESTRA_URL/transform/profile/id/$tprofile1_id '' ''
  mecho 'Charlie can get nothing'
  test_api 401 GET $ORCHESTRA_URL/transform/profile/count            "$BAD_AUTH" ''
  test_api 401 GET $ORCHESTRA_URL/transform/profile                  "$BAD_AUTH" ''
  test_api 401 GET $ORCHESTRA_URL/transform/profile/id/$tprofile1_id "$BAD_AUTH" ''
  mecho 'Root can get nothing'
  test_api 403 GET $ORCHESTRA_URL/transform/profile/count            "$ROOT_AUTH" ''
  test_api 403 GET $ORCHESTRA_URL/transform/profile                  "$ROOT_AUTH" ''
  test_api 403 GET $ORCHESTRA_URL/transform/profile/id/$tprofile1_id "$ROOT_AUTH" ''
  test_api 415 GET $ORCHESTRA_URL/transform/profile/id/salut         "$ROOT_AUTH" ''
  mecho 'Node can get nothing'
  test_api 403 GET $ORCHESTRA_URL/transform/profile/count            "$NODE_AUTH" ''
  test_api 403 GET $ORCHESTRA_URL/transform/profile                  "$NODE_AUTH" ''
  test_api 403 GET $ORCHESTRA_URL/transform/profile/id/$tprofile1_id "$NODE_AUTH" ''
  test_api 415 GET $ORCHESTRA_URL/transform/profile/id/salut         "$NODE_AUTH" ''
  mecho 'Admin can get a lot of things'
  test_api 200 GET $ORCHESTRA_URL/transform/profile/count            "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/transform/profile                  "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/transform/profile/id/$tprofile1_id "$user1_auth" ''
  test_api 415 GET $ORCHESTRA_URL/transform/profile/id/salut         "$user1_auth" ''
  mecho 'Simple user can a lot of things'
  test_api 200 GET $ORCHESTRA_URL/transform/profile/count            "$user2_auth" ''
  test_api 200 GET $ORCHESTRA_URL/transform/profile                  "$user2_auth" ''
  test_api 200 GET $ORCHESTRA_URL/transform/profile/id/$tprofile1_id "$user2_auth" ''
  test_api 415 GET $ORCHESTRA_URL/transform/profile/id/salut         "$user2_auth" ''
}

api_test_tjob()
{
  pecho 'Test transform job API'
  #test_api 200 GET  $ORCHESTRA_URL/transform/job/count "$user2_auth" ''
  #test_api 200 GET  $ORCHESTRA_URL/transform/job       "$user2_auth" ''
  #test_api 404 POST $ORCHESTRA_URL/transform/job       "$user2_auth" "$tjob0_json"
  #test_api 404 POST $ORCHESTRA_URL/transform/job       "$user2_auth" "$tjob0b_json"
  #test_api 404 POST $ORCHESTRA_URL/transform/job       "$user2_auth" "$tjob1_json"
  #test_api 200 POST $ORCHESTRA_URL/transform/job       "$user2_auth" "$tjob2_json"; tjob2_id=$ID
  #echo $tjob2_id
  #test_api 415 GET  $ORCHESTRA_URL/job/transform/1   "$admin" ''
  #test_api 200 GET  $ORCHESTRA_URL/job/transform/$id "$admin" ''
  #test_api 400 POST $ORCHESTRA_URL/transform/job     "$user2_auth"  "$tprofile1_json"

  #while read post_job
  #do
  #  [ "$post_job" ] && test_api 0 POST $ORCHESTRA_URL/job/transform "$admin" "$post_job"
  #done < "$ORCHESTRA_SCRIPTS_PATH/tests.jobs"

  #test_api 501 PATCH  $ORCHESTRA_URL/job/transform/$id "$admin" ''
  #test_api 200 DELETE $ORCHESTRA_URL/job/transform/$id "$admin" ''
}

api_get_all()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) api_get_all"
  fi
  ok=$true

  get_auth 'user1'; user1_auth=$REPLY
  test_api 200 GET $ORCHESTRA_URL                         '' ''
  test_api 200 GET $ORCHESTRA_URL/user/count              "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/user                    "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/media/count             "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/media/HEAD              "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/media                   "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/transform/profile/count "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/transform/profile       "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/transform/queue         "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/transform/job/count     "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/transform/job/HEAD      "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/transform/job           "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/publish/queue           "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/publisher/queue         "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/unpublish/queue         "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/publish/job/count       "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/publish/job/HEAD        "$user1_auth" ''
  test_api 200 GET $ORCHESTRA_URL/publish/job             "$user1_auth" ''
}

webui_test_common()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) webui_test_common"
  fi
  ok=$true

  . "$CHARMS_PATH/oscied-webui/hooks_lib/common.sh"

  ip1='10.10.4.3'
  ip2='10.10.0.7'
  ip3='1.1.1.1'
  ip4='2.2.2.2'
  rm proxy_ips 2>/dev/null
  update_proxies add    $ip1; [ "$(cat proxy_ips)" != "$ip1"           ] && xecho '1'
  update_proxies add    $ip2; [ "$(cat proxy_ips)" != "$ip1,$ip2"      ] && xecho '2'
  update_proxies add    $ip3; [ "$(cat proxy_ips)" != "$ip1,$ip2,$ip3" ] && xecho '3'
  update_proxies remove $ip3; [ "$(cat proxy_ips)" != "$ip1,$ip2"      ] && xecho '4'
  update_proxies remove $ip3; [ "$(cat proxy_ips)" != "$ip1,$ip2"      ] && xecho '5'
  update_proxies add    $ip4; [ "$(cat proxy_ips)" != "$ip1,$ip2,$ip4" ] && xecho '6'
  update_proxies remove $ip2; [ "$(cat proxy_ips)" != "$ip1,$ip4"      ] && xecho '7'
  update_proxies remove $ip1; [ "$(cat proxy_ips)" != "$ip4"           ] && xecho '8'
  rm proxy_ips
  mecho 'Unit test passed (update_proxies OK)'
}

rsync_orchestra()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_orchestra"
  fi
  ok=$true

  certif="$CONFIG_JUJU_ID_RSA"
  chmod 600 "$certif" || xecho 'Unable to find id_rsa certificate'

  get_unit_public_url 'oscied-orchestra' '0'
  host="ubuntu@$REPLY"
  dest='/var/lib/juju/units/oscied-orchestra-0/charm'
  ssh -i "$certif" "$host" -n "sudo chown 1000:1000 $dest -R"
  rsync -avhL --progress --delete -e "ssh -i '$certif'" --exclude=.git --exclude=config.json \
    --exclude=celeryconfig.py --exclude=*.pyc "$CHARMS_PATH/oscied-orchestra/" "$host:$dest/"
  ssh -i "$certif" "$host" -n "sudo chown root:root $dest -R"
}

rsync_publisher()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_publisher"
  fi
  ok=$true

  certif="$CONFIG_JUJU_ID_RSA"
  chmod 600 "$certif" || xecho 'Unable to find id_rsa certificate'

  get_unit_public_url 'oscied-publisher' '0'
  host="ubuntu@$REPLY"
  dest='/var/lib/juju/units/oscied-publisher-0/charm/lib/'
  ssh -i "$certif" "$host" -n "sudo chown 1000:1000 $dest -R"
  rsync -avh --progress --delete -e "ssh -i '$certif'" --exclude=.git \
    --exclude=*.pyc "$CHARMS_PATH/lib/" "$host:$dest/"
  ssh -i "$certif" "$host" -n "sudo chown root:root $dest -R"
}

rsync_transform()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_transform"
  fi
  ok=$true

  certif="$CONFIG_JUJU_ID_RSA"
  chmod 600 "$certif" || xecho 'Unable to find id_rsa certificate'

  get_unit_public_url 'oscied-transform' '0'
  host="ubuntu@$REPLY"
  dest='/var/lib/juju/units/oscied-transform-0/charm/lib/'
  ssh -i "$certif" "$host" -n "sudo chown 1000:1000 $dest -R"
  rsync -avh --progress --delete -e "ssh -i '$certif'" --exclude=.git \
    --exclude=*.pyc "$CHARMS_PATH/lib/" "$host:$dest/"
  ssh -i "$certif" "$host" -n "sudo chown root:root $dest -R"
}

rsync_webui()
{
  if [ $# -ne 0 ]; then
    xecho "Usage: $(basename $0) rsync_webui"
  fi
  ok=$true

  certif="$CONFIG_JUJU_ID_RSA"
  chmod 600 "$certif" || xecho 'Unable to find id_rsa certificate'

  get_unit_public_url 'oscied-webui'
  host="ubuntu@$REPLY"
  dest='/var/www'
  ssh -i "$certif" "$host" -n "sudo chown 1000:1000 $dest -R"
  rsync -avh --progress -e "ssh -i '$certif'" --exclude=.git --exclude=.htaccess \
    --exclude=application/config/config.php --exclude=application/config/database.php \
    --exclude=medias --exclude=uploads --exclude=orchestra_relation_ok --delete \
    "$CHARMS_PATH/oscied-webui/www/" "$host:$dest/"
  ssh -i "$certif" "$host" -n "sudo chown www-data:www-data $dest -R"
}

main "$@"
