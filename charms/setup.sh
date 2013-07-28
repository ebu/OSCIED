oscied_install()
{
  echo 'Install OSCIED Library'
  echo '1/3 - Install Python modules prerequisites'
  apt-get -y install build-essential git-core python-dev python-pip
  echo '2/3 - Install Python module called pyutils'
  cd pyutils && ./setup.py develop || { echo 'Unable to install pyutils module' 1>&2; exit 2; }
  echo '3/3 - Install Python module called oscied_lib'
  cd .. && ./setup.py develop || { echo 'Unable to install oscied_lib module' 1>&2; exit 3; }
}

oscied_install 2>&1 > 'setup.log'
