Installation procedure of OSCIED for IBC 2013
*********************************************

Setup of OSCIED the physical setup
==================================

* Configure BIOS to wake-on-lan, (TODO)
* Plug-them into their own LAN with a switch and a router with IP=192.168.0.1/24
* Plug the desktop station (MAAS cluster controller) to same network with IP=192.168.0.3/24

Setup of OSCIED-Desktop part 1
==============================

TODO explanations

david@TECW7W02-Ubuntu:~$ sudo nano /etc/network/interfaces 
auto lo
iface lo inet loopback

auto eth0
iface eth0 inet static
	address 192.168.0.3
	netmask 255.255.255.0
	gateway 192.168.0.1
	dns-nameservers 192.168.0.2 8.8.8.8

TODO service networking restart

david@TECW7W02-Ubuntu:~$ ifconfig eth0
eth0      Link encap:Ethernet  HWaddr 44:37:e6:8a:c0:c7  
          inet adr:192.168.0.3  Bcast:192.168.0.255  Masque:255.255.255.0
          adr inet6: fe80::4637:e6ff:fe8a:c0c7/64 Scope:Lien
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          Packets reçus:7308974 erreurs:0 :0 overruns:0 frame:0
          TX packets:6078222 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 lg file transmission:1000 
          Octets reçus:4175017573 (4.1 GB) Octets transmis:3806771971 (3.8 GB)
          Interruption:20 Mémoire:fe700000-fe720000 


david@TECW7W02-Ubuntu:~$ ssh-keygen -t rsa
Generating public/private rsa key pair.
Enter file in which to save the key (/home/david/.ssh/id_rsa): 
/home/david/.ssh/id_rsa already exists.
Overwrite (y/n)? y
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/david/.ssh/id_rsa.
Your public key has been saved in /home/david/.ssh/id_rsa.pub.
The key fingerprint is:
d5:d5:7b:7d:e2:b9:4f:69:06:9f:00:3b:b9:a3:79:ed david@TECW7W02-Ubuntu
The key's randomart image is:
+--[ RSA 2048]----+
|              .. |
|           . .  .|
|          ...   o|
|         .  + ..+|
|        S  + + oo|
|            o * o|
|           o.  B.|
|          o...+. |
|         o. .E ..|
+-----------------+

david@TECW7W02-Ubuntu:~$ cat .ssh/id_rsa.pub 
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDnxJoWC84mFQv2znI1KLFG******* david@TECW7W02-Ubuntu
david@TECW7W02-Ubuntu:~$ ssh-add
Identity added: /home/david/.ssh/id_rsa (/home/david/.ssh/id_rsa)

Setup of OSCIED-MAAS-Master part 1
==================================

TODO screenshots + explanations

Setup of OSCIED-MAAS-Master part 2 (ssh'ed from OSCIED-Desktop)
===============================================================

TODO explanations

david@TECW7W02-Ubuntu:~$ ssh oadmin@192.168.0.2
The authenticity of host '192.168.0.2 (192.168.0.2)' can't be established.
ECDSA key fingerprint is 5b:55:20:46:46:94:ef:d6:bd:8b:41:46:db:b5:bd:89.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '192.168.0.2' (ECDSA) to the list of known hosts.
oadmin@192.168.0.2's password: 
Welcome to Ubuntu 13.04 (GNU/Linux 3.8.0-19-generic x86_64)

 * Documentation:  https://help.ubuntu.com/
Last login: Tue Aug 13 11:32:35 2013
oadmin@OSCIED-MAAS-Master:~$ 
oadmin@OSCIED-MAAS-Master:~$ sudo su
[sudo] password for oadmin:
root@OSCIED-MAAS-Master:/home/oadmin# apt-get update; apt-get -y upgrade; apt-get -y dist-upgrade; apt-get -y autoremove; apt-get -y autoclean
Hit http://security.ubuntu.com raring-security Release.gpg
Hit http://ch.archive.ubuntu.com raring Release.gpg     
Hit http://security.ubuntu.com raring-security Release  
Hit http://ch.archive.ubuntu.com raring-updates Release.gpg
Hit http://ch.archive.ubuntu.com raring-backports Release.gpg
(...)
Reading package lists... Done
Building dependency tree       
Reading state information... Done
The following packages have been kept back:
  linux-generic linux-headers-generic linux-image-generic
The following packages will be upgraded:
  bind9-host dbus dnsutils gnupg gpgv isc-dhcp-client isc-dhcp-common
  libbind9-90 libcurl3-gnutls libdbus-1-3 libdns95 libdrm2 libgcrypt11
  libgnutls26 libisc92 libisccc90 libisccfg90 libldap-2.4-2 liblwres90
  libplymouth2 libssl1.0.0 libudev1 libx11-6 libx11-data libxcb1 libxext6
  libxml2 linux-headers-3.8.0-19 linux-headers-3.8.0-19-generic
  linux-image-3.8.0-19-generic linux-image-extra-3.8.0-19-generic login
  lsb-base lsb-release openssl passwd plymouth plymouth-theme-ubuntu-text
  python3-distupgrade python3-update-manager rsyslog
  ubuntu-release-upgrader-core update-manager-core
43 upgraded, 0 newly installed, 0 to remove and 3 not upgraded.
Need to get 67.6 MB of archives.
After this operation, 27.6 kB of additional disk space will be used.
Get:1 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main login amd64 1:4.1.5.1-1ubuntu4.1 [328 kB]
Get:2 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libssl1.0.0 amd64 1.0.1c-4ubuntu8.1 [1,050 kB]
Get:3 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libdbus-1-3 amd64 1.6.8-1ubuntu6.1 [151 kB]
(...)
Preparing to replace dbus 1.6.8-1ubuntu6 (using .../dbus_1.6.8-1ubuntu6.1_amd64.deb) ...
Unpacking replacement dbus ...
(...)
done
Setting up linux-image-generic (3.8.0.27.45) ...
Setting up linux-headers-3.8.0-27 (3.8.0-27.40) ...
Setting up linux-headers-3.8.0-27-generic (3.8.0-27.40) ...
Setting up linux-headers-generic (3.8.0.27.45) ...
Setting up linux-generic (3.8.0.27.45) ...
Reading package lists... Done
Building dependency tree       
Reading state information... Done
0 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
Reading package lists... Done
Building dependency tree       
Reading state information... Done
root@OSCIED-MAAS-Master:/home/oadmin# reboot

Broadcast message from oadmin@OSCIED-MAAS-Master
	(/dev/pts/2) at 11:45 ...

The system is going down for reboot NOW!
root@OSCIED-MAAS-Master:/home/oadmin# Connection to 192.168.0.2 closed by remote host.
Connection to 192.168.0.2 closed.

david@TECW7W02-Ubuntu:~$ ssh-copy-id oadmin@192.168.0.2
oadmin@192.168.0.2's password: 
Now try logging into the machine, with "ssh 'oadmin@192.168.0.2'", and check in:

  ~/.ssh/authorized_keys

to make sure we haven't added extra keys that you weren't expecting.

david@TECW7W02-Ubuntu:~$ ssh oadmin@192.168.0.2
Welcome to Ubuntu 13.04 (GNU/Linux 3.8.0-27-generic x86_64)

 * Documentation:  https://help.ubuntu.com/
Last login: Tue Aug 13 11:45:53 2013 from tecw7w02-ubuntu.local

TODO : go to 192.168.0.2/MAAS/

oadmin@OSCIED-MAAS-Master:~$
oadmin@OSCIED-MAAS-Master:~$ sudo maas createsuperuser
[sudo] password for oadmin: 
Username (leave blank to use 'root'): 
E-mail address: david.fischer.ch@gmail.com
Password: 
Password (again): 
Superuser created successfully.
oadmin@OSCIED-MAAS-Master:~$ sudo su
[sudo] password for oadmin: 
root@OSCIED-MAAS-Master:/home/oadmin# apt-get install maas-dhcp maas-dns
Reading package lists... Done
Building dependency tree       
Reading state information... Done
The following extra packages will be installed:
  bind9 isc-dhcp-server
Suggested packages:
  bind9-doc isc-dhcp-server-ldap
The following NEW packages will be installed
  bind9 isc-dhcp-server maas-dhcp maas-dns
0 upgraded, 4 newly installed, 0 to remove and 0 not upgraded.
Need to get 1,323 kB of archives.
After this operation, 3,297 kB of additional disk space will be used.
Do you want to continue [Y/n]? 
Get:1 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main bind9 amd64 1:9.9.2.dfsg.P1-2ubuntu2.1 [397 kB]
Get:2 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main isc-dhcp-server amd64 4.2.4-5ubuntu2.1 [916 kB]
Get:3 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/universe maas-dhcp all 1.3+bzr1461+dfsg-0ubuntu2.1 [7,738 B]
Get:4 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/universe maas-dns all 1.3+bzr1461+dfsg-0ubuntu2.1 [2,312 B]
Fetched 1,323 kB in 0s (1,389 kB/s)
Preconfiguring packages ...
Selecting previously unselected package bind9.
(Reading database ... 109752 files and directories currently installed.)
Unpacking bind9 (from .../bind9_1%3a9.9.2.dfsg.P1-2ubuntu2.1_amd64.deb) ...
Selecting previously unselected package isc-dhcp-server.
Unpacking isc-dhcp-server (from .../isc-dhcp-server_4.2.4-5ubuntu2.1_amd64.deb) ...
Selecting previously unselected package maas-dhcp.
Unpacking maas-dhcp (from .../maas-dhcp_1.3+bzr1461+dfsg-0ubuntu2.1_all.deb) ...
Selecting previously unselected package maas-dns.
Unpacking maas-dns (from .../maas-dns_1.3+bzr1461+dfsg-0ubuntu2.1_all.deb) ...
Processing triggers for man-db ...
Processing triggers for ureadahead ...
ureadahead will be reprofiled on next reboot
Processing triggers for ufw ...
Setting up bind9 (1:9.9.2.dfsg.P1-2ubuntu2.1) ...
Adding group `bind' (GID 117) ...
Done.
Adding system user `bind' (UID 109) ...
Adding new user `bind' (UID 109) with group `bind' ...
Not creating home directory `/var/cache/bind'.
wrote key file "/etc/bind/rndc.key"
#
 * Starting domain name service... bind9                        [ OK ] 
Setting up isc-dhcp-server (4.2.4-5ubuntu2.1) ...
Generating /etc/default/isc-dhcp-server...
isc-dhcp-server6 stop/pre-start, process 3006
Processing triggers for ureadahead ...
Setting up maas-dhcp (1.3+bzr1461+dfsg-0ubuntu2.1) ...
maas-dhcp-server start/running, process 3077
Processing triggers for ureadahead ...
Processing triggers for ufw ...
Setting up maas-dns (1.3+bzr1461+dfsg-0ubuntu2.1) ...
 * Stopping domain name service... bind9   waiting for pid 2911 to die
    [ OK ]
 * Starting domain name service... bind9                        [ OK ] 
root@OSCIED-MAAS-Master:/home/oadmin# 

TODO : login to 192.168.0.2/MAAS/
TODO : 192.168.0.2/MAAS/account/prefs/ & copy MAAS Key
TODO snapshot no servers

Register the Servers into the Cluster
=====================================

TODO screenshots & explanations


Setup of OSCIED-Desktop part 2
==============================

TODO explanations

david@TECW7W02-Ubuntu:~$ git clone git@github.com:ebu/OSCIED.git
Cloning into 'OSCIED'...
remote: Counting objects: 4914, done.
remote: Compressing objects: 100% (1901/1901), done.
remote: Total 4914 (delta 3131), reused 4699 (delta 2917)
Receiving objects: 100% (4914/4914), 128.61 MiB | 9.32 MiB/s, done.
Resolving deltas: 100% (3131/3131), done.

david@TECW7W02-Ubuntu:~$ sudo apt-get install uuid
[sudo] password for david: 
Lecture des listes de paquets... Fait
Construction de l'arbre des dépendances       
Lecture des informations d'état... Fait
uuid est déjà la plus récente version disponible.
0 mis à jour, 0 nouvellement installés, 0 à enlever et 0 non mis à jour.

david@TECW7W02-Ubuntu:~$ uuid -v 4 -n 5 | sed 's:-::g'
63bd126776c7436087f9a9fbe9e3de9e
ba6ea1f7afb342f8972500b6c0aca075
59f481ee7cf04a7f84d39f16c73dfca9
787b7258c55e4f33b9144279aba72303
9a6effb8c5b04a4388ddff08e0cd9276

david@TECW7W02-Ubuntu:~$ nano OSCIED/config/juju/environments.yaml

default: maas
environments:
  amazon:
    type: ec2
    access-key: AKIAIADEYC6IBHCMCTZQ
    secret-key: Vl**/QL*********************************
    control-bucket: juju-63bd126776c7436087f9a9fbe9e3de9e.s3-website-us-east-1.amazonaws.com
    admin-secret: ba6ea1f7afb342f8972500b6c0aca075
    ssl-hostname-verification: true
    default-series: precise
    juju-origin: ppa
  maas:
    type: maas
    maas-server: http://192.168.0.2:80/MAAS
    maas-oauth: "cK****************:TW****************:X3******************************"
    admin-secret: 59f481ee7cf04a7f84d39f16c73dfca9
    ssl-hostname-verification: true
    default-series: precise
  local:
    type: local
    control-bucket: juju-787b7258c55e4f33b9144279aba72303
    admin-secret: 9a6effb8c5b04a4388ddff08e0cd9276
    data-dir: /home/david/.juju/storage
    ssl-hostname-verification: true
    default-series: precise
    juju-origin: ppa

TODO references to precise instead of raring !

Setup OSCIED with menu.sh
=========================



        ┌───────────────────────────────────────────────────────────────────────────────┐
        │ Please select an operation                                                    │  
        │ ┌───────────────────────────────────────────────────────────────────────────┐ │  
        │ │   install               Download / update documents and tools             │ │  
        │ │   cleanup               Cleanup configuration of charms (deploy path)     │ │  
        │ │   revup                 Increment all charm's revision (+1)               │ │  
        │ │   api_init_setup        Initialize demo setup with Orchestra API          │ │  
        │ │   api_launch_transform  Launch a transformation task with Orchestra API   │ │  
        │ │   api_revoke_transform  Revoke a transformation task with Orchestra API   │ │  
        │ │   api_launch_publish    Launch a publication task with Orchestra API      │ │  
        │ │   api_revoke_publish    Revoke a publication task with Orchestra API      │ │  
        │ │   api_test_all          Test the whole methods of Orchestra API           │ │  
        │ │   api_get_all           Get listings of all things with Orchestra API     │ │  
        │ │   webui_test_common     Test some functions of Web UI hooks               │ │  
        │ │   rsync_orchestra       Rsync local code to running Orchestra instance    │ │  
        │ │   rsync_publisher       Rsync local code to running Publisher instance    │ │  
        │ │   rsync_storage         Rsync local code to running Storage instance      │ │  
        │ │   rsync_transform       Rsync local code to running Transform instance    │ │  
        │ │   rsync_webui           Rsync local code to running Web UI instance       │ │  
        │ └───────────────────────────────────────────────────────────────────────────┘ │  
        │                                                                               │  
        │                                                                               │  
        ├───────────────────────────────────────────────────────────────────────────────┤  
        │                       <Accepter>            <Annuler >                        │  
        └───────────────────────────────────────────────────────────────────────────────┘  

david@TECW7W02-Ubuntu:~$ cd OSCIED/scripts/

Install 1/2
-----------

david@TECW7W02-Ubuntu:~/OSCIED/scripts$ sh menu.sh 
Execute operation install
Binary git of package git-core founded, nothing to do !
Update submodules
 371b06528afa7748eb3212440d2230a8c2e1552c charms/pyutils (v2.0.1-beta-17-g371b065)
 a5f333b87d55b20ff06b4126493b9298cd107bfd docs/references/openstack-folsom-guide (heads/master)
 d7d21ea8edd9ddd1809ac2a75c6e71956d53aa6b docs/wiki/build (d7d21ea)
 52682891d245e7ada9c6c0584267489aac55a9e7 tools/celery-examples (heads/master)
 761578aa87e332d38bc8e2dd3307d34f154606ac tools/celery-source (v3.0.21-912-g761578a)
 06139e7b085e14e3b1801ee1c470d874bb8b0377 tools/flask-source (0.10.1-23-g06139e7)
 06ed8060b80408b3182b62f8845564b33fdafd23 tools/logicielsUbuntu (06ed806)
 c539bf133de7fb1d94bcd96b7709ce7bfc577997 tools/openstack-scripts (heads/master)
 589f0ae699eae855895c92138a86e06a0df6541f tools/rabbitmq-tutorials (remotes/origin/bug24343-27-g589f0ae)
 0a54a4a4b0897bb8eaaf7a7857fb54924ccbd7ef tools/sqlalchemy-source (rel_0_8_1-300-g0a54a4a)
Import logicielsUbuntu
LogicielsUbuntuExports successfully appended to /home/david/.bashrc
Please restart this script once from a new terminal !
or after having executed the following: !
> source ~/.bashrc
press any key to continue ...

Install 2/2
-----------

david@TECW7W02-Ubuntu:~/OSCIED/scripts$ sh menu.sh 
Execute operation install
Binary git of package git-core founded, nothing to do !
Update submodules
(...)
Import logicielsUbuntu
Ubuntu's Softwares Setup Menu [Packages and Scripts]
---------------------------- copyright David Fischer

FileXYZ.lu-dep + logicielsUbuntuUtils -> FileXYZ

generating ./common.sh from common.sh.lu-dep
[sudo] password for david: 
/home/david/OSCIED/charms/setup.sh: ligne 32: ./setup.py: Aucun fichier ou dossier de ce type
Unable to install pyutils module
Install prerequisites
Lecture des listes de paquets...
Construction de l'arbre des dépendances...
Lecture des informations d'état...
bzr est déjà la plus récente version disponible.
texlive-fonts-recommended est déjà la plus récente version disponible.
texlive-latex-extra est déjà la plus récente version disponible.
texlive-latex-recommended est déjà la plus récente version disponible.
rst2pdf est déjà la plus récente version disponible.
Les paquets suivants ont été installés automatiquement et ne sont plus nécessaires :
  libzookeeper-mt2 python-pyasn1 python-pydot python-pyparsing python-twisted python-twisted-conch python-twisted-lore python-twisted-mail python-twisted-news python-twisted-runner python-twisted-words python-txaws
  python-txzookeeper python-zookeeper
Veuillez utiliser « apt-get autoremove » pour les supprimer.
0 mis à jour, 0 nouvellement installés, 0 à enlever et 1 non mis à jour.
Requirement already up-to-date: coverage in /usr/local/lib/python2.7/dist-packages
Downloading/unpacking docutils from https://pypi.python.org/packages/source/d/docutils/docutils-0.11.tar.gz#md5=20ac380a18b369824276864d98ec0ad6
  Running setup.py egg_info for package docutils
    
    warning: no files found matching 'MANIFEST'
    warning: no files found matching '*' under directory 'extras'
    warning: no previously-included files matching '.cvsignore' found under directory '*'
    warning: no previously-included files matching '*.pyc' found under directory '*'
    warning: no previously-included files matching '*~' found under directory '*'
    warning: no previously-included files matching '.DS_Store' found under directory '*'
Requirement already up-to-date: nose in /usr/local/lib/python2.7/dist-packages
Requirement already up-to-date: pygments in /usr/local/lib/python2.7/dist-packages
Requirement already up-to-date: rednose in /usr/local/lib/python2.7/dist-packages
Requirement already up-to-date: sphinx in /usr/local/lib/python2.7/dist-packages
Requirement already up-to-date: sphinxcontrib-email in /usr/local/lib/python2.7/dist-packages
Requirement already up-to-date: sphinxcontrib-googlechart in /usr/local/lib/python2.7/dist-packages
Requirement already up-to-date: sphinxcontrib-httpdomain in /usr/local/lib/python2.7/dist-packages
Requirement already up-to-date: setuptools in /usr/local/lib/python2.7/dist-packages (from rednose)
Requirement already up-to-date: python-termstyle>=0.1.7 in /usr/local/lib/python2.7/dist-packages (from rednose)
Requirement already up-to-date: Jinja2>=2.3 in /usr/local/lib/python2.7/dist-packages (from sphinx)
Requirement already up-to-date: funcparserlib in /usr/local/lib/python2.7/dist-packages (from sphinxcontrib-googlechart)
Requirement already up-to-date: markupsafe in /usr/local/lib/python2.7/dist-packages (from Jinja2>=2.3->sphinx)
Installing collected packages: docutils
  Found existing installation: docutils 0.10
    Can't uninstall 'docutils'. No files were found to uninstall.
  Running setup.py install for docutils
    
    warning: no files found matching 'MANIFEST'
    warning: no files found matching '*' under directory 'extras'
    warning: no previously-included files matching '.cvsignore' found under directory '*'
    warning: no previously-included files matching '*.pyc' found under directory '*'
    warning: no previously-included files matching '*~' found under directory '*'
    warning: no previously-included files matching '.DS_Store' found under directory '*'
    changing mode of /usr/local/bin/rst2xml.py to 755
    changing mode of /usr/local/bin/rst2s5.py to 755
    changing mode of /usr/local/bin/rst2latex.py to 755
    changing mode of /usr/local/bin/rst2html.py to 755
    changing mode of /usr/local/bin/rst2odt.py to 755
    changing mode of /usr/local/bin/rst2man.py to 755
    changing mode of /usr/local/bin/rst2odt_prepstyles.py to 755
    changing mode of /usr/local/bin/rst2xetex.py to 755
    changing mode of /usr/local/bin/rst2pseudoxml.py to 755
    changing mode of /usr/local/bin/rstpep2html.py to 755
Successfully installed docutils
Cleaning up...
Download references
--2013-08-13 13:43:33--  http://docs.openstack.org/trunk/openstack-compute/install/apt/openstack-install-guide-apt-trunk.pdf
Résolution de docs.openstack.org (docs.openstack.org)... 98.129.229.174
Connexion vers docs.openstack.org (docs.openstack.org)|98.129.229.174|:80... connecté.
requête HTTP transmise, en attente de la réponse... 200 OK
Taille : 1631185 (1.6M) [application/pdf]
Fichier du serveur pas plus récent que le fichier local «openstack-install-guide-apt-trunk.pdf» -- non récupéré.

--2013-08-13 13:43:33--  http://docs.openstack.org/cli/quick-start/content/cli-guide.pdf
Résolution de docs.openstack.org (docs.openstack.org)... 98.129.229.174
Connexion vers docs.openstack.org (docs.openstack.org)|98.129.229.174|:80... connecté.
requête HTTP transmise, en attente de la réponse... 301 Moved Permanently
Emplacement : http://docs.openstack.org/user-guide/content/cli-guide.pdf [suivant]
--2013-08-13 13:43:33--  http://docs.openstack.org/user-guide/content/cli-guide.pdf
Réutilisation de la connexion existante vers docs.openstack.org:80.
requête HTTP transmise, en attente de la réponse... 404 Not Found
2013-08-13 13:43:33 ERREUR 404: Not Found.

--2013-08-13 13:43:33--  http://docs.openstack.org/api/openstack-compute/programmer/openstackapi-programming.pdf
Résolution de docs.openstack.org (docs.openstack.org)... 98.129.229.174
Connexion vers docs.openstack.org (docs.openstack.org)|98.129.229.174|:80... connecté.
requête HTTP transmise, en attente de la réponse... 200 OK
Taille : 305687 (299K) [application/pdf]
Fichier du serveur pas plus récent que le fichier local «openstackapi-programming.pdf» -- non récupéré.

--2013-08-13 13:43:34--  http://docs.openstack.org/folsom/openstack-compute/admin/bk-compute-adminguide-folsom.pdf
Résolution de docs.openstack.org (docs.openstack.org)... 98.129.229.174
Connexion vers docs.openstack.org (docs.openstack.org)|98.129.229.174|:80... connecté.
requête HTTP transmise, en attente de la réponse... 200 OK
Taille : 5026107 (4.8M) [application/pdf]
Fichier du serveur pas plus récent que le fichier local «bk-compute-adminguide-folsom.pdf» -- non récupéré.

--2013-08-13 13:43:34--  http://docs.openstack.org/folsom/openstack-network/admin/bk-quantum-admin-guide-folsom.pdf
Résolution de docs.openstack.org (docs.openstack.org)... 98.129.229.174
Connexion vers docs.openstack.org (docs.openstack.org)|98.129.229.174|:80... connecté.
requête HTTP transmise, en attente de la réponse... 200 OK
Taille : 627582 (613K) [application/pdf]
Fichier du serveur pas plus récent que le fichier local «bk-quantum-admin-guide-folsom.pdf» -- non récupéré.

--2013-08-13 13:43:34--  http://docs.openstack.org/folsom/openstack-object-storage/admin/os-objectstorage-adminguide-folsom.pdf
Résolution de docs.openstack.org (docs.openstack.org)... 98.129.229.174
Connexion vers docs.openstack.org (docs.openstack.org)|98.129.229.174|:80... connecté.
requête HTTP transmise, en attente de la réponse... 200 OK
Taille : 1494004 (1.4M) [application/pdf]
Fichier du serveur pas plus récent que le fichier local «os-objectstorage-adminguide-folsom.pdf» -- non récupéré.

Download tools
--2013-08-13 13:43:34--  http://switch.dl.sourceforge.net/project/clonezilla/clonezilla_live_stable/2.1.1-25/clonezilla-live-2.1.1-25-amd64.zip
Résolution de switch.dl.sourceforge.net (switch.dl.sourceforge.net)... 130.59.138.21, 2001:620:0:1b::21
Connexion vers switch.dl.sourceforge.net (switch.dl.sourceforge.net)|130.59.138.21|:80... connecté.
requête HTTP transmise, en attente de la réponse... 302 Found
Emplacement : http://downloads.sourceforge.net/project/clonezilla/clonezilla_live_stable/2.1.1-25/clonezilla-live-2.1.1-25-amd64.zip?download&failedmirror=switch.dl.sourceforge.net [suivant]
--2013-08-13 13:43:34--  http://downloads.sourceforge.net/project/clonezilla/clonezilla_live_stable/2.1.1-25/clonezilla-live-2.1.1-25-amd64.zip?download&failedmirror=switch.dl.sourceforge.net
Résolution de downloads.sourceforge.net (downloads.sourceforge.net)... 216.34.181.59
Connexion vers downloads.sourceforge.net (downloads.sourceforge.net)|216.34.181.59|:80... connecté.
requête HTTP transmise, en attente de la réponse... 302 Found
Emplacement : http://garr.dl.sourceforge.net/project/clonezilla/clonezilla_live_stable/2.1.1-25/clonezilla-live-2.1.1-25-amd64.zip [suivant]
--2013-08-13 13:43:35--  http://garr.dl.sourceforge.net/project/clonezilla/clonezilla_live_stable/2.1.1-25/clonezilla-live-2.1.1-25-amd64.zip
Résolution de garr.dl.sourceforge.net (garr.dl.sourceforge.net)... 193.206.140.34, 2001:760:ffff:b0::34
Connexion vers garr.dl.sourceforge.net (garr.dl.sourceforge.net)|193.206.140.34|:80... connecté.
requête HTTP transmise, en attente de la réponse... 200 OK
Taille : 119156464 (114M) [application/octet-stream]
Fichier du serveur pas plus récent que le fichier local «clonezilla-live-2.1.1-25-amd64.zip» -- non récupéré.

Merging from remembered parent location http://bazaar.launchpad.net/~juju/juju/trunk/
Nothing to do.                        
gpg: le porte-clefs « /tmp/tmphl_8p0/secring.gpg » a été créé
gpg: le porte-clefs « /tmp/tmphl_8p0/pubring.gpg » a été créé
gpg: demande de la clef C8068B11 sur le serveur hkp keyserver.ubuntu.com
gpg: /tmp/tmphl_8p0/trustdb.gpg : base de confiance créée
gpg: clef C8068B11 : clef publique « Launchpad Ensemble PPA » importée
gpg: Quantité totale traitée : 1
gpg:               importées : 1  (RSA: 1)
OK
Repository file : juju-pkgs-raring.list
Checking if the juju's repository does exist for raring ...
Using the juju's repository for raring
Lecture des listes de paquets...
Construction de l'arbre des dépendances...
Lecture des informations d'état...
Les paquets supplémentaires suivants seront installés : 
  juju-0.7
Paquets suggérés :
  capistrano
Les NOUVEAUX paquets suivants seront installés :
  juju juju-0.7 juju-jitsu
0 mis à jour, 3 nouvellement installés, 5 réinstallés, 0 à enlever et 1 non mis à jour.
Il est nécessaire de prendre 0 o/2'514 ko dans les archives.
Après cette opération, 3'333 ko d'espace disque supplémentaires seront utilisés.
Préconfiguration des paquets...
(Lecture de la base de données... 309781 fichiers et répertoires déjà installés.)
Préparation du remplacement de apt-cacher-ng 0.7.11-1 (en utilisant .../apt-cacher-ng_0.7.11-1_amd64.deb) ...
 * Stopping apt-cacher-ng apt-cacher-ng                       [ OK ] 
Dépaquetage de la mise à jour de apt-cacher-ng ...
Préparation du remplacement de lxc 0.9.0-0ubuntu3.4 (en utilisant .../lxc_0.9.0-0ubuntu3.4_amd64.deb) ...
Dépaquetage de la mise à jour de lxc ...
Préparation du remplacement de charm-tools 0.3+bzr179-7~raring1 (en utilisant .../charm-tools_0.3+bzr179-7~raring1_all.deb) ...
Dépaquetage de la mise à jour de charm-tools ...
Dépaquetage de juju-0.7 (à partir de .../juju-0.7_0.7+bzr628+bzr631~raring1_all.deb) ...
Sélection du paquet juju précédemment désélectionné.
Dépaquetage de juju (à partir de .../juju_0.7+bzr628+bzr631~raring1_all.deb) ...
Sélection du paquet juju-jitsu précédemment désélectionné.
Dépaquetage de juju-jitsu (à partir de .../juju-jitsu_0.22-0stable1~raring1_all.deb) ...
Préparation du remplacement de libzookeeper-java 3.4.5+dfsg-1~exp2 (en utilisant .../libzookeeper-java_3.4.5+dfsg-1~exp2_all.deb) ...
Dépaquetage de la mise à jour de libzookeeper-java ...
Préparation du remplacement de zookeeper 3.4.5+dfsg-1~exp2 (en utilisant .../zookeeper_3.4.5+dfsg-1~exp2_all.deb) ...
Dépaquetage de la mise à jour de zookeeper ...
Traitement des actions différées (« triggers ») pour « man-db »...
Traitement des actions différées (« triggers ») pour « doc-base »...
Processing 1 changed doc-base file...
Enregistrement des documents avec scrollkeeper...
Traitement des actions différées (« triggers ») pour « ureadahead »...
Paramétrage de apt-cacher-ng (0.7.11-1) ...
 * Starting apt-cacher-ng apt-cacher-ng                       [ OK ] 
Paramétrage de lxc (0.9.0-0ubuntu3.4) ...
Setting up lxc dnsmasq configuration.
Paramétrage de charm-tools (0.3+bzr179-7~raring1) ...
Paramétrage de juju-0.7 (0.7+bzr628+bzr631~raring1) ...
update-alternatives: utilisation de « /usr/lib/juju-0.7/bin/juju » pour fournir « /usr/bin/juju » (juju) en mode automatique
Paramétrage de juju (0.7+bzr628+bzr631~raring1) ...
Paramétrage de juju-jitsu (0.22-0stable1~raring1) ...
Paramétrage de libzookeeper-java (3.4.5+dfsg-1~exp2) ...
Paramétrage de zookeeper (3.4.5+dfsg-1~exp2) ...
--2013-08-13 13:43:48--  http://downloads.sourceforge.net/project/plantuml/plantuml.jar
Résolution de downloads.sourceforge.net (downloads.sourceforge.net)... 216.34.181.59
Connexion vers downloads.sourceforge.net (downloads.sourceforge.net)|216.34.181.59|:80... connecté.
requête HTTP transmise, en attente de la réponse... 302 Found
Emplacement : http://garr.dl.sourceforge.net/project/plantuml/plantuml.jar [suivant]
--2013-08-13 13:43:48--  http://garr.dl.sourceforge.net/project/plantuml/plantuml.jar
Résolution de garr.dl.sourceforge.net (garr.dl.sourceforge.net)... 193.206.140.34, 2001:760:ffff:b0::34
Connexion vers garr.dl.sourceforge.net (garr.dl.sourceforge.net)|193.206.140.34|:80... connecté.
requête HTTP transmise, en attente de la réponse... 200 OK
Taille : 2165154 (2.1M) [application/java-archive]
Enregistre : «plantuml.jar»

100%[=================================================================================================================================================================================>] 2'165'154   2.71MB/s   ds 0.8s   

2013-08-13 13:43:49 (2.71 MB/s) - «plantuml.jar» enregistré [2165154/2165154]

--2013-08-13 13:43:49--  http://downloads.sourceforge.net/project/plantuml/PlantUML%20Language%20Reference%20Guide.pdf
Résolution de downloads.sourceforge.net (downloads.sourceforge.net)... 216.34.181.59
Connexion vers downloads.sourceforge.net (downloads.sourceforge.net)|216.34.181.59|:80... connecté.
requête HTTP transmise, en attente de la réponse... 302 Found
Emplacement : http://kent.dl.sourceforge.net/project/plantuml/PlantUML%20Language%20Reference%20Guide.pdf [suivant]
--2013-08-13 13:43:50--  http://kent.dl.sourceforge.net/project/plantuml/PlantUML%20Language%20Reference%20Guide.pdf
Résolution de kent.dl.sourceforge.net (kent.dl.sourceforge.net)... 212.219.56.185
Connexion vers kent.dl.sourceforge.net (kent.dl.sourceforge.net)|212.219.56.185|:80... connecté.
requête HTTP transmise, en attente de la réponse... 200 OK
Taille : 1610757 (1.5M) [application/octet-stream]
Enregistre : «PlantUML Language Reference Guide.pdf»

100%[=================================================================================================================================================================================>] 1'610'757   1.97MB/s   ds 0.8s   

2013-08-13 13:43:50 (1.97 MB/s) - «PlantUML Language Reference Guide.pdf» enregistré [1610757/1610757]

Please enter local RabbitMQ guest user password [default=guest] ?

# Not currently on any branch.
# Changes not staged for commit:
#   (use "git add <file>..." to update what will be committed)
#   (use "git checkout -- <file>..." to discard changes in working directory)
#
#	modified:   python-puka/emit_log.py
#	modified:   python-puka/emit_log_direct.py
#	modified:   python-puka/emit_log_topic.py
#	modified:   python-puka/new_task.py
#	modified:   python-puka/receive.py
#	modified:   python-puka/receive_logs.py
#	modified:   python-puka/receive_logs_direct.py
#	modified:   python-puka/receive_logs_topic.py
#	modified:   python-puka/rpc_client.py
#	modified:   python-puka/rpc_server.py
#	modified:   python-puka/send.py
#	modified:   python-puka/worker.py
#
no changes added to commit (use "git add" and/or "git commit -a")
Fixes bitbucket.org/birkenfeld/sphinx/pull-request/98/fixes-typeerror-raised-from/diff
Fixes #7 - https://github.com/ebu/OSCIED/issues/7
press any key to continue ...

Overwrite
---------

david@TECW7W02-Ubuntu:~$ cd OSCIED/scripts/
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ sh juju-menu.sh 
Execute operation overwrite
sending incremental file list
./
.gitignore
          13 100%    0.00kB/s    0:00:00 (xfer#1, to-check=90/92)
config.yaml
       2.04K 100%    1.94MB/s    0:00:00 (xfer#2, to-check=89/92)
copyright
         752 100%  734.38kB/s    0:00:00 (xfer#3, to-check=88/92)
local_config.pkl
       1.01K 100%  987.30kB/s    0:00:00 (xfer#4, to-check=87/92)
metadata.yaml
         359 100%  350.59kB/s    0:00:00 (xfer#5, to-check=86/92)
orchestra.py
      86.35K 100%   27.45MB/s    0:00:00 (xfer#6, to-check=85/92)
revision
           2 100%    0.49kB/s    0:00:00 (xfer#7, to-check=84/92)
setup.py
       2.43K 100%  592.29kB/s    0:00:00 (xfer#8, to-check=83/92)
setup.sh
       1.81K 100%  442.87kB/s    0:00:00 (xfer#9, to-check=82/92)
(...)

sent 12.25M bytes  received 8.22K bytes  24.52M bytes/sec
total size is 12.22M  speedup is 1.00
Ubuntu's Softwares Setup Menu [Packages and Scripts]
---------------------------- copyright David Fischer

FileXYZ.lu-dep + logicielsUbuntuUtils -> FileXYZ

press any key to continue ...

Bootstrap
=========

david@TECW7W02-Ubuntu:~$ cd OSCIED/scripts/
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ sh juju-menu.sh 
Execute operation deploy
Initialize JuJu orchestrator configuration
Identity added: /home/david/.ssh/id_rsa (/home/david/.ssh/id_rsa)
Using user defined environment : /home/david/OSCIED/config/juju/environments.yaml
[sudo] password for david: 
Le pare-feu est arrêté et désactivé lors du démarrage du système
Copy JuJu environments file & SSH keys to Orchestra charm's deployment path
Initialize scenarios menu

* TODO SELECT osciedIBC2013_maas  Launch_IBC_2013_cluster_setup_(MaaS_Cluster_with_3_machines)

Deploy on MaaS Cluster [y/N] ?
y
Deploy services on private MaaS Cluster
Cleanup and bootstrap juju maas environment
do it now [y/N] ?
y
WARNING: this command will destroy the 'maas' environment (type: maas).
This includes all machines, services, data, and other resources. Continue [y/N] y
2013-08-14 10:56:53,640 INFO Destroying environment 'maas' (type: maas)...
2013-08-14 10:56:53,902 INFO 'destroy_environment' command finished successfully
2013-08-14 10:56:54,666 INFO Bootstrapping environment 'maas' (origin: distro type: maas)...
2013-08-14 10:56:55,810 INFO 'bootstrap' command finished successfully
Deploy Orchestra (1 instance)
Using user define Orchestra configuration : /home/david/OSCIED/config/juju/osciedIBC2013_maas.yaml
do it now [y/N] ?

TODO SKIP NEXT STEPS (KEEP OPEN THIS COMMAND LINE), PLUG A SCREEN TO THE SERVER THAT IS ALLOCATED TO ROOT (TO DEPLOY JUJU UNIT)
AND WATCH FOR ANY ERROR DURING THE SETUP OF UBUNTU (AND CROSS FINGERS)

Get status
----------

david@TECW7W02-Ubuntu:~/OSCIED$ juju status
2013-08-14 11:10:36,645 INFO Connecting to environment...
2013-08-14 11:10:37,373 INFO Connected to environment.
machines:
  0:
    agent-state: running
    dns-name: ahpga.master
    instance-id: /MAAS/api/1.0/nodes/node-76481f62-0413-11e3-a611-080027b25b70/
    instance-state: unknown
services: {}
2013-08-14 11:10:37,644 INFO 'status' command finished successfully

Start the debug log
-------------------

david@TECW7W02-Ubuntu:~/OSCIED/scripts$ juju debug-log
2013-08-14 11:10:26,826 INFO Connecting to environment...
The authenticity of host 'ahpga.master (192.168.0.5)' can't be established.
ECDSA key fingerprint is d5:82:bc:fe:ba:74:c7:39:54:0c:f4:c5:f3:b9:b6:7b.
Are you sure you want to continue connecting (yes/no)? yes
2013-08-14 11:10:28,622 INFO Connected to environment.
2013-08-14 11:10:28,622 INFO Enabling distributed debug log.
2013-08-14 11:10:28,638 INFO Tailing logs - Ctrl-C to stop.

Deploy
======

Deploy on MaaS Cluster [y/N] ?
y
Deploy services on private MaaS Cluster
Cleanup and bootstrap juju maas environment
do it now [y/N] ?
y
WARNING: this command will destroy the 'maas' environment (type: maas).
This includes all machines, services, data, and other resources. Continue [y/N] y
2013-08-14 14:37:36,542 INFO Destroying environment 'maas' (type: maas)...
2013-08-14 14:37:36,865 INFO 'destroy_environment' command finished successfully
2013-08-14 14:37:37,707 INFO Bootstrapping environment 'maas' (origin: distro type: maas)...
2013-08-14 14:37:39,233 INFO 'bootstrap' command finished successfully
Deploy Orchestra (1 instance)
Using user define Orchestra configuration : /home/david/OSCIED/config/juju/osciedIBC2013_maas.yaml
do it now [y/N] ?
y
2013-08-14 14:51:17,750 jitsu.deploy-to:INFO Searching for charm local:precise/oscied-orchestra in local charm repository: /home/david/OSCIED/charms/deploy
2013-08-14 14:51:17,900 juju.common:INFO Connecting to environment...
2013-08-14 14:51:18,195 juju.common:DEBUG Connecting to environment using ahpga.master...
2013-08-14 14:51:18,195 juju.state.sshforward:DEBUG Spawning SSH process with remote_user="ubuntu" remote_host="ahpga.master" remote_port="2181" local_port="59231".
2013-08-14 14:51:18,708 juju.common:DEBUG Environment is initialized.
2013-08-14 14:51:18,708 juju.common:INFO Connected to environment.
2013-08-14 14:51:29,570 jitsu.deploy-to:INFO Charm deployed as service: 'oscied-orchestra'
2013-08-14 14:51:30,159 INFO Connecting to environment...
2013-08-14 14:51:31,086 INFO Connected to environment.
2013-08-14 14:51:31,094 INFO Service 'oscied-orchestra' was exposed.
2013-08-14 14:51:31,095 INFO 'expose' command finished successfully
Deploy Storage (2 instance without replication)
Using user define Storage configuration : /home/david/OSCIED/config/juju/osciedIBC2013_maas.yaml
do it now [y/N] ?
y
2013-08-14 14:51:34,544 INFO Searching for charm local:precise/oscied-storage in local charm repository: /home/david/OSCIED/charms/deploy
2013-08-14 14:51:34,806 INFO Connecting to environment...
2013-08-14 14:51:35,922 INFO Connected to environment.
2013-08-14 14:51:38,808 INFO Charm deployed as service: 'oscied-storage'
2013-08-14 14:51:38,809 INFO 'deploy' command finished successfully
2013-08-14 14:51:39,178 INFO Connecting to environment...
2013-08-14 14:51:40,012 INFO Connected to environment.
2013-08-14 14:51:40,019 INFO Service 'oscied-storage' was exposed.
2013-08-14 14:51:40,020 INFO 'expose' command finished successfully
Deploy Web UI (1 instance)
Using user define Web UI configuration : /home/david/OSCIED/config/juju/osciedIBC2013_maas.yaml
do it now [y/N] ?
n
Deploy Transform (2 instances)
Using user define Transform configuration : /home/david/OSCIED/config/juju/osciedIBC2013_maas.yaml
do it now [y/N] ?
y
2013-08-14 15:07:53,324 jitsu.deploy-to:INFO Searching for charm local:precise/oscied-transform in local charm repository: /home/david/OSCIED/charms/deploy
2013-08-14 15:07:53,527 juju.common:INFO Connecting to environment...
2013-08-14 15:07:53,967 juju.common:DEBUG Connecting to environment using ahpga.master...
2013-08-14 15:07:53,967 juju.state.sshforward:DEBUG Spawning SSH process with remote_user="ubuntu" remote_host="ahpga.master" remote_port="2181" local_port="53873".
2013-08-14 15:07:54,475 juju.common:DEBUG Environment is initialized.
2013-08-14 15:07:54,475 juju.common:INFO Connected to environment.
2013-08-14 15:08:00,357 jitsu.deploy-to:INFO Charm deployed as service: 'oscied-transform1'
2013-08-14 15:08:01,878 jitsu.deploy-to:INFO Searching for charm local:precise/oscied-transform in local charm repository: /home/david/OSCIED/charms/deploy
2013-08-14 15:08:02,081 juju.common:INFO Connecting to environment...
2013-08-14 15:08:02,365 juju.common:DEBUG Connecting to environment using ahpga.master...
2013-08-14 15:08:02,365 juju.state.sshforward:DEBUG Spawning SSH process with remote_user="ubuntu" remote_host="ahpga.master" remote_port="2181" local_port="48319".
2013-08-14 15:08:02,872 juju.common:DEBUG Environment is initialized.
2013-08-14 15:08:02,873 juju.common:INFO Connected to environment.
2013-08-14 15:08:02,877 juju.charm:INFO Using cached charm version of oscied-transform
2013-08-14 15:08:03,432 jitsu.deploy-to:INFO Charm deployed as service: 'oscied-transform2'
Deploy Publisher (2 instances)
Using user define Publisher configuration : /home/david/OSCIED/config/juju/osciedIBC2013_maas.yaml
do it now [y/N] ?
y
2013-08-14 15:09:10,729 jitsu.deploy-to:INFO Searching for charm local:precise/oscied-publisher in local charm repository: /home/david/OSCIED/charms/deploy
2013-08-14 15:09:10,865 juju.common:INFO Connecting to environment...
2013-08-14 15:09:11,119 juju.common:DEBUG Connecting to environment using ahpga.master...
2013-08-14 15:09:11,120 juju.state.sshforward:DEBUG Spawning SSH process with remote_user="ubuntu" remote_host="ahpga.master" remote_port="2181" local_port="34430".
2013-08-14 15:09:11,626 juju.common:DEBUG Environment is initialized.
2013-08-14 15:09:11,626 juju.common:INFO Connected to environment.
2013-08-14 15:09:12,437 jitsu.deploy-to:INFO Charm deployed as service: 'oscied-publisher1'
2013-08-14 15:09:13,568 jitsu.deploy-to:INFO Searching for charm local:precise/oscied-publisher in local charm repository: /home/david/OSCIED/charms/deploy
2013-08-14 15:09:13,725 juju.common:INFO Connecting to environment...
2013-08-14 15:09:14,027 juju.common:DEBUG Connecting to environment using ahpga.master...
2013-08-14 15:09:14,027 juju.state.sshforward:DEBUG Spawning SSH process with remote_user="ubuntu" remote_host="ahpga.master" remote_port="2181" local_port="55620".
2013-08-14 15:09:14,534 juju.common:DEBUG Environment is initialized.
2013-08-14 15:09:14,534 juju.common:INFO Connected to environment.
2013-08-14 15:09:14,539 juju.charm:INFO Using cached charm version of oscied-publisher
2013-08-14 15:09:14,970 jitsu.deploy-to:INFO Charm deployed as service: 'oscied-publisher2'
2013-08-14 15:09:15,572 INFO Connecting to environment...
2013-08-14 15:09:16,348 INFO Connected to environment.
2013-08-14 15:09:16,356 INFO Service 'oscied-publisher1' was exposed.
2013-08-14 15:09:16,356 INFO 'expose' command finished successfully
2013-08-14 15:09:16,890 INFO Connecting to environment...
2013-08-14 15:09:17,735 INFO Connected to environment.
2013-08-14 15:09:17,756 INFO Service 'oscied-publisher2' was exposed.
2013-08-14 15:09:17,756 INFO 'expose' command finished successfully
Disconnect all services [DEBUG PURPOSE ONLY] (with juju remove-relation)
do it now [y/N] ?
n
Connect all services together (with juju add-relation)
do it now [y/N] ?
y
2013-08-14 15:09:56,616 INFO Connecting to environment...
2013-08-14 15:09:57,472 INFO Connected to environment.
2013-08-14 15:09:57,508 INFO Added mount relation to all service units.
2013-08-14 15:09:57,508 INFO 'add_relation' command finished successfully
2013-08-14 15:09:58,036 INFO Connecting to environment...
2013-08-14 15:09:58,862 INFO Connected to environment.
2013-08-14 15:09:58,870 ERROR Service 'oscied-webui' was not found
2013-08-14 15:09:59,291 INFO Connecting to environment...
2013-08-14 15:10:00,194 INFO Connected to environment.
2013-08-14 15:10:00,229 INFO Added mount relation to all service units.
2013-08-14 15:10:00,229 INFO 'add_relation' command finished successfully
2013-08-14 15:10:00,784 INFO Connecting to environment...
2013-08-14 15:10:01,888 INFO Connected to environment.
2013-08-14 15:10:01,931 INFO Added mount relation to all service units.
2013-08-14 15:10:01,931 INFO 'add_relation' command finished successfully
2013-08-14 15:10:02,492 INFO Connecting to environment...
2013-08-14 15:10:03,194 INFO Connected to environment.
2013-08-14 15:10:03,235 INFO Added mount relation to all service units.
2013-08-14 15:10:03,235 INFO 'add_relation' command finished successfully
2013-08-14 15:10:03,821 INFO Connecting to environment...
2013-08-14 15:10:04,618 INFO Connected to environment.
2013-08-14 15:10:04,661 INFO Added mount relation to all service units.
2013-08-14 15:10:04,661 INFO 'add_relation' command finished successfully
now this is orchestra relation with the web user interface units
press any key to continue ...

2013-08-14 15:11:02,567 INFO Connecting to environment...
2013-08-14 15:11:03,512 INFO Connected to environment.
2013-08-14 15:11:03,522 ERROR Service 'oscied-webui' was not found
now this is orchestra relation with transformation units
press any key to continue ...

2013-08-14 15:11:08,071 INFO Connecting to environment...
2013-08-14 15:11:08,852 INFO Connected to environment.
2013-08-14 15:11:08,908 INFO Added subordinate relation to all service units.
2013-08-14 15:11:08,908 INFO 'add_relation' command finished successfully
2013-08-14 15:11:09,277 INFO Connecting to environment...
2013-08-14 15:11:10,052 INFO Connected to environment.
2013-08-14 15:11:10,093 INFO Added subordinate relation to all service units.
2013-08-14 15:11:10,094 INFO 'add_relation' command finished successfully
now this is orchestra relation with publication units
press any key to continue ...

2013-08-14 15:11:23,206 INFO Connecting to environment...
2013-08-14 15:11:24,118 INFO Connected to environment.
2013-08-14 15:11:24,159 INFO Added subordinate relation to all service units.
2013-08-14 15:11:24,160 INFO 'add_relation' command finished successfully
2013-08-14 15:11:24,506 INFO Connecting to environment...
2013-08-14 15:11:25,261 INFO Connected to environment.
2013-08-14 15:11:25,304 INFO Added subordinate relation to all service units.
2013-08-14 15:11:25,304 INFO 'add_relation' command finished successfully
press any key to continue ...


The status
----------

david@TECW7W02-Ubuntu:~/OSCIED/scripts$ juju status
2013-08-14 15:13:03,874 INFO Connecting to environment...
2013-08-14 15:13:04,735 INFO Connected to environment.
machines:
  0:
    agent-state: running
    dns-name: ahpga.master
    instance-id: /MAAS/api/1.0/nodes/node-76481f62-0413-11e3-a611-080027b25b70/
    instance-state: unknown
  1:
    agent-state: running
    dns-name: dx9yb.master
    instance-id: /MAAS/api/1.0/nodes/node-f1ea330e-0421-11e3-b256-080027b25b70/
    instance-state: unknown
  2:
    agent-state: running
    dns-name: nnqrp.master
    instance-id: /MAAS/api/1.0/nodes/node-f439fcfc-0421-11e3-97e2-080027b25b70/
    instance-state: unknown
services:
  oscied-orchestra:
    charm: local:precise/oscied-orchestra-10
    exposed: true
    relations:
      publisher:
      - oscied-publisher1
      - oscied-publisher2
      storage:
      - oscied-storage
      transform:
      - oscied-transform1
      - oscied-transform2
    units:
      oscied-orchestra/0:
        agent-state: started
        machine: 0
        open-ports:
        - 5000/tcp
        - 27017/tcp
        - 5672/tcp
        public-address: ahpga.master
  oscied-publisher1:
    charm: local:precise/oscied-publisher-8
    exposed: true
    relations:
      publisher:
      - oscied-orchestra
      storage:
      - oscied-storage
    units:
      oscied-publisher1/0:
        agent-state: started
        machine: 1
        open-ports:
        - 80/tcp
        public-address: dx9yb.master
        relation-errors:
          publisher:
          - oscied-orchestra
  oscied-publisher2:
    charm: local:precise/oscied-publisher-8
    exposed: true
    relations:
      publisher:
      - oscied-orchestra
      storage:
      - oscied-storage
    units:
      oscied-publisher2/0:
        agent-state: started
        machine: 2
        open-ports:
        - 80/tcp
        public-address: nnqrp.master
        relation-errors:
          publisher:
          - oscied-orchestra
  oscied-storage:
    charm: local:precise/oscied-storage-16
    exposed: true
    relations:
      peer:
      - oscied-storage
      storage:
      - oscied-orchestra
      - oscied-publisher1
      - oscied-publisher2
      - oscied-transform1
      - oscied-transform2
    units:
      oscied-storage/0:
        agent-state: started
        machine: 1
        open-ports:
        - 111/tcp
        - 24007/tcp
        - 24009/tcp
        - 24010/tcp
        public-address: dx9yb.master
      oscied-storage/1:
        agent-state: started
        machine: 2
        open-ports:
        - 111/tcp
        - 24007/tcp
        - 24009/tcp
        - 24010/tcp
        public-address: nnqrp.master
  oscied-transform1:
    charm: local:precise/oscied-transform-9
    relations:
      storage:
      - oscied-storage
      transform:
      - oscied-orchestra
    units:
      oscied-transform1/0:
        agent-state: started
        machine: 1
        public-address: dx9yb.master
        relation-errors:
          transform:
          - oscied-orchestra
  oscied-transform2:
    charm: local:precise/oscied-transform-9
    relations:
      storage:
      - oscied-storage
      transform:
      - oscied-orchestra
    units:
      oscied-transform2/0:
        agent-state: started
        machine: 2
        public-address: nnqrp.master
        relation-errors:
          transform:
          - oscied-orchestra
2013-08-14 15:13:05,627 INFO 'status' command finished successfully

Questions & Answers
===================

If you want to deploy Ubuntu 12.04LTS (precise) and not Ubuntu 13.04 (raring)
-----------------------------------------------------------------------------

david@TECW7W02-Ubuntu:~/OSCIED/scripts$ grep -r raring
common.sh.lu-dep:RELEASE='raring'      # Update this according to your needs
common.py:RELEASE = u'raring'      # Update this according to your needs
fast-local.sh:  lxc_cache='/var/cache/lxc/cloud-raring'
fast-local.sh:  cloud_image_url="$cloud_host/server/releases/raring/release-20130423/ubuntu-13.04-server-cloudimg-amd64-root.tar.gz"
common.sh:RELEASE='raring'      # Update this according to your needs
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ source ~/.bashrc 
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ lu-replaceContent raring precise
Ubuntu's Softwares Setup Menu [Packages and Scripts]
---------------------------- copyright David Fischer

Sed files content to replace a pattern with a substitution string
Remark : .svn and .git paths are avoided !

david@TECW7W02-Ubuntu:~/OSCIED/scripts$ grep -r precise
common.sh.lu-dep:RELEASE='precise'      # Update this according to your needs
common.py:RELEASE = u'precise'      # Update this according to your needs
fast-local.sh:  lxc_cache='/var/cache/lxc/cloud-precise'
fast-local.sh:  cloud_image_url="$cloud_host/server/releases/precise/release-20130423/ubuntu-13.04-server-cloudimg-amd64-root.tar.gz"
common.sh:RELEASE='precise'      # Update this according to your needs
common.sh:  for actual in "$last" 'quantal' 'precise' 'oneiric' 'maverick' 'lucid'

If the servers fails to boot via PXE (TFTP ...)
-----------------------------------------------

TODO https://bugs.launchpad.net/maas/+bug/1115178 ... arm based image of raring release is not (yet) available, so disable raring or the arm architecture.

david@TECW7W02-Ubuntu:~/OSCIED/scripts$ ssh oadmin@192.168.0.2
Welcome to Ubuntu 13.04 (GNU/Linux 3.8.0-27-generic x86_64)

 * Documentation:  https://help.ubuntu.com/
Last login: Tue Aug 13 11:46:37 2013 from tecw7w02-ubuntu.local
oadmin@OSCIED-MAAS-Master:~$ 
oadmin@OSCIED-MAAS-Master:~$ sudo maas
maas                    maas-cli                maas-import-ephemerals  maas-import-pxe-files   maas-provision          maas-region-celeryd     
oadmin@OSCIED-MAAS-Master:~$ sudo maas
maas                    maas-cli                maas-import-ephemerals  maas-import-pxe-files   maas-provision          maas-region-celeryd     
oadmin@OSCIED-MAAS-Master:~$ sudo maas-import-pxe-files 
[sudo] password for oadmin: 
Downloading to temporary location /tmp/tmp.lWgVf7kZuL.
/tmp/tmp.lWgVf7kZuL ~
2013-08-13 14:03:22 URL:http://archive.ubuntu.com/ubuntu//dists/precise/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//linux [4965840/4965840] -> "linux" [1]
2013-08-13 14:03:25 URL:http://archive.ubuntu.com/ubuntu//dists/precise/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//initrd.gz [17446386/17446386] -> "initrd.gz" [1]
2013-08-13 14:03:26 URL:http://archive.ubuntu.com/ubuntu//dists/quantal/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//linux [5130968/5130968] -> "linux" [1]
2013-08-13 14:03:28 URL:http://archive.ubuntu.com/ubuntu//dists/quantal/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//initrd.gz [18668122/18668122] -> "initrd.gz" [1]
2013-08-13 14:03:29 URL:http://archive.ubuntu.com/ubuntu//dists/raring/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//linux [5357848/5357848] -> "linux" [1]
2013-08-13 14:03:31 URL:http://archive.ubuntu.com/ubuntu//dists/raring/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//initrd.gz [19119185/19119185] -> "initrd.gz" [1]
2013-08-13 14:03:31 URL:http://archive.ubuntu.com/ubuntu//dists/precise/main/installer-i386/current/images/netboot/ubuntu-installer/i386//linux [5015840/5015840] -> "linux" [1]
2013-08-13 14:03:33 URL:http://archive.ubuntu.com/ubuntu//dists/precise/main/installer-i386/current/images/netboot/ubuntu-installer/i386//initrd.gz [15977428/15977428] -> "initrd.gz" [1]
2013-08-13 14:03:34 URL:http://archive.ubuntu.com/ubuntu//dists/quantal/main/installer-i386/current/images/netboot/ubuntu-installer/i386//linux [5171760/5171760] -> "linux" [1]
2013-08-13 14:03:36 URL:http://archive.ubuntu.com/ubuntu//dists/quantal/main/installer-i386/current/images/netboot/ubuntu-installer/i386//initrd.gz [17086667/17086667] -> "initrd.gz" [1]
2013-08-13 14:03:37 URL:http://archive.ubuntu.com/ubuntu//dists/raring/main/installer-i386/current/images/netboot/ubuntu-installer/i386//linux [5367344/5367344] -> "linux" [1]
2013-08-13 14:03:39 URL:http://archive.ubuntu.com/ubuntu//dists/raring/main/installer-i386/current/images/netboot/ubuntu-installer/i386//initrd.gz [17454164/17454164] -> "initrd.gz" [1]
2013-08-13 14:03:39 URL:http://ports.ubuntu.com/ubuntu-ports//dists/precise-updates/main/installer-armhf/current/images/highbank/netboot//vmlinuz [2978672/2978672] -> "vmlinuz" [1]
2013-08-13 14:03:40 URL:http://ports.ubuntu.com/ubuntu-ports//dists/precise-updates/main/installer-armhf/current/images/highbank/netboot//initrd.gz [4951617/4951617] -> "initrd.gz" [1]
2013-08-13 14:03:41 URL:http://ports.ubuntu.com/ubuntu-ports//dists/quantal/main/installer-armhf/current/images/highbank/netboot//vmlinuz [3738504/3738504] -> "vmlinuz" [1]
2013-08-13 14:03:42 URL:http://ports.ubuntu.com/ubuntu-ports//dists/quantal/main/installer-armhf/current/images/highbank/netboot//initrd.gz [6213909/6213909] -> "initrd.gz" [1]
http://ports.ubuntu.com/ubuntu-ports//dists/raring/main/installer-armhf/current/images/highbank/netboot//vmlinuz:
2013-08-13 14:03:43 ERROR 404: Not Found.
oadmin@OSCIED-MAAS-Master:~$ sudo nano /etc/maas/import_pxe_files 
oadmin@OSCIED-MAAS-Master:~$ cat /etc/maas/import_pxe_files 
# This file replaces an older one called import_isos.  Include that here for
# compatibility.
if [ -f /etc/maas/import_isos ]
then
    cat >&2 <<EOF

Including obsolete /etc/maas/import_isos in configuration.  This file has been
superseded by import_pxe_files.  Please see if it can be removed.

EOF
    . /etc/maas/import_isos
fi


#RELEASES="precise"
# XXX: rvb 2013-02-13 bug=1115178: raring images are not there yet.
RELEASES="precise quantal"
#ARCHES="amd64/generic i386/generic armhf/highbank"
LOCALE="fr_CH"
#IMPORT_EPHEMERALS=12013-08-14 10:05:02,028 Machine:0: juju.agents.machine DEBUG: Units changed old:set(['orchestra/0']) new:set(['webui/0', 'orchestra/0'])
2013-08-14 10:05:02,028 Machine:0: juju.agents.machine DEBUG: Starting service unit: webui/0 ...
2013-08-14 10:05:02,077 Machine:0: unit.deploy DEBUG: Downloading charm local:precise/oscied-webui-5 to /var/lib/juju/charms
2013-08-14 10:05:03,591 Machine:0: unit.deploy DEBUG: Using <juju.machine.unit.UnitMachineDeployment object at 0x2b229d0> for webui/0 in /var/lib/juju
2013-08-14 10:05:03,591 Machine:0: unit.deploy DEBUG: Starting service unit webui/0...
2013-08-14 10:05:04,056 unit:webui/0: hook.executor DEBUG: started
2013-08-14 10:05:04,062 unit:webui/0: statemachine DEBUG: unitworkflowstate: transition install (None -> installed) {}
2013-08-14 10:05:04,062 unit:webui/0: statemachine DEBUG: unitworkflowstate:  execute action do_install
2013-08-14 10:05:04,077 unit:webui/0: hook.output DEBUG: Cached relation hook contexts: []
2013-08-14 10:05:04,081 unit:webui/0: hook.executor DEBUG: Running hook: /var/lib/juju/units/webui-0/charm/hooks/install
2013-08-14 10:05:04,082 unit:webui/0: hook.executor DEBUG: Hook error: /var/lib/juju/units/webui-0/charm/hooks/install 'JUJU_ENV_UUID'
2013-08-14 10:05:04,082 unit:webui/0: twisted ERROR: Unhandled error in Deferred:
2013-08-14 10:05:04,083 unit:webui/0: twisted ERROR: Unhandled Error
Traceback (most recent call last):
Failure: exceptions.KeyError: 'JUJU_ENV_UUID'

2013-08-14 10:05:04,215 Machine:0: unit.deploy INFO: Started service unit webui/0

oadmin@OSCIED-MAAS-Master:~$ sudo maas-import-pxe-files 
Downloading to temporary location /tmp/tmp.i7ZFEQIXnv.
/tmp/tmp.i7ZFEQIXnv ~
2013-08-13 14:05:06 URL:http://archive.ubuntu.com/ubuntu//dists/precise/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//linux [4965840/4965840] -> "linux" [1]
2013-08-13 14:05:07 URL:http://archive.ubuntu.com/ubuntu//dists/precise/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//initrd.gz [17446386/17446386] -> "initrd.gz" [1]
2013-08-13 14:05:08 URL:http://archive.ubuntu.com/ubuntu//dists/quantal/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//linux [5130968/5130968] -> "linux" [1]
(...)
~
precise/amd64: updating [maas-precise-12.04-amd64-ephemeral-20121008]
--2013-08-13 14:05:19--  https://maas.ubuntu.com/images/ephemeral/releases/precise/release-20121008/precise-ephemeral-maas-amd64.tar.gz
Resolving maas.ubuntu.com (maas.ubuntu.com)... 91.189.90.19, 91.189.89.122
Connecting to maas.ubuntu.com (maas.ubuntu.com)|91.189.90.19|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 272250525 (260M) [application/x-gzip]
Saving to: ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/amd64/dist.tar.gz’
(...)
2013-08-13 14:18:34 (5.65 MB/s) - ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist.tar.gz’ saved [251417816/251417816]

Tue, 13 Aug 2013 14:19:01 +0200: converting /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist-root.tar.gz
Tue, 13 Aug 2013 14:19:01 +0200: extracting *.img from /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist.tar.gz
quantal-ephemeral-maas-armhf.img
Tue, 13 Aug 2013 14:19:30 +0200: copying contents of quantal-ephemeral-maas-armhf.img in /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist-root.tar.gz
Tue, 13 Aug 2013 14:20:02 +0200: finished. wrote to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist-root.tar.gz

If any juju command returns a SSH forwarding error
--------------------------------------------------

TODO The error
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ juju debug-log
2013-08-14 09:41:55,763 INFO Connecting to environment...
2013-08-14 09:41:59,128 ERROR SSH forwarding error: ssh: connect to host nnqrp.master port 22: No route to host
TODO explanations (wait for the juju unit to be ready or open a bug report into launchpad)

If juju fails : JUJU_ENV_UUID key error
---------------------------------------

TODO https://bugs.launchpad.net/juju/+bug/1212146

If juju bootstrap fails : 400 BAD REQUEST
-----------------------------------------

-> https://bugs.launchpad.net/maas/+bug/1204507

The problem:

david@TECW7W02-Ubuntu:~/OSCIED/scripts$ juju bootstrap -e maas -v
2013-08-27 08:45:18 ERROR juju supercommand.go:235 command failed: cannot create bootstrap state file: gomaasapi: got error back from server: 400 BAD REQUEST

The solution:

May enable 'proposed' packages, please read instructions (the link).

If juju bootstrap fails : no tools available
--------------------------------------------

-> http://askubuntu.com/questions/285395/how-can-i-copy-juju-tools-for-use-in-my-deployment

The problem:

david@TECW7W02-Ubuntu:~/OSCIED/scripts$ juju bootstrap -e maas2 -v
2013-08-27 09:53:45 INFO juju tools.go:26 environs: reading tools with major version 1
2013-08-27 09:53:45 INFO juju tools.go:30 environs: falling back to public bucket
2013-08-27 09:53:45 ERROR juju supercommand.go:235 command failed: no tools available
error: no tools available

The solution:

david@TECW7W02-Ubuntu:~/OSCIED/scripts$ sudo juju destroy-environment -e maas2
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ juju sync-tools --all -e maas2
listing the source bucket
found 14 tools
listing target bucket
found 0 tools in target; 14 tools to be copied
copying tools/juju-1.10.0-precise-amd64.tgz^[[A^[[A, download 2205kB, uploading
copying tools/juju-1.10.0-precise-i386.tgz, download 2306kB, uploading
copying tools/juju-1.10.0-quantal-amd64.tgz, download 2209kB, uploading
copying tools/juju-1.10.0-quantal-i386.tgz, download 2311kB, uploading
copying tools/juju-1.10.0-raring-amd64.tgz, download 2208kB, uploading
copying tools/juju-1.10.0-raring-i386.tgz, download 2312kB, uploading
copying tools/juju-1.12.0-precise-amd64.tgz, download 4023kB, uploading
copying tools/juju-1.12.0-precise-i386.tgz, download 3911kB, uploading
copying tools/juju-1.12.0-quantal-amd64.tgz, download 4023kB, uploading
copying tools/juju-1.12.0-quantal-i386.tgz, download 3911kB, uploading
copying tools/juju-1.12.0-raring-amd64.tgz, download 4023kB, uploading
copying tools/juju-1.12.0-raring-i386.tgz, download 3911kB, uploading
copying tools/juju-1.12.0-saucy-amd64.tgz, download 4023kB, uploading
copying tools/juju-1.12.0-saucy-i386.tgz, download 3911kB, uploading
copied 14 tools
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ juju bootstrap -e maas2 -v
2013-08-27 09:58:27 INFO juju tools.go:26 environs: reading tools with major version 1
2013-08-27 09:58:37 INFO juju tools.go:53 environs: filtering tools by series: precise
2013-08-27 09:58:37 INFO juju tools.go:66 environs: filtering tools by released version
2013-08-27 09:58:37 INFO juju tools.go:76 environs: picked newest version: 1.12.0
2013-08-27 09:58:38 WARNING juju.environs.maas environ.go:240 picked arbitrary tools "1.12.0-precise-amd64"
2013-08-27 09:58:38 INFO juju supercommand.go:237 command finished

If juju destroy-environment fails : 409 CONFLICT
------------------------------------------------

-> http://askubuntu.com/questions/176468/juju-bootstrap-gives-me-a-409-conflict-error

The problem:

david@TECW7W02-Ubuntu:~/OSCIED/scripts$ sudo juju destroy-environment -e maas2
error: gomaasapi: got error back from server: 409 CONFLICT

The solution:

Be patient, please read instructions (the link).
