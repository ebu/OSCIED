#!/usr/bin/env bash

echo 'Generate python from EBUCore XML Schema'
if ! which generateDS.py > /dev/null; then
  sudo pip install generateds
fi
cd schemas && generateDS.py -o ../EBUCore.py -s ../EBUCore_subs.py EBU_CORE_20130107.xsd
