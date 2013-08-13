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
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDnxJoWC84mFQv2znI1KLFGJVRiByzhzZXxs8cotEyCOaKMiJly8I6m1ihmo7MArRzED4OLOEV9l16SXLnoGzLWulay7rRdCPlZiHaeZi8vWLGCqTpX6JgDw875v72BvC9Z6N2Zz7N1w9G5FAVRKnBYamFRQb5GdNHSAuxPQODh/iWq/9QbbsOjf+qE316opXZ4moZeuytAS3ue+Gv4n00hxPHkpwVtcMWrUdn/IbusUMxynWlQGNffDhA1RiDytgaXblRp3NGudthZyocKShcO6WMQScb7pTva3pjdrRWwl8z8r1gKLrxsICI5A9R2OS774gjWYwz4Kk6hx9mMRRDR david@TECW7W02-Ubuntu
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
Hit http://ch.archive.ubuntu.com raring Release
Hit http://security.ubuntu.com raring-security/main Sources           
Hit http://ch.archive.ubuntu.com raring-updates Release
Hit http://ch.archive.ubuntu.com raring-backports Release             
Hit http://security.ubuntu.com raring-security/restricted Sources     
Hit http://ch.archive.ubuntu.com raring/main Sources                  
Hit http://ch.archive.ubuntu.com raring/restricted Sources            
Hit http://security.ubuntu.com raring-security/universe Sources
Hit http://ch.archive.ubuntu.com raring/universe Sources
Hit http://ch.archive.ubuntu.com raring/multiverse Sources
Hit http://security.ubuntu.com raring-security/multiverse Sources
Hit http://ch.archive.ubuntu.com raring/main amd64 Packages
Hit http://ch.archive.ubuntu.com raring/restricted amd64 Packages
Hit http://security.ubuntu.com raring-security/main amd64 Packages
Hit http://ch.archive.ubuntu.com raring/universe amd64 Packages
Hit http://security.ubuntu.com raring-security/restricted amd64 Packages
Hit http://ch.archive.ubuntu.com raring/multiverse amd64 Packages
Hit http://ch.archive.ubuntu.com raring/main i386 Packages
Hit http://security.ubuntu.com raring-security/universe amd64 Packages
Hit http://ch.archive.ubuntu.com raring/restricted i386 Packages
Hit http://security.ubuntu.com raring-security/multiverse amd64 Packages
Hit http://security.ubuntu.com raring-security/main i386 Packages
Hit http://ch.archive.ubuntu.com raring/universe i386 Packages
Hit http://ch.archive.ubuntu.com raring/multiverse i386 Packages
Hit http://security.ubuntu.com raring-security/restricted i386 Packages
Hit http://ch.archive.ubuntu.com raring/main Translation-en_GB
Hit http://ch.archive.ubuntu.com raring/main Translation-en
Hit http://security.ubuntu.com raring-security/universe i386 Packages
Hit http://ch.archive.ubuntu.com raring/multiverse Translation-en_GB
Hit http://security.ubuntu.com raring-security/multiverse i386 Packages
Hit http://ch.archive.ubuntu.com raring/multiverse Translation-en
Hit http://ch.archive.ubuntu.com raring/restricted Translation-en_GB
Hit http://ch.archive.ubuntu.com raring/restricted Translation-en
Hit http://ch.archive.ubuntu.com raring/universe Translation-en_GB
Hit http://security.ubuntu.com raring-security/main Translation-en
Hit http://ch.archive.ubuntu.com raring/universe Translation-en
Hit http://ch.archive.ubuntu.com raring-updates/main Sources
Hit http://ch.archive.ubuntu.com raring-updates/restricted Sources
Hit http://ch.archive.ubuntu.com raring-updates/universe Sources
Hit http://ch.archive.ubuntu.com raring-updates/multiverse Sources
Hit http://ch.archive.ubuntu.com raring-updates/main amd64 Packages
Hit http://ch.archive.ubuntu.com raring-updates/restricted amd64 Packages
Hit http://ch.archive.ubuntu.com raring-updates/universe amd64 Packages
Hit http://ch.archive.ubuntu.com raring-updates/multiverse amd64 Packages
Hit http://ch.archive.ubuntu.com raring-updates/main i386 Packages
Hit http://security.ubuntu.com raring-security/multiverse Translation-en
Hit http://ch.archive.ubuntu.com raring-updates/restricted i386 Packages
Hit http://ch.archive.ubuntu.com raring-updates/universe i386 Packages
Hit http://ch.archive.ubuntu.com raring-updates/multiverse i386 Packages
Hit http://security.ubuntu.com raring-security/restricted Translation-en
Hit http://ch.archive.ubuntu.com raring-updates/main Translation-en
Hit http://security.ubuntu.com raring-security/universe Translation-en
Hit http://ch.archive.ubuntu.com raring-updates/multiverse Translation-en
Hit http://ch.archive.ubuntu.com raring-updates/restricted Translation-en
Hit http://ch.archive.ubuntu.com raring-updates/universe Translation-en
Hit http://ch.archive.ubuntu.com raring-backports/main Sources
Hit http://ch.archive.ubuntu.com raring-backports/restricted Sources
Hit http://ch.archive.ubuntu.com raring-backports/universe Sources
Hit http://ch.archive.ubuntu.com raring-backports/multiverse Sources
Hit http://ch.archive.ubuntu.com raring-backports/main amd64 Packages
Hit http://ch.archive.ubuntu.com raring-backports/restricted amd64 Packages
Hit http://ch.archive.ubuntu.com raring-backports/universe amd64 Packages
Hit http://ch.archive.ubuntu.com raring-backports/multiverse amd64 Packages
Hit http://ch.archive.ubuntu.com raring-backports/main i386 Packages
Hit http://ch.archive.ubuntu.com raring-backports/restricted i386 Packages
Hit http://ch.archive.ubuntu.com raring-backports/universe i386 Packages
Hit http://ch.archive.ubuntu.com raring-backports/multiverse i386 Packages
Hit http://ch.archive.ubuntu.com raring-backports/main Translation-en
Ign http://security.ubuntu.com raring-security/main Translation-en_GB
Hit http://ch.archive.ubuntu.com raring-backports/multiverse Translation-en
Hit http://ch.archive.ubuntu.com raring-backports/restricted Translation-en
Hit http://ch.archive.ubuntu.com raring-backports/universe Translation-en
Ign http://security.ubuntu.com raring-security/multiverse Translation-en_GB
Ign http://security.ubuntu.com raring-security/restricted Translation-en_GB
Ign http://security.ubuntu.com raring-security/universe Translation-en_GB
Ign http://ch.archive.ubuntu.com raring-updates/main Translation-en_GB
Ign http://ch.archive.ubuntu.com raring-updates/multiverse Translation-en_GB
Ign http://ch.archive.ubuntu.com raring-updates/restricted Translation-en_GB
Ign http://ch.archive.ubuntu.com raring-updates/universe Translation-en_GB
Ign http://ch.archive.ubuntu.com raring-backports/main Translation-en_GB
Ign http://ch.archive.ubuntu.com raring-backports/multiverse Translation-en_GB
Ign http://ch.archive.ubuntu.com raring-backports/restricted Translation-en_GB
Ign http://ch.archive.ubuntu.com raring-backports/universe Translation-en_GB
Reading package lists... Done
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
Get:4 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libdrm2 amd64 2.4.43-0ubuntu1.1 [26.3 kB]
Get:5 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main plymouth amd64 0.8.8-0ubuntu6.1 [130 kB]
Get:6 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libplymouth2 amd64 0.8.8-0ubuntu6.1 [100 kB]
Get:7 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libudev1 amd64 198-0ubuntu11.1 [35.7 kB]
Get:8 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libgcrypt11 amd64 1.5.0-3ubuntu2.2 [279 kB]
Get:9 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libgnutls26 amd64 2.12.23-1ubuntu1.1 [461 kB]
Get:10 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libldap-2.4-2 amd64 2.4.31-1ubuntu2.1 [186 kB]
Get:11 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libcurl3-gnutls amd64 7.29.0-1ubuntu3.1 [234 kB]
Get:12 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libx11-data all 2:1.5.0-1ubuntu1.1 [179 kB]
Get:13 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libxcb1 amd64 1.8.1-2ubuntu2.1 [45.0 kB]
Get:14 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libx11-6 amd64 2:1.5.0-1ubuntu1.1 [772 kB]
Get:15 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libxext6 amd64 2:1.3.1-2ubuntu0.13.04.1 [34.2 kB]
Get:16 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libxml2 amd64 2.9.0+dfsg1-4ubuntu4.3 [692 kB]
Get:17 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main linux-image-3.8.0-19-generic amd64 3.8.0-19.30 [12.4 MB]
Get:18 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main gpgv amd64 1.4.12-7ubuntu1.1 [186 kB]
Get:19 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main gnupg amd64 1.4.12-7ubuntu1.1 [816 kB]
Get:20 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main lsb-base all 4.0-0ubuntu27.1 [10.4 kB]
Get:21 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main passwd amd64 1:4.1.5.1-1ubuntu4.1 [1,073 kB]
Get:22 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main isc-dhcp-client amd64 4.2.4-5ubuntu2.1 [777 kB]
Get:23 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main isc-dhcp-common amd64 4.2.4-5ubuntu2.1 [836 kB]
Get:24 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main lsb-release all 4.0-0ubuntu27.1 [10.9 kB]
Get:25 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main rsyslog amd64 5.8.11-2ubuntu2.2 [434 kB]
Get:26 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main dnsutils amd64 1:9.9.2.dfsg.P1-2ubuntu2.1 [148 kB]
Get:27 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main bind9-host amd64 1:9.9.2.dfsg.P1-2ubuntu2.1 [55.3 kB]
Get:28 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libisc92 amd64 1:9.9.2.dfsg.P1-2ubuntu2.1 [166 kB]
Get:29 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libdns95 amd64 1:9.9.2.dfsg.P1-2ubuntu2.1 [743 kB]
Get:30 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libisccc90 amd64 1:9.9.2.dfsg.P1-2ubuntu2.1 [18.1 kB]
Get:31 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libisccfg90 amd64 1:9.9.2.dfsg.P1-2ubuntu2.1 [44.7 kB]
Get:32 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main liblwres90 amd64 1:9.9.2.dfsg.P1-2ubuntu2.1 [39.0 kB]
Get:33 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main libbind9-90 amd64 1:9.9.2.dfsg.P1-2ubuntu2.1 [24.8 kB]
Get:34 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main dbus amd64 1.6.8-1ubuntu6.1 [361 kB]
Get:35 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main openssl amd64 1.0.1c-4ubuntu8.1 [525 kB]
Get:36 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main plymouth-theme-ubuntu-text amd64 0.8.8-0ubuntu6.1 [9,208 B]
Get:37 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main ubuntu-release-upgrader-core all 1:0.192.12 [23.9 kB]
Get:38 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main python3-distupgrade all 1:0.192.12 [143 kB]
Get:39 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main python3-update-manager all 1:0.186.1 [33.5 kB]
Get:40 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main update-manager-core all 1:0.186.1 [5,180 B]
Get:41 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main linux-headers-3.8.0-19 all 3.8.0-19.30 [12.2 MB]
Get:42 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main linux-headers-3.8.0-19-generic amd64 3.8.0-19.30 [997 kB]
Get:43 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main linux-image-extra-3.8.0-19-generic amd64 3.8.0-19.30 [30.9 MB]
Fetched 67.6 MB in 7s (8,995 kB/s)                                                                                                                                                                                        
Extract templates from packages: 100%
Preconfiguring packages ...
(Reading database ... 81594 files and directories currently installed.)
Preparing to replace login 1:4.1.5.1-1ubuntu4 (using .../login_1%3a4.1.5.1-1ubuntu4.1_amd64.deb) ...
Unpacking replacement login ...
Processing triggers for man-db ...
Setting up login (1:4.1.5.1-1ubuntu4.1) ...
(Reading database ... 81594 files and directories currently installed.)
Preparing to replace libssl1.0.0:amd64 1.0.1c-4ubuntu8 (using .../libssl1.0.0_1.0.1c-4ubuntu8.1_amd64.deb) ...
Unpacking replacement libssl1.0.0:amd64 ...
Preparing to replace libdbus-1-3:amd64 1.6.8-1ubuntu6 (using .../libdbus-1-3_1.6.8-1ubuntu6.1_amd64.deb) ...
Unpacking replacement libdbus-1-3:amd64 ...
Preparing to replace libdrm2:amd64 2.4.43-0ubuntu1 (using .../libdrm2_2.4.43-0ubuntu1.1_amd64.deb) ...
Unpacking replacement libdrm2:amd64 ...
Preparing to replace plymouth 0.8.8-0ubuntu6 (using .../plymouth_0.8.8-0ubuntu6.1_amd64.deb) ...
Unpacking replacement plymouth ...
Preparing to replace libplymouth2:amd64 0.8.8-0ubuntu6 (using .../libplymouth2_0.8.8-0ubuntu6.1_amd64.deb) ...
Unpacking replacement libplymouth2:amd64 ...
Preparing to replace libudev1:amd64 198-0ubuntu11 (using .../libudev1_198-0ubuntu11.1_amd64.deb) ...
Unpacking replacement libudev1:amd64 ...
Preparing to replace libgcrypt11:amd64 1.5.0-3ubuntu2.1 (using .../libgcrypt11_1.5.0-3ubuntu2.2_amd64.deb) ...
Unpacking replacement libgcrypt11:amd64 ...
Preparing to replace libgnutls26:amd64 2.12.23-1ubuntu1 (using .../libgnutls26_2.12.23-1ubuntu1.1_amd64.deb) ...
Unpacking replacement libgnutls26:amd64 ...
Preparing to replace libldap-2.4-2:amd64 2.4.31-1ubuntu2 (using .../libldap-2.4-2_2.4.31-1ubuntu2.1_amd64.deb) ...
Unpacking replacement libldap-2.4-2:amd64 ...
Preparing to replace libcurl3-gnutls:amd64 7.29.0-1ubuntu3 (using .../libcurl3-gnutls_7.29.0-1ubuntu3.1_amd64.deb) ...
Unpacking replacement libcurl3-gnutls:amd64 ...
Preparing to replace libx11-data 2:1.5.0-1ubuntu1 (using .../libx11-data_2%3a1.5.0-1ubuntu1.1_all.deb) ...
Unpacking replacement libx11-data ...
Preparing to replace libxcb1:amd64 1.8.1-2ubuntu2 (using .../libxcb1_1.8.1-2ubuntu2.1_amd64.deb) ...
Unpacking replacement libxcb1:amd64 ...
Preparing to replace libx11-6:amd64 2:1.5.0-1ubuntu1 (using .../libx11-6_2%3a1.5.0-1ubuntu1.1_amd64.deb) ...
Unpacking replacement libx11-6:amd64 ...
Preparing to replace libxext6:amd64 2:1.3.1-2 (using .../libxext6_2%3a1.3.1-2ubuntu0.13.04.1_amd64.deb) ...
Unpacking replacement libxext6:amd64 ...
Preparing to replace libxml2:amd64 2.9.0+dfsg1-4ubuntu4 (using .../libxml2_2.9.0+dfsg1-4ubuntu4.3_amd64.deb) ...
Unpacking replacement libxml2:amd64 ...
Preparing to replace linux-image-3.8.0-19-generic 3.8.0-19.29 (using .../linux-image-3.8.0-19-generic_3.8.0-19.30_amd64.deb) ...
Done.
Unpacking replacement linux-image-3.8.0-19-generic ...
Examining /etc/kernel/postrm.d .
run-parts: executing /etc/kernel/postrm.d/initramfs-tools 3.8.0-19-generic /boot/vmlinuz-3.8.0-19-generic
run-parts: executing /etc/kernel/postrm.d/zz-update-grub 3.8.0-19-generic /boot/vmlinuz-3.8.0-19-generic
Preparing to replace gpgv 1.4.12-7ubuntu1 (using .../gpgv_1.4.12-7ubuntu1.1_amd64.deb) ...
Unpacking replacement gpgv ...
Processing triggers for ureadahead ...
ureadahead will be reprofiled on next reboot
Processing triggers for man-db ...
Setting up gpgv (1.4.12-7ubuntu1.1) ...
(Reading database ... 81596 files and directories currently installed.)
Preparing to replace gnupg 1.4.12-7ubuntu1 (using .../gnupg_1.4.12-7ubuntu1.1_amd64.deb) ...
Unpacking replacement gnupg ...
Processing triggers for install-info ...
Processing triggers for man-db ...
Setting up gnupg (1.4.12-7ubuntu1.1) ...
(Reading database ... 81596 files and directories currently installed.)
Preparing to replace lsb-base 4.0-0ubuntu27 (using .../lsb-base_4.0-0ubuntu27.1_all.deb) ...
Unpacking replacement lsb-base ...
Setting up lsb-base (4.0-0ubuntu27.1) ...
(Reading database ... 81596 files and directories currently installed.)
Preparing to replace passwd 1:4.1.5.1-1ubuntu4 (using .../passwd_1%3a4.1.5.1-1ubuntu4.1_amd64.deb) ...
Unpacking replacement passwd ...
Processing triggers for ureadahead ...
Processing triggers for man-db ...
Setting up passwd (1:4.1.5.1-1ubuntu4.1) ...
(Reading database ... 81596 files and directories currently installed.)
Preparing to replace isc-dhcp-client 4.2.4-5ubuntu2 (using .../isc-dhcp-client_4.2.4-5ubuntu2.1_amd64.deb) ...
Unpacking replacement isc-dhcp-client ...
Preparing to replace isc-dhcp-common 4.2.4-5ubuntu2 (using .../isc-dhcp-common_4.2.4-5ubuntu2.1_amd64.deb) ...
Unpacking replacement isc-dhcp-common ...
Preparing to replace lsb-release 4.0-0ubuntu27 (using .../lsb-release_4.0-0ubuntu27.1_all.deb) ...
Unpacking replacement lsb-release ...
Preparing to replace rsyslog 5.8.11-2ubuntu2 (using .../rsyslog_5.8.11-2ubuntu2.2_amd64.deb) ...
Unpacking replacement rsyslog ...
Preparing to replace dnsutils 1:9.9.2.dfsg.P1-2ubuntu2 (using .../dnsutils_1%3a9.9.2.dfsg.P1-2ubuntu2.1_amd64.deb) ...
Unpacking replacement dnsutils ...
Preparing to replace bind9-host 1:9.9.2.dfsg.P1-2ubuntu2 (using .../bind9-host_1%3a9.9.2.dfsg.P1-2ubuntu2.1_amd64.deb) ...
Unpacking replacement bind9-host ...
Preparing to replace libisc92 1:9.9.2.dfsg.P1-2ubuntu2 (using .../libisc92_1%3a9.9.2.dfsg.P1-2ubuntu2.1_amd64.deb) ...
Unpacking replacement libisc92 ...
Preparing to replace libdns95 1:9.9.2.dfsg.P1-2ubuntu2 (using .../libdns95_1%3a9.9.2.dfsg.P1-2ubuntu2.1_amd64.deb) ...
Unpacking replacement libdns95 ...
Preparing to replace libisccc90 1:9.9.2.dfsg.P1-2ubuntu2 (using .../libisccc90_1%3a9.9.2.dfsg.P1-2ubuntu2.1_amd64.deb) ...
Unpacking replacement libisccc90 ...
Preparing to replace libisccfg90 1:9.9.2.dfsg.P1-2ubuntu2 (using .../libisccfg90_1%3a9.9.2.dfsg.P1-2ubuntu2.1_amd64.deb) ...
Unpacking replacement libisccfg90 ...
Preparing to replace liblwres90 1:9.9.2.dfsg.P1-2ubuntu2 (using .../liblwres90_1%3a9.9.2.dfsg.P1-2ubuntu2.1_amd64.deb) ...
Unpacking replacement liblwres90 ...
Preparing to replace libbind9-90 1:9.9.2.dfsg.P1-2ubuntu2 (using .../libbind9-90_1%3a9.9.2.dfsg.P1-2ubuntu2.1_amd64.deb) ...
Unpacking replacement libbind9-90 ...
Preparing to replace dbus 1.6.8-1ubuntu6 (using .../dbus_1.6.8-1ubuntu6.1_amd64.deb) ...
Unpacking replacement dbus ...
Preparing to replace openssl 1.0.1c-4ubuntu8 (using .../openssl_1.0.1c-4ubuntu8.1_amd64.deb) ...
Unpacking replacement openssl ...
Preparing to replace plymouth-theme-ubuntu-text 0.8.8-0ubuntu6 (using .../plymouth-theme-ubuntu-text_0.8.8-0ubuntu6.1_amd64.deb) ...
Unpacking replacement plymouth-theme-ubuntu-text ...
Preparing to replace ubuntu-release-upgrader-core 1:0.192.10 (using .../ubuntu-release-upgrader-core_1%3a0.192.12_all.deb) ...
Unpacking replacement ubuntu-release-upgrader-core ...
Preparing to replace python3-distupgrade 1:0.192.10 (using .../python3-distupgrade_1%3a0.192.12_all.deb) ...
Unpacking replacement python3-distupgrade ...
Preparing to replace python3-update-manager 1:0.186 (using .../python3-update-manager_1%3a0.186.1_all.deb) ...
Unpacking replacement python3-update-manager ...
Preparing to replace update-manager-core 1:0.186 (using .../update-manager-core_1%3a0.186.1_all.deb) ...
Unpacking replacement update-manager-core ...
Preparing to replace linux-headers-3.8.0-19 3.8.0-19.29 (using .../linux-headers-3.8.0-19_3.8.0-19.30_all.deb) ...
Unpacking replacement linux-headers-3.8.0-19 ...
Preparing to replace linux-headers-3.8.0-19-generic 3.8.0-19.29 (using .../linux-headers-3.8.0-19-generic_3.8.0-19.30_amd64.deb) ...
Unpacking replacement linux-headers-3.8.0-19-generic ...
Preparing to replace linux-image-extra-3.8.0-19-generic 3.8.0-19.29 (using .../linux-image-extra-3.8.0-19-generic_3.8.0-19.30_amd64.deb) ...
Unpacking replacement linux-image-extra-3.8.0-19-generic ...
Examining /etc/kernel/postrm.d .
run-parts: executing /etc/kernel/postrm.d/initramfs-tools 3.8.0-19-generic /boot/vmlinuz-3.8.0-19-generic
run-parts: executing /etc/kernel/postrm.d/zz-update-grub 3.8.0-19-generic /boot/vmlinuz-3.8.0-19-generic
Processing triggers for man-db ...
Processing triggers for ureadahead ...
Setting up libssl1.0.0:amd64 (1.0.1c-4ubuntu8.1) ...
Setting up libdbus-1-3:amd64 (1.6.8-1ubuntu6.1) ...
Setting up libdrm2:amd64 (2.4.43-0ubuntu1.1) ...
Setting up libplymouth2:amd64 (0.8.8-0ubuntu6.1) ...
Setting up plymouth (0.8.8-0ubuntu6.1) ...
update-initramfs: deferring update (trigger activated)
Setting up libudev1:amd64 (198-0ubuntu11.1) ...
Setting up libgcrypt11:amd64 (1.5.0-3ubuntu2.2) ...
Setting up libgnutls26:amd64 (2.12.23-1ubuntu1.1) ...
Setting up libldap-2.4-2:amd64 (2.4.31-1ubuntu2.1) ...
Setting up libcurl3-gnutls:amd64 (7.29.0-1ubuntu3.1) ...
Setting up libx11-data (2:1.5.0-1ubuntu1.1) ...
Setting up libxcb1:amd64 (1.8.1-2ubuntu2.1) ...
Setting up libx11-6:amd64 (2:1.5.0-1ubuntu1.1) ...
Setting up libxext6:amd64 (2:1.3.1-2ubuntu0.13.04.1) ...
Setting up libxml2:amd64 (2.9.0+dfsg1-4ubuntu4.3) ...
Setting up linux-image-3.8.0-19-generic (3.8.0-19.30) ...
Running depmod.
update-initramfs: deferring update (hook will be called later)
Not updating initrd symbolic links since we are being updated/reinstalled 
(3.8.0-19.29 was configured last, according to dpkg)
Not updating image symbolic links since we are being updated/reinstalled 
(3.8.0-19.29 was configured last, according to dpkg)
Examining /etc/kernel/postinst.d.
run-parts: executing /etc/kernel/postinst.d/apt-auto-removal 3.8.0-19-generic /boot/vmlinuz-3.8.0-19-generic
run-parts: executing /etc/kernel/postinst.d/initramfs-tools 3.8.0-19-generic /boot/vmlinuz-3.8.0-19-generic
update-initramfs: Generating /boot/initrd.img-3.8.0-19-generic
run-parts: executing /etc/kernel/postinst.d/zz-update-grub 3.8.0-19-generic /boot/vmlinuz-3.8.0-19-generic
Generating grub.cfg ...
Found linux image: /boot/vmlinuz-3.8.0-19-generic
Found initrd image: /boot/initrd.img-3.8.0-19-generic
Found memtest86+ image: /boot/memtest86+.bin
done
Setting up isc-dhcp-common (4.2.4-5ubuntu2.1) ...
Setting up isc-dhcp-client (4.2.4-5ubuntu2.1) ...
Setting up lsb-release (4.0-0ubuntu27.1) ...
Setting up rsyslog (5.8.11-2ubuntu2.2) ...
Skipping profile in /etc/apparmor.d/disable: usr.sbin.rsyslogd
rsyslog stop/waiting
rsyslog start/running, process 12181
Setting up libisc92 (1:9.9.2.dfsg.P1-2ubuntu2.1) ...
Setting up libdns95 (1:9.9.2.dfsg.P1-2ubuntu2.1) ...
Setting up libisccc90 (1:9.9.2.dfsg.P1-2ubuntu2.1) ...
Setting up libisccfg90 (1:9.9.2.dfsg.P1-2ubuntu2.1) ...
Setting up libbind9-90 (1:9.9.2.dfsg.P1-2ubuntu2.1) ...
Setting up liblwres90 (1:9.9.2.dfsg.P1-2ubuntu2.1) ...
Setting up bind9-host (1:9.9.2.dfsg.P1-2ubuntu2.1) ...
Setting up dnsutils (1:9.9.2.dfsg.P1-2ubuntu2.1) ...
Setting up dbus (1.6.8-1ubuntu6.1) ...
Setting up openssl (1.0.1c-4ubuntu8.1) ...
Setting up linux-headers-3.8.0-19 (3.8.0-19.30) ...
Setting up linux-headers-3.8.0-19-generic (3.8.0-19.30) ...
Setting up linux-image-extra-3.8.0-19-generic (3.8.0-19.30) ...
Running depmod.
update-initramfs: deferring update (hook will be called later)
Not updating initrd symbolic links since we are being updated/reinstalled 
(3.8.0-19.29 was configured last, according to dpkg)
Not updating image symbolic links since we are being updated/reinstalled 
(3.8.0-19.29 was configured last, according to dpkg)
Examining /etc/kernel/postinst.d.
run-parts: executing /etc/kernel/postinst.d/apt-auto-removal 3.8.0-19-generic /boot/vmlinuz-3.8.0-19-generic
run-parts: executing /etc/kernel/postinst.d/initramfs-tools 3.8.0-19-generic /boot/vmlinuz-3.8.0-19-generic
update-initramfs: Generating /boot/initrd.img-3.8.0-19-generic
run-parts: executing /etc/kernel/postinst.d/zz-update-grub 3.8.0-19-generic /boot/vmlinuz-3.8.0-19-generic
Generating grub.cfg ...
Found linux image: /boot/vmlinuz-3.8.0-19-generic
Found initrd image: /boot/initrd.img-3.8.0-19-generic
Found memtest86+ image: /boot/memtest86+.bin
done
Processing triggers for ureadahead ...
Setting up plymouth-theme-ubuntu-text (0.8.8-0ubuntu6.1) ...
update-initramfs: deferring update (trigger activated)
Setting up python3-distupgrade (1:0.192.12) ...
Setting up python3-update-manager (1:0.186.1) ...
Setting up ubuntu-release-upgrader-core (1:0.192.12) ...
Setting up update-manager-core (1:0.186.1) ...
Processing triggers for libc-bin ...
ldconfig deferred processing now taking place
Processing triggers for initramfs-tools ...
update-initramfs: Generating /boot/initrd.img-3.8.0-19-generic
Reading package lists... Done
Building dependency tree       
Reading state information... Done
Calculating upgrade... Done
The following NEW packages will be installed
  linux-headers-3.8.0-27 linux-headers-3.8.0-27-generic linux-image-3.8.0-27-generic linux-image-extra-3.8.0-27-generic
The following packages will be upgraded:
  linux-generic linux-headers-generic linux-image-generic
3 upgraded, 4 newly installed, 0 to remove and 0 not upgraded.
Need to get 56.5 MB of archives.
After this operation, 236 MB of additional disk space will be used.
Get:1 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main linux-image-3.8.0-27-generic amd64 3.8.0-27.40 [12.5 MB]
Get:2 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main linux-image-extra-3.8.0-27-generic amd64 3.8.0-27.40 [30.9 MB]
Get:3 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main linux-generic amd64 3.8.0.27.45 [1,722 B]
Get:4 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main linux-image-generic amd64 3.8.0.27.45 [2,322 B]
Get:5 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main linux-headers-3.8.0-27 all 3.8.0-27.40 [12.2 MB]
Get:6 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main linux-headers-3.8.0-27-generic amd64 3.8.0-27.40 [1,005 kB]
Get:7 http://ch.archive.ubuntu.com/ubuntu/ raring-updates/main linux-headers-generic amd64 3.8.0.27.45 [2,308 B]
Fetched 56.5 MB in 5s (11.0 MB/s)            
Selecting previously unselected package linux-image-3.8.0-27-generic.
(Reading database ... 81596 files and directories currently installed.)
Unpacking linux-image-3.8.0-27-generic (from .../linux-image-3.8.0-27-generic_3.8.0-27.40_amd64.deb) ...
Done.
Selecting previously unselected package linux-image-extra-3.8.0-27-generic.
Unpacking linux-image-extra-3.8.0-27-generic (from .../linux-image-extra-3.8.0-27-generic_3.8.0-27.40_amd64.deb) ...
Preparing to replace linux-generic 3.8.0.19.35 (using .../linux-generic_3.8.0.27.45_amd64.deb) ...
Unpacking replacement linux-generic ...
Preparing to replace linux-image-generic 3.8.0.19.35 (using .../linux-image-generic_3.8.0.27.45_amd64.deb) ...
Unpacking replacement linux-image-generic ...
Selecting previously unselected package linux-headers-3.8.0-27.
Unpacking linux-headers-3.8.0-27 (from .../linux-headers-3.8.0-27_3.8.0-27.40_all.deb) ...
Selecting previously unselected package linux-headers-3.8.0-27-generic.
Unpacking linux-headers-3.8.0-27-generic (from .../linux-headers-3.8.0-27-generic_3.8.0-27.40_amd64.deb) ...
Preparing to replace linux-headers-generic 3.8.0.19.35 (using .../linux-headers-generic_3.8.0.27.45_amd64.deb) ...
Unpacking replacement linux-headers-generic ...
Setting up linux-image-3.8.0-27-generic (3.8.0-27.40) ...
Running depmod.
update-initramfs: deferring update (hook will be called later)
Examining /etc/kernel/postinst.d.
run-parts: executing /etc/kernel/postinst.d/apt-auto-removal 3.8.0-27-generic /boot/vmlinuz-3.8.0-27-generic
run-parts: executing /etc/kernel/postinst.d/initramfs-tools 3.8.0-27-generic /boot/vmlinuz-3.8.0-27-generic
update-initramfs: Generating /boot/initrd.img-3.8.0-27-generic
run-parts: executing /etc/kernel/postinst.d/zz-update-grub 3.8.0-27-generic /boot/vmlinuz-3.8.0-27-generic
Generating grub.cfg ...
Found linux image: /boot/vmlinuz-3.8.0-27-generic
Found initrd image: /boot/initrd.img-3.8.0-27-generic
Found linux image: /boot/vmlinuz-3.8.0-19-generic
Found initrd image: /boot/initrd.img-3.8.0-19-generic
Found memtest86+ image: /boot/memtest86+.bin
done
Setting up linux-image-extra-3.8.0-27-generic (3.8.0-27.40) ...
Running depmod.
update-initramfs: deferring update (hook will be called later)
Examining /etc/kernel/postinst.d.
run-parts: executing /etc/kernel/postinst.d/apt-auto-removal 3.8.0-27-generic /boot/vmlinuz-3.8.0-27-generic
run-parts: executing /etc/kernel/postinst.d/initramfs-tools 3.8.0-27-generic /boot/vmlinuz-3.8.0-27-generic
update-initramfs: Generating /boot/initrd.img-3.8.0-27-generic
run-parts: executing /etc/kernel/postinst.d/zz-update-grub 3.8.0-27-generic /boot/vmlinuz-3.8.0-27-generic
Generating grub.cfg ...
Found linux image: /boot/vmlinuz-3.8.0-27-generic
Found initrd image: /boot/initrd.img-3.8.0-27-generic
Found linux image: /boot/vmlinuz-3.8.0-19-generic
Found initrd image: /boot/initrd.img-3.8.0-19-generic
Found memtest86+ image: /boot/memtest86+.bin
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
 * Starting domain name service... bind9                                                                                                                                                                            [ OK ] 
Setting up isc-dhcp-server (4.2.4-5ubuntu2.1) ...
Generating /etc/default/isc-dhcp-server...
isc-dhcp-server6 stop/pre-start, process 3006
Processing triggers for ureadahead ...
Setting up maas-dhcp (1.3+bzr1461+dfsg-0ubuntu2.1) ...
maas-dhcp-server start/running, process 3077
Processing triggers for ureadahead ...
Processing triggers for ufw ...
Setting up maas-dns (1.3+bzr1461+dfsg-0ubuntu2.1) ...
 * Stopping domain name service... bind9                                                                                                                                                                                   waiting for pid 2911 to die
                                                                                                                                                                                                                    [ OK ]
 * Starting domain name service... bind9                                                                                                                                                                            [ OK ] 
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

Install 1/2
-----------

david@TECW7W02-Ubuntu:~$ cd OSCIED/scripts/
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ sh menu.sh 
Binary dialog of package dialog founded, nothing to do !

 OSCIED General Operations
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

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

david@TECW7W02-Ubuntu:~$ cd OSCIED/scripts/
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ ls
api-client.py  common.py  common.sh  common.sh.lu-dep  fast-local.sh  generate-doc.py  hls.sh  __init__.py  juju-menu.sh  meld.sh  menu.sh  pyutils  setup.log
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ sh menu.sh 
Binary dialog of package dialog founded, nothing to do !

 OSCIED General Operations
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

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
 * Stopping apt-cacher-ng apt-cacher-ng                                                                                                                                                                             [ OK ] 
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
 * Starting apt-cacher-ng apt-cacher-ng                                                                                                                                                                             [ OK ] 
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




























































 OSCIED General Operations
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────














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
                                                                      
















[1]+  Stoppé                 sh menu.sh
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ 

Overwrite
---------

david@TECW7W02-Ubuntu:~$ cd OSCIED/scripts/
david@TECW7W02-Ubuntu:~/OSCIED/scripts$ sh juju-menu.sh 
Binary dialog of package dialog founded, nothing to do !
























































 OSCIED Operations with JuJu
 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────















                                                                          ┌──────────────────────────────────────────────────────────────────┐
                                                                          │ Please select an operation                                       │  
                                                                          │ ┌──────────────────────────────────────────────────────────────┐ │  
                                                                          │ │   overwrite        Overwrite charms in deployment path       │ │  
                                                                          │ │   deploy           Launch a deployment scenario              │ │  
                                                                          │ │   destroy          Destroy a deployed environment            │ │  
                                                                          │ │   standalone       Play with a charm locally (yes, really)   │ │  
                                                                          │ │   status           Display juju status                       │ │  
                                                                          │ │   status_svg       Display juju status as a SVG graphic      │ │  
                                                                          │ │   log              Launch juju debug log in a screen         │ │  
                                                                          │ │   config           Update units public url listing file      │ │  
                                                                          │ │   unit_ssh         Access to units with secure shell         │ │  
                                                                          │ │   unit_add         Add a new unit to a running service       │ │  
                                                                          │ │   unit_remove      Remove an unit from a running service     │ │  
                                                                          │ │   service_destroy  Destroy a running service                 │ │  
                                                                          │ └──────────────────────────────────────────────────────────────┘ │  
                                                                          │                                                                  │  
                                                                          │                                                                  │  
                                                                          ├──────────────────────────────────────────────────────────────────┤  
                                                                          │                 <Accepter>         <Annuler >                    │  
                                                                          └──────────────────────────────────────────────────────────────────┘  
                                                                            
















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
hooks/
hooks/api-relation-changed
          77 100%   15.04kB/s    0:00:00 (xfer#10, to-check=76/92)
hooks/api-relation-joined
          76 100%   14.84kB/s    0:00:00 (xfer#11, to-check=75/92)
hooks/config-changed
          71 100%   13.87kB/s    0:00:00 (xfer#12, to-check=74/92)
hooks/install
          75 100%   12.21kB/s    0:00:00 (xfer#13, to-check=73/92)
hooks/publisher-relation-changed
          83 100%   13.51kB/s    0:00:00 (xfer#14, to-check=72/92)
hooks/publisher-relation-joined
          82 100%   13.35kB/s    0:00:00 (xfer#15, to-check=71/92)
hooks/start
          62 100%   10.09kB/s    0:00:00 (xfer#16, to-check=70/92)
hooks/stop
          61 100%    9.93kB/s    0:00:00 (xfer#17, to-check=69/92)
hooks/storage-relation-broken
          80 100%   11.16kB/s    0:00:00 (xfer#18, to-check=68/92)
hooks/storage-relation-changed
          81 100%   11.30kB/s    0:00:00 (xfer#19, to-check=67/92)
hooks/storage-relation-joined
          80 100%   11.16kB/s    0:00:00 (xfer#20, to-check=66/92)
hooks/transform-relation-changed
          83 100%   10.13kB/s    0:00:00 (xfer#21, to-check=65/92)
hooks/transform-relation-joined
          82 100%   10.01kB/s    0:00:00 (xfer#22, to-check=64/92)
hooks/uninstall
          66 100%    8.06kB/s    0:00:00 (xfer#23, to-check=63/92)
oscied_lib/
oscied_lib/.gitignore
          50 100%    6.10kB/s    0:00:00 (xfer#24, to-check=62/92)
oscied_lib/Callback.py
       2.72K 100%  295.46kB/s    0:00:00 (xfer#25, to-check=61/92)
oscied_lib/CharmConfig.py
       2.18K 100%  236.87kB/s    0:00:00 (xfer#26, to-check=60/92)
oscied_lib/CharmConfig_Storage.py
       5.68K 100%  554.49kB/s    0:00:00 (xfer#27, to-check=59/92)
oscied_lib/CharmHooks.py
      12.55K 100%    1.20MB/s    0:00:00 (xfer#28, to-check=58/92)
oscied_lib/CharmHooks_Storage.py
       7.12K 100%  632.37kB/s    0:00:00 (xfer#29, to-check=57/92)
oscied_lib/CharmHooks_Subordinate.py
       4.92K 100%  400.72kB/s    0:00:00 (xfer#30, to-check=56/92)
oscied_lib/CharmHooks_Website.py
       3.71K 100%  301.60kB/s    0:00:00 (xfer#31, to-check=55/92)
oscied_lib/Media.py
       4.37K 100%  328.50kB/s    0:00:00 (xfer#32, to-check=54/92)
oscied_lib/Orchestra.py
      30.96K 100%    2.11MB/s    0:00:00 (xfer#33, to-check=53/92)
oscied_lib/OrchestraConfig.py
       4.37K 100%  284.31kB/s    0:00:00 (xfer#34, to-check=52/92)
oscied_lib/OrchestraHooks.py
      13.21K 100%  859.70kB/s    0:00:00 (xfer#35, to-check=51/92)
oscied_lib/OsciedDBModel.py
       1.82K 100%  118.55kB/s    0:00:00 (xfer#36, to-check=50/92)
oscied_lib/PublishTask.py
       3.66K 100%  223.21kB/s    0:00:00 (xfer#37, to-check=49/92)
oscied_lib/Publisher.py
       4.97K 100%  303.47kB/s    0:00:00 (xfer#38, to-check=48/92)
oscied_lib/PublisherConfig.py
       3.12K 100%  179.46kB/s    0:00:00 (xfer#39, to-check=47/92)
oscied_lib/PublisherHooks.py
       6.93K 100%  398.09kB/s    0:00:00 (xfer#40, to-check=46/92)
oscied_lib/Storage.py
       3.72K 100%  213.58kB/s    0:00:00 (xfer#41, to-check=45/92)
oscied_lib/StorageConfig.py
       2.22K 100%  120.28kB/s    0:00:00 (xfer#42, to-check=44/92)
oscied_lib/StorageHooks.py
      11.98K 100%  650.07kB/s    0:00:00 (xfer#43, to-check=43/92)
oscied_lib/Transform.py
      13.66K 100%  702.05kB/s    0:00:00 (xfer#44, to-check=42/92)
oscied_lib/TransformConfig.py
       2.49K 100%  128.08kB/s    0:00:00 (xfer#45, to-check=41/92)
oscied_lib/TransformHooks.py
       5.54K 100%  270.51kB/s    0:00:00 (xfer#46, to-check=40/92)
oscied_lib/TransformProfile.py
       2.75K 100%  134.23kB/s    0:00:00 (xfer#47, to-check=39/92)
oscied_lib/TransformTask.py
       5.49K 100%  255.39kB/s    0:00:00 (xfer#48, to-check=38/92)
oscied_lib/User.py
       4.18K 100%  194.29kB/s    0:00:00 (xfer#49, to-check=37/92)
oscied_lib/WebuiConfig.py
       3.66K 100%  170.06kB/s    0:00:00 (xfer#50, to-check=36/92)
oscied_lib/WebuiHooks.py
      10.33K 100%  458.67kB/s    0:00:00 (xfer#51, to-check=35/92)
oscied_lib/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#52, to-check=34/92)
pyutils/
pyutils/.gitignore
          48 100%    2.13kB/s    0:00:00 (xfer#53, to-check=33/92)
pyutils/.travis.yml
         331 100%   14.69kB/s    0:00:00 (xfer#54, to-check=32/92)
pyutils/AUTHORS
          14 100%    0.62kB/s    0:00:00 (xfer#55, to-check=31/92)
pyutils/COPYING
      35.15K 100%    1.40MB/s    0:00:00 (xfer#56, to-check=30/92)
pyutils/README.rst
       1.39K 100%   56.52kB/s    0:00:00 (xfer#57, to-check=29/92)
pyutils/setup.cfg
         196 100%    7.98kB/s    0:00:00 (xfer#58, to-check=28/92)
pyutils/setup.py
       3.10K 100%  126.30kB/s    0:00:00 (xfer#59, to-check=27/92)
pyutils/pyutils/
pyutils/pyutils/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#60, to-check=24/92)
pyutils/pyutils/py_crypto.py
       1.89K 100%   76.70kB/s    0:00:00 (xfer#61, to-check=23/92)
pyutils/pyutils/py_datetime.py
       3.07K 100%  125.08kB/s    0:00:00 (xfer#62, to-check=22/92)
pyutils/pyutils/py_exception.py
       1.34K 100%   54.61kB/s    0:00:00 (xfer#63, to-check=21/92)
pyutils/pyutils/py_ffmpeg.py
       6.84K 100%  278.28kB/s    0:00:00 (xfer#64, to-check=20/92)
pyutils/pyutils/py_filesystem.py
      10.20K 100%  398.40kB/s    0:00:00 (xfer#65, to-check=19/92)
pyutils/pyutils/py_flask.py
       3.03K 100%  118.48kB/s    0:00:00 (xfer#66, to-check=18/92)
pyutils/pyutils/py_juju.py
      10.17K 100%  382.14kB/s    0:00:00 (xfer#67, to-check=17/92)
pyutils/pyutils/py_logging.py
       3.49K 100%  131.12kB/s    0:00:00 (xfer#68, to-check=16/92)
pyutils/pyutils/py_mock.py
       2.56K 100%   96.27kB/s    0:00:00 (xfer#69, to-check=15/92)
pyutils/pyutils/py_serialization.py
       6.85K 100%  257.32kB/s    0:00:00 (xfer#70, to-check=14/92)
pyutils/pyutils/py_subprocess.py
       5.48K 100%  198.31kB/s    0:00:00 (xfer#71, to-check=13/92)
pyutils/pyutils/py_unicode.py
       2.29K 100%   82.75kB/s    0:00:00 (xfer#72, to-check=12/92)
pyutils/pyutils/py_validation.py
       4.47K 100%  161.53kB/s    0:00:00 (xfer#73, to-check=11/92)
pyutils/pyutils/pyutils.py
       3.00K 100%  108.69kB/s    0:00:00 (xfer#74, to-check=10/92)
pyutils/pyutils/ming/
pyutils/pyutils/ming/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#75, to-check=8/92)
pyutils/pyutils/ming/extensions.py
       1.79K 100%   64.71kB/s    0:00:00 (xfer#76, to-check=7/92)
pyutils/pyutils/ming/schema.py
       4.22K 100%  152.52kB/s    0:00:00 (xfer#77, to-check=6/92)
pyutils/pyutils/ming/session.py
       1.47K 100%   53.17kB/s    0:00:00 (xfer#78, to-check=5/92)
pyutils/tests/
pyutils/tests/TestPyutils.py
       5.52K 100%  192.63kB/s    0:00:00 (xfer#79, to-check=4/92)
pyutils/tests/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#80, to-check=3/92)
pyutils/tests/unicode.csv
          49 100%    1.71kB/s    0:00:00 (xfer#81, to-check=2/92)
ssh/
ssh/config
          25 100%    0.87kB/s    0:00:00 (xfer#82, to-check=1/92)
templates/
templates/celeryconfig.py.template
       2.64K 100%   92.04kB/s    0:00:00 (xfer#83, to-check=0/92)

sent 400.34K bytes  received 1.62K bytes  803.93K bytes/sec
total size is 394.82K  speedup is 0.98
sending incremental file list
./
apache_mod_h264_streaming-2.2.7.tar.gz
     320.61K 100%   39.21MB/s    0:00:00 (xfer#1, to-check=86/88)
config.yaml
       2.26K 100%  315.71kB/s    0:00:00 (xfer#2, to-check=85/88)
copyright
         752 100%   91.80kB/s    0:00:00 (xfer#3, to-check=84/88)
get-dependencies.sh
         124 100%   15.14kB/s    0:00:00 (xfer#4, to-check=83/88)
local_config.pkl
         652 100%   79.59kB/s    0:00:00 (xfer#5, to-check=82/88)
metadata.yaml
         395 100%   48.22kB/s    0:00:00 (xfer#6, to-check=81/88)
revision
           2 100%    0.22kB/s    0:00:00 (xfer#7, to-check=80/88)
setup.py
       2.43K 100%  263.24kB/s    0:00:00 (xfer#8, to-check=79/88)
setup.sh
       1.81K 100%  196.83kB/s    0:00:00 (xfer#9, to-check=78/88)
hooks/
hooks/config-changed
          71 100%    7.70kB/s    0:00:00 (xfer#10, to-check=73/88)
hooks/install
          75 100%    8.14kB/s    0:00:00 (xfer#11, to-check=72/88)
hooks/publisher-relation-broken
          84 100%    8.20kB/s    0:00:00 (xfer#12, to-check=71/88)
hooks/publisher-relation-changed
          85 100%    8.30kB/s    0:00:00 (xfer#13, to-check=70/88)
hooks/publisher-relation-joined
          84 100%    8.20kB/s    0:00:00 (xfer#14, to-check=69/88)
hooks/start
          62 100%    6.05kB/s    0:00:00 (xfer#15, to-check=68/88)
hooks/stop
          61 100%    5.96kB/s    0:00:00 (xfer#16, to-check=67/88)
hooks/storage-relation-broken
          80 100%    7.10kB/s    0:00:00 (xfer#17, to-check=66/88)
hooks/storage-relation-changed
          81 100%    7.19kB/s    0:00:00 (xfer#18, to-check=65/88)
hooks/storage-relation-joined
          80 100%    7.10kB/s    0:00:00 (xfer#19, to-check=64/88)
hooks/uninstall
          66 100%    5.86kB/s    0:00:00 (xfer#20, to-check=63/88)
hooks/website-relation-joined
          80 100%    7.10kB/s    0:00:00 (xfer#21, to-check=62/88)
oscied_lib/
oscied_lib/.gitignore
          50 100%    4.44kB/s    0:00:00 (xfer#22, to-check=61/88)
oscied_lib/Callback.py
       2.72K 100%  221.60kB/s    0:00:00 (xfer#23, to-check=60/88)
oscied_lib/CharmConfig.py
       2.18K 100%  177.65kB/s    0:00:00 (xfer#24, to-check=59/88)
oscied_lib/CharmConfig_Storage.py
       5.68K 100%  462.08kB/s    0:00:00 (xfer#25, to-check=58/88)
oscied_lib/CharmHooks.py
      12.55K 100% 1021.48kB/s    0:00:00 (xfer#26, to-check=57/88)
oscied_lib/CharmHooks_Storage.py
       7.12K 100%  496.86kB/s    0:00:00 (xfer#27, to-check=56/88)
oscied_lib/CharmHooks_Subordinate.py
       4.92K 100%  343.47kB/s    0:00:00 (xfer#28, to-check=55/88)
oscied_lib/CharmHooks_Website.py
       3.71K 100%  241.28kB/s    0:00:00 (xfer#29, to-check=54/88)
oscied_lib/Media.py
       4.37K 100%  284.70kB/s    0:00:00 (xfer#30, to-check=53/88)
oscied_lib/Orchestra.py
      30.96K 100%    1.85MB/s    0:00:00 (xfer#31, to-check=52/88)
oscied_lib/OrchestraConfig.py
       4.37K 100%  266.54kB/s    0:00:00 (xfer#32, to-check=51/88)
oscied_lib/OrchestraHooks.py
      13.21K 100%  758.56kB/s    0:00:00 (xfer#33, to-check=50/88)
oscied_lib/OsciedDBModel.py
       1.82K 100%  104.61kB/s    0:00:00 (xfer#34, to-check=49/88)
oscied_lib/PublishTask.py
       3.66K 100%  210.08kB/s    0:00:00 (xfer#35, to-check=48/88)
oscied_lib/Publisher.py
       4.97K 100%  285.62kB/s    0:00:00 (xfer#36, to-check=47/88)
oscied_lib/PublisherConfig.py
       3.12K 100%  179.46kB/s    0:00:00 (xfer#37, to-check=46/88)
oscied_lib/PublisherHooks.py
       6.93K 100%  398.09kB/s    0:00:00 (xfer#38, to-check=45/88)
oscied_lib/Storage.py
       3.72K 100%  201.71kB/s    0:00:00 (xfer#39, to-check=44/88)
oscied_lib/StorageConfig.py
       2.22K 100%  120.28kB/s    0:00:00 (xfer#40, to-check=43/88)
oscied_lib/StorageHooks.py
      11.98K 100%  650.07kB/s    0:00:00 (xfer#41, to-check=42/88)
oscied_lib/Transform.py
      13.66K 100%  702.05kB/s    0:00:00 (xfer#42, to-check=41/88)
oscied_lib/TransformConfig.py
       2.49K 100%  128.08kB/s    0:00:00 (xfer#43, to-check=40/88)
oscied_lib/TransformHooks.py
       5.54K 100%  284.75kB/s    0:00:00 (xfer#44, to-check=39/88)
oscied_lib/TransformProfile.py
       2.75K 100%  141.29kB/s    0:00:00 (xfer#45, to-check=38/88)
oscied_lib/TransformTask.py
       5.49K 100%  282.28kB/s    0:00:00 (xfer#46, to-check=37/88)
oscied_lib/User.py
       4.18K 100%  214.74kB/s    0:00:00 (xfer#47, to-check=36/88)
oscied_lib/WebuiConfig.py
       3.66K 100%  187.96kB/s    0:00:00 (xfer#48, to-check=35/88)
oscied_lib/WebuiHooks.py
      10.33K 100%  504.54kB/s    0:00:00 (xfer#49, to-check=34/88)
oscied_lib/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#50, to-check=33/88)
pyutils/
pyutils/.gitignore
          48 100%    2.34kB/s    0:00:00 (xfer#51, to-check=32/88)
pyutils/.travis.yml
         331 100%   16.16kB/s    0:00:00 (xfer#52, to-check=31/88)
pyutils/AUTHORS
          14 100%    0.68kB/s    0:00:00 (xfer#53, to-check=30/88)
pyutils/COPYING
      35.15K 100%    1.60MB/s    0:00:00 (xfer#54, to-check=29/88)
pyutils/README.rst
       1.39K 100%   64.59kB/s    0:00:00 (xfer#55, to-check=28/88)
pyutils/setup.cfg
         196 100%    9.11kB/s    0:00:00 (xfer#56, to-check=27/88)
pyutils/setup.py
       3.10K 100%  144.35kB/s    0:00:00 (xfer#57, to-check=26/88)
pyutils/pyutils/
pyutils/pyutils/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#58, to-check=23/88)
pyutils/pyutils/py_crypto.py
       1.89K 100%   87.66kB/s    0:00:00 (xfer#59, to-check=22/88)
pyutils/pyutils/py_datetime.py
       3.07K 100%  142.95kB/s    0:00:00 (xfer#60, to-check=21/88)
pyutils/pyutils/py_exception.py
       1.34K 100%   62.41kB/s    0:00:00 (xfer#61, to-check=20/88)
pyutils/pyutils/py_ffmpeg.py
       6.84K 100%  318.03kB/s    0:00:00 (xfer#62, to-check=19/88)
pyutils/pyutils/py_filesystem.py
      10.20K 100%  474.28kB/s    0:00:00 (xfer#63, to-check=18/88)
pyutils/pyutils/py_flask.py
       3.03K 100%  134.63kB/s    0:00:00 (xfer#64, to-check=17/88)
pyutils/pyutils/py_juju.py
      10.17K 100%  451.62kB/s    0:00:00 (xfer#65, to-check=16/88)
pyutils/pyutils/py_logging.py
       3.49K 100%  154.96kB/s    0:00:00 (xfer#66, to-check=15/88)
pyutils/pyutils/py_mock.py
       2.56K 100%  113.77kB/s    0:00:00 (xfer#67, to-check=14/88)
pyutils/pyutils/py_serialization.py
       6.85K 100%  304.11kB/s    0:00:00 (xfer#68, to-check=13/88)
pyutils/pyutils/py_subprocess.py
       5.48K 100%  232.80kB/s    0:00:00 (xfer#69, to-check=12/88)
pyutils/pyutils/py_unicode.py
       2.29K 100%   97.15kB/s    0:00:00 (xfer#70, to-check=11/88)
pyutils/pyutils/py_validation.py
       4.47K 100%  189.62kB/s    0:00:00 (xfer#71, to-check=10/88)
pyutils/pyutils/pyutils.py
       3.00K 100%  127.59kB/s    0:00:00 (xfer#72, to-check=9/88)
pyutils/pyutils/ming/
pyutils/pyutils/ming/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#73, to-check=7/88)
pyutils/pyutils/ming/extensions.py
       1.79K 100%   75.96kB/s    0:00:00 (xfer#74, to-check=6/88)
pyutils/pyutils/ming/schema.py
       4.22K 100%  179.05kB/s    0:00:00 (xfer#75, to-check=5/88)
pyutils/pyutils/ming/session.py
       1.47K 100%   62.42kB/s    0:00:00 (xfer#76, to-check=4/88)
pyutils/tests/
pyutils/tests/TestPyutils.py
       5.52K 100%  234.50kB/s    0:00:00 (xfer#77, to-check=3/88)
pyutils/tests/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#78, to-check=2/88)
pyutils/tests/unicode.csv
          49 100%    2.08kB/s    0:00:00 (xfer#79, to-check=1/88)
templates/
templates/celeryconfig.py.template
       1.84K 100%   78.34kB/s    0:00:00 (xfer#80, to-check=0/88)

sent 633.48K bytes  received 1.56K bytes  1.27M bytes/sec
total size is 628.12K  speedup is 0.99
sending incremental file list
./
.gitignore
           6 100%    0.00kB/s    0:00:00 (xfer#1, to-check=82/84)
config.yaml
         846 100%  826.17kB/s    0:00:00 (xfer#2, to-check=81/84)
copyright
         743 100%  725.59kB/s    0:00:00 (xfer#3, to-check=80/84)
local_config.pkl
         368 100%  359.38kB/s    0:00:00 (xfer#4, to-check=79/84)
metadata.yaml
         300 100%  292.97kB/s    0:00:00 (xfer#5, to-check=78/84)
revision
           3 100%    2.93kB/s    0:00:00 (xfer#6, to-check=77/84)
setup.py
       2.43K 100%    2.31MB/s    0:00:00 (xfer#7, to-check=76/84)
setup.sh
       1.81K 100%    1.73MB/s    0:00:00 (xfer#8, to-check=75/84)
hooks/
hooks/config-changed
          69 100%   67.38kB/s    0:00:00 (xfer#9, to-check=71/84)
hooks/install
          73 100%   71.29kB/s    0:00:00 (xfer#10, to-check=70/84)
hooks/peer-relation-broken
          75 100%   73.24kB/s    0:00:00 (xfer#11, to-check=69/84)
hooks/peer-relation-changed
          76 100%   74.22kB/s    0:00:00 (xfer#12, to-check=68/84)
hooks/peer-relation-joined
          75 100%   73.24kB/s    0:00:00 (xfer#13, to-check=67/84)
hooks/start
          60 100%   29.30kB/s    0:00:00 (xfer#14, to-check=66/84)
hooks/stop
          59 100%   28.81kB/s    0:00:00 (xfer#15, to-check=65/84)
hooks/storage-relation-broken
          78 100%   38.09kB/s    0:00:00 (xfer#16, to-check=64/84)
hooks/storage-relation-departed
          80 100%   39.06kB/s    0:00:00 (xfer#17, to-check=63/84)
hooks/storage-relation-joined
          78 100%   38.09kB/s    0:00:00 (xfer#18, to-check=62/84)
hooks/uninstall
          64 100%   31.25kB/s    0:00:00 (xfer#19, to-check=61/84)
oscied_lib/
oscied_lib/.gitignore
          50 100%   24.41kB/s    0:00:00 (xfer#20, to-check=60/84)
oscied_lib/Callback.py
       2.72K 100%    1.30MB/s    0:00:00 (xfer#21, to-check=59/84)
oscied_lib/CharmConfig.py
       2.18K 100%  710.61kB/s    0:00:00 (xfer#22, to-check=58/84)
oscied_lib/CharmConfig_Storage.py
       5.68K 100%    1.80MB/s    0:00:00 (xfer#23, to-check=57/84)
oscied_lib/CharmHooks.py
      12.55K 100%    3.99MB/s    0:00:00 (xfer#24, to-check=56/84)
oscied_lib/CharmHooks_Storage.py
       7.12K 100%    1.70MB/s    0:00:00 (xfer#25, to-check=55/84)
oscied_lib/CharmHooks_Subordinate.py
       4.92K 100%    1.17MB/s    0:00:00 (xfer#26, to-check=54/84)
oscied_lib/CharmHooks_Website.py
       3.71K 100%  904.79kB/s    0:00:00 (xfer#27, to-check=53/84)
oscied_lib/Media.py
       4.37K 100%    1.04MB/s    0:00:00 (xfer#28, to-check=52/84)
oscied_lib/Orchestra.py
      30.96K 100%    5.90MB/s    0:00:00 (xfer#29, to-check=51/84)
oscied_lib/OrchestraConfig.py
       4.37K 100%  852.93kB/s    0:00:00 (xfer#30, to-check=50/84)
oscied_lib/OrchestraHooks.py
      13.21K 100%    2.52MB/s    0:00:00 (xfer#31, to-check=49/84)
oscied_lib/OsciedDBModel.py
       1.82K 100%  355.66kB/s    0:00:00 (xfer#32, to-check=48/84)
oscied_lib/PublishTask.py
       3.66K 100%  714.26kB/s    0:00:00 (xfer#33, to-check=47/84)
oscied_lib/Publisher.py
       4.97K 100%  971.09kB/s    0:00:00 (xfer#34, to-check=46/84)
oscied_lib/PublisherConfig.py
       3.12K 100%  610.16kB/s    0:00:00 (xfer#35, to-check=45/84)
oscied_lib/PublisherHooks.py
       6.93K 100%    1.32MB/s    0:00:00 (xfer#36, to-check=44/84)
oscied_lib/Storage.py
       3.72K 100%  726.17kB/s    0:00:00 (xfer#37, to-check=43/84)
oscied_lib/StorageConfig.py
       2.22K 100%  433.01kB/s    0:00:00 (xfer#38, to-check=42/84)
oscied_lib/StorageHooks.py
      11.98K 100%    1.90MB/s    0:00:00 (xfer#39, to-check=41/84)
oscied_lib/Transform.py
      13.66K 100%    2.17MB/s    0:00:00 (xfer#40, to-check=40/84)
oscied_lib/TransformConfig.py
       2.49K 100%  405.60kB/s    0:00:00 (xfer#41, to-check=39/84)
oscied_lib/TransformHooks.py
       5.54K 100%  772.88kB/s    0:00:00 (xfer#42, to-check=38/84)
oscied_lib/TransformProfile.py
       2.75K 100%  383.51kB/s    0:00:00 (xfer#43, to-check=37/84)
oscied_lib/TransformTask.py
       5.49K 100%  766.18kB/s    0:00:00 (xfer#44, to-check=36/84)
oscied_lib/User.py
       4.18K 100%  582.87kB/s    0:00:00 (xfer#45, to-check=35/84)
oscied_lib/WebuiConfig.py
       3.66K 100%  510.18kB/s    0:00:00 (xfer#46, to-check=34/84)
oscied_lib/WebuiHooks.py
      10.33K 100%    1.41MB/s    0:00:00 (xfer#47, to-check=33/84)
oscied_lib/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#48, to-check=32/84)
pyutils/
pyutils/.gitignore
          48 100%    6.70kB/s    0:00:00 (xfer#49, to-check=31/84)
pyutils/.travis.yml
         331 100%   46.18kB/s    0:00:00 (xfer#50, to-check=30/84)
pyutils/AUTHORS
          14 100%    1.95kB/s    0:00:00 (xfer#51, to-check=29/84)
pyutils/COPYING
      35.15K 100%    4.19MB/s    0:00:00 (xfer#52, to-check=28/84)
pyutils/README.rst
       1.39K 100%  169.56kB/s    0:00:00 (xfer#53, to-check=27/84)
pyutils/setup.cfg
         196 100%   23.93kB/s    0:00:00 (xfer#54, to-check=26/84)
pyutils/setup.py
       3.10K 100%  336.81kB/s    0:00:00 (xfer#55, to-check=25/84)
pyutils/pyutils/
pyutils/pyutils/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#56, to-check=22/84)
pyutils/pyutils/py_crypto.py
       1.89K 100%  204.54kB/s    0:00:00 (xfer#57, to-check=21/84)
pyutils/pyutils/py_datetime.py
       3.07K 100%  333.55kB/s    0:00:00 (xfer#58, to-check=20/84)
pyutils/pyutils/py_exception.py
       1.34K 100%  145.62kB/s    0:00:00 (xfer#59, to-check=19/84)
pyutils/pyutils/py_ffmpeg.py
       6.84K 100%  742.08kB/s    0:00:00 (xfer#60, to-check=18/84)
pyutils/pyutils/py_filesystem.py
      10.20K 100%    1.08MB/s    0:00:00 (xfer#61, to-check=17/84)
pyutils/pyutils/py_flask.py
       3.03K 100%  329.10kB/s    0:00:00 (xfer#62, to-check=16/84)
pyutils/pyutils/py_juju.py
      10.17K 100%  993.55kB/s    0:00:00 (xfer#63, to-check=15/84)
pyutils/pyutils/py_logging.py
       3.49K 100%  340.92kB/s    0:00:00 (xfer#64, to-check=14/84)
pyutils/pyutils/py_mock.py
       2.56K 100%  250.29kB/s    0:00:00 (xfer#65, to-check=13/84)
pyutils/pyutils/py_serialization.py
       6.85K 100%  669.04kB/s    0:00:00 (xfer#66, to-check=12/84)
pyutils/pyutils/py_subprocess.py
       5.48K 100%  535.45kB/s    0:00:00 (xfer#67, to-check=11/84)
pyutils/pyutils/py_unicode.py
       2.29K 100%  203.12kB/s    0:00:00 (xfer#68, to-check=10/84)
pyutils/pyutils/py_validation.py
       4.47K 100%  396.48kB/s    0:00:00 (xfer#69, to-check=9/84)
pyutils/pyutils/pyutils.py
       3.00K 100%  266.78kB/s    0:00:00 (xfer#70, to-check=8/84)
pyutils/pyutils/ming/
pyutils/pyutils/ming/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#71, to-check=6/84)
pyutils/pyutils/ming/extensions.py
       1.79K 100%  158.82kB/s    0:00:00 (xfer#72, to-check=5/84)
pyutils/pyutils/ming/schema.py
       4.22K 100%  374.38kB/s    0:00:00 (xfer#73, to-check=4/84)
pyutils/pyutils/ming/session.py
       1.47K 100%  130.50kB/s    0:00:00 (xfer#74, to-check=3/84)
pyutils/tests/
pyutils/tests/TestPyutils.py
       5.52K 100%  490.32kB/s    0:00:00 (xfer#75, to-check=2/84)
pyutils/tests/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#76, to-check=1/84)
pyutils/tests/unicode.csv
          49 100%    4.35kB/s    0:00:00 (xfer#77, to-check=0/84)

sent 308.65K bytes  received 1.50K bytes  620.30K bytes/sec
total size is 303.62K  speedup is 0.98
sending incremental file list
./
.gitignore
           6 100%    0.00kB/s    0:00:00 (xfer#1, to-check=85/87)
config.yaml
       1.65K 100%    1.58MB/s    0:00:00 (xfer#2, to-check=84/87)
copyright
         752 100%  734.38kB/s    0:00:00 (xfer#3, to-check=83/87)
gpac.tar.bz2
       8.55M 100%   27.46MB/s    0:00:00 (xfer#4, to-check=82/87)
local_config.pkl
         522 100%    1.71kB/s    0:00:00 (xfer#5, to-check=81/87)
metadata.yaml
         341 100%    1.12kB/s    0:00:00 (xfer#6, to-check=80/87)
revision
           2 100%    0.01kB/s    0:00:00 (xfer#7, to-check=79/87)
setup.py
       2.43K 100%    7.95kB/s    0:00:00 (xfer#8, to-check=78/87)
setup.sh
       1.81K 100%    5.94kB/s    0:00:00 (xfer#9, to-check=77/87)
hooks/
hooks/config-changed
          71 100%    0.23kB/s    0:00:00 (xfer#10, to-check=72/87)
hooks/install
          75 100%    0.24kB/s    0:00:00 (xfer#11, to-check=71/87)
hooks/start
          62 100%    0.20kB/s    0:00:00 (xfer#12, to-check=70/87)
hooks/stop
          61 100%    0.20kB/s    0:00:00 (xfer#13, to-check=69/87)
hooks/storage-relation-broken
          80 100%    0.26kB/s    0:00:00 (xfer#14, to-check=68/87)
hooks/storage-relation-changed
          81 100%    0.26kB/s    0:00:00 (xfer#15, to-check=67/87)
hooks/storage-relation-joined
          80 100%    0.26kB/s    0:00:00 (xfer#16, to-check=66/87)
hooks/transform-relation-broken
          84 100%    0.27kB/s    0:00:00 (xfer#17, to-check=65/87)
hooks/transform-relation-changed
          85 100%    0.28kB/s    0:00:00 (xfer#18, to-check=64/87)
hooks/transform-relation-joined
          84 100%    0.27kB/s    0:00:00 (xfer#19, to-check=63/87)
hooks/uninstall
          66 100%    0.21kB/s    0:00:00 (xfer#20, to-check=62/87)
oscied_lib/
oscied_lib/.gitignore
          50 100%    0.16kB/s    0:00:00 (xfer#21, to-check=61/87)
oscied_lib/Callback.py
       2.72K 100%    8.81kB/s    0:00:00 (xfer#22, to-check=60/87)
oscied_lib/CharmConfig.py
       2.18K 100%    7.06kB/s    0:00:00 (xfer#23, to-check=59/87)
oscied_lib/CharmConfig_Storage.py
       5.68K 100%   18.36kB/s    0:00:00 (xfer#24, to-check=58/87)
oscied_lib/CharmHooks.py
      12.55K 100%   40.59kB/s    0:00:00 (xfer#25, to-check=57/87)
oscied_lib/CharmHooks_Storage.py
       7.12K 100%   22.81kB/s    0:00:00 (xfer#26, to-check=56/87)
oscied_lib/CharmHooks_Subordinate.py
       4.92K 100%   15.77kB/s    0:00:00 (xfer#27, to-check=55/87)
oscied_lib/CharmHooks_Website.py
       3.71K 100%   11.87kB/s    0:00:00 (xfer#28, to-check=54/87)
oscied_lib/Media.py
       4.37K 100%   14.00kB/s    0:00:00 (xfer#29, to-check=53/87)
oscied_lib/Orchestra.py
      30.96K 100%   98.47kB/s    0:00:00 (xfer#30, to-check=52/87)
oscied_lib/OrchestraConfig.py
       4.37K 100%   13.89kB/s    0:00:00 (xfer#31, to-check=51/87)
oscied_lib/OrchestraHooks.py
      13.21K 100%   42.00kB/s    0:00:00 (xfer#32, to-check=50/87)
oscied_lib/OsciedDBModel.py
       1.82K 100%    5.79kB/s    0:00:00 (xfer#33, to-check=49/87)
oscied_lib/PublishTask.py
       3.66K 100%   11.63kB/s    0:00:00 (xfer#34, to-check=48/87)
oscied_lib/Publisher.py
       4.97K 100%   15.82kB/s    0:00:00 (xfer#35, to-check=47/87)
oscied_lib/PublisherConfig.py
       3.12K 100%    9.94kB/s    0:00:00 (xfer#36, to-check=46/87)
oscied_lib/PublisherHooks.py
       6.93K 100%   21.97kB/s    0:00:00 (xfer#37, to-check=45/87)
oscied_lib/Storage.py
       3.72K 100%   11.79kB/s    0:00:00 (xfer#38, to-check=44/87)
oscied_lib/StorageConfig.py
       2.22K 100%    7.03kB/s    0:00:00 (xfer#39, to-check=43/87)
oscied_lib/StorageHooks.py
      11.98K 100%   37.87kB/s    0:00:00 (xfer#40, to-check=42/87)
oscied_lib/Transform.py
      13.66K 100%   43.17kB/s    0:00:00 (xfer#41, to-check=41/87)
oscied_lib/TransformConfig.py
       2.49K 100%    7.88kB/s    0:00:00 (xfer#42, to-check=40/87)
oscied_lib/TransformHooks.py
       5.54K 100%   17.45kB/s    0:00:00 (xfer#43, to-check=39/87)
oscied_lib/TransformProfile.py
       2.75K 100%    8.66kB/s    0:00:00 (xfer#44, to-check=38/87)
oscied_lib/TransformTask.py
       5.49K 100%   17.30kB/s    0:00:00 (xfer#45, to-check=37/87)
oscied_lib/User.py
       4.18K 100%   13.16kB/s    0:00:00 (xfer#46, to-check=36/87)
oscied_lib/WebuiConfig.py
       3.66K 100%   11.52kB/s    0:00:00 (xfer#47, to-check=35/87)
oscied_lib/WebuiHooks.py
      10.33K 100%   32.45kB/s    0:00:00 (xfer#48, to-check=34/87)
oscied_lib/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#49, to-check=33/87)
pyutils/
pyutils/.gitignore
          48 100%    0.15kB/s    0:00:00 (xfer#50, to-check=32/87)
pyutils/.travis.yml
         331 100%    1.04kB/s    0:00:00 (xfer#51, to-check=31/87)
pyutils/AUTHORS
          14 100%    0.04kB/s    0:00:00 (xfer#52, to-check=30/87)
pyutils/COPYING
      35.15K 100%  109.66kB/s    0:00:00 (xfer#53, to-check=29/87)
pyutils/README.rst
       1.39K 100%    4.33kB/s    0:00:00 (xfer#54, to-check=28/87)
pyutils/setup.cfg
         196 100%    0.61kB/s    0:00:00 (xfer#55, to-check=27/87)
pyutils/setup.py
       3.10K 100%    9.68kB/s    0:00:00 (xfer#56, to-check=26/87)
pyutils/pyutils/
pyutils/pyutils/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#57, to-check=23/87)
pyutils/pyutils/py_crypto.py
       1.89K 100%    5.88kB/s    0:00:00 (xfer#58, to-check=22/87)
pyutils/pyutils/py_datetime.py
       3.07K 100%    9.59kB/s    0:00:00 (xfer#59, to-check=21/87)
pyutils/pyutils/py_exception.py
       1.34K 100%    4.19kB/s    0:00:00 (xfer#60, to-check=20/87)
pyutils/pyutils/py_ffmpeg.py
       6.84K 100%   21.34kB/s    0:00:00 (xfer#61, to-check=19/87)
pyutils/pyutils/py_filesystem.py
      10.20K 100%   31.72kB/s    0:00:00 (xfer#62, to-check=18/87)
pyutils/pyutils/py_flask.py
       3.03K 100%    9.43kB/s    0:00:00 (xfer#63, to-check=17/87)
pyutils/pyutils/py_juju.py
      10.17K 100%   31.54kB/s    0:00:00 (xfer#64, to-check=16/87)
pyutils/pyutils/py_logging.py
       3.49K 100%   10.82kB/s    0:00:00 (xfer#65, to-check=15/87)
pyutils/pyutils/py_mock.py
       2.56K 100%    7.95kB/s    0:00:00 (xfer#66, to-check=14/87)
pyutils/pyutils/py_serialization.py
       6.85K 100%   21.17kB/s    0:00:00 (xfer#67, to-check=13/87)
pyutils/pyutils/py_subprocess.py
       5.48K 100%   16.94kB/s    0:00:00 (xfer#68, to-check=12/87)
pyutils/pyutils/py_unicode.py
       2.29K 100%    7.07kB/s    0:00:00 (xfer#69, to-check=11/87)
pyutils/pyutils/py_validation.py
       4.47K 100%   13.80kB/s    0:00:00 (xfer#70, to-check=10/87)
pyutils/pyutils/pyutils.py
       3.00K 100%    9.29kB/s    0:00:00 (xfer#71, to-check=9/87)
pyutils/pyutils/ming/
pyutils/pyutils/ming/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#72, to-check=7/87)
pyutils/pyutils/ming/extensions.py
       1.79K 100%    5.51kB/s    0:00:00 (xfer#73, to-check=6/87)
pyutils/pyutils/ming/schema.py
       4.22K 100%   12.99kB/s    0:00:00 (xfer#74, to-check=5/87)
pyutils/pyutils/ming/session.py
       1.47K 100%    4.53kB/s    0:00:00 (xfer#75, to-check=4/87)
pyutils/tests/
pyutils/tests/TestPyutils.py
       5.52K 100%   17.01kB/s    0:00:00 (xfer#76, to-check=3/87)
pyutils/tests/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#77, to-check=2/87)
pyutils/tests/unicode.csv
          49 100%    0.15kB/s    0:00:00 (xfer#78, to-check=1/87)
templates/
templates/celeryconfig.py.template
       1.84K 100%    5.68kB/s    0:00:00 (xfer#79, to-check=0/87)

sent 8.87M bytes  received 1.54K bytes  5.91M bytes/sec
total size is 8.86M  speedup is 1.00
sending incremental file list
./
AUTHORS
          31 100%    0.00kB/s    0:00:00 (xfer#1, to-check=495/497)
README.rst
         203 100%  198.24kB/s    0:00:00 (xfer#2, to-check=494/497)
apache2.conf
       9.38K 100%    8.95MB/s    0:00:00 (xfer#3, to-check=493/497)
config.yaml
       1.66K 100%    1.58MB/s    0:00:00 (xfer#4, to-check=492/497)
copyright
         752 100%  734.38kB/s    0:00:00 (xfer#5, to-check=491/497)
local_config.pkl
       1.12K 100%    1.07MB/s    0:00:00 (xfer#6, to-check=490/497)
metadata.yaml
         348 100%  169.92kB/s    0:00:00 (xfer#7, to-check=489/497)
revision
           2 100%    0.98kB/s    0:00:00 (xfer#8, to-check=488/497)
setup.py
       2.43K 100%    1.16MB/s    0:00:00 (xfer#9, to-check=487/497)
setup.sh
       1.81K 100%  885.74kB/s    0:00:00 (xfer#10, to-check=486/497)
webui-db.sql
       1.72K 100%  838.87kB/s    0:00:00 (xfer#11, to-check=485/497)
hooks/
hooks/api-relation-broken
          72 100%   35.16kB/s    0:00:00 (xfer#12, to-check=479/497)
hooks/api-relation-changed
          73 100%   23.76kB/s    0:00:00 (xfer#13, to-check=478/497)
hooks/api-relation-joined
          72 100%   23.44kB/s    0:00:00 (xfer#14, to-check=477/497)
hooks/config-changed
          67 100%   21.81kB/s    0:00:00 (xfer#15, to-check=476/497)
hooks/install
          71 100%   23.11kB/s    0:00:00 (xfer#16, to-check=475/497)
hooks/start
          58 100%   14.16kB/s    0:00:00 (xfer#17, to-check=474/497)
hooks/stop
          57 100%   13.92kB/s    0:00:00 (xfer#18, to-check=473/497)
hooks/storage-relation-broken
          76 100%   18.55kB/s    0:00:00 (xfer#19, to-check=472/497)
hooks/storage-relation-changed
          77 100%   18.80kB/s    0:00:00 (xfer#20, to-check=471/497)
hooks/storage-relation-joined
          76 100%   14.84kB/s    0:00:00 (xfer#21, to-check=470/497)
hooks/uninstall
          62 100%   12.11kB/s    0:00:00 (xfer#22, to-check=469/497)
hooks/website-relation-broken
          76 100%   14.84kB/s    0:00:00 (xfer#23, to-check=468/497)
hooks/website-relation-changed
          77 100%   15.04kB/s    0:00:00 (xfer#24, to-check=467/497)
hooks/website-relation-departed
          78 100%   12.70kB/s    0:00:00 (xfer#25, to-check=466/497)
hooks/website-relation-joined
          76 100%   12.37kB/s    0:00:00 (xfer#26, to-check=465/497)
oscied_lib/
oscied_lib/.gitignore
          50 100%    8.14kB/s    0:00:00 (xfer#27, to-check=464/497)
oscied_lib/Callback.py
       2.72K 100%  443.20kB/s    0:00:00 (xfer#28, to-check=463/497)
oscied_lib/CharmConfig.py
       2.18K 100%  355.31kB/s    0:00:00 (xfer#29, to-check=462/497)
oscied_lib/CharmConfig_Storage.py
       5.68K 100%  924.15kB/s    0:00:00 (xfer#30, to-check=461/497)
oscied_lib/CharmHooks.py
      12.55K 100%    2.00MB/s    0:00:00 (xfer#31, to-check=460/497)
oscied_lib/CharmHooks_Storage.py
       7.12K 100%    1.13MB/s    0:00:00 (xfer#32, to-check=459/497)
oscied_lib/CharmHooks_Subordinate.py
       4.92K 100%  601.07kB/s    0:00:00 (xfer#33, to-check=458/497)
oscied_lib/CharmHooks_Website.py
       3.71K 100%  402.13kB/s    0:00:00 (xfer#34, to-check=457/497)
oscied_lib/Media.py
       4.37K 100%  474.50kB/s    0:00:00 (xfer#35, to-check=456/497)
oscied_lib/Orchestra.py
      30.96K 100%    2.95MB/s    0:00:00 (xfer#36, to-check=455/497)
oscied_lib/OrchestraConfig.py
       4.37K 100%  387.70kB/s    0:00:00 (xfer#37, to-check=454/497)
oscied_lib/OrchestraHooks.py
      13.21K 100%    1.14MB/s    0:00:00 (xfer#38, to-check=453/497)
oscied_lib/OsciedDBModel.py
       1.82K 100%  161.67kB/s    0:00:00 (xfer#39, to-check=452/497)
oscied_lib/PublishTask.py
       3.66K 100%  324.66kB/s    0:00:00 (xfer#40, to-check=451/497)
oscied_lib/Publisher.py
       4.97K 100%  441.41kB/s    0:00:00 (xfer#41, to-check=450/497)
oscied_lib/PublisherConfig.py
       3.12K 100%  277.34kB/s    0:00:00 (xfer#42, to-check=449/497)
oscied_lib/PublisherHooks.py
       6.93K 100%  563.96kB/s    0:00:00 (xfer#43, to-check=448/497)
oscied_lib/Storage.py
       3.72K 100%  302.57kB/s    0:00:00 (xfer#44, to-check=447/497)
oscied_lib/StorageConfig.py
       2.22K 100%  180.42kB/s    0:00:00 (xfer#45, to-check=446/497)
oscied_lib/StorageHooks.py
      11.98K 100%  975.10kB/s    0:00:00 (xfer#46, to-check=445/497)
oscied_lib/Transform.py
      13.66K 100%    1.00MB/s    0:00:00 (xfer#47, to-check=444/497)
oscied_lib/TransformConfig.py
       2.49K 100%  187.20kB/s    0:00:00 (xfer#48, to-check=443/497)
oscied_lib/TransformHooks.py
       5.54K 100%  386.44kB/s    0:00:00 (xfer#49, to-check=442/497)
oscied_lib/TransformProfile.py
       2.75K 100%  191.76kB/s    0:00:00 (xfer#50, to-check=441/497)
oscied_lib/TransformTask.py
       5.49K 100%  383.09kB/s    0:00:00 (xfer#51, to-check=440/497)
oscied_lib/User.py
       4.18K 100%  291.43kB/s    0:00:00 (xfer#52, to-check=439/497)
oscied_lib/WebuiConfig.py
       3.66K 100%  255.09kB/s    0:00:00 (xfer#53, to-check=438/497)
oscied_lib/WebuiHooks.py
      10.33K 100%  672.72kB/s    0:00:00 (xfer#54, to-check=437/497)
oscied_lib/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#55, to-check=436/497)
pyutils/
pyutils/.gitignore
          48 100%    3.12kB/s    0:00:00 (xfer#56, to-check=435/497)
pyutils/.travis.yml
         331 100%   21.55kB/s    0:00:00 (xfer#57, to-check=434/497)
pyutils/AUTHORS
          14 100%    0.91kB/s    0:00:00 (xfer#58, to-check=433/497)
pyutils/COPYING
      35.15K 100%    1.97MB/s    0:00:00 (xfer#59, to-check=432/497)
pyutils/README.rst
       1.39K 100%   79.79kB/s    0:00:00 (xfer#60, to-check=431/497)
pyutils/setup.cfg
         196 100%   11.26kB/s    0:00:00 (xfer#61, to-check=430/497)
pyutils/setup.py
       3.10K 100%  168.40kB/s    0:00:00 (xfer#62, to-check=429/497)
pyutils/pyutils/
pyutils/pyutils/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#63, to-check=426/497)
pyutils/pyutils/py_crypto.py
       1.89K 100%  102.27kB/s    0:00:00 (xfer#64, to-check=425/497)
pyutils/pyutils/py_datetime.py
       3.07K 100%  166.78kB/s    0:00:00 (xfer#65, to-check=424/497)
pyutils/pyutils/py_exception.py
       1.34K 100%   72.81kB/s    0:00:00 (xfer#66, to-check=423/497)
pyutils/pyutils/py_ffmpeg.py
       6.84K 100%  371.04kB/s    0:00:00 (xfer#67, to-check=422/497)
pyutils/pyutils/py_filesystem.py
      10.20K 100%  553.33kB/s    0:00:00 (xfer#68, to-check=421/497)
pyutils/pyutils/py_flask.py
       3.03K 100%  164.55kB/s    0:00:00 (xfer#69, to-check=420/497)
pyutils/pyutils/py_juju.py
      10.17K 100%  496.78kB/s    0:00:00 (xfer#70, to-check=419/497)
pyutils/pyutils/py_logging.py
       3.49K 100%  170.46kB/s    0:00:00 (xfer#71, to-check=418/497)
pyutils/pyutils/py_mock.py
       2.56K 100%  125.15kB/s    0:00:00 (xfer#72, to-check=417/497)
pyutils/pyutils/py_serialization.py
       6.85K 100%  334.52kB/s    0:00:00 (xfer#73, to-check=416/497)
pyutils/pyutils/py_subprocess.py
       5.48K 100%  267.72kB/s    0:00:00 (xfer#74, to-check=415/497)
pyutils/pyutils/py_unicode.py
       2.29K 100%  111.72kB/s    0:00:00 (xfer#75, to-check=414/497)
pyutils/pyutils/py_validation.py
       4.47K 100%  218.07kB/s    0:00:00 (xfer#76, to-check=413/497)
pyutils/pyutils/pyutils.py
       3.00K 100%  146.73kB/s    0:00:00 (xfer#77, to-check=412/497)
pyutils/pyutils/ming/
pyutils/pyutils/ming/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#78, to-check=410/497)
pyutils/pyutils/ming/extensions.py
       1.79K 100%   87.35kB/s    0:00:00 (xfer#79, to-check=409/497)
pyutils/pyutils/ming/schema.py
       4.22K 100%  205.91kB/s    0:00:00 (xfer#80, to-check=408/497)
pyutils/pyutils/ming/session.py
       1.47K 100%   71.78kB/s    0:00:00 (xfer#81, to-check=407/497)
pyutils/tests/
pyutils/tests/TestPyutils.py
       5.52K 100%  269.68kB/s    0:00:00 (xfer#82, to-check=406/497)
pyutils/tests/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#83, to-check=405/497)
pyutils/tests/unicode.csv
          49 100%    2.39kB/s    0:00:00 (xfer#84, to-check=404/497)
templates/
templates/000-default
         691 100%   32.13kB/s    0:00:00 (xfer#85, to-check=403/497)
templates/config.php.template
      14.36K 100%  667.78kB/s    0:00:00 (xfer#86, to-check=402/497)
templates/database.php.template
       3.24K 100%  150.81kB/s    0:00:00 (xfer#87, to-check=401/497)
templates/htaccess.template
         410 100%   19.07kB/s    0:00:00 (xfer#88, to-check=400/497)
www/
www/index.php
       6.36K 100%  282.18kB/s    0:00:00 (xfer#89, to-check=399/497)
www/license.txt
       2.50K 100%  110.80kB/s    0:00:00 (xfer#90, to-check=398/497)
www/application/
www/application/.htaccess
          13 100%    0.58kB/s    0:00:00 (xfer#91, to-check=391/497)
www/application/index.html
         114 100%    4.84kB/s    0:00:00 (xfer#92, to-check=390/497)
www/application/cache/
www/application/cache/.htaccess
          13 100%    0.55kB/s    0:00:00 (xfer#93, to-check=376/497)
www/application/cache/index.html
         114 100%    4.84kB/s    0:00:00 (xfer#94, to-check=375/497)
www/application/config/
www/application/config/autoload.php
       3.15K 100%  127.97kB/s    0:00:00 (xfer#95, to-check=374/497)
www/application/config/constants.php
       1.71K 100%   69.66kB/s    0:00:00 (xfer#96, to-check=373/497)
www/application/config/doctypes.php
       1.14K 100%   46.31kB/s    0:00:00 (xfer#97, to-check=372/497)
www/application/config/foreign_chars.php
       1.78K 100%   69.57kB/s    0:00:00 (xfer#98, to-check=371/497)
www/application/config/hooks.php
         498 100%   19.45kB/s    0:00:00 (xfer#99, to-check=370/497)
www/application/config/index.html
         114 100%    4.45kB/s    0:00:00 (xfer#100, to-check=369/497)
www/application/config/migration.php
       1.28K 100%   50.08kB/s    0:00:00 (xfer#101, to-check=368/497)
www/application/config/mimes.php
       5.42K 100%  203.76kB/s    0:00:00 (xfer#102, to-check=367/497)
www/application/config/pagination.php
       1.03K 100%   38.65kB/s    0:00:00 (xfer#103, to-check=366/497)
www/application/config/profiler.php
         564 100%   21.18kB/s    0:00:00 (xfer#104, to-check=365/497)
www/application/config/routes.php
       1.57K 100%   59.08kB/s    0:00:00 (xfer#105, to-check=364/497)
www/application/config/smileys.php
       3.29K 100%  123.76kB/s    0:00:00 (xfer#106, to-check=363/497)
www/application/config/user_agents.php
       5.59K 100%  202.15kB/s    0:00:00 (xfer#107, to-check=362/497)
www/application/controllers/
www/application/controllers/index.html
         114 100%    4.12kB/s    0:00:00 (xfer#108, to-check=361/497)
www/application/controllers/media.php
       8.43K 100%  294.05kB/s    0:00:00 (xfer#109, to-check=360/497)
www/application/controllers/misc.php
         620 100%   21.62kB/s    0:00:00 (xfer#110, to-check=359/497)
www/application/controllers/profile.php
       5.61K 100%  144.25kB/s    0:00:00 (xfer#111, to-check=358/497)
www/application/controllers/publisher.php
       5.16K 100%  132.61kB/s    0:00:00 (xfer#112, to-check=357/497)
www/application/controllers/transform.php
       5.81K 100%  145.41kB/s    0:00:00 (xfer#113, to-check=356/497)
www/application/controllers/upload_files.php
       2.53K 100%   63.43kB/s    0:00:00 (xfer#114, to-check=355/497)
www/application/controllers/users.php
      10.32K 100%  258.34kB/s    0:00:00 (xfer#115, to-check=354/497)
www/application/core/
www/application/core/MY_Controller.php
         733 100%   17.90kB/s    0:00:00 (xfer#116, to-check=353/497)
www/application/core/MY_Loader.php
       7.11K 100%  173.46kB/s    0:00:00 (xfer#117, to-check=352/497)
www/application/core/index.html
         114 100%    2.78kB/s    0:00:00 (xfer#118, to-check=351/497)
www/application/errors/
www/application/errors/error_404.php
       1.16K 100%   28.32kB/s    0:00:00 (xfer#119, to-check=350/497)
www/application/errors/error_db.php
       1.16K 100%   28.22kB/s    0:00:00 (xfer#120, to-check=349/497)
www/application/errors/error_general.php
       1.15K 100%   27.32kB/s    0:00:00 (xfer#121, to-check=348/497)
www/application/errors/error_php.php
         288 100%    6.86kB/s    0:00:00 (xfer#122, to-check=347/497)
www/application/errors/index.html
         114 100%    2.72kB/s    0:00:00 (xfer#123, to-check=346/497)
www/application/helpers/
www/application/helpers/MY_download_helper.php
       3.12K 100%   74.29kB/s    0:00:00 (xfer#124, to-check=345/497)
www/application/helpers/flash_message_helper.php
       1.39K 100%   33.04kB/s    0:00:00 (xfer#125, to-check=344/497)
www/application/helpers/index.html
         114 100%    2.72kB/s    0:00:00 (xfer#126, to-check=343/497)
www/application/helpers/simple_html_dom_helper.php
      53.22K 100%    1.18MB/s    0:00:00 (xfer#127, to-check=342/497)
www/application/hooks/
www/application/hooks/index.html
         114 100%    2.59kB/s    0:00:00 (xfer#128, to-check=341/497)
www/application/language/
www/application/language/english/
www/application/language/english/index.html
         114 100%    2.59kB/s    0:00:00 (xfer#129, to-check=339/497)
www/application/libraries/
www/application/libraries/Css_js.php
         794 100%   18.03kB/s    0:00:00 (xfer#130, to-check=338/497)
www/application/libraries/MY_Form_validation.php
         488 100%   11.08kB/s    0:00:00 (xfer#131, to-check=337/497)
www/application/libraries/User.php
       1.41K 100%   31.91kB/s    0:00:00 (xfer#132, to-check=336/497)
www/application/libraries/index.html
         114 100%    2.59kB/s    0:00:00 (xfer#133, to-check=335/497)
www/application/logs/
www/application/logs/index.html
         114 100%    2.53kB/s    0:00:00 (xfer#134, to-check=334/497)
www/application/models/
www/application/models/files_model.php
       1.66K 100%   36.75kB/s    0:00:00 (xfer#135, to-check=333/497)
www/application/models/index.html
         114 100%    2.53kB/s    0:00:00 (xfer#136, to-check=332/497)
www/application/models/tmp_files_model.php
       1.49K 100%   33.03kB/s    0:00:00 (xfer#137, to-check=331/497)
www/application/third_party/
www/application/third_party/index.html
         114 100%    2.53kB/s    0:00:00 (xfer#138, to-check=330/497)
www/application/views/
www/application/views/contact.php
          11 100%    0.24kB/s    0:00:00 (xfer#139, to-check=329/497)
www/application/views/homepage.php
          24 100%    0.53kB/s    0:00:00 (xfer#140, to-check=328/497)
www/application/views/index.html
         114 100%    2.47kB/s    0:00:00 (xfer#141, to-check=327/497)
www/application/views/fileupload/
www/application/views/fileupload/scripts.php
       4.63K 100%  100.54kB/s    0:00:00 (xfer#142, to-check=319/497)
www/application/views/fileupload/upload.php
         968 100%   21.01kB/s    0:00:00 (xfer#143, to-check=318/497)
www/application/views/layouts/
www/application/views/layouts/default.php
       1.77K 100%   38.39kB/s    0:00:00 (xfer#144, to-check=317/497)
www/application/views/layouts/default_header.php
       3.79K 100%   82.29kB/s    0:00:00 (xfer#145, to-check=316/497)
www/application/views/media/
www/application/views/media/add_media_form.php
       3.57K 100%   77.45kB/s    0:00:00 (xfer#146, to-check=315/497)
www/application/views/media/show.php
         642 100%   13.63kB/s    0:00:00 (xfer#147, to-check=314/497)
www/application/views/media/show_medias.php
       2.67K 100%   56.73kB/s    0:00:00 (xfer#148, to-check=313/497)
www/application/views/profile/
www/application/views/profile/add_profile_form.php
       1.72K 100%   36.49kB/s    0:00:00 (xfer#149, to-check=312/497)
www/application/views/profile/show.php
         660 100%   14.01kB/s    0:00:00 (xfer#150, to-check=311/497)
www/application/views/profile/show_profiles.php
       1.39K 100%   29.55kB/s    0:00:00 (xfer#151, to-check=310/497)
www/application/views/publisher/
www/application/views/publisher/launch_publish_form.php
       1.41K 100%   29.87kB/s    0:00:00 (xfer#152, to-check=309/497)
www/application/views/publisher/show.php
         658 100%   13.67kB/s    0:00:00 (xfer#153, to-check=308/497)
www/application/views/publisher/show_tasks.php
       4.52K 100%   93.92kB/s    0:00:00 (xfer#154, to-check=307/497)
www/application/views/transform/
www/application/views/transform/launch_transform_form.php
       1.84K 100%   38.21kB/s    0:00:00 (xfer#155, to-check=306/497)
www/application/views/transform/show.php
         658 100%   13.67kB/s    0:00:00 (xfer#156, to-check=305/497)
www/application/views/transform/show_tasks.php
       4.79K 100%   97.51kB/s    0:00:00 (xfer#157, to-check=304/497)
www/application/views/users/
www/application/views/users/add_user_form.php
       1.80K 100%   36.68kB/s    0:00:00 (xfer#158, to-check=303/497)
www/application/views/users/login_modal.php
       1.60K 100%   32.59kB/s    0:00:00 (xfer#159, to-check=302/497)
www/application/views/users/show.php
       1.82K 100%   37.09kB/s    0:00:00 (xfer#160, to-check=301/497)
www/application/views/users/show_users.php
       3.32K 100%   67.55kB/s    0:00:00 (xfer#161, to-check=300/497)
www/assets/
www/assets/index.html
         114 100%    2.27kB/s    0:00:00 (xfer#162, to-check=299/497)
www/assets/css/
www/assets/css/bootstrap-responsive.css
      21.75K 100%  433.49kB/s    0:00:00 (xfer#163, to-check=295/497)
www/assets/css/bootstrap-responsive.min.css
      16.55K 100%  323.30kB/s    0:00:00 (xfer#164, to-check=294/497)
www/assets/css/bootstrap.css
     124.22K 100%    2.24MB/s    0:00:00 (xfer#165, to-check=293/497)
www/assets/css/bootstrap.min.css
     103.31K 100%    1.76MB/s    0:00:00 (xfer#166, to-check=292/497)
www/assets/css/custom.css
       1.30K 100%   22.20kB/s    0:00:00 (xfer#167, to-check=291/497)
www/assets/css/style.css
       2.14K 100%   36.60kB/s    0:00:00 (xfer#168, to-check=290/497)
www/assets/css/fileupload/
www/assets/css/fileupload/bootstrap-image-gallery.min.css
       1.69K 100%   28.99kB/s    0:00:00 (xfer#169, to-check=288/497)
www/assets/css/fileupload/jquery-ui.css
      33.40K 100%  562.42kB/s    0:00:00 (xfer#170, to-check=287/497)
www/assets/css/fileupload/jquery.fileupload-ui.css
       1.28K 100%   21.48kB/s    0:00:00 (xfer#171, to-check=286/497)
www/assets/img/
www/assets/img/glyphicons-halflings-white.png
       8.78K 100%  147.78kB/s    0:00:00 (xfer#172, to-check=285/497)
www/assets/img/glyphicons-halflings.png
      12.80K 100%  211.85kB/s    0:00:00 (xfer#173, to-check=284/497)
www/assets/img/home-bg.jpg
       9.26M 100%   24.07MB/s    0:00:00 (xfer#174, to-check=283/497)
www/assets/img/home-bg11.jpg
      82.00K 100%  215.84kB/s    0:00:00 (xfer#175, to-check=282/497)
www/assets/img/fileupload/
www/assets/img/fileupload/loading.gif
       3.90K 100%   10.26kB/s    0:00:00 (xfer#176, to-check=279/497)
www/assets/img/fileupload/progressbar.gif
       3.32K 100%    8.72kB/s    0:00:00 (xfer#177, to-check=278/497)
www/assets/img/icons/
www/assets/img/icons/add.png
       5.49K 100%   14.42kB/s    0:00:00 (xfer#178, to-check=277/497)
www/assets/img/icons/calendar.png
       3.98K 100%   10.45kB/s    0:00:00 (xfer#179, to-check=276/497)
www/assets/img/icons/chat.png
       5.54K 100%   14.50kB/s    0:00:00 (xfer#180, to-check=275/497)
www/assets/img/icons/comment.png
       5.24K 100%   13.71kB/s    0:00:00 (xfer#181, to-check=274/497)
www/assets/img/icons/contacts.png
       5.90K 100%   15.40kB/s    0:00:00 (xfer#182, to-check=273/497)
www/assets/img/icons/contacts2.png
       5.77K 100%   15.07kB/s    0:00:00 (xfer#183, to-check=272/497)
www/assets/img/icons/delete.png
       5.49K 100%   14.30kB/s    0:00:00 (xfer#184, to-check=271/497)
www/assets/img/icons/edit.png
       5.08K 100%   13.24kB/s    0:00:00 (xfer#185, to-check=270/497)
www/assets/img/icons/edit2.png
       4.36K 100%   11.33kB/s    0:00:00 (xfer#186, to-check=269/497)
www/assets/img/icons/email.png
       4.56K 100%   11.84kB/s    0:00:00 (xfer#187, to-check=268/497)
www/assets/img/icons/favorite.png
       5.04K 100%   13.04kB/s    0:00:00 (xfer#188, to-check=267/497)
www/assets/img/icons/picture.png
       4.29K 100%   11.12kB/s    0:00:00 (xfer#189, to-check=266/497)
www/assets/img/icons/preferences.png
       6.26K 100%   16.16kB/s    0:00:00 (xfer#190, to-check=265/497)
www/assets/img/icons/rss.png
       4.91K 100%   12.67kB/s    0:00:00 (xfer#191, to-check=264/497)
www/assets/img/icons/save.png
       3.69K 100%    9.51kB/s    0:00:00 (xfer#192, to-check=263/497)
www/assets/img/icons/search.png
       5.12K 100%   13.20kB/s    0:00:00 (xfer#193, to-check=262/497)
www/assets/img/icons/user.png
       4.05K 100%   10.44kB/s    0:00:00 (xfer#194, to-check=261/497)
www/assets/img/icons/validate.png
       4.41K 100%   11.33kB/s    0:00:00 (xfer#195, to-check=260/497)
www/assets/img/icons/video.png
       4.27K 100%   10.97kB/s    0:00:00 (xfer#196, to-check=259/497)
www/assets/img/icons/pack1/
www/assets/img/icons/pack1/calendar.png
       4.18K 100%   10.70kB/s    0:00:00 (xfer#197, to-check=257/497)
www/assets/img/icons/pack1/comment.png
       4.12K 100%   10.57kB/s    0:00:00 (xfer#198, to-check=256/497)
www/assets/img/icons/pack1/comment2.png
       4.16K 100%   10.63kB/s    0:00:00 (xfer#199, to-check=255/497)
www/assets/img/icons/pack1/delete.png
       4.48K 100%   11.42kB/s    0:00:00 (xfer#200, to-check=254/497)
www/assets/img/icons/pack1/edit.png
       4.36K 100%   11.13kB/s    0:00:00 (xfer#201, to-check=253/497)
www/assets/img/icons/pack1/info.png
       4.44K 100%   11.29kB/s    0:00:00 (xfer#202, to-check=252/497)
www/assets/img/icons/pack1/picture.png
       4.53K 100%   11.52kB/s    0:00:00 (xfer#203, to-check=251/497)
www/assets/img/icons/pack1/save.png
       3.77K 100%    9.56kB/s    0:00:00 (xfer#204, to-check=250/497)
www/assets/img/icons/pack1/search.png
       4.66K 100%   11.82kB/s    0:00:00 (xfer#205, to-check=249/497)
www/assets/img/icons/pack1/validate.png
       4.14K 100%   10.49kB/s    0:00:00 (xfer#206, to-check=248/497)
www/assets/img/icons/pack1/video.png
       3.87K 100%    9.78kB/s    0:00:00 (xfer#207, to-check=247/497)
www/assets/js/
www/assets/js/bootstrap.js
      58.52K 100%  147.28kB/s    0:00:00 (xfer#208, to-check=246/497)
www/assets/js/bootstrap.min.js
      31.60K 100%   79.32kB/s    0:00:00 (xfer#209, to-check=245/497)
www/assets/js/jquery-1.8.0.min.js
      92.56K 100%  230.58kB/s    0:00:00 (xfer#210, to-check=244/497)
www/assets/js/fileupload/
www/assets/js/fileupload/canvas-to-blob.js
         859 100%    2.14kB/s    0:00:00 (xfer#211, to-check=242/497)
www/assets/js/fileupload/jquery-ui.min.js
     200.10K 100%  489.76kB/s    0:00:00 (xfer#212, to-check=241/497)
www/assets/js/fileupload/jquery.fileupload-fp.js
       8.40K 100%   20.56kB/s    0:00:00 (xfer#213, to-check=240/497)
www/assets/js/fileupload/jquery.fileupload-ui.js
      27.99K 100%   67.66kB/s    0:00:00 (xfer#214, to-check=239/497)
www/assets/js/fileupload/jquery.fileupload.js
      42.37K 100%  101.92kB/s    0:00:00 (xfer#215, to-check=238/497)
www/assets/js/fileupload/jquery.iframe-transport.js
       8.09K 100%   19.46kB/s    0:00:00 (xfer#216, to-check=237/497)
www/assets/js/fileupload/load-image.js
       1.28K 100%    3.07kB/s    0:00:00 (xfer#217, to-check=236/497)
www/assets/js/fileupload/locale.js
         781 100%    1.87kB/s    0:00:00 (xfer#218, to-check=235/497)
www/assets/js/fileupload/main.js
       1.89K 100%    4.53kB/s    0:00:00 (xfer#219, to-check=234/497)
www/assets/js/fileupload/tmpl.js
         971 100%    2.33kB/s    0:00:00 (xfer#220, to-check=233/497)
www/assets/js/fileupload/tmpl.min.js
         971 100%    2.33kB/s    0:00:00 (xfer#221, to-check=232/497)
www/assets/js/fileupload/cors/
www/assets/js/fileupload/cors/jquery.postmessage-transport.js
       4.00K 100%    9.60kB/s    0:00:00 (xfer#222, to-check=229/497)
www/assets/js/fileupload/cors/jquery.xdr-transport.js
       3.21K 100%    7.69kB/s    0:00:00 (xfer#223, to-check=228/497)
www/assets/js/fileupload/cors/result.html
         504 100%    1.21kB/s    0:00:00 (xfer#224, to-check=227/497)
www/assets/js/fileupload/vendor/
www/assets/js/fileupload/vendor/jquery.ui.widget.js
       7.28K 100%   17.43kB/s    0:00:00 (xfer#225, to-check=226/497)
www/profiles/
www/profiles/default_profile.png
       2.15K 100%    5.13kB/s    0:00:00 (xfer#226, to-check=225/497)
www/profiles/profile_1.jpg
       4.00K 100%    9.54kB/s    0:00:00 (xfer#227, to-check=224/497)
www/sparks/
www/sparks/curl/
www/sparks/curl/1.2.1/
www/sparks/curl/1.2.1/README.md
       2.40K 100%    5.72kB/s    0:00:00 (xfer#228, to-check=220/497)
www/sparks/curl/1.2.1/spark.info
          58 100%    0.14kB/s    0:00:00 (xfer#229, to-check=219/497)
www/sparks/curl/1.2.1/config/
www/sparks/curl/1.2.1/config/autoload.php
          99 100%    0.24kB/s    0:00:00 (xfer#230, to-check=216/497)
www/sparks/curl/1.2.1/libraries/
www/sparks/curl/1.2.1/libraries/Curl.php
       9.68K 100%   23.07kB/s    0:00:00 (xfer#231, to-check=215/497)
www/sparks/restclient/
www/sparks/restclient/2.1.0/
www/sparks/restclient/2.1.0/README.md
         862 100%    2.05kB/s    0:00:00 (xfer#232, to-check=213/497)
www/sparks/restclient/2.1.0/spark.info
          79 100%    0.19kB/s    0:00:00 (xfer#233, to-check=212/497)
www/sparks/restclient/2.1.0/config/
www/sparks/restclient/2.1.0/config/autoload.php
          95 100%    0.23kB/s    0:00:00 (xfer#234, to-check=209/497)
www/sparks/restclient/2.1.0/libraries/
www/sparks/restclient/2.1.0/libraries/Rest.php
       8.22K 100%   19.54kB/s    0:00:00 (xfer#235, to-check=208/497)
www/sparks/restclient/2.1.0/libraries/index.html
         114 100%    0.27kB/s    0:00:00 (xfer#236, to-check=207/497)
www/system/
www/system/.htaccess
          13 100%    0.03kB/s    0:00:00 (xfer#237, to-check=206/497)
www/system/index.html
         114 100%    0.27kB/s    0:00:00 (xfer#238, to-check=205/497)
www/system/core/
www/system/core/Benchmark.php
       2.95K 100%    6.97kB/s    0:00:00 (xfer#239, to-check=198/497)
www/system/core/CodeIgniter.php
      11.39K 100%   26.94kB/s    0:00:00 (xfer#240, to-check=197/497)
www/system/core/Common.php
      13.42K 100%   31.65kB/s    0:00:00 (xfer#241, to-check=196/497)
www/system/core/Config.php
       8.16K 100%   19.25kB/s    0:00:00 (xfer#242, to-check=195/497)
www/system/core/Controller.php
       1.57K 100%    3.69kB/s    0:00:00 (xfer#243, to-check=194/497)
www/system/core/Exceptions.php
       4.70K 100%   11.05kB/s    0:00:00 (xfer#244, to-check=193/497)
www/system/core/Hooks.php
       4.70K 100%   11.03kB/s    0:00:00 (xfer#245, to-check=192/497)
www/system/core/Input.php
      18.43K 100%   43.26kB/s    0:00:00 (xfer#246, to-check=191/497)
www/system/core/Lang.php
       3.63K 100%    8.53kB/s    0:00:00 (xfer#247, to-check=190/497)
www/system/core/Loader.php
      30.58K 100%   71.61kB/s    0:00:00 (xfer#248, to-check=189/497)
www/system/core/Model.php
       1.19K 100%    2.79kB/s    0:00:00 (xfer#249, to-check=188/497)
www/system/core/Output.php
      12.94K 100%   30.22kB/s    0:00:00 (xfer#250, to-check=187/497)
www/system/core/Router.php
      12.39K 100%   28.96kB/s    0:00:00 (xfer#251, to-check=186/497)
www/system/core/Security.php
      21.92K 100%   51.09kB/s    0:00:00 (xfer#252, to-check=185/497)
www/system/core/URI.php
      14.44K 100%   33.58kB/s    0:00:00 (xfer#253, to-check=184/497)
www/system/core/Utf8.php
       3.58K 100%    8.33kB/s    0:00:00 (xfer#254, to-check=183/497)
www/system/core/index.html
         114 100%    0.27kB/s    0:00:00 (xfer#255, to-check=182/497)
www/system/database/
www/system/database/DB.php
       4.19K 100%    9.74kB/s    0:00:00 (xfer#256, to-check=181/497)
www/system/database/DB_active_rec.php
      42.98K 100%   99.69kB/s    0:00:00 (xfer#257, to-check=180/497)
www/system/database/DB_cache.php
       4.38K 100%   10.13kB/s    0:00:00 (xfer#258, to-check=179/497)
www/system/database/DB_driver.php
      32.65K 100%   75.55kB/s    0:00:00 (xfer#259, to-check=178/497)
www/system/database/DB_forge.php
       7.45K 100%   17.19kB/s    0:00:00 (xfer#260, to-check=177/497)
www/system/database/DB_result.php
       9.02K 100%   20.82kB/s    0:00:00 (xfer#261, to-check=176/497)
www/system/database/DB_utility.php
       9.80K 100%   22.58kB/s    0:00:00 (xfer#262, to-check=175/497)
www/system/database/index.html
         114 100%    0.26kB/s    0:00:00 (xfer#263, to-check=174/497)
www/system/database/drivers/
www/system/database/drivers/index.html
         114 100%    0.26kB/s    0:00:00 (xfer#264, to-check=172/497)
www/system/database/drivers/cubrid/
www/system/database/drivers/cubrid/cubrid_driver.php
      17.89K 100%   41.11kB/s    0:00:00 (xfer#265, to-check=161/497)
www/system/database/drivers/cubrid/cubrid_forge.php
       7.06K 100%   16.18kB/s    0:00:00 (xfer#266, to-check=160/497)
www/system/database/drivers/cubrid/cubrid_result.php
       4.51K 100%   10.33kB/s    0:00:00 (xfer#267, to-check=159/497)
www/system/database/drivers/cubrid/cubrid_utility.php
       2.87K 100%    6.58kB/s    0:00:00 (xfer#268, to-check=158/497)
www/system/database/drivers/cubrid/index.html
         114 100%    0.26kB/s    0:00:00 (xfer#269, to-check=157/497)
www/system/database/drivers/mssql/
www/system/database/drivers/mssql/index.html
         114 100%    0.26kB/s    0:00:00 (xfer#270, to-check=156/497)
www/system/database/drivers/mssql/mssql_driver.php
      14.84K 100%   33.93kB/s    0:00:00 (xfer#271, to-check=155/497)
www/system/database/drivers/mssql/mssql_forge.php
       5.79K 100%   13.22kB/s    0:00:00 (xfer#272, to-check=154/497)
www/system/database/drivers/mssql/mssql_result.php
       3.37K 100%    7.70kB/s    0:00:00 (xfer#273, to-check=153/497)
www/system/database/drivers/mssql/mssql_utility.php
       1.98K 100%    4.51kB/s    0:00:00 (xfer#274, to-check=152/497)
www/system/database/drivers/mysql/
www/system/database/drivers/mysql/index.html
         114 100%    0.26kB/s    0:00:00 (xfer#275, to-check=151/497)
www/system/database/drivers/mysql/mysql_driver.php
      17.37K 100%   39.54kB/s    0:00:00 (xfer#276, to-check=150/497)
www/system/database/drivers/mysql/mysql_forge.php
       6.44K 100%   14.66kB/s    0:00:00 (xfer#277, to-check=149/497)
www/system/database/drivers/mysql/mysql_result.php
       3.62K 100%    8.23kB/s    0:00:00 (xfer#278, to-check=148/497)
www/system/database/drivers/mysql/mysql_utility.php
       4.61K 100%   10.47kB/s    0:00:00 (xfer#279, to-check=147/497)
www/system/database/drivers/mysqli/
www/system/database/drivers/mysqli/index.html
         114 100%    0.26kB/s    0:00:00 (xfer#280, to-check=146/497)
www/system/database/drivers/mysqli/mysqli_driver.php
      17.41K 100%   39.45kB/s    0:00:00 (xfer#281, to-check=145/497)
www/system/database/drivers/mysqli/mysqli_forge.php
       6.10K 100%   13.83kB/s    0:00:00 (xfer#282, to-check=144/497)
www/system/database/drivers/mysqli/mysqli_result.php
       3.64K 100%    8.23kB/s    0:00:00 (xfer#283, to-check=143/497)
www/system/database/drivers/mysqli/mysqli_utility.php
       1.98K 100%    4.48kB/s    0:00:00 (xfer#284, to-check=142/497)
www/system/database/drivers/oci8/
www/system/database/drivers/oci8/index.html
         114 100%    0.26kB/s    0:00:00 (xfer#285, to-check=141/497)
www/system/database/drivers/oci8/oci8_driver.php
      18.55K 100%   41.83kB/s    0:00:00 (xfer#286, to-check=140/497)
www/system/database/drivers/oci8/oci8_forge.php
       5.61K 100%   12.65kB/s    0:00:00 (xfer#287, to-check=139/497)
www/system/database/drivers/oci8/oci8_result.php
       4.49K 100%   10.11kB/s    0:00:00 (xfer#288, to-check=138/497)
www/system/database/drivers/oci8/oci8_utility.php
       1.93K 100%    4.34kB/s    0:00:00 (xfer#289, to-check=137/497)
www/system/database/drivers/odbc/
www/system/database/drivers/odbc/index.html
         114 100%    0.26kB/s    0:00:00 (xfer#290, to-check=136/497)
www/system/database/drivers/odbc/odbc_driver.php
      13.89K 100%   31.19kB/s    0:00:00 (xfer#291, to-check=135/497)
www/system/database/drivers/odbc/odbc_forge.php
       6.12K 100%   13.73kB/s    0:00:00 (xfer#292, to-check=134/497)
www/system/database/drivers/odbc/odbc_result.php
       4.59K 100%   10.31kB/s    0:00:00 (xfer#293, to-check=133/497)
www/system/database/drivers/odbc/odbc_utility.php
       2.26K 100%    5.07kB/s    0:00:00 (xfer#294, to-check=132/497)
www/system/database/drivers/pdo/
www/system/database/drivers/pdo/index.html
         114 100%    0.26kB/s    0:00:00 (xfer#295, to-check=131/497)
www/system/database/drivers/pdo/pdo_driver.php
      17.61K 100%   39.43kB/s    0:00:00 (xfer#296, to-check=130/497)
www/system/database/drivers/pdo/pdo_forge.php
       6.09K 100%   13.62kB/s    0:00:00 (xfer#297, to-check=129/497)
www/system/database/drivers/pdo/pdo_result.php
       3.51K 100%    7.84kB/s    0:00:00 (xfer#298, to-check=128/497)
www/system/database/drivers/pdo/pdo_utility.php
       2.24K 100%    5.00kB/s    0:00:00 (xfer#299, to-check=127/497)
www/system/database/drivers/postgre/
www/system/database/drivers/postgre/index.html
         114 100%    0.25kB/s    0:00:00 (xfer#300, to-check=126/497)
www/system/database/drivers/postgre/postgre_driver.php
      15.51K 100%   34.58kB/s    0:00:00 (xfer#301, to-check=125/497)
www/system/database/drivers/postgre/postgre_forge.php
       7.35K 100%   16.35kB/s    0:00:00 (xfer#302, to-check=124/497)
www/system/database/drivers/postgre/postgre_result.php
       3.44K 100%    7.65kB/s    0:00:00 (xfer#303, to-check=123/497)
www/system/database/drivers/postgre/postgre_utility.php
       1.85K 100%    4.13kB/s    0:00:00 (xfer#304, to-check=122/497)
www/system/database/drivers/sqlite/
www/system/database/drivers/sqlite/index.html
         114 100%    0.25kB/s    0:00:00 (xfer#305, to-check=121/497)
www/system/database/drivers/sqlite/sqlite_driver.php
      14.05K 100%   31.27kB/s    0:00:00 (xfer#306, to-check=120/497)
www/system/database/drivers/sqlite/sqlite_forge.php
       6.30K 100%   13.99kB/s    0:00:00 (xfer#307, to-check=119/497)
www/system/database/drivers/sqlite/sqlite_result.php
       3.55K 100%    7.88kB/s    0:00:00 (xfer#308, to-check=118/497)
www/system/database/drivers/sqlite/sqlite_utility.php
       2.15K 100%    4.77kB/s    0:00:00 (xfer#309, to-check=117/497)
www/system/database/drivers/sqlsrv/
www/system/database/drivers/sqlsrv/index.html
         114 100%    0.25kB/s    0:00:00 (xfer#310, to-check=116/497)
www/system/database/drivers/sqlsrv/sqlsrv_driver.php
      13.54K 100%   29.99kB/s    0:00:00 (xfer#311, to-check=115/497)
www/system/database/drivers/sqlsrv/sqlsrv_forge.php
       5.79K 100%   12.83kB/s    0:00:00 (xfer#312, to-check=114/497)
www/system/database/drivers/sqlsrv/sqlsrv_result.php
       3.42K 100%    7.56kB/s    0:00:00 (xfer#313, to-check=113/497)
www/system/database/drivers/sqlsrv/sqlsrv_utility.php
       1.98K 100%    4.37kB/s    0:00:00 (xfer#314, to-check=112/497)
www/system/fonts/
www/system/fonts/index.html
         114 100%    0.25kB/s    0:00:00 (xfer#315, to-check=111/497)
www/system/fonts/texb.ttf
     143.83K 100%  315.64kB/s    0:00:00 (xfer#316, to-check=110/497)
www/system/helpers/
www/system/helpers/array_helper.php
       2.51K 100%    5.49kB/s    0:00:00 (xfer#317, to-check=109/497)
www/system/helpers/captcha_helper.php
       6.17K 100%   13.51kB/s    0:00:00 (xfer#318, to-check=108/497)
www/system/helpers/cookie_helper.php
       2.59K 100%    5.67kB/s    0:00:00 (xfer#319, to-check=107/497)
www/system/helpers/date_helper.php
      12.97K 100%   28.34kB/s    0:00:00 (xfer#320, to-check=106/497)
www/system/helpers/directory_helper.php
       2.06K 100%    4.50kB/s    0:00:00 (xfer#321, to-check=105/497)
www/system/helpers/download_helper.php
       2.75K 100%    5.99kB/s    0:00:00 (xfer#322, to-check=104/497)
www/system/helpers/email_helper.php
       1.48K 100%    3.23kB/s    0:00:00 (xfer#323, to-check=103/497)
www/system/helpers/file_helper.php
      11.38K 100%   24.82kB/s    0:00:00 (xfer#324, to-check=102/497)
www/system/helpers/form_helper.php
      21.77K 100%   47.35kB/s    0:00:00 (xfer#325, to-check=101/497)
www/system/helpers/html_helper.php
       8.80K 100%   19.13kB/s    0:00:00 (xfer#326, to-check=100/497)
www/system/helpers/index.html
         114 100%    0.25kB/s    0:00:00 (xfer#327, to-check=99/497)
www/system/helpers/inflector_helper.php
       5.37K 100%   11.54kB/s    0:00:00 (xfer#328, to-check=98/497)
www/system/helpers/language_helper.php
       1.41K 100%    3.02kB/s    0:00:00 (xfer#329, to-check=97/497)
www/system/helpers/number_helper.php
       1.86K 100%    3.99kB/s    0:00:00 (xfer#330, to-check=96/497)
www/system/helpers/path_helper.php
       1.78K 100%    3.82kB/s    0:00:00 (xfer#331, to-check=95/497)
www/system/helpers/security_helper.php
       2.67K 100%    5.74kB/s    0:00:00 (xfer#332, to-check=94/497)
www/system/helpers/smiley_helper.php
       6.47K 100%   13.85kB/s    0:00:00 (xfer#333, to-check=93/497)
www/system/helpers/string_helper.php
       6.43K 100%   13.78kB/s    0:00:00 (xfer#334, to-check=92/497)
www/system/helpers/text_helper.php
      13.13K 100%   28.07kB/s    0:00:00 (xfer#335, to-check=91/497)
www/system/helpers/typography_helper.php
       2.24K 100%    4.78kB/s    0:00:00 (xfer#336, to-check=90/497)
www/system/helpers/url_helper.php
      12.36K 100%   26.35kB/s    0:00:00 (xfer#337, to-check=89/497)
www/system/helpers/xml_helper.php
       1.79K 100%    3.81kB/s    0:00:00 (xfer#338, to-check=88/497)
www/system/language/
www/system/language/index.html
         114 100%    0.24kB/s    0:00:00 (xfer#339, to-check=87/497)
www/system/language/english/
www/system/language/english/calendar_lang.php
       1.44K 100%    3.06kB/s    0:00:00 (xfer#340, to-check=84/497)
www/system/language/english/date_lang.php
       3.18K 100%    6.76kB/s    0:00:00 (xfer#341, to-check=83/497)
www/system/language/english/db_lang.php
       2.27K 100%    4.84kB/s    0:00:00 (xfer#342, to-check=82/497)
www/system/language/english/email_lang.php
       1.71K 100%    3.63kB/s    0:00:00 (xfer#343, to-check=81/497)
www/system/language/english/form_validation_lang.php
       1.82K 100%    3.86kB/s    0:00:00 (xfer#344, to-check=80/497)
www/system/language/english/ftp_lang.php
       1.28K 100%    2.73kB/s    0:00:00 (xfer#345, to-check=79/497)
www/system/language/english/imglib_lang.php
       2.01K 100%    4.27kB/s    0:00:00 (xfer#346, to-check=78/497)
www/system/language/english/index.html
         114 100%    0.24kB/s    0:00:00 (xfer#347, to-check=77/497)
www/system/language/english/migration_lang.php
         715 100%    1.52kB/s    0:00:00 (xfer#348, to-check=76/497)
www/system/language/english/number_lang.php
         249 100%    0.53kB/s    0:00:00 (xfer#349, to-check=75/497)
www/system/language/english/profiler_lang.php
       1.12K 100%    2.37kB/s    0:00:00 (xfer#350, to-check=74/497)
www/system/language/english/unit_test_lang.php
         808 100%    1.71kB/s    0:00:00 (xfer#351, to-check=73/497)
www/system/language/english/upload_lang.php
       1.62K 100%    3.43kB/s    0:00:00 (xfer#352, to-check=72/497)
www/system/language/french/
www/system/language/french/calendar_lang.php
       1.44K 100%    3.04kB/s    0:00:00 (xfer#353, to-check=71/497)
www/system/language/french/date_lang.php
       3.18K 100%    6.72kB/s    0:00:00 (xfer#354, to-check=70/497)
www/system/language/french/db_lang.php
       2.27K 100%    4.80kB/s    0:00:00 (xfer#355, to-check=69/497)
www/system/language/french/email_lang.php
       1.71K 100%    3.61kB/s    0:00:00 (xfer#356, to-check=68/497)
www/system/language/french/form_validation_lang.php
       2.00K 100%    4.22kB/s    0:00:00 (xfer#357, to-check=67/497)
www/system/language/french/ftp_lang.php
       1.28K 100%    2.71kB/s    0:00:00 (xfer#358, to-check=66/497)
www/system/language/french/imglib_lang.php
       2.01K 100%    4.24kB/s    0:00:00 (xfer#359, to-check=65/497)
www/system/language/french/index.html
         114 100%    0.24kB/s    0:00:00 (xfer#360, to-check=64/497)
www/system/language/french/migration_lang.php
         715 100%    1.50kB/s    0:00:00 (xfer#361, to-check=63/497)
www/system/language/french/number_lang.php
         249 100%    0.52kB/s    0:00:00 (xfer#362, to-check=62/497)
www/system/language/french/profiler_lang.php
       1.12K 100%    2.35kB/s    0:00:00 (xfer#363, to-check=61/497)
www/system/language/french/unit_test_lang.php
         808 100%    1.70kB/s    0:00:00 (xfer#364, to-check=60/497)
www/system/language/french/upload_lang.php
       1.62K 100%    3.40kB/s    0:00:00 (xfer#365, to-check=59/497)
www/system/libraries/
www/system/libraries/Calendar.php
      12.67K 100%   26.55kB/s    0:00:00 (xfer#366, to-check=58/497)
www/system/libraries/Cart.php
      15.07K 100%   31.58kB/s    0:00:00 (xfer#367, to-check=57/497)
www/system/libraries/Driver.php
       5.42K 100%   11.32kB/s    0:00:00 (xfer#368, to-check=56/497)
www/system/libraries/Email.php
      47.97K 100%   99.87kB/s    0:00:00 (xfer#369, to-check=55/497)
www/system/libraries/Encrypt.php
      11.52K 100%   23.99kB/s    0:00:00 (xfer#370, to-check=54/497)
www/system/libraries/Form_validation.php
      29.59K 100%   61.49kB/s    0:00:00 (xfer#371, to-check=53/497)
www/system/libraries/Ftp.php
      12.57K 100%   26.06kB/s    0:00:00 (xfer#372, to-check=52/497)
www/system/libraries/Image_lib.php
      37.34K 100%   77.09kB/s    0:00:00 (xfer#373, to-check=51/497)
www/system/libraries/Javascript.php
      20.12K 100%   41.53kB/s    0:00:00 (xfer#374, to-check=50/497)
www/system/libraries/Log.php
       2.70K 100%    5.55kB/s    0:00:00 (xfer#375, to-check=49/497)
www/system/libraries/Migration.php
       8.23K 100%   16.95kB/s    0:00:00 (xfer#376, to-check=48/497)
www/system/libraries/Pagination.php
       9.05K 100%   18.61kB/s    0:00:00 (xfer#377, to-check=47/497)
www/system/libraries/Parser.php
       4.43K 100%    9.10kB/s    0:00:00 (xfer#378, to-check=46/497)
www/system/libraries/Profiler.php
      19.28K 100%   39.55kB/s    0:00:00 (xfer#379, to-check=45/497)
www/system/libraries/Session.php
      19.22K 100%   38.45kB/s    0:00:00 (xfer#380, to-check=44/497)
www/system/libraries/Sha1.php
       5.00K 100%   10.00kB/s    0:00:00 (xfer#381, to-check=43/497)
www/system/libraries/Table.php
      11.37K 100%   22.70kB/s    0:00:00 (xfer#382, to-check=42/497)
www/system/libraries/Trackback.php
      11.99K 100%   23.95kB/s    0:00:00 (xfer#383, to-check=41/497)
www/system/libraries/Typography.php
      12.72K 100%   25.40kB/s    0:00:00 (xfer#384, to-check=40/497)
www/system/libraries/Unit_test.php
       8.20K 100%   16.34kB/s    0:00:00 (xfer#385, to-check=39/497)
www/system/libraries/Upload.php
      27.55K 100%   54.79kB/s    0:00:00 (xfer#386, to-check=38/497)
www/system/libraries/User_agent.php
      10.51K 100%   20.86kB/s    0:00:00 (xfer#387, to-check=37/497)
www/system/libraries/Xmlrpc.php
      33.57K 100%   66.49kB/s    0:00:00 (xfer#388, to-check=36/497)
www/system/libraries/Xmlrpcs.php
      15.55K 100%   30.74kB/s    0:00:00 (xfer#389, to-check=35/497)
www/system/libraries/Zip.php
      10.16K 100%   20.09kB/s    0:00:00 (xfer#390, to-check=34/497)
www/system/libraries/index.html
         114 100%    0.23kB/s    0:00:00 (xfer#391, to-check=33/497)
www/system/libraries/Cache/
www/system/libraries/Cache/Cache.php
       4.68K 100%    9.23kB/s    0:00:00 (xfer#392, to-check=30/497)
www/system/libraries/Cache/drivers/
www/system/libraries/Cache/drivers/Cache_apc.php
       3.31K 100%    6.52kB/s    0:00:00 (xfer#393, to-check=28/497)
www/system/libraries/Cache/drivers/Cache_dummy.php
       2.66K 100%    5.24kB/s    0:00:00 (xfer#394, to-check=27/497)
www/system/libraries/Cache/drivers/Cache_file.php
       4.15K 100%    8.17kB/s    0:00:00 (xfer#395, to-check=26/497)
www/system/libraries/Cache/drivers/Cache_memcached.php
       5.03K 100%    9.90kB/s    0:00:00 (xfer#396, to-check=25/497)
www/system/libraries/javascript/
www/system/libraries/javascript/Jquery.php
      24.19K 100%   47.54kB/s    0:00:00 (xfer#397, to-check=24/497)
www/tools/
www/tools/README.md
       1.04K 100%    2.05kB/s    0:00:00 (xfer#398, to-check=23/497)
www/tools/spark
         746 100%    1.46kB/s    0:00:00 (xfer#399, to-check=22/497)
www/tools/lib/
www/tools/lib/spark/
www/tools/lib/spark/sources
          68 100%    0.13kB/s    0:00:00 (xfer#400, to-check=18/497)
www/tools/lib/spark/spark_cli.php
       8.74K 100%   17.14kB/s    0:00:00 (xfer#401, to-check=17/497)
www/tools/lib/spark/spark_exception.php
          52 100%    0.10kB/s    0:00:00 (xfer#402, to-check=16/497)
www/tools/lib/spark/spark_source.php
       3.47K 100%    6.79kB/s    0:00:00 (xfer#403, to-check=15/497)
www/tools/lib/spark/spark_type.php
       4.82K 100%    9.43kB/s    0:00:00 (xfer#404, to-check=14/497)
www/tools/lib/spark/spark_utils.php
       2.66K 100%    5.20kB/s    0:00:00 (xfer#405, to-check=13/497)
www/tools/lib/spark/spark_types/
www/tools/lib/spark/spark_types/git_spark.php
       1.27K 100%    2.48kB/s    0:00:00 (xfer#406, to-check=11/497)
www/tools/lib/spark/spark_types/hg_spark.php
       1.04K 100%    2.04kB/s    0:00:00 (xfer#407, to-check=10/497)
www/tools/lib/spark/spark_types/zip_spark.php
       1.27K 100%    2.49kB/s    0:00:00 (xfer#408, to-check=9/497)
www/tools/test/
www/tools/test/install_test.php
       1.87K 100%    3.65kB/s    0:00:00 (xfer#409, to-check=8/497)
www/tools/test/phpunit.xml
         250 100%    0.49kB/s    0:00:00 (xfer#410, to-check=7/497)
www/tools/test/remove_test.php
       2.43K 100%    4.74kB/s    0:00:00 (xfer#411, to-check=6/497)
www/tools/test/search_test.php
         381 100%    0.74kB/s    0:00:00 (xfer#412, to-check=5/497)
www/tools/test/version_test.php
       1.04K 100%    2.03kB/s    0:00:00 (xfer#413, to-check=4/497)
www/tools/test/lib/
www/tools/test/lib/bootstrap.php
         887 100%    1.73kB/s    0:00:00 (xfer#414, to-check=2/497)
www/tools/test/lib/test-sparks/
www/tools/test/lib/test-sparks/.gitkeep
           0 100%    0.00kB/s    0:00:00 (xfer#415, to-check=0/497)

sent 12.25M bytes  received 8.22K bytes  24.52M bytes/sec
total size is 12.22M  speedup is 1.00
sending incremental file list
./
.gitignore
           6 100%    0.00kB/s    0:00:00 (xfer#1, to-check=82/84)
config.yaml
         846 100%  826.17kB/s    0:00:00 (xfer#2, to-check=81/84)
copyright
         743 100%  725.59kB/s    0:00:00 (xfer#3, to-check=80/84)
local_config.pkl
         368 100%  359.38kB/s    0:00:00 (xfer#4, to-check=79/84)
metadata.yaml
         300 100%  292.97kB/s    0:00:00 (xfer#5, to-check=78/84)
revision
           3 100%    2.93kB/s    0:00:00 (xfer#6, to-check=77/84)
setup.py
       2.43K 100%    2.31MB/s    0:00:00 (xfer#7, to-check=76/84)
setup.sh
       1.81K 100%    1.73MB/s    0:00:00 (xfer#8, to-check=75/84)
hooks/
hooks/config-changed
          69 100%   67.38kB/s    0:00:00 (xfer#9, to-check=71/84)
hooks/install
          73 100%   71.29kB/s    0:00:00 (xfer#10, to-check=70/84)
hooks/peer-relation-broken
          75 100%   73.24kB/s    0:00:00 (xfer#11, to-check=69/84)
hooks/peer-relation-changed
          76 100%   74.22kB/s    0:00:00 (xfer#12, to-check=68/84)
hooks/peer-relation-joined
          75 100%   73.24kB/s    0:00:00 (xfer#13, to-check=67/84)
hooks/start
          60 100%   58.59kB/s    0:00:00 (xfer#14, to-check=66/84)
hooks/stop
          59 100%   57.62kB/s    0:00:00 (xfer#15, to-check=65/84)
hooks/storage-relation-broken
          78 100%   76.17kB/s    0:00:00 (xfer#16, to-check=64/84)
hooks/storage-relation-departed
          80 100%   78.12kB/s    0:00:00 (xfer#17, to-check=63/84)
hooks/storage-relation-joined
          78 100%   76.17kB/s    0:00:00 (xfer#18, to-check=62/84)
hooks/uninstall
          64 100%   62.50kB/s    0:00:00 (xfer#19, to-check=61/84)
oscied_lib/
oscied_lib/.gitignore
          50 100%   48.83kB/s    0:00:00 (xfer#20, to-check=60/84)
oscied_lib/Callback.py
       2.72K 100%    2.60MB/s    0:00:00 (xfer#21, to-check=59/84)
oscied_lib/CharmConfig.py
       2.18K 100%    2.08MB/s    0:00:00 (xfer#22, to-check=58/84)
oscied_lib/CharmConfig_Storage.py
       5.68K 100%    5.41MB/s    0:00:00 (xfer#23, to-check=57/84)
oscied_lib/CharmHooks.py
      12.55K 100%   11.97MB/s    0:00:00 (xfer#24, to-check=56/84)
oscied_lib/CharmHooks_Storage.py
       7.12K 100%    2.26MB/s    0:00:00 (xfer#25, to-check=55/84)
oscied_lib/CharmHooks_Subordinate.py
       4.92K 100%    1.57MB/s    0:00:00 (xfer#26, to-check=54/84)
oscied_lib/CharmHooks_Website.py
       3.71K 100%    1.18MB/s    0:00:00 (xfer#27, to-check=53/84)
oscied_lib/Media.py
       4.37K 100%    1.39MB/s    0:00:00 (xfer#28, to-check=52/84)
oscied_lib/Orchestra.py
      30.96K 100%    7.38MB/s    0:00:00 (xfer#29, to-check=51/84)
oscied_lib/OrchestraConfig.py
       4.37K 100%    1.04MB/s    0:00:00 (xfer#30, to-check=50/84)
oscied_lib/OrchestraHooks.py
      13.21K 100%    3.15MB/s    0:00:00 (xfer#31, to-check=49/84)
oscied_lib/OsciedDBModel.py
       1.82K 100%  444.58kB/s    0:00:00 (xfer#32, to-check=48/84)
oscied_lib/PublishTask.py
       3.66K 100%  892.82kB/s    0:00:00 (xfer#33, to-check=47/84)
oscied_lib/Publisher.py
       4.97K 100%    1.19MB/s    0:00:00 (xfer#34, to-check=46/84)
oscied_lib/PublisherConfig.py
       3.12K 100%  762.70kB/s    0:00:00 (xfer#35, to-check=45/84)
oscied_lib/PublisherHooks.py
       6.93K 100%    1.32MB/s    0:00:00 (xfer#36, to-check=44/84)
oscied_lib/Storage.py
       3.72K 100%  726.17kB/s    0:00:00 (xfer#37, to-check=43/84)
oscied_lib/StorageConfig.py
       2.22K 100%  433.01kB/s    0:00:00 (xfer#38, to-check=42/84)
oscied_lib/StorageHooks.py
      11.98K 100%    2.29MB/s    0:00:00 (xfer#39, to-check=41/84)
oscied_lib/Transform.py
      13.66K 100%    2.17MB/s    0:00:00 (xfer#40, to-check=40/84)
oscied_lib/TransformConfig.py
       2.49K 100%  405.60kB/s    0:00:00 (xfer#41, to-check=39/84)
oscied_lib/TransformHooks.py
       5.54K 100%  901.69kB/s    0:00:00 (xfer#42, to-check=38/84)
oscied_lib/TransformProfile.py
       2.75K 100%  447.43kB/s    0:00:00 (xfer#43, to-check=37/84)
oscied_lib/TransformTask.py
       5.49K 100%  893.88kB/s    0:00:00 (xfer#44, to-check=36/84)
oscied_lib/User.py
       4.18K 100%  680.01kB/s    0:00:00 (xfer#45, to-check=35/84)
oscied_lib/WebuiConfig.py
       3.66K 100%  595.21kB/s    0:00:00 (xfer#46, to-check=34/84)
oscied_lib/WebuiHooks.py
      10.33K 100%    1.64MB/s    0:00:00 (xfer#47, to-check=33/84)
oscied_lib/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#48, to-check=32/84)
pyutils/
pyutils/.gitignore
          48 100%    7.81kB/s    0:00:00 (xfer#49, to-check=31/84)
pyutils/.travis.yml
         331 100%   53.87kB/s    0:00:00 (xfer#50, to-check=30/84)
pyutils/AUTHORS
          14 100%    2.28kB/s    0:00:00 (xfer#51, to-check=29/84)
pyutils/COPYING
      35.15K 100%    4.19MB/s    0:00:00 (xfer#52, to-check=28/84)
pyutils/README.rst
       1.39K 100%  169.56kB/s    0:00:00 (xfer#53, to-check=27/84)
pyutils/setup.cfg
         196 100%   23.93kB/s    0:00:00 (xfer#54, to-check=26/84)
pyutils/setup.py
       3.10K 100%  378.91kB/s    0:00:00 (xfer#55, to-check=25/84)
pyutils/pyutils/
pyutils/pyutils/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#56, to-check=22/84)
pyutils/pyutils/py_crypto.py
       1.89K 100%  230.10kB/s    0:00:00 (xfer#57, to-check=21/84)
pyutils/pyutils/py_datetime.py
       3.07K 100%  375.24kB/s    0:00:00 (xfer#58, to-check=20/84)
pyutils/pyutils/py_exception.py
       1.34K 100%  163.82kB/s    0:00:00 (xfer#59, to-check=19/84)
pyutils/pyutils/py_ffmpeg.py
       6.84K 100%  834.84kB/s    0:00:00 (xfer#60, to-check=18/84)
pyutils/pyutils/py_filesystem.py
      10.20K 100%    1.22MB/s    0:00:00 (xfer#61, to-check=17/84)
pyutils/pyutils/py_flask.py
       3.03K 100%  329.10kB/s    0:00:00 (xfer#62, to-check=16/84)
pyutils/pyutils/py_juju.py
      10.17K 100%  993.55kB/s    0:00:00 (xfer#63, to-check=15/84)
pyutils/pyutils/py_logging.py
       3.49K 100%  340.92kB/s    0:00:00 (xfer#64, to-check=14/84)
pyutils/pyutils/py_mock.py
       2.56K 100%  250.29kB/s    0:00:00 (xfer#65, to-check=13/84)
pyutils/pyutils/py_serialization.py
       6.85K 100%  669.04kB/s    0:00:00 (xfer#66, to-check=12/84)
pyutils/pyutils/py_subprocess.py
       5.48K 100%  535.45kB/s    0:00:00 (xfer#67, to-check=11/84)
pyutils/pyutils/py_unicode.py
       2.29K 100%  223.44kB/s    0:00:00 (xfer#68, to-check=10/84)
pyutils/pyutils/py_validation.py
       4.47K 100%  436.13kB/s    0:00:00 (xfer#69, to-check=9/84)
pyutils/pyutils/pyutils.py
       3.00K 100%  293.46kB/s    0:00:00 (xfer#70, to-check=8/84)
pyutils/pyutils/ming/
pyutils/pyutils/ming/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#71, to-check=6/84)
pyutils/pyutils/ming/extensions.py
       1.79K 100%  174.71kB/s    0:00:00 (xfer#72, to-check=5/84)
pyutils/pyutils/ming/schema.py
       4.22K 100%  374.38kB/s    0:00:00 (xfer#73, to-check=4/84)
pyutils/pyutils/ming/session.py
       1.47K 100%  130.50kB/s    0:00:00 (xfer#74, to-check=3/84)
pyutils/tests/
pyutils/tests/TestPyutils.py
       5.52K 100%  490.32kB/s    0:00:00 (xfer#75, to-check=2/84)
pyutils/tests/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#76, to-check=1/84)
pyutils/tests/unicode.csv
          49 100%    4.35kB/s    0:00:00 (xfer#77, to-check=0/84)

sent 308.65K bytes  received 1.50K bytes  620.30K bytes/sec
total size is 303.62K  speedup is 0.98
sending incremental file list
./
.gitignore
           6 100%    0.00kB/s    0:00:00 (xfer#1, to-check=85/87)
config.yaml
       1.65K 100%    1.58MB/s    0:00:00 (xfer#2, to-check=84/87)
copyright
         752 100%  734.38kB/s    0:00:00 (xfer#3, to-check=83/87)
gpac.tar.bz2
       8.55M 100%   40.99MB/s    0:00:00 (xfer#4, to-check=82/87)
local_config.pkl
         522 100%    2.56kB/s    0:00:00 (xfer#5, to-check=81/87)
metadata.yaml
         341 100%    1.67kB/s    0:00:00 (xfer#6, to-check=80/87)
revision
           2 100%    0.01kB/s    0:00:00 (xfer#7, to-check=79/87)
setup.py
       2.43K 100%   11.91kB/s    0:00:00 (xfer#8, to-check=78/87)
setup.sh
       1.81K 100%    8.90kB/s    0:00:00 (xfer#9, to-check=77/87)
hooks/
hooks/config-changed
          71 100%    0.35kB/s    0:00:00 (xfer#10, to-check=72/87)
hooks/install
          75 100%    0.37kB/s    0:00:00 (xfer#11, to-check=71/87)
hooks/start
          62 100%    0.30kB/s    0:00:00 (xfer#12, to-check=70/87)
hooks/stop
          61 100%    0.30kB/s    0:00:00 (xfer#13, to-check=69/87)
hooks/storage-relation-broken
          80 100%    0.39kB/s    0:00:00 (xfer#14, to-check=68/87)
hooks/storage-relation-changed
          81 100%    0.40kB/s    0:00:00 (xfer#15, to-check=67/87)
hooks/storage-relation-joined
          80 100%    0.39kB/s    0:00:00 (xfer#16, to-check=66/87)
hooks/transform-relation-broken
          84 100%    0.41kB/s    0:00:00 (xfer#17, to-check=65/87)
hooks/transform-relation-changed
          85 100%    0.42kB/s    0:00:00 (xfer#18, to-check=64/87)
hooks/transform-relation-joined
          84 100%    0.41kB/s    0:00:00 (xfer#19, to-check=63/87)
hooks/uninstall
          66 100%    0.32kB/s    0:00:00 (xfer#20, to-check=62/87)
oscied_lib/
oscied_lib/.gitignore
          50 100%    0.24kB/s    0:00:00 (xfer#21, to-check=61/87)
oscied_lib/Callback.py
       2.72K 100%   13.30kB/s    0:00:00 (xfer#22, to-check=60/87)
oscied_lib/CharmConfig.py
       2.18K 100%   10.66kB/s    0:00:00 (xfer#23, to-check=59/87)
oscied_lib/CharmConfig_Storage.py
       5.68K 100%   27.72kB/s    0:00:00 (xfer#24, to-check=58/87)
oscied_lib/CharmHooks.py
      12.55K 100%   60.68kB/s    0:00:00 (xfer#25, to-check=57/87)
oscied_lib/CharmHooks_Storage.py
       7.12K 100%   34.10kB/s    0:00:00 (xfer#26, to-check=56/87)
oscied_lib/CharmHooks_Subordinate.py
       4.92K 100%   23.46kB/s    0:00:00 (xfer#27, to-check=55/87)
oscied_lib/CharmHooks_Website.py
       3.71K 100%   17.65kB/s    0:00:00 (xfer#28, to-check=54/87)
oscied_lib/Media.py
       4.37K 100%   20.83kB/s    0:00:00 (xfer#29, to-check=53/87)
oscied_lib/Orchestra.py
      30.96K 100%  146.75kB/s    0:00:00 (xfer#30, to-check=52/87)
oscied_lib/OrchestraConfig.py
       4.37K 100%   20.70kB/s    0:00:00 (xfer#31, to-check=51/87)
oscied_lib/OrchestraHooks.py
      13.21K 100%   62.30kB/s    0:00:00 (xfer#32, to-check=50/87)
oscied_lib/OsciedDBModel.py
       1.82K 100%    8.59kB/s    0:00:00 (xfer#33, to-check=49/87)
oscied_lib/PublishTask.py
       3.66K 100%   17.25kB/s    0:00:00 (xfer#34, to-check=48/87)
oscied_lib/Publisher.py
       4.97K 100%   23.46kB/s    0:00:00 (xfer#35, to-check=47/87)
oscied_lib/PublisherConfig.py
       3.12K 100%   14.74kB/s    0:00:00 (xfer#36, to-check=46/87)
oscied_lib/PublisherHooks.py
       6.93K 100%   32.54kB/s    0:00:00 (xfer#37, to-check=45/87)
oscied_lib/Storage.py
       3.72K 100%   17.46kB/s    0:00:00 (xfer#38, to-check=44/87)
oscied_lib/StorageConfig.py
       2.22K 100%   10.41kB/s    0:00:00 (xfer#39, to-check=43/87)
oscied_lib/StorageHooks.py
      11.98K 100%   56.26kB/s    0:00:00 (xfer#40, to-check=42/87)
oscied_lib/Transform.py
      13.66K 100%   63.82kB/s    0:00:00 (xfer#41, to-check=41/87)
oscied_lib/TransformConfig.py
       2.49K 100%   11.64kB/s    0:00:00 (xfer#42, to-check=40/87)
oscied_lib/TransformHooks.py
       5.54K 100%   25.89kB/s    0:00:00 (xfer#43, to-check=39/87)
oscied_lib/TransformProfile.py
       2.75K 100%   12.78kB/s    0:00:00 (xfer#44, to-check=38/87)
oscied_lib/TransformTask.py
       5.49K 100%   25.54kB/s    0:00:00 (xfer#45, to-check=37/87)
oscied_lib/User.py
       4.18K 100%   19.43kB/s    0:00:00 (xfer#46, to-check=36/87)
oscied_lib/WebuiConfig.py
       3.66K 100%   17.01kB/s    0:00:00 (xfer#47, to-check=35/87)
oscied_lib/WebuiHooks.py
      10.33K 100%   48.05kB/s    0:00:00 (xfer#48, to-check=34/87)
oscied_lib/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#49, to-check=33/87)
pyutils/
pyutils/.gitignore
          48 100%    0.22kB/s    0:00:00 (xfer#50, to-check=32/87)
pyutils/.travis.yml
         331 100%    1.53kB/s    0:00:00 (xfer#51, to-check=31/87)
pyutils/AUTHORS
          14 100%    0.06kB/s    0:00:00 (xfer#52, to-check=30/87)
pyutils/COPYING
      35.15K 100%  161.14kB/s    0:00:00 (xfer#53, to-check=29/87)
pyutils/README.rst
       1.39K 100%    6.37kB/s    0:00:00 (xfer#54, to-check=28/87)
pyutils/setup.cfg
         196 100%    0.90kB/s    0:00:00 (xfer#55, to-check=27/87)
pyutils/setup.py
       3.10K 100%   14.23kB/s    0:00:00 (xfer#56, to-check=26/87)
pyutils/pyutils/
pyutils/pyutils/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#57, to-check=23/87)
pyutils/pyutils/py_crypto.py
       1.89K 100%    8.64kB/s    0:00:00 (xfer#58, to-check=22/87)
pyutils/pyutils/py_datetime.py
       3.07K 100%   14.09kB/s    0:00:00 (xfer#59, to-check=21/87)
pyutils/pyutils/py_exception.py
       1.34K 100%    6.15kB/s    0:00:00 (xfer#60, to-check=20/87)
pyutils/pyutils/py_ffmpeg.py
       6.84K 100%   31.36kB/s    0:00:00 (xfer#61, to-check=19/87)
pyutils/pyutils/py_filesystem.py
      10.20K 100%   46.76kB/s    0:00:00 (xfer#62, to-check=18/87)
pyutils/pyutils/py_flask.py
       3.03K 100%   13.84kB/s    0:00:00 (xfer#63, to-check=17/87)
pyutils/pyutils/py_juju.py
      10.17K 100%   45.79kB/s    0:00:00 (xfer#64, to-check=16/87)
pyutils/pyutils/py_logging.py
       3.49K 100%   15.71kB/s    0:00:00 (xfer#65, to-check=15/87)
pyutils/pyutils/py_mock.py
       2.56K 100%   11.53kB/s    0:00:00 (xfer#66, to-check=14/87)
pyutils/pyutils/py_serialization.py
       6.85K 100%   30.83kB/s    0:00:00 (xfer#67, to-check=13/87)
pyutils/pyutils/py_subprocess.py
       5.48K 100%   24.56kB/s    0:00:00 (xfer#68, to-check=12/87)
pyutils/pyutils/py_unicode.py
       2.29K 100%   10.25kB/s    0:00:00 (xfer#69, to-check=11/87)
pyutils/pyutils/py_validation.py
       4.47K 100%   20.01kB/s    0:00:00 (xfer#70, to-check=10/87)
pyutils/pyutils/pyutils.py
       3.00K 100%   13.46kB/s    0:00:00 (xfer#71, to-check=9/87)
pyutils/pyutils/ming/
pyutils/pyutils/ming/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#72, to-check=7/87)
pyutils/pyutils/ming/extensions.py
       1.79K 100%    8.01kB/s    0:00:00 (xfer#73, to-check=6/87)
pyutils/pyutils/ming/schema.py
       4.22K 100%   18.89kB/s    0:00:00 (xfer#74, to-check=5/87)
pyutils/pyutils/ming/session.py
       1.47K 100%    6.56kB/s    0:00:00 (xfer#75, to-check=4/87)
pyutils/tests/
pyutils/tests/TestPyutils.py
       5.52K 100%   24.63kB/s    0:00:00 (xfer#76, to-check=3/87)
pyutils/tests/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#77, to-check=2/87)
pyutils/tests/unicode.csv
          49 100%    0.22kB/s    0:00:00 (xfer#78, to-check=1/87)
templates/
templates/celeryconfig.py.template
       1.84K 100%    8.23kB/s    0:00:00 (xfer#79, to-check=0/87)

sent 8.87M bytes  received 1.54K bytes  5.91M bytes/sec
total size is 8.86M  speedup is 1.00
sending incremental file list
./
apache_mod_h264_streaming-2.2.7.tar.gz
     320.61K 100%   45.75MB/s    0:00:00 (xfer#1, to-check=86/88)
config.yaml
       2.26K 100%  315.71kB/s    0:00:00 (xfer#2, to-check=85/88)
copyright
         752 100%  104.91kB/s    0:00:00 (xfer#3, to-check=84/88)
get-dependencies.sh
         124 100%   17.30kB/s    0:00:00 (xfer#4, to-check=83/88)
local_config.pkl
         652 100%   90.96kB/s    0:00:00 (xfer#5, to-check=82/88)
metadata.yaml
         395 100%   55.11kB/s    0:00:00 (xfer#6, to-check=81/88)
revision
           2 100%    0.28kB/s    0:00:00 (xfer#7, to-check=80/88)
setup.py
       2.43K 100%  338.45kB/s    0:00:00 (xfer#8, to-check=79/88)
setup.sh
       1.81K 100%  253.07kB/s    0:00:00 (xfer#9, to-check=78/88)
hooks/
hooks/config-changed
          71 100%    9.91kB/s    0:00:00 (xfer#10, to-check=73/88)
hooks/install
          75 100%   10.46kB/s    0:00:00 (xfer#11, to-check=72/88)
hooks/publisher-relation-broken
          84 100%   11.72kB/s    0:00:00 (xfer#12, to-check=71/88)
hooks/publisher-relation-changed
          85 100%   11.86kB/s    0:00:00 (xfer#13, to-check=70/88)
hooks/publisher-relation-joined
          84 100%   11.72kB/s    0:00:00 (xfer#14, to-check=69/88)
hooks/start
          62 100%    8.65kB/s    0:00:00 (xfer#15, to-check=68/88)
hooks/stop
          61 100%    7.45kB/s    0:00:00 (xfer#16, to-check=67/88)
hooks/storage-relation-broken
          80 100%    9.77kB/s    0:00:00 (xfer#17, to-check=66/88)
hooks/storage-relation-changed
          81 100%    9.89kB/s    0:00:00 (xfer#18, to-check=65/88)
hooks/storage-relation-joined
          80 100%    9.77kB/s    0:00:00 (xfer#19, to-check=64/88)
hooks/uninstall
          66 100%    8.06kB/s    0:00:00 (xfer#20, to-check=63/88)
hooks/website-relation-joined
          80 100%    9.77kB/s    0:00:00 (xfer#21, to-check=62/88)
oscied_lib/
oscied_lib/.gitignore
          50 100%    6.10kB/s    0:00:00 (xfer#22, to-check=61/88)
oscied_lib/Callback.py
       2.72K 100%  332.40kB/s    0:00:00 (xfer#23, to-check=60/88)
oscied_lib/CharmConfig.py
       2.18K 100%  266.48kB/s    0:00:00 (xfer#24, to-check=59/88)
oscied_lib/CharmConfig_Storage.py
       5.68K 100%  693.12kB/s    0:00:00 (xfer#25, to-check=58/88)
oscied_lib/CharmHooks.py
      12.55K 100%    1.50MB/s    0:00:00 (xfer#26, to-check=57/88)
oscied_lib/CharmHooks_Storage.py
       7.12K 100%  632.37kB/s    0:00:00 (xfer#27, to-check=56/88)
oscied_lib/CharmHooks_Subordinate.py
       4.92K 100%  400.72kB/s    0:00:00 (xfer#28, to-check=55/88)
oscied_lib/CharmHooks_Website.py
       3.71K 100%  301.60kB/s    0:00:00 (xfer#29, to-check=54/88)
oscied_lib/Media.py
       4.37K 100%  355.88kB/s    0:00:00 (xfer#30, to-check=53/88)
oscied_lib/Orchestra.py
      30.96K 100%    2.11MB/s    0:00:00 (xfer#31, to-check=52/88)
oscied_lib/OrchestraConfig.py
       4.37K 100%  304.62kB/s    0:00:00 (xfer#32, to-check=51/88)
oscied_lib/OrchestraHooks.py
      13.21K 100%  921.11kB/s    0:00:00 (xfer#33, to-check=50/88)
oscied_lib/OsciedDBModel.py
       1.82K 100%  127.02kB/s    0:00:00 (xfer#34, to-check=49/88)
oscied_lib/PublishTask.py
       3.66K 100%  255.09kB/s    0:00:00 (xfer#35, to-check=48/88)
oscied_lib/Publisher.py
       4.97K 100%  346.82kB/s    0:00:00 (xfer#36, to-check=47/88)
oscied_lib/PublisherConfig.py
       3.12K 100%  217.91kB/s    0:00:00 (xfer#37, to-check=46/88)
oscied_lib/PublisherHooks.py
       6.93K 100%  451.17kB/s    0:00:00 (xfer#38, to-check=45/88)
oscied_lib/Storage.py
       3.72K 100%  242.06kB/s    0:00:00 (xfer#39, to-check=44/88)
oscied_lib/StorageConfig.py
       2.22K 100%  144.34kB/s    0:00:00 (xfer#40, to-check=43/88)
oscied_lib/StorageHooks.py
      11.98K 100%  780.08kB/s    0:00:00 (xfer#41, to-check=42/88)
oscied_lib/Transform.py
      13.66K 100%  741.05kB/s    0:00:00 (xfer#42, to-check=41/88)
oscied_lib/TransformConfig.py
       2.49K 100%  135.20kB/s    0:00:00 (xfer#43, to-check=40/88)
oscied_lib/TransformHooks.py
       5.54K 100%  300.56kB/s    0:00:00 (xfer#44, to-check=39/88)
oscied_lib/TransformProfile.py
       2.75K 100%  141.29kB/s    0:00:00 (xfer#45, to-check=38/88)
oscied_lib/TransformTask.py
       5.49K 100%  282.28kB/s    0:00:00 (xfer#46, to-check=37/88)
oscied_lib/User.py
       4.18K 100%  214.74kB/s    0:00:00 (xfer#47, to-check=36/88)
oscied_lib/WebuiConfig.py
       3.66K 100%  187.96kB/s    0:00:00 (xfer#48, to-check=35/88)
oscied_lib/WebuiHooks.py
      10.33K 100%  531.10kB/s    0:00:00 (xfer#49, to-check=34/88)
oscied_lib/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#50, to-check=33/88)
pyutils/
pyutils/.gitignore
          48 100%    2.34kB/s    0:00:00 (xfer#51, to-check=32/88)
pyutils/.travis.yml
         331 100%   16.16kB/s    0:00:00 (xfer#52, to-check=31/88)
pyutils/AUTHORS
          14 100%    0.68kB/s    0:00:00 (xfer#53, to-check=30/88)
pyutils/COPYING
      35.15K 100%    1.52MB/s    0:00:00 (xfer#54, to-check=29/88)
pyutils/README.rst
       1.39K 100%   61.66kB/s    0:00:00 (xfer#55, to-check=28/88)
pyutils/setup.cfg
         196 100%    8.70kB/s    0:00:00 (xfer#56, to-check=27/88)
pyutils/setup.py
       3.10K 100%  137.78kB/s    0:00:00 (xfer#57, to-check=26/88)
pyutils/pyutils/
pyutils/pyutils/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#58, to-check=23/88)
pyutils/pyutils/py_crypto.py
       1.89K 100%   83.67kB/s    0:00:00 (xfer#59, to-check=22/88)
pyutils/pyutils/py_datetime.py
       3.07K 100%  136.45kB/s    0:00:00 (xfer#60, to-check=21/88)
pyutils/pyutils/py_exception.py
       1.34K 100%   59.57kB/s    0:00:00 (xfer#61, to-check=20/88)
pyutils/pyutils/py_ffmpeg.py
       6.84K 100%  303.58kB/s    0:00:00 (xfer#62, to-check=19/88)
pyutils/pyutils/py_filesystem.py
      10.20K 100%  452.73kB/s    0:00:00 (xfer#63, to-check=18/88)
pyutils/pyutils/py_flask.py
       3.03K 100%  128.78kB/s    0:00:00 (xfer#64, to-check=17/88)
pyutils/pyutils/py_juju.py
      10.17K 100%  413.98kB/s    0:00:00 (xfer#65, to-check=16/88)
pyutils/pyutils/py_logging.py
       3.49K 100%  142.05kB/s    0:00:00 (xfer#66, to-check=15/88)
pyutils/pyutils/py_mock.py
       2.56K 100%  104.29kB/s    0:00:00 (xfer#67, to-check=14/88)
pyutils/pyutils/py_serialization.py
       6.85K 100%  278.77kB/s    0:00:00 (xfer#68, to-check=13/88)
pyutils/pyutils/py_subprocess.py
       5.48K 100%  223.10kB/s    0:00:00 (xfer#69, to-check=12/88)
pyutils/pyutils/py_unicode.py
       2.29K 100%   89.38kB/s    0:00:00 (xfer#70, to-check=11/88)
pyutils/pyutils/py_validation.py
       4.47K 100%  174.45kB/s    0:00:00 (xfer#71, to-check=10/88)
pyutils/pyutils/pyutils.py
       3.00K 100%  117.38kB/s    0:00:00 (xfer#72, to-check=9/88)
pyutils/pyutils/ming/
pyutils/pyutils/ming/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#73, to-check=7/88)
pyutils/pyutils/ming/extensions.py
       1.79K 100%   69.88kB/s    0:00:00 (xfer#74, to-check=6/88)
pyutils/pyutils/ming/schema.py
       4.22K 100%  164.73kB/s    0:00:00 (xfer#75, to-check=5/88)
pyutils/pyutils/ming/session.py
       1.47K 100%   57.42kB/s    0:00:00 (xfer#76, to-check=4/88)
pyutils/tests/
pyutils/tests/TestPyutils.py
       5.52K 100%  215.74kB/s    0:00:00 (xfer#77, to-check=3/88)
pyutils/tests/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#78, to-check=2/88)
pyutils/tests/unicode.csv
          49 100%    1.84kB/s    0:00:00 (xfer#79, to-check=1/88)
templates/
templates/celeryconfig.py.template
       1.84K 100%   69.30kB/s    0:00:00 (xfer#80, to-check=0/88)

sent 633.48K bytes  received 1.56K bytes  1.27M bytes/sec
total size is 628.12K  speedup is 0.99
sending incremental file list
./
AUTHORS
          31 100%    0.00kB/s    0:00:00 (xfer#1, to-check=495/497)
README.rst
         203 100%  198.24kB/s    0:00:00 (xfer#2, to-check=494/497)
apache2.conf
       9.38K 100%    8.95MB/s    0:00:00 (xfer#3, to-check=493/497)
config.yaml
       1.66K 100%    1.58MB/s    0:00:00 (xfer#4, to-check=492/497)
copyright
         752 100%  734.38kB/s    0:00:00 (xfer#5, to-check=491/497)
local_config.pkl
       1.12K 100%    1.07MB/s    0:00:00 (xfer#6, to-check=490/497)
metadata.yaml
         348 100%  339.84kB/s    0:00:00 (xfer#7, to-check=489/497)
revision
           2 100%    1.95kB/s    0:00:00 (xfer#8, to-check=488/497)
setup.py
       2.43K 100%    2.31MB/s    0:00:00 (xfer#9, to-check=487/497)
setup.sh
       1.81K 100%    1.73MB/s    0:00:00 (xfer#10, to-check=486/497)
webui-db.sql
       1.72K 100%    1.64MB/s    0:00:00 (xfer#11, to-check=485/497)
hooks/
hooks/api-relation-broken
          72 100%   70.31kB/s    0:00:00 (xfer#12, to-check=479/497)
hooks/api-relation-changed
          73 100%   71.29kB/s    0:00:00 (xfer#13, to-check=478/497)
hooks/api-relation-joined
          72 100%   70.31kB/s    0:00:00 (xfer#14, to-check=477/497)
hooks/config-changed
          67 100%   65.43kB/s    0:00:00 (xfer#15, to-check=476/497)
hooks/install
          71 100%   69.34kB/s    0:00:00 (xfer#16, to-check=475/497)
hooks/start
          58 100%   56.64kB/s    0:00:00 (xfer#17, to-check=474/497)
hooks/stop
          57 100%   55.66kB/s    0:00:00 (xfer#18, to-check=473/497)
hooks/storage-relation-broken
          76 100%   74.22kB/s    0:00:00 (xfer#19, to-check=472/497)
hooks/storage-relation-changed
          77 100%   75.20kB/s    0:00:00 (xfer#20, to-check=471/497)
hooks/storage-relation-joined
          76 100%   74.22kB/s    0:00:00 (xfer#21, to-check=470/497)
hooks/uninstall
          62 100%   60.55kB/s    0:00:00 (xfer#22, to-check=469/497)
hooks/website-relation-broken
          76 100%   74.22kB/s    0:00:00 (xfer#23, to-check=468/497)
hooks/website-relation-changed
          77 100%   75.20kB/s    0:00:00 (xfer#24, to-check=467/497)
hooks/website-relation-departed
          78 100%   76.17kB/s    0:00:00 (xfer#25, to-check=466/497)
hooks/website-relation-joined
          76 100%   74.22kB/s    0:00:00 (xfer#26, to-check=465/497)
oscied_lib/
oscied_lib/.gitignore
          50 100%   48.83kB/s    0:00:00 (xfer#27, to-check=464/497)
oscied_lib/Callback.py
       2.72K 100%    2.60MB/s    0:00:00 (xfer#28, to-check=463/497)
oscied_lib/CharmConfig.py
       2.18K 100%    2.08MB/s    0:00:00 (xfer#29, to-check=462/497)
oscied_lib/CharmConfig_Storage.py
       5.68K 100%    5.41MB/s    0:00:00 (xfer#30, to-check=461/497)
oscied_lib/CharmHooks.py
      12.55K 100%   11.97MB/s    0:00:00 (xfer#31, to-check=460/497)
oscied_lib/CharmHooks_Storage.py
       7.12K 100%    3.40MB/s    0:00:00 (xfer#32, to-check=459/497)
oscied_lib/CharmHooks_Subordinate.py
       4.92K 100%    1.57MB/s    0:00:00 (xfer#33, to-check=458/497)
oscied_lib/CharmHooks_Website.py
       3.71K 100%    1.18MB/s    0:00:00 (xfer#34, to-check=457/497)
oscied_lib/Media.py
       4.37K 100%    1.39MB/s    0:00:00 (xfer#35, to-check=456/497)
oscied_lib/Orchestra.py
      30.96K 100%    7.38MB/s    0:00:00 (xfer#36, to-check=455/497)
oscied_lib/OrchestraConfig.py
       4.37K 100%    1.04MB/s    0:00:00 (xfer#37, to-check=454/497)
oscied_lib/OrchestraHooks.py
      13.21K 100%    3.15MB/s    0:00:00 (xfer#38, to-check=453/497)
oscied_lib/OsciedDBModel.py
       1.82K 100%  444.58kB/s    0:00:00 (xfer#39, to-check=452/497)
oscied_lib/PublishTask.py
       3.66K 100%  892.82kB/s    0:00:00 (xfer#40, to-check=451/497)
oscied_lib/Publisher.py
       4.97K 100%    1.19MB/s    0:00:00 (xfer#41, to-check=450/497)
oscied_lib/PublisherConfig.py
       3.12K 100%  762.70kB/s    0:00:00 (xfer#42, to-check=449/497)
oscied_lib/PublisherHooks.py
       6.93K 100%    1.65MB/s    0:00:00 (xfer#43, to-check=448/497)
oscied_lib/Storage.py
       3.72K 100%  907.71kB/s    0:00:00 (xfer#44, to-check=447/497)
oscied_lib/StorageConfig.py
       2.22K 100%  541.26kB/s    0:00:00 (xfer#45, to-check=446/497)
oscied_lib/StorageHooks.py
      11.98K 100%    2.29MB/s    0:00:00 (xfer#46, to-check=445/497)
oscied_lib/Transform.py
      13.66K 100%    2.61MB/s    0:00:00 (xfer#47, to-check=444/497)
oscied_lib/TransformConfig.py
       2.49K 100%  486.72kB/s    0:00:00 (xfer#48, to-check=443/497)
oscied_lib/TransformHooks.py
       5.54K 100%    1.06MB/s    0:00:00 (xfer#49, to-check=442/497)
oscied_lib/TransformProfile.py
       2.75K 100%  536.91kB/s    0:00:00 (xfer#50, to-check=441/497)
oscied_lib/TransformTask.py
       5.49K 100%    1.05MB/s    0:00:00 (xfer#51, to-check=440/497)
oscied_lib/User.py
       4.18K 100%  680.01kB/s    0:00:00 (xfer#52, to-check=439/497)
oscied_lib/WebuiConfig.py
       3.66K 100%  595.21kB/s    0:00:00 (xfer#53, to-check=438/497)
oscied_lib/WebuiHooks.py
      10.33K 100%    1.64MB/s    0:00:00 (xfer#54, to-check=437/497)
oscied_lib/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#55, to-check=436/497)
pyutils/
pyutils/.gitignore
          48 100%    7.81kB/s    0:00:00 (xfer#56, to-check=435/497)
pyutils/.travis.yml
         331 100%   53.87kB/s    0:00:00 (xfer#57, to-check=434/497)
pyutils/AUTHORS
          14 100%    2.28kB/s    0:00:00 (xfer#58, to-check=433/497)
pyutils/COPYING
      35.15K 100%    4.79MB/s    0:00:00 (xfer#59, to-check=432/497)
pyutils/README.rst
       1.39K 100%  193.78kB/s    0:00:00 (xfer#60, to-check=431/497)
pyutils/setup.cfg
         196 100%   27.34kB/s    0:00:00 (xfer#61, to-check=430/497)
pyutils/setup.py
       3.10K 100%  433.04kB/s    0:00:00 (xfer#62, to-check=429/497)
pyutils/pyutils/
pyutils/pyutils/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#63, to-check=426/497)
pyutils/pyutils/py_crypto.py
       1.89K 100%  262.97kB/s    0:00:00 (xfer#64, to-check=425/497)
pyutils/pyutils/py_datetime.py
       3.07K 100%  428.85kB/s    0:00:00 (xfer#65, to-check=424/497)
pyutils/pyutils/py_exception.py
       1.34K 100%  187.22kB/s    0:00:00 (xfer#66, to-check=423/497)
pyutils/pyutils/py_ffmpeg.py
       6.84K 100%  954.10kB/s    0:00:00 (xfer#67, to-check=422/497)
pyutils/pyutils/py_filesystem.py
      10.20K 100%    1.39MB/s    0:00:00 (xfer#68, to-check=421/497)
pyutils/pyutils/py_flask.py
       3.03K 100%  423.13kB/s    0:00:00 (xfer#69, to-check=420/497)
pyutils/pyutils/py_juju.py
      10.17K 100%    1.21MB/s    0:00:00 (xfer#70, to-check=419/497)
pyutils/pyutils/py_logging.py
       3.49K 100%  426.15kB/s    0:00:00 (xfer#71, to-check=418/497)
pyutils/pyutils/py_mock.py
       2.56K 100%  312.87kB/s    0:00:00 (xfer#72, to-check=417/497)
pyutils/pyutils/py_serialization.py
       6.85K 100%  836.30kB/s    0:00:00 (xfer#73, to-check=416/497)
pyutils/pyutils/py_subprocess.py
       5.48K 100%  669.31kB/s    0:00:00 (xfer#74, to-check=415/497)
pyutils/pyutils/py_unicode.py
       2.29K 100%  279.30kB/s    0:00:00 (xfer#75, to-check=414/497)
pyutils/pyutils/py_validation.py
       4.47K 100%  545.17kB/s    0:00:00 (xfer#76, to-check=413/497)
pyutils/pyutils/pyutils.py
       3.00K 100%  326.06kB/s    0:00:00 (xfer#77, to-check=412/497)
pyutils/pyutils/ming/
pyutils/pyutils/ming/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#78, to-check=410/497)
pyutils/pyutils/ming/extensions.py
       1.79K 100%  194.12kB/s    0:00:00 (xfer#79, to-check=409/497)
pyutils/pyutils/ming/schema.py
       4.22K 100%  457.57kB/s    0:00:00 (xfer#80, to-check=408/497)
pyutils/pyutils/ming/session.py
       1.47K 100%  159.51kB/s    0:00:00 (xfer#81, to-check=407/497)
pyutils/tests/
pyutils/tests/TestPyutils.py
       5.52K 100%  385.25kB/s    0:00:00 (xfer#82, to-check=406/497)
pyutils/tests/__init__.py
           0 100%    0.00kB/s    0:00:00 (xfer#83, to-check=405/497)
pyutils/tests/unicode.csv
          49 100%    3.19kB/s    0:00:00 (xfer#84, to-check=404/497)
templates/
templates/000-default
         691 100%   44.99kB/s    0:00:00 (xfer#85, to-check=403/497)
templates/config.php.template
      14.36K 100%  934.90kB/s    0:00:00 (xfer#86, to-check=402/497)
templates/database.php.template
       3.24K 100%  211.13kB/s    0:00:00 (xfer#87, to-check=401/497)
templates/htaccess.template
         410 100%   26.69kB/s    0:00:00 (xfer#88, to-check=400/497)
www/
www/index.php
       6.36K 100%  413.87kB/s    0:00:00 (xfer#89, to-check=399/497)
www/license.txt
       2.50K 100%  162.50kB/s    0:00:00 (xfer#90, to-check=398/497)
www/application/
www/application/.htaccess
          13 100%    0.85kB/s    0:00:00 (xfer#91, to-check=391/497)
www/application/index.html
         114 100%    7.42kB/s    0:00:00 (xfer#92, to-check=390/497)
www/application/cache/
www/application/cache/.htaccess
          13 100%    0.85kB/s    0:00:00 (xfer#93, to-check=376/497)
www/application/cache/index.html
         114 100%    7.42kB/s    0:00:00 (xfer#94, to-check=375/497)
www/application/config/
www/application/config/autoload.php
       3.15K 100%  204.75kB/s    0:00:00 (xfer#95, to-check=374/497)
www/application/config/constants.php
       1.71K 100%  111.46kB/s    0:00:00 (xfer#96, to-check=373/497)
www/application/config/doctypes.php
       1.14K 100%   74.09kB/s    0:00:00 (xfer#97, to-check=372/497)
www/application/config/foreign_chars.php
       1.78K 100%  115.95kB/s    0:00:00 (xfer#98, to-check=371/497)
www/application/config/hooks.php
         498 100%   32.42kB/s    0:00:00 (xfer#99, to-check=370/497)
www/application/config/index.html
         114 100%    7.42kB/s    0:00:00 (xfer#100, to-check=369/497)
www/application/config/migration.php
       1.28K 100%   83.46kB/s    0:00:00 (xfer#101, to-check=368/497)
www/application/config/mimes.php
       5.42K 100%  353.19kB/s    0:00:00 (xfer#102, to-check=367/497)
www/application/config/pagination.php
       1.03K 100%   66.99kB/s    0:00:00 (xfer#103, to-check=366/497)
www/application/config/profiler.php
         564 100%   34.42kB/s    0:00:00 (xfer#104, to-check=365/497)
www/application/config/routes.php
       1.57K 100%   96.01kB/s    0:00:00 (xfer#105, to-check=364/497)
www/application/config/smileys.php
       3.29K 100%  178.77kB/s    0:00:00 (xfer#106, to-check=363/497)
www/application/config/user_agents.php
       5.59K 100%  303.22kB/s    0:00:00 (xfer#107, to-check=362/497)
www/application/controllers/
www/application/controllers/index.html
         114 100%    6.18kB/s    0:00:00 (xfer#108, to-check=361/497)
www/application/controllers/media.php
       8.43K 100%  457.41kB/s    0:00:00 (xfer#109, to-check=360/497)
www/application/controllers/misc.php
         620 100%   33.64kB/s    0:00:00 (xfer#110, to-check=359/497)
www/application/controllers/profile.php
       5.61K 100%  288.50kB/s    0:00:00 (xfer#111, to-check=358/497)
www/application/controllers/publisher.php
       5.16K 100%  265.21kB/s    0:00:00 (xfer#112, to-check=357/497)
www/application/controllers/transform.php
       5.81K 100%  298.47kB/s    0:00:00 (xfer#113, to-check=356/497)
www/application/controllers/upload_files.php
       2.53K 100%  130.19kB/s    0:00:00 (xfer#114, to-check=355/497)
www/application/controllers/users.php
      10.32K 100%  530.27kB/s    0:00:00 (xfer#115, to-check=354/497)
www/application/core/
www/application/core/MY_Controller.php
         733 100%   37.67kB/s    0:00:00 (xfer#116, to-check=353/497)
www/application/core/MY_Loader.php
       7.11K 100%  346.92kB/s    0:00:00 (xfer#117, to-check=352/497)
www/application/core/index.html
         114 100%    5.57kB/s    0:00:00 (xfer#118, to-check=351/497)
www/application/errors/
www/application/errors/error_404.php
       1.16K 100%   56.64kB/s    0:00:00 (xfer#119, to-check=350/497)
www/application/errors/error_db.php
       1.16K 100%   56.45kB/s    0:00:00 (xfer#120, to-check=349/497)
www/application/errors/error_general.php
       1.15K 100%   56.01kB/s    0:00:00 (xfer#121, to-check=348/497)
www/application/errors/error_php.php
         288 100%   14.06kB/s    0:00:00 (xfer#122, to-check=347/497)
www/application/errors/index.html
         114 100%    5.57kB/s    0:00:00 (xfer#123, to-check=346/497)
www/application/helpers/
www/application/helpers/MY_download_helper.php
       3.12K 100%  152.29kB/s    0:00:00 (xfer#124, to-check=345/497)
www/application/helpers/flash_message_helper.php
       1.39K 100%   67.72kB/s    0:00:00 (xfer#125, to-check=344/497)
www/application/helpers/index.html
         114 100%    5.57kB/s    0:00:00 (xfer#126, to-check=343/497)
www/application/helpers/simple_html_dom_helper.php
      53.22K 100%    2.42MB/s    0:00:00 (xfer#127, to-check=342/497)
www/application/hooks/
www/application/hooks/index.html
         114 100%    5.30kB/s    0:00:00 (xfer#128, to-check=341/497)
www/application/language/
www/application/language/english/
www/application/language/english/index.html
         114 100%    5.30kB/s    0:00:00 (xfer#129, to-check=339/497)
www/application/libraries/
www/application/libraries/Css_js.php
         794 100%   36.92kB/s    0:00:00 (xfer#130, to-check=338/497)
www/application/libraries/MY_Form_validation.php
         488 100%   22.69kB/s    0:00:00 (xfer#131, to-check=337/497)
www/application/libraries/User.php
       1.41K 100%   65.34kB/s    0:00:00 (xfer#132, to-check=336/497)
www/application/libraries/index.html
         114 100%    5.06kB/s    0:00:00 (xfer#133, to-check=335/497)
www/application/logs/
www/application/logs/index.html
         114 100%    5.06kB/s    0:00:00 (xfer#134, to-check=334/497)
www/application/models/
www/application/models/files_model.php
       1.66K 100%   67.38kB/s    0:00:00 (xfer#135, to-check=333/497)
www/application/models/index.html
         114 100%    4.64kB/s    0:00:00 (xfer#136, to-check=332/497)
www/application/models/tmp_files_model.php
       1.49K 100%   60.55kB/s    0:00:00 (xfer#137, to-check=331/497)
www/application/third_party/
www/application/third_party/index.html
         114 100%    4.64kB/s    0:00:00 (xfer#138, to-check=330/497)
www/application/views/
www/application/views/contact.php
          11 100%    0.45kB/s    0:00:00 (xfer#139, to-check=329/497)
www/application/views/homepage.php
          24 100%    0.98kB/s    0:00:00 (xfer#140, to-check=328/497)
www/application/views/index.html
         114 100%    4.64kB/s    0:00:00 (xfer#141, to-check=327/497)
www/application/views/fileupload/
www/application/views/fileupload/scripts.php
       4.63K 100%  188.52kB/s    0:00:00 (xfer#142, to-check=319/497)
www/application/views/fileupload/upload.php
         968 100%   39.39kB/s    0:00:00 (xfer#143, to-check=318/497)
www/application/views/layouts/
www/application/views/layouts/default.php
       1.77K 100%   71.98kB/s    0:00:00 (xfer#144, to-check=317/497)
www/application/views/layouts/default_header.php
       3.79K 100%  154.30kB/s    0:00:00 (xfer#145, to-check=316/497)
www/application/views/media/
www/application/views/media/add_media_form.php
       3.57K 100%  145.22kB/s    0:00:00 (xfer#146, to-check=315/497)
www/application/views/media/show.php
         642 100%   26.12kB/s    0:00:00 (xfer#147, to-check=314/497)
www/application/views/media/show_medias.php
       2.67K 100%  108.72kB/s    0:00:00 (xfer#148, to-check=313/497)
www/application/views/profile/
www/application/views/profile/add_profile_form.php
       1.72K 100%   69.95kB/s    0:00:00 (xfer#149, to-check=312/497)
www/application/views/profile/show.php
         660 100%   26.86kB/s    0:00:00 (xfer#150, to-check=311/497)
www/application/views/profile/show_profiles.php
       1.39K 100%   56.64kB/s    0:00:00 (xfer#151, to-check=310/497)
www/application/views/publisher/
www/application/views/publisher/launch_publish_form.php
       1.41K 100%   57.25kB/s    0:00:00 (xfer#152, to-check=309/497)
www/application/views/publisher/show.php
         658 100%   26.77kB/s    0:00:00 (xfer#153, to-check=308/497)
www/application/views/publisher/show_tasks.php
       4.52K 100%  183.92kB/s    0:00:00 (xfer#154, to-check=307/497)
www/application/views/transform/
www/application/views/transform/launch_transform_form.php
       1.84K 100%   74.83kB/s    0:00:00 (xfer#155, to-check=306/497)
www/application/views/transform/show.php
         658 100%   25.70kB/s    0:00:00 (xfer#156, to-check=305/497)
www/application/views/transform/show_tasks.php
       4.79K 100%  180.03kB/s    0:00:00 (xfer#157, to-check=304/497)
www/application/views/users/
www/application/views/users/add_user_form.php
       1.80K 100%   31.44kB/s    0:00:00 (xfer#158, to-check=303/497)
www/application/views/users/login_modal.php
       1.60K 100%   27.94kB/s    0:00:00 (xfer#159, to-check=302/497)
www/application/views/users/show.php
       1.82K 100%   31.79kB/s    0:00:00 (xfer#160, to-check=301/497)
www/application/views/users/show_users.php
       3.32K 100%   57.90kB/s    0:00:00 (xfer#161, to-check=300/497)
www/assets/
www/assets/index.html
         114 100%    1.99kB/s    0:00:00 (xfer#162, to-check=299/497)
www/assets/css/
www/assets/css/bootstrap-responsive.css
      21.75K 100%  379.31kB/s    0:00:00 (xfer#163, to-check=295/497)
www/assets/css/bootstrap-responsive.min.css
      16.55K 100%  278.71kB/s    0:00:00 (xfer#164, to-check=294/497)
www/assets/css/bootstrap.css
     124.22K 100%    2.01MB/s    0:00:00 (xfer#165, to-check=293/497)
www/assets/css/bootstrap.min.css
     103.31K 100%    1.62MB/s    0:00:00 (xfer#166, to-check=292/497)
www/assets/css/custom.css
       1.30K 100%   20.75kB/s    0:00:00 (xfer#167, to-check=291/497)
www/assets/css/style.css
       2.14K 100%   34.20kB/s    0:00:00 (xfer#168, to-check=290/497)
www/assets/css/fileupload/
www/assets/css/fileupload/bootstrap-image-gallery.min.css
       1.69K 100%   27.09kB/s    0:00:00 (xfer#169, to-check=288/497)
www/assets/css/fileupload/jquery-ui.css
      33.40K 100%  517.78kB/s    0:00:00 (xfer#170, to-check=287/497)
www/assets/css/fileupload/jquery.fileupload-ui.css
       1.28K 100%   19.78kB/s    0:00:00 (xfer#171, to-check=286/497)
www/assets/img/
www/assets/img/glyphicons-halflings-white.png
       8.78K 100%  136.05kB/s    0:00:00 (xfer#172, to-check=285/497)
www/assets/img/glyphicons-halflings.png
      12.80K 100%  198.40kB/s    0:00:00 (xfer#173, to-check=284/497)
www/assets/img/home-bg.jpg
       9.26M 100%   33.21MB/s    0:00:00 (xfer#174, to-check=283/497)
www/assets/img/home-bg11.jpg
      82.00K 100%  297.68kB/s    0:00:00 (xfer#175, to-check=282/497)
www/assets/img/fileupload/
www/assets/img/fileupload/loading.gif
       3.90K 100%   14.15kB/s    0:00:00 (xfer#176, to-check=279/497)
www/assets/img/fileupload/progressbar.gif
       3.32K 100%   12.06kB/s    0:00:00 (xfer#177, to-check=278/497)
www/assets/img/icons/
www/assets/img/icons/add.png
       5.49K 100%   19.94kB/s    0:00:00 (xfer#178, to-check=277/497)
www/assets/img/icons/calendar.png
       3.98K 100%   14.46kB/s    0:00:00 (xfer#179, to-check=276/497)
www/assets/img/icons/chat.png
       5.54K 100%   20.11kB/s    0:00:00 (xfer#180, to-check=275/497)
www/assets/img/icons/comment.png
       5.24K 100%   19.00kB/s    0:00:00 (xfer#181, to-check=274/497)
www/assets/img/icons/contacts.png
       5.90K 100%   21.33kB/s    0:00:00 (xfer#182, to-check=273/497)
www/assets/img/icons/contacts2.png
       5.77K 100%   20.80kB/s    0:00:00 (xfer#183, to-check=272/497)
www/assets/img/icons/delete.png
       5.49K 100%   19.79kB/s    0:00:00 (xfer#184, to-check=271/497)
www/assets/img/icons/edit.png
       5.08K 100%   18.32kB/s    0:00:00 (xfer#185, to-check=270/497)
www/assets/img/icons/edit2.png
       4.36K 100%   15.73kB/s    0:00:00 (xfer#186, to-check=269/497)
www/assets/img/icons/email.png
       4.56K 100%   16.36kB/s    0:00:00 (xfer#187, to-check=268/497)
www/assets/img/icons/favorite.png
       5.04K 100%   18.08kB/s    0:00:00 (xfer#188, to-check=267/497)
www/assets/img/icons/picture.png
       4.29K 100%   15.41kB/s    0:00:00 (xfer#189, to-check=266/497)
www/assets/img/icons/preferences.png
       6.26K 100%   22.46kB/s    0:00:00 (xfer#190, to-check=265/497)
www/assets/img/icons/rss.png
       4.91K 100%   17.55kB/s    0:00:00 (xfer#191, to-check=264/497)
www/assets/img/icons/save.png
       3.69K 100%   13.20kB/s    0:00:00 (xfer#192, to-check=263/497)
www/assets/img/icons/search.png
       5.12K 100%   18.33kB/s    0:00:00 (xfer#193, to-check=262/497)
www/assets/img/icons/user.png
       4.05K 100%   14.50kB/s    0:00:00 (xfer#194, to-check=261/497)
www/assets/img/icons/validate.png
       4.41K 100%   15.71kB/s    0:00:00 (xfer#195, to-check=260/497)
www/assets/img/icons/video.png
       4.27K 100%   15.21kB/s    0:00:00 (xfer#196, to-check=259/497)
www/assets/img/icons/pack1/
www/assets/img/icons/pack1/calendar.png
       4.18K 100%   14.88kB/s    0:00:00 (xfer#197, to-check=257/497)
www/assets/img/icons/pack1/comment.png
       4.12K 100%   14.70kB/s    0:00:00 (xfer#198, to-check=256/497)
www/assets/img/icons/pack1/comment2.png
       4.16K 100%   14.82kB/s    0:00:00 (xfer#199, to-check=255/497)
www/assets/img/icons/pack1/delete.png
       4.48K 100%   15.91kB/s    0:00:00 (xfer#200, to-check=254/497)
www/assets/img/icons/pack1/edit.png
       4.36K 100%   15.50kB/s    0:00:00 (xfer#201, to-check=253/497)
www/assets/img/icons/pack1/info.png
       4.44K 100%   15.65kB/s    0:00:00 (xfer#202, to-check=252/497)
www/assets/img/icons/pack1/picture.png
       4.53K 100%   15.96kB/s    0:00:00 (xfer#203, to-check=251/497)
www/assets/img/icons/pack1/save.png
       3.77K 100%   13.23kB/s    0:00:00 (xfer#204, to-check=250/497)
www/assets/img/icons/pack1/search.png
       4.66K 100%   16.36kB/s    0:00:00 (xfer#205, to-check=249/497)
www/assets/img/icons/pack1/validate.png
       4.14K 100%   14.53kB/s    0:00:00 (xfer#206, to-check=248/497)
www/assets/img/icons/pack1/video.png
       3.87K 100%   13.58kB/s    0:00:00 (xfer#207, to-check=247/497)
www/assets/js/
www/assets/js/bootstrap.js
      58.52K 100%  203.36kB/s    0:00:00 (xfer#208, to-check=246/497)
www/assets/js/bootstrap.min.js
      31.60K 100%  109.81kB/s    0:00:00 (xfer#209, to-check=245/497)
www/assets/js/jquery-1.8.0.min.js
      92.56K 100%  319.38kB/s    0:00:00 (xfer#210, to-check=244/497)
www/assets/js/fileupload/
www/assets/js/fileupload/canvas-to-blob.js
         859 100%    2.96kB/s    0:00:00 (xfer#211, to-check=242/497)
www/assets/js/fileupload/jquery-ui.min.js
     200.10K 100%  680.89kB/s    0:00:00 (xfer#212, to-check=241/497)
www/assets/js/fileupload/jquery.fileupload-fp.js
       8.40K 100%   28.59kB/s    0:00:00 (xfer#213, to-check=240/497)
www/assets/js/fileupload/jquery.fileupload-ui.js
      27.99K 100%   93.93kB/s    0:00:00 (xfer#214, to-check=239/497)
www/assets/js/fileupload/jquery.fileupload.js
      42.37K 100%  141.71kB/s    0:00:00 (xfer#215, to-check=238/497)
www/assets/js/fileupload/jquery.iframe-transport.js
       8.09K 100%   27.05kB/s    0:00:00 (xfer#216, to-check=237/497)
www/assets/js/fileupload/load-image.js
       1.28K 100%    4.27kB/s    0:00:00 (xfer#217, to-check=236/497)
www/assets/js/fileupload/locale.js
         781 100%    2.61kB/s    0:00:00 (xfer#218, to-check=235/497)
www/assets/js/fileupload/main.js
       1.89K 100%    6.32kB/s    0:00:00 (xfer#219, to-check=234/497)
www/assets/js/fileupload/tmpl.js
         971 100%    3.25kB/s    0:00:00 (xfer#220, to-check=233/497)
www/assets/js/fileupload/tmpl.min.js
         971 100%    3.25kB/s    0:00:00 (xfer#221, to-check=232/497)
www/assets/js/fileupload/cors/
www/assets/js/fileupload/cors/jquery.postmessage-transport.js
       4.00K 100%   13.38kB/s    0:00:00 (xfer#222, to-check=229/497)
www/assets/js/fileupload/cors/jquery.xdr-transport.js
       3.21K 100%   10.75kB/s    0:00:00 (xfer#223, to-check=228/497)
www/assets/js/fileupload/cors/result.html
         504 100%    1.68kB/s    0:00:00 (xfer#224, to-check=227/497)
www/assets/js/fileupload/vendor/
www/assets/js/fileupload/vendor/jquery.ui.widget.js
       7.28K 100%   24.27kB/s    0:00:00 (xfer#225, to-check=226/497)
www/profiles/
www/profiles/default_profile.png
       2.15K 100%    7.16kB/s    0:00:00 (xfer#226, to-check=225/497)
www/profiles/profile_1.jpg
       4.00K 100%   13.32kB/s    0:00:00 (xfer#227, to-check=224/497)
www/sparks/
www/sparks/curl/
www/sparks/curl/1.2.1/
www/sparks/curl/1.2.1/README.md
       2.40K 100%    7.99kB/s    0:00:00 (xfer#228, to-check=220/497)
www/sparks/curl/1.2.1/spark.info
          58 100%    0.19kB/s    0:00:00 (xfer#229, to-check=219/497)
www/sparks/curl/1.2.1/config/
www/sparks/curl/1.2.1/config/autoload.php
          99 100%    0.33kB/s    0:00:00 (xfer#230, to-check=216/497)
www/sparks/curl/1.2.1/libraries/
www/sparks/curl/1.2.1/libraries/Curl.php
       9.68K 100%   32.17kB/s    0:00:00 (xfer#231, to-check=215/497)
www/sparks/restclient/
www/sparks/restclient/2.1.0/
www/sparks/restclient/2.1.0/README.md
         862 100%    2.86kB/s    0:00:00 (xfer#232, to-check=213/497)
www/sparks/restclient/2.1.0/spark.info
          79 100%    0.26kB/s    0:00:00 (xfer#233, to-check=212/497)
www/sparks/restclient/2.1.0/config/
www/sparks/restclient/2.1.0/config/autoload.php
          95 100%    0.32kB/s    0:00:00 (xfer#234, to-check=209/497)
www/sparks/restclient/2.1.0/libraries/
www/sparks/restclient/2.1.0/libraries/Rest.php
       8.22K 100%   27.22kB/s    0:00:00 (xfer#235, to-check=208/497)
www/sparks/restclient/2.1.0/libraries/index.html
         114 100%    0.38kB/s    0:00:00 (xfer#236, to-check=207/497)
www/system/
www/system/.htaccess
          13 100%    0.04kB/s    0:00:00 (xfer#237, to-check=206/497)
www/system/index.html
         114 100%    0.38kB/s    0:00:00 (xfer#238, to-check=205/497)
www/system/core/
www/system/core/Benchmark.php
       2.95K 100%    9.76kB/s    0:00:00 (xfer#239, to-check=198/497)
www/system/core/CodeIgniter.php
      11.39K 100%   37.58kB/s    0:00:00 (xfer#240, to-check=197/497)
www/system/core/Common.php
      13.42K 100%   44.11kB/s    0:00:00 (xfer#241, to-check=196/497)
www/system/core/Config.php
       8.16K 100%   26.75kB/s    0:00:00 (xfer#242, to-check=195/497)
www/system/core/Controller.php
       1.57K 100%    5.14kB/s    0:00:00 (xfer#243, to-check=194/497)
www/system/core/Exceptions.php
       4.70K 100%   15.39kB/s    0:00:00 (xfer#244, to-check=193/497)
www/system/core/Hooks.php
       4.70K 100%   15.39kB/s    0:00:00 (xfer#245, to-check=192/497)
www/system/core/Input.php
      18.43K 100%   60.19kB/s    0:00:00 (xfer#246, to-check=191/497)
www/system/core/Lang.php
       3.63K 100%   11.86kB/s    0:00:00 (xfer#247, to-check=190/497)
www/system/core/Loader.php
      30.58K 100%   99.53kB/s    0:00:00 (xfer#248, to-check=189/497)
www/system/core/Model.php
       1.19K 100%    3.87kB/s    0:00:00 (xfer#249, to-check=188/497)
www/system/core/Output.php
      12.94K 100%   42.11kB/s    0:00:00 (xfer#250, to-check=187/497)
www/system/core/Router.php
      12.39K 100%   40.21kB/s    0:00:00 (xfer#251, to-check=186/497)
www/system/core/Security.php
      21.92K 100%   70.88kB/s    0:00:00 (xfer#252, to-check=185/497)
www/system/core/URI.php
      14.44K 100%   46.70kB/s    0:00:00 (xfer#253, to-check=184/497)
www/system/core/Utf8.php
       3.58K 100%   11.59kB/s    0:00:00 (xfer#254, to-check=183/497)
www/system/core/index.html
         114 100%    0.37kB/s    0:00:00 (xfer#255, to-check=182/497)
www/system/database/
www/system/database/DB.php
       4.19K 100%   13.50kB/s    0:00:00 (xfer#256, to-check=181/497)
www/system/database/DB_active_rec.php
      42.98K 100%  138.06kB/s    0:00:00 (xfer#257, to-check=180/497)
www/system/database/DB_cache.php
       4.38K 100%   14.06kB/s    0:00:00 (xfer#258, to-check=179/497)
www/system/database/DB_driver.php
      32.65K 100%  104.20kB/s    0:00:00 (xfer#259, to-check=178/497)
www/system/database/DB_forge.php
       7.45K 100%   23.77kB/s    0:00:00 (xfer#260, to-check=177/497)
www/system/database/DB_result.php
       9.02K 100%   28.78kB/s    0:00:00 (xfer#261, to-check=176/497)
www/system/database/DB_utility.php
       9.80K 100%   31.29kB/s    0:00:00 (xfer#262, to-check=175/497)
www/system/database/index.html
         114 100%    0.36kB/s    0:00:00 (xfer#263, to-check=174/497)
www/system/database/drivers/
www/system/database/drivers/index.html
         114 100%    0.36kB/s    0:00:00 (xfer#264, to-check=172/497)
www/system/database/drivers/cubrid/
www/system/database/drivers/cubrid/cubrid_driver.php
      17.89K 100%   56.91kB/s    0:00:00 (xfer#265, to-check=161/497)
www/system/database/drivers/cubrid/cubrid_forge.php
       7.06K 100%   22.45kB/s    0:00:00 (xfer#266, to-check=160/497)
www/system/database/drivers/cubrid/cubrid_result.php
       4.51K 100%   14.33kB/s    0:00:00 (xfer#267, to-check=159/497)
www/system/database/drivers/cubrid/cubrid_utility.php
       2.87K 100%    9.10kB/s    0:00:00 (xfer#268, to-check=158/497)
www/system/database/drivers/cubrid/index.html
         114 100%    0.36kB/s    0:00:00 (xfer#269, to-check=157/497)
www/system/database/drivers/mssql/
www/system/database/drivers/mssql/index.html
         114 100%    0.36kB/s    0:00:00 (xfer#270, to-check=156/497)
www/system/database/drivers/mssql/mssql_driver.php
      14.84K 100%   47.04kB/s    0:00:00 (xfer#271, to-check=155/497)
www/system/database/drivers/mssql/mssql_forge.php
       5.79K 100%   18.36kB/s    0:00:00 (xfer#272, to-check=154/497)
www/system/database/drivers/mssql/mssql_result.php
       3.37K 100%   10.66kB/s    0:00:00 (xfer#273, to-check=153/497)
www/system/database/drivers/mssql/mssql_utility.php
       1.98K 100%    6.25kB/s    0:00:00 (xfer#274, to-check=152/497)
www/system/database/drivers/mysql/
www/system/database/drivers/mysql/index.html
         114 100%    0.36kB/s    0:00:00 (xfer#275, to-check=151/497)
www/system/database/drivers/mysql/mysql_driver.php
      17.37K 100%   54.72kB/s    0:00:00 (xfer#276, to-check=150/497)
www/system/database/drivers/mysql/mysql_forge.php
       6.44K 100%   20.29kB/s    0:00:00 (xfer#277, to-check=149/497)
www/system/database/drivers/mysql/mysql_result.php
       3.62K 100%   11.42kB/s    0:00:00 (xfer#278, to-check=148/497)
www/system/database/drivers/mysql/mysql_utility.php
       4.61K 100%   14.48kB/s    0:00:00 (xfer#279, to-check=147/497)
www/system/database/drivers/mysqli/
www/system/database/drivers/mysqli/index.html
         114 100%    0.36kB/s    0:00:00 (xfer#280, to-check=146/497)
www/system/database/drivers/mysqli/mysqli_driver.php
      17.41K 100%   54.67kB/s    0:00:00 (xfer#281, to-check=145/497)
www/system/database/drivers/mysqli/mysqli_forge.php
       6.10K 100%   19.16kB/s    0:00:00 (xfer#282, to-check=144/497)
www/system/database/drivers/mysqli/mysqli_result.php
       3.64K 100%   11.40kB/s    0:00:00 (xfer#283, to-check=143/497)
www/system/database/drivers/mysqli/mysqli_utility.php
       1.98K 100%    6.21kB/s    0:00:00 (xfer#284, to-check=142/497)
www/system/database/drivers/oci8/
www/system/database/drivers/oci8/index.html
         114 100%    0.36kB/s    0:00:00 (xfer#285, to-check=141/497)
www/system/database/drivers/oci8/oci8_driver.php
      18.55K 100%   57.86kB/s    0:00:00 (xfer#286, to-check=140/497)
www/system/database/drivers/oci8/oci8_forge.php
       5.61K 100%   17.01kB/s    0:00:00 (xfer#287, to-check=139/497)
www/system/database/drivers/oci8/oci8_result.php
       4.49K 100%   13.58kB/s    0:00:00 (xfer#288, to-check=138/497)
www/system/database/drivers/oci8/oci8_utility.php
       1.93K 100%    5.83kB/s    0:00:00 (xfer#289, to-check=137/497)
www/system/database/drivers/odbc/
www/system/database/drivers/odbc/index.html
         114 100%    0.34kB/s    0:00:00 (xfer#290, to-check=136/497)
www/system/database/drivers/odbc/odbc_driver.php
      13.89K 100%   42.01kB/s    0:00:00 (xfer#291, to-check=135/497)
www/system/database/drivers/odbc/odbc_forge.php
       6.12K 100%   18.49kB/s    0:00:00 (xfer#292, to-check=134/497)
www/system/database/drivers/odbc/odbc_result.php
       4.59K 100%   13.89kB/s    0:00:00 (xfer#293, to-check=133/497)
www/system/database/drivers/odbc/odbc_utility.php
       2.26K 100%    6.83kB/s    0:00:00 (xfer#294, to-check=132/497)
www/system/database/drivers/pdo/
www/system/database/drivers/pdo/index.html
         114 100%    0.34kB/s    0:00:00 (xfer#295, to-check=131/497)
www/system/database/drivers/pdo/pdo_driver.php
      17.61K 100%   53.07kB/s    0:00:00 (xfer#296, to-check=130/497)
www/system/database/drivers/pdo/pdo_forge.php
       6.09K 100%   18.37kB/s    0:00:00 (xfer#297, to-check=129/497)
www/system/database/drivers/pdo/pdo_result.php
       3.51K 100%   10.57kB/s    0:00:00 (xfer#298, to-check=128/497)
www/system/database/drivers/pdo/pdo_utility.php
       2.24K 100%    6.72kB/s    0:00:00 (xfer#299, to-check=127/497)
www/system/database/drivers/postgre/
www/system/database/drivers/postgre/index.html
         114 100%    0.34kB/s    0:00:00 (xfer#300, to-check=126/497)
www/system/database/drivers/postgre/postgre_driver.php
      15.51K 100%   46.61kB/s    0:00:00 (xfer#301, to-check=125/497)
www/system/database/drivers/postgre/postgre_forge.php
       7.35K 100%   22.09kB/s    0:00:00 (xfer#302, to-check=124/497)
www/system/database/drivers/postgre/postgre_result.php
       3.44K 100%   10.33kB/s    0:00:00 (xfer#303, to-check=123/497)
www/system/database/drivers/postgre/postgre_utility.php
       1.85K 100%    5.56kB/s    0:00:00 (xfer#304, to-check=122/497)
www/system/database/drivers/sqlite/
www/system/database/drivers/sqlite/index.html
         114 100%    0.34kB/s    0:00:00 (xfer#305, to-check=121/497)
www/system/database/drivers/sqlite/sqlite_driver.php
      14.05K 100%   42.10kB/s    0:00:00 (xfer#306, to-check=120/497)
www/system/database/drivers/sqlite/sqlite_forge.php
       6.30K 100%   18.88kB/s    0:00:00 (xfer#307, to-check=119/497)
www/system/database/drivers/sqlite/sqlite_result.php
       3.55K 100%   10.63kB/s    0:00:00 (xfer#308, to-check=118/497)
www/system/database/drivers/sqlite/sqlite_utility.php
       2.15K 100%    6.42kB/s    0:00:00 (xfer#309, to-check=117/497)
www/system/database/drivers/sqlsrv/
www/system/database/drivers/sqlsrv/index.html
         114 100%    0.34kB/s    0:00:00 (xfer#310, to-check=116/497)
www/system/database/drivers/sqlsrv/sqlsrv_driver.php
      13.54K 100%   40.45kB/s    0:00:00 (xfer#311, to-check=115/497)
www/system/database/drivers/sqlsrv/sqlsrv_forge.php
       5.79K 100%   17.25kB/s    0:00:00 (xfer#312, to-check=114/497)
www/system/database/drivers/sqlsrv/sqlsrv_result.php
       3.42K 100%   10.17kB/s    0:00:00 (xfer#313, to-check=113/497)
www/system/database/drivers/sqlsrv/sqlsrv_utility.php
       1.98K 100%    5.89kB/s    0:00:00 (xfer#314, to-check=112/497)
www/system/fonts/
www/system/fonts/index.html
         114 100%    0.34kB/s    0:00:00 (xfer#315, to-check=111/497)
www/system/fonts/texb.ttf
     143.83K 100%  424.35kB/s    0:00:00 (xfer#316, to-check=110/497)
www/system/helpers/
www/system/helpers/array_helper.php
       2.51K 100%    7.40kB/s    0:00:00 (xfer#317, to-check=109/497)
www/system/helpers/captcha_helper.php
       6.17K 100%   18.20kB/s    0:00:00 (xfer#318, to-check=108/497)
www/system/helpers/cookie_helper.php
       2.59K 100%    7.64kB/s    0:00:00 (xfer#319, to-check=107/497)
www/system/helpers/date_helper.php
      12.97K 100%   38.27kB/s    0:00:00 (xfer#320, to-check=106/497)
www/system/helpers/directory_helper.php
       2.06K 100%    6.08kB/s    0:00:00 (xfer#321, to-check=105/497)
www/system/helpers/download_helper.php
       2.75K 100%    8.08kB/s    0:00:00 (xfer#322, to-check=104/497)
www/system/helpers/email_helper.php
       1.48K 100%    4.36kB/s    0:00:00 (xfer#323, to-check=103/497)
www/system/helpers/file_helper.php
      11.38K 100%   33.49kB/s    0:00:00 (xfer#324, to-check=102/497)
www/system/helpers/form_helper.php
      21.77K 100%   63.85kB/s    0:00:00 (xfer#325, to-check=101/497)
www/system/helpers/html_helper.php
       8.80K 100%   25.80kB/s    0:00:00 (xfer#326, to-check=100/497)
www/system/helpers/index.html
         114 100%    0.33kB/s    0:00:00 (xfer#327, to-check=99/497)
www/system/helpers/inflector_helper.php
       5.37K 100%   15.74kB/s    0:00:00 (xfer#328, to-check=98/497)
www/system/helpers/language_helper.php
       1.41K 100%    4.13kB/s    0:00:00 (xfer#329, to-check=97/497)
www/system/helpers/number_helper.php
       1.86K 100%    5.45kB/s    0:00:00 (xfer#330, to-check=96/497)
www/system/helpers/path_helper.php
       1.78K 100%    5.22kB/s    0:00:00 (xfer#331, to-check=95/497)
www/system/helpers/security_helper.php
       2.67K 100%    7.84kB/s    0:00:00 (xfer#332, to-check=94/497)
www/system/helpers/smiley_helper.php
       6.47K 100%   18.96kB/s    0:00:00 (xfer#333, to-check=93/497)
www/system/helpers/string_helper.php
       6.43K 100%   18.87kB/s    0:00:00 (xfer#334, to-check=92/497)
www/system/helpers/text_helper.php
      13.13K 100%   38.40kB/s    0:00:00 (xfer#335, to-check=91/497)
www/system/helpers/typography_helper.php
       2.24K 100%    6.55kB/s    0:00:00 (xfer#336, to-check=90/497)
www/system/helpers/url_helper.php
      12.36K 100%   34.29kB/s    0:00:00 (xfer#337, to-check=89/497)
www/system/helpers/xml_helper.php
       1.79K 100%    4.96kB/s    0:00:00 (xfer#338, to-check=88/497)
www/system/language/
www/system/language/index.html
         114 100%    0.32kB/s    0:00:00 (xfer#339, to-check=87/497)
www/system/language/english/
www/system/language/english/calendar_lang.php
       1.44K 100%    3.99kB/s    0:00:00 (xfer#340, to-check=84/497)
www/system/language/english/date_lang.php
       3.18K 100%    8.81kB/s    0:00:00 (xfer#341, to-check=83/497)
www/system/language/english/db_lang.php
       2.27K 100%    6.31kB/s    0:00:00 (xfer#342, to-check=82/497)
www/system/language/english/email_lang.php
       1.71K 100%    4.74kB/s    0:00:00 (xfer#343, to-check=81/497)
www/system/language/english/form_validation_lang.php
       1.82K 100%    5.05kB/s    0:00:00 (xfer#344, to-check=80/497)
www/system/language/english/ftp_lang.php
       1.28K 100%    3.57kB/s    0:00:00 (xfer#345, to-check=79/497)
www/system/language/english/imglib_lang.php
       2.01K 100%    5.56kB/s    0:00:00 (xfer#346, to-check=78/497)
www/system/language/english/index.html
         114 100%    0.32kB/s    0:00:00 (xfer#347, to-check=77/497)
www/system/language/english/migration_lang.php
         715 100%    1.98kB/s    0:00:00 (xfer#348, to-check=76/497)
www/system/language/english/number_lang.php
         249 100%    0.69kB/s    0:00:00 (xfer#349, to-check=75/497)
www/system/language/english/profiler_lang.php
       1.12K 100%    3.09kB/s    0:00:00 (xfer#350, to-check=74/497)
www/system/language/english/unit_test_lang.php
         808 100%    2.24kB/s    0:00:00 (xfer#351, to-check=73/497)
www/system/language/english/upload_lang.php
       1.62K 100%    4.48kB/s    0:00:00 (xfer#352, to-check=72/497)
www/system/language/french/
www/system/language/french/calendar_lang.php
       1.44K 100%    3.98kB/s    0:00:00 (xfer#353, to-check=71/497)
www/system/language/french/date_lang.php
       3.18K 100%    8.79kB/s    0:00:00 (xfer#354, to-check=70/497)
www/system/language/french/db_lang.php
       2.27K 100%    6.29kB/s    0:00:00 (xfer#355, to-check=69/497)
www/system/language/french/email_lang.php
       1.71K 100%    4.72kB/s    0:00:00 (xfer#356, to-check=68/497)
www/system/language/french/form_validation_lang.php
       2.00K 100%    5.54kB/s    0:00:00 (xfer#357, to-check=67/497)
www/system/language/french/ftp_lang.php
       1.28K 100%    3.54kB/s    0:00:00 (xfer#358, to-check=66/497)
www/system/language/french/imglib_lang.php
       2.01K 100%    5.55kB/s    0:00:00 (xfer#359, to-check=65/497)
www/system/language/french/index.html
         114 100%    0.31kB/s    0:00:00 (xfer#360, to-check=64/497)
www/system/language/french/migration_lang.php
         715 100%    1.97kB/s    0:00:00 (xfer#361, to-check=63/497)
www/system/language/french/number_lang.php
         249 100%    0.63kB/s    0:00:00 (xfer#362, to-check=62/497)
www/system/language/french/profiler_lang.php
       1.12K 100%    2.84kB/s    0:00:00 (xfer#363, to-check=61/497)
www/system/language/french/unit_test_lang.php
         808 100%    2.05kB/s    0:00:00 (xfer#364, to-check=60/497)
www/system/language/french/upload_lang.php
       1.62K 100%    4.12kB/s    0:00:00 (xfer#365, to-check=59/497)
www/system/libraries/
www/system/libraries/Calendar.php
      12.67K 100%   32.21kB/s    0:00:00 (xfer#366, to-check=58/497)
www/system/libraries/Cart.php
      15.07K 100%   38.23kB/s    0:00:00 (xfer#367, to-check=57/497)
www/system/libraries/Driver.php
       5.42K 100%   13.70kB/s    0:00:00 (xfer#368, to-check=56/497)
www/system/libraries/Email.php
      47.97K 100%  121.35kB/s    0:00:00 (xfer#369, to-check=55/497)
www/system/libraries/Encrypt.php
      11.52K 100%   29.07kB/s    0:00:00 (xfer#370, to-check=54/497)
www/system/libraries/Form_validation.php
      29.59K 100%   74.68kB/s    0:00:00 (xfer#371, to-check=53/497)
www/system/libraries/Ftp.php
      12.57K 100%   31.64kB/s    0:00:00 (xfer#372, to-check=52/497)
www/system/libraries/Image_lib.php
      37.34K 100%   93.74kB/s    0:00:00 (xfer#373, to-check=51/497)
www/system/libraries/Javascript.php
      20.12K 100%   50.50kB/s    0:00:00 (xfer#374, to-check=50/497)
www/system/libraries/Log.php
       2.70K 100%    6.77kB/s    0:00:00 (xfer#375, to-check=49/497)
www/system/libraries/Migration.php
       8.23K 100%   20.65kB/s    0:00:00 (xfer#376, to-check=48/497)
www/system/libraries/Pagination.php
       9.05K 100%   22.73kB/s    0:00:00 (xfer#377, to-check=47/497)
www/system/libraries/Parser.php
       4.43K 100%   11.11kB/s    0:00:00 (xfer#378, to-check=46/497)
www/system/libraries/Profiler.php
      19.28K 100%   48.28kB/s    0:00:00 (xfer#379, to-check=45/497)
www/system/libraries/Session.php
      19.22K 100%   47.99kB/s    0:00:00 (xfer#380, to-check=44/497)
www/system/libraries/Sha1.php
       5.00K 100%   12.48kB/s    0:00:00 (xfer#381, to-check=43/497)
www/system/libraries/Table.php
      11.37K 100%   28.40kB/s    0:00:00 (xfer#382, to-check=42/497)
www/system/libraries/Trackback.php
      11.99K 100%   29.96kB/s    0:00:00 (xfer#383, to-check=41/497)
www/system/libraries/Typography.php
      12.72K 100%   31.69kB/s    0:00:00 (xfer#384, to-check=40/497)
www/system/libraries/Unit_test.php
       8.20K 100%   20.43kB/s    0:00:00 (xfer#385, to-check=39/497)
www/system/libraries/Upload.php
      27.55K 100%   68.45kB/s    0:00:00 (xfer#386, to-check=38/497)
www/system/libraries/User_agent.php
      10.51K 100%   26.11kB/s    0:00:00 (xfer#387, to-check=37/497)
www/system/libraries/Xmlrpc.php
      33.57K 100%   83.20kB/s    0:00:00 (xfer#388, to-check=36/497)
www/system/libraries/Xmlrpcs.php
      15.55K 100%   38.55kB/s    0:00:00 (xfer#389, to-check=35/497)
www/system/libraries/Zip.php
      10.16K 100%   25.19kB/s    0:00:00 (xfer#390, to-check=34/497)
www/system/libraries/index.html
         114 100%    0.28kB/s    0:00:00 (xfer#391, to-check=33/497)
www/system/libraries/Cache/
www/system/libraries/Cache/Cache.php
       4.68K 100%   11.57kB/s    0:00:00 (xfer#392, to-check=30/497)
www/system/libraries/Cache/drivers/
www/system/libraries/Cache/drivers/Cache_apc.php
       3.31K 100%    8.18kB/s    0:00:00 (xfer#393, to-check=28/497)
www/system/libraries/Cache/drivers/Cache_dummy.php
       2.66K 100%    6.57kB/s    0:00:00 (xfer#394, to-check=27/497)
www/system/libraries/Cache/drivers/Cache_file.php
       4.15K 100%   10.26kB/s    0:00:00 (xfer#395, to-check=26/497)
www/system/libraries/Cache/drivers/Cache_memcached.php
       5.03K 100%   12.43kB/s    0:00:00 (xfer#396, to-check=25/497)
www/system/libraries/javascript/
www/system/libraries/javascript/Jquery.php
      24.19K 100%   59.51kB/s    0:00:00 (xfer#397, to-check=24/497)
www/tools/
www/tools/README.md
       1.04K 100%    2.56kB/s    0:00:00 (xfer#398, to-check=23/497)
www/tools/spark
         746 100%    1.84kB/s    0:00:00 (xfer#399, to-check=22/497)
www/tools/lib/
www/tools/lib/spark/
www/tools/lib/spark/sources
          68 100%    0.17kB/s    0:00:00 (xfer#400, to-check=18/497)
www/tools/lib/spark/spark_cli.php
       8.74K 100%   21.50kB/s    0:00:00 (xfer#401, to-check=17/497)
www/tools/lib/spark/spark_exception.php
          52 100%    0.13kB/s    0:00:00 (xfer#402, to-check=16/497)
www/tools/lib/spark/spark_source.php
       3.47K 100%    8.54kB/s    0:00:00 (xfer#403, to-check=15/497)
www/tools/lib/spark/spark_type.php
       4.82K 100%   11.85kB/s    0:00:00 (xfer#404, to-check=14/497)
www/tools/lib/spark/spark_utils.php
       2.66K 100%    6.55kB/s    0:00:00 (xfer#405, to-check=13/497)
www/tools/lib/spark/spark_types/
www/tools/lib/spark/spark_types/git_spark.php
       1.27K 100%    3.12kB/s    0:00:00 (xfer#406, to-check=11/497)
www/tools/lib/spark/spark_types/hg_spark.php
       1.04K 100%    2.56kB/s    0:00:00 (xfer#407, to-check=10/497)
www/tools/lib/spark/spark_types/zip_spark.php
       1.27K 100%    3.14kB/s    0:00:00 (xfer#408, to-check=9/497)
www/tools/test/
www/tools/test/install_test.php
       1.87K 100%    4.58kB/s    0:00:00 (xfer#409, to-check=8/497)
www/tools/test/phpunit.xml
         250 100%    0.61kB/s    0:00:00 (xfer#410, to-check=7/497)
www/tools/test/remove_test.php
       2.43K 100%    5.97kB/s    0:00:00 (xfer#411, to-check=6/497)
www/tools/test/search_test.php
         381 100%    0.93kB/s    0:00:00 (xfer#412, to-check=5/497)
www/tools/test/version_test.php
       1.04K 100%    2.55kB/s    0:00:00 (xfer#413, to-check=4/497)
www/tools/test/lib/
www/tools/test/lib/bootstrap.php
         887 100%    2.18kB/s    0:00:00 (xfer#414, to-check=2/497)
www/tools/test/lib/test-sparks/
www/tools/test/lib/test-sparks/.gitkeep
           0 100%    0.00kB/s    0:00:00 (xfer#415, to-check=0/497)

sent 12.25M bytes  received 8.22K bytes  24.52M bytes/sec
total size is 12.22M  speedup is 1.00
Ubuntu's Softwares Setup Menu [Packages and Scripts]
---------------------------- copyright David Fischer

FileXYZ.lu-dep + logicielsUbuntuUtils -> FileXYZ

press any key to continue ...


Bootstrap
=========

FIXME FIXME TODO

Deploy
======

FIXME FIXME TODO

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
oadmin@OSCIED-MAAS-Master:~$ sudo nano /etc/
Display all 177 possibilities? (y or n)
oadmin@OSCIED-MAAS-Master:~$ sudo nano /etc/maas/
dhcpd.conf                          import_pxe_files                    maas-cluster-http.conf              maas_local_celeryconfig_cluster.py  maas_local_settings.py              txlongpoll.yaml
import_ephemerals                   maas_cluster.conf                   maas-http.conf                      maas_local_celeryconfig.py          pserv.yaml                          
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
#IMPORT_EPHEMERALS=1
oadmin@OSCIED-MAAS-Master:~$ sudo maas-import-pxe-files 
Downloading to temporary location /tmp/tmp.i7ZFEQIXnv.
/tmp/tmp.i7ZFEQIXnv ~
2013-08-13 14:05:06 URL:http://archive.ubuntu.com/ubuntu//dists/precise/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//linux [4965840/4965840] -> "linux" [1]
2013-08-13 14:05:07 URL:http://archive.ubuntu.com/ubuntu//dists/precise/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//initrd.gz [17446386/17446386] -> "initrd.gz" [1]
2013-08-13 14:05:08 URL:http://archive.ubuntu.com/ubuntu//dists/quantal/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//linux [5130968/5130968] -> "linux" [1]
2013-08-13 14:05:10 URL:http://archive.ubuntu.com/ubuntu//dists/quantal/main/installer-amd64/current/images/netboot/ubuntu-installer/amd64//initrd.gz [18668122/18668122] -> "initrd.gz" [1]
2013-08-13 14:05:11 URL:http://archive.ubuntu.com/ubuntu//dists/precise/main/installer-i386/current/images/netboot/ubuntu-installer/i386//linux [5015840/5015840] -> "linux" [1]
2013-08-13 14:05:13 URL:http://archive.ubuntu.com/ubuntu//dists/precise/main/installer-i386/current/images/netboot/ubuntu-installer/i386//initrd.gz [15977428/15977428] -> "initrd.gz" [1]
2013-08-13 14:05:14 URL:http://archive.ubuntu.com/ubuntu//dists/quantal/main/installer-i386/current/images/netboot/ubuntu-installer/i386//linux [5171760/5171760] -> "linux" [1]
2013-08-13 14:05:15 URL:http://archive.ubuntu.com/ubuntu//dists/quantal/main/installer-i386/current/images/netboot/ubuntu-installer/i386//initrd.gz [17086667/17086667] -> "initrd.gz" [1]
2013-08-13 14:05:16 URL:http://ports.ubuntu.com/ubuntu-ports//dists/precise-updates/main/installer-armhf/current/images/highbank/netboot//vmlinuz [2978672/2978672] -> "vmlinuz" [1]
2013-08-13 14:05:17 URL:http://ports.ubuntu.com/ubuntu-ports//dists/precise-updates/main/installer-armhf/current/images/highbank/netboot//initrd.gz [4951617/4951617] -> "initrd.gz" [1]
2013-08-13 14:05:18 URL:http://ports.ubuntu.com/ubuntu-ports//dists/quantal/main/installer-armhf/current/images/highbank/netboot//vmlinuz [3738504/3738504] -> "vmlinuz" [1]
2013-08-13 14:05:19 URL:http://ports.ubuntu.com/ubuntu-ports//dists/quantal/main/installer-armhf/current/images/highbank/netboot//initrd.gz [6213909/6213909] -> "initrd.gz" [1]
~
precise/amd64: updating [maas-precise-12.04-amd64-ephemeral-20121008]
--2013-08-13 14:05:19--  https://maas.ubuntu.com/images/ephemeral/releases/precise/release-20121008/precise-ephemeral-maas-amd64.tar.gz
Resolving maas.ubuntu.com (maas.ubuntu.com)... 91.189.90.19, 91.189.89.122
Connecting to maas.ubuntu.com (maas.ubuntu.com)|91.189.90.19|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 272250525 (260M) [application/x-gzip]
Saving to: ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/amd64/dist.tar.gz’

     0K ........ ........ ........ ........ ........ ........  1% 2.40M 1m47s
  3072K ........ ........ ........ ........ ........ ........  2% 2.74M 99s
  6144K ........ ........ ........ ........ ........ ........  3% 2.75M 96s
  9216K ........ ........ ........ ........ ........ ........  4% 3.84M 87s
 12288K ........ ........ ........ ........ ........ ........  5% 4.31M 80s
 15360K ........ ........ ........ ........ ........ ........  6% 4.89M 74s
 18432K ........ ........ ........ ........ ........ ........  8% 5.27M 69s
 21504K ........ ........ ........ ........ ........ ........  9% 6.80M 64s
 24576K ........ ........ ........ ........ ........ ........ 10% 7.75M 60s
 27648K ........ ........ ........ ........ ........ ........ 11% 6.59M 56s
 30720K ........ ........ ........ ........ ........ ........ 12% 6.99M 54s
 33792K ........ ........ ........ ........ ........ ........ 13% 7.37M 51s
 36864K ........ ........ ........ ........ ........ ........ 15% 7.51M 49s
 39936K ........ ........ ........ ........ ........ ........ 16% 6.91M 47s
 43008K ........ ........ ........ ........ ........ ........ 17% 5.34M 46s
 46080K ........ ........ ........ ........ ........ ........ 18% 5.43M 45s
 49152K ........ ........ ........ ........ ........ ........ 19% 5.53M 44s
 52224K ........ ........ ........ ........ ........ ........ 20% 6.37M 43s
 55296K ........ ........ ........ ........ ........ ........ 21% 6.68M 41s
 58368K ........ ........ ........ ........ ........ ........ 23% 6.66M 40s
 61440K ........ ........ ........ ........ ........ ........ 24% 6.75M 39s
 64512K ........ ........ ........ ........ ........ ........ 25% 6.78M 38s
 67584K ........ ........ ........ ........ ........ ........ 26% 6.81M 37s
 70656K ........ ........ ........ ........ ........ ........ 27% 6.94M 36s
 73728K ........ ........ ........ ........ ........ ........ 28% 6.85M 35s
 76800K ........ ........ ........ ........ ........ ........ 30% 7.13M 34s
 79872K ........ ........ ........ ........ ........ ........ 31% 7.07M 33s
 82944K ........ ........ ........ ........ ........ ........ 32% 7.13M 32s
 86016K ........ ........ ........ ........ ........ ........ 33% 7.34M 32s
 89088K ........ ........ ........ ........ ........ ........ 34% 7.34M 31s
 92160K ........ ........ ........ ........ ........ ........ 35% 7.53M 30s
 95232K ........ ........ ........ ........ ........ ........ 36% 7.78M 29s
 98304K ........ ........ ........ ........ ........ ........ 38% 7.63M 28s
101376K ........ ........ ........ ........ ........ ........ 39% 5.44M 28s
104448K ........ ........ ........ ........ ........ ........ 40% 6.14M 27s
107520K ........ ........ ........ ........ ........ ........ 41% 6.98M 27s
110592K ........ ........ ........ ........ ........ ........ 42% 7.24M 26s
113664K ........ ........ ........ ........ ........ ........ 43% 7.21M 25s
116736K ........ ........ ........ ........ ........ ........ 45% 7.46M 25s
119808K ........ ........ ........ ........ ........ ........ 46% 7.57M 24s
122880K ........ ........ ........ ........ ........ ........ 47% 7.57M 23s
125952K ........ ........ ........ ........ ........ ........ 48% 7.72M 23s
129024K ........ ........ ........ ........ ........ ........ 49% 7.71M 22s
132096K ........ ........ ........ ........ ........ ........ 50% 7.73M 21s
135168K ........ ........ ........ ........ ........ ........ 51% 7.66M 21s
138240K ........ ........ ........ ........ ........ ........ 53% 3.54M 21s
141312K ........ ........ ........ ........ ........ ........ 54% 3.10M 21s
144384K ........ ........ ........ ........ ........ ........ 55% 2.87M 20s
147456K ........ ........ ........ ........ ........ ........ 56% 3.80M 20s
150528K ........ ........ ........ ........ ........ ........ 57% 4.03M 20s
153600K ........ ........ ........ ........ ........ ........ 58% 4.12M 19s
156672K ........ ........ ........ ........ ........ ........ 60% 4.52M 19s
159744K ........ ........ ........ ........ ........ ........ 61% 4.89M 18s
162816K ........ ........ ........ ........ ........ ........ 62% 5.02M 18s
165888K ........ ........ ........ ........ ........ ........ 63% 5.07M 17s
168960K ........ ........ ........ ........ ........ ........ 64% 5.25M 17s
172032K ........ ........ ........ ........ ........ ........ 65% 5.16M 16s
175104K ........ ........ ........ ........ ........ ........ 67% 5.35M 16s
178176K ........ ........ ........ ........ ........ ........ 68% 6.38M 15s
181248K ........ ........ ........ ........ ........ ........ 69% 7.42M 14s
184320K ........ ........ ........ ........ ........ ........ 70% 8.30M 14s
187392K ........ ........ ........ ........ ........ ........ 71% 9.46M 13s
190464K ........ ........ ........ ........ ........ ........ 72% 10.2M 13s
193536K ........ ........ ........ ........ ........ ........ 73% 10.9M 12s
196608K ........ ........ ........ ........ ........ ........ 75% 8.49M 11s
199680K ........ ........ ........ ........ ........ ........ 76% 8.97M 11s
202752K ........ ........ ........ ........ ........ ........ 77% 9.55M 10s
205824K ........ ........ ........ ........ ........ ........ 78% 9.99M 10s
208896K ........ ........ ........ ........ ........ ........ 79% 10.3M 9s
211968K ........ ........ ........ ........ ........ ........ 80% 10.3M 8s
215040K ........ ........ ........ ........ ........ ........ 82% 8.09M 8s
218112K ........ ........ ........ ........ ........ ........ 83% 7.43M 7s
221184K ........ ........ ........ ........ ........ ........ 84% 7.65M 7s
224256K ........ ........ ........ ........ ........ ........ 85% 7.85M 6s
227328K ........ ........ ........ ........ ........ ........ 86% 8.01M 6s
230400K ........ ........ ........ ........ ........ ........ 87% 8.12M 5s
233472K ........ ........ ........ ........ ........ ........ 88% 8.21M 5s
236544K ........ ........ ........ ........ ........ ........ 90% 8.13M 4s
239616K ........ ........ ........ ........ ........ ........ 91% 8.28M 4s
242688K ........ ........ ........ ........ ........ ........ 92% 8.22M 3s
245760K ........ ........ ........ ........ ........ ........ 93% 8.25M 3s
248832K ........ ........ ........ ........ ........ ........ 94% 8.52M 2s
251904K ........ ........ ........ ........ ........ ........ 95% 8.84M 2s
254976K ........ ........ ........ ........ ........ ........ 97% 9.15M 1s
258048K ........ ........ ........ ........ ........ ........ 98% 9.30M 1s
261120K ........ ........ ........ ........ ........ ........ 99% 9.47M 0s
264192K ........ ........ ........ ..                        100% 9.35M=42s

2013-08-13 14:06:01 (6.20 MB/s) - ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/amd64/dist.tar.gz’ saved [272250525/272250525]

Tue, 13 Aug 2013 14:06:22 +0200: converting /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/amd64/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/amd64/dist-root.tar.gz
Tue, 13 Aug 2013 14:06:22 +0200: extracting *.img from /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/amd64/dist.tar.gz
precise-ephemeral-maas-amd64.img
Tue, 13 Aug 2013 14:06:55 +0200: copying contents of precise-ephemeral-maas-amd64.img in /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/amd64/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/amd64/dist-root.tar.gz
Tue, 13 Aug 2013 14:07:32 +0200: finished. wrote to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/amd64/dist-root.tar.gz
precise/i386: updating [maas-precise-12.04-i386-ephemeral-20121008]
--2013-08-13 14:07:49--  https://maas.ubuntu.com/images/ephemeral/releases/precise/release-20121008/precise-ephemeral-maas-i386.tar.gz
Resolving maas.ubuntu.com (maas.ubuntu.com)... 91.189.90.19, 91.189.89.122
Connecting to maas.ubuntu.com (maas.ubuntu.com)|91.189.90.19|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 264779988 (253M) [application/x-gzip]
Saving to: ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/i386/dist.tar.gz’

     0K ........ ........ ........ ........ ........ ........  1% 1.60M 2m36s
  3072K ........ ........ ........ ........ ........ ........  2% 2.08M 2m16s
  6144K ........ ........ ........ ........ ........ ........  3% 2.63M 2m1s
  9216K ........ ........ ........ ........ ........ ........  4% 2.45M 1m54s
 12288K ........ ........ ........ ........ ........ ........  5% 5.12M 99s
 15360K ........ ........ ........ ........ ........ ........  7% 4.78M 90s
 18432K ........ ........ ........ ........ ........ ........  8% 5.06M 83s
 21504K ........ ........ ........ ........ ........ ........  9% 5.18M 77s
 24576K ........ ........ ........ ........ ........ ........ 10% 5.26M 72s
 27648K ........ ........ ........ ........ ........ ........ 11% 5.29M 68s
 30720K ........ ........ ........ ........ ........ ........ 13% 5.23M 65s
 33792K ........ ........ ........ ........ ........ ........ 14% 5.38M 62s
 36864K ........ ........ ........ ........ ........ ........ 15% 5.29M 60s
 39936K ........ ........ ........ ........ ........ ........ 16% 5.38M 57s
 43008K ........ ........ ........ ........ ........ ........ 17% 5.36M 55s
 46080K ........ ........ ........ ........ ........ ........ 19% 5.31M 54s
 49152K ........ ........ ........ ........ ........ ........ 20% 5.46M 52s
 52224K ........ ........ ........ ........ ........ ........ 21% 5.55M 50s
 55296K ........ ........ ........ ........ ........ ........ 22% 6.29M 49s
 58368K ........ ........ ........ ........ ........ ........ 23% 6.94M 47s
 61440K ........ ........ ........ ........ ........ ........ 24% 7.18M 45s
 64512K ........ ........ ........ ........ ........ ........ 26% 7.40M 44s
 67584K ........ ........ ........ ........ ........ ........ 27% 8.16M 42s
 70656K ........ ........ ........ ........ ........ ........ 28% 8.68M 40s
 73728K ........ ........ ........ ........ ........ ........ 29% 9.81M 39s
 76800K ........ ........ ........ ........ ........ ........ 30% 10.1M 37s
 79872K ........ ........ ........ ........ ........ ........ 32% 10.3M 36s
 82944K ........ ........ ........ ........ ........ ........ 33% 11.5M 35s
 86016K ........ ........ ........ ........ ........ ........ 34% 11.1M 33s
 89088K ........ ........ ........ ........ ........ ........ 35% 8.50M 32s
 92160K ........ ........ ........ ........ ........ ........ 36% 8.81M 31s
 95232K ........ ........ ........ ........ ........ ........ 38% 9.44M 30s
 98304K ........ ........ ........ ........ ........ ........ 39% 9.71M 29s
101376K ........ ........ ........ ........ ........ ........ 40% 9.87M 28s
104448K ........ ........ ........ ........ ........ ........ 41% 10.7M 27s
107520K ........ ........ ........ ........ ........ ........ 42% 10.6M 26s
110592K ........ ........ ........ ........ ........ ........ 43% 10.7M 26s
113664K ........ ........ ........ ........ ........ ........ 45% 10.8M 25s
116736K ........ ........ ........ ........ ........ ........ 46% 11.0M 24s
119808K ........ ........ ........ ........ ........ ........ 47% 10.1M 23s
122880K ........ ........ ........ ........ ........ ........ 48% 7.27M 22s
125952K ........ ........ ........ ........ ........ ........ 49% 6.92M 22s
129024K ........ ........ ........ ........ ........ ........ 51% 7.19M 21s
132096K ........ ........ ........ ........ ........ ........ 52% 7.25M 21s
135168K ........ ........ ........ ........ ........ ........ 53% 7.47M 20s
138240K ........ ........ ........ ........ ........ ........ 54% 7.45M 19s
141312K ........ ........ ........ ........ ........ ........ 55% 7.55M 19s
144384K ........ ........ ........ ........ ........ ........ 57% 7.64M 18s
147456K ........ ........ ........ ........ ........ ........ 58% 7.53M 18s
150528K ........ ........ ........ ........ ........ ........ 59% 1.44M 18s
153600K ........ ........ ........ ........ ........ ........ 60% 2.66M 18s
156672K ........ ........ ........ ........ ........ ........ 61% 2.08M 18s
159744K ........ ........ ........ ........ ........ ........ 62% 3.01M 18s
162816K ........ ........ ........ ........ ........ ........ 64% 3.93M 17s
165888K ........ ........ ........ ........ ........ ........ 65% 3.17M 17s
168960K ........ ........ ........ ........ ........ ........ 66% 4.13M 16s
172032K ........ ........ ........ ........ ........ ........ 67% 4.58M 16s
175104K ........ ........ ........ ........ ........ ........ 68% 4.86M 15s
178176K ........ ........ ........ ........ ........ ........ 70% 5.21M 15s
181248K ........ ........ ........ ........ ........ ........ 71% 5.97M 14s
184320K ........ ........ ........ ........ ........ ........ 72% 7.26M 13s
187392K ........ ........ ........ ........ ........ ........ 73% 8.28M 13s
190464K ........ ........ ........ ........ ........ ........ 74% 9.61M 12s
193536K ........ ........ ........ ........ ........ ........ 76% 10.3M 11s
196608K ........ ........ ........ ........ ........ ........ 77% 11.1M 11s
199680K ........ ........ ........ ........ ........ ........ 78% 10.5M 10s
202752K ........ ........ ........ ........ ........ ........ 79% 8.34M 10s
205824K ........ ........ ........ ........ ........ ........ 80% 9.25M 9s
208896K ........ ........ ........ ........ ........ ........ 81% 6.82M 8s
211968K ........ ........ ........ ........ ........ ........ 83% 6.95M 8s
215040K ........ ........ ........ ........ ........ ........ 84% 7.11M 7s
218112K ........ ........ ........ ........ ........ ........ 85% 7.40M 7s
221184K ........ ........ ........ ........ ........ ........ 86% 7.18M 6s
224256K ........ ........ ........ ........ ........ ........ 87% 6.02M 6s
227328K ........ ........ ........ ........ ........ ........ 89% 5.21M 5s
230400K ........ ........ ........ ........ ........ ........ 90% 5.15M 4s
233472K ........ ........ ........ ........ ........ ........ 91% 5.42M 4s
236544K ........ ........ ........ ........ ........ ........ 92% 5.32M 3s
239616K ........ ........ ........ ........ ........ ........ 93% 5.38M 3s
242688K ........ ........ ........ ........ ........ ........ 95% 5.54M 2s
245760K ........ ........ ........ ........ ........ ........ 96% 5.51M 2s
248832K ........ ........ ........ ........ ........ ........ 97% 5.77M 1s
251904K ........ ........ ........ ........ ........ ........ 98% 5.52M 1s
254976K ........ ........ ........ ........ ........ ........ 99% 5.11M 0s
258048K ........                                             100% 5.26M=46s

2013-08-13 14:08:35 (5.50 MB/s) - ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/i386/dist.tar.gz’ saved [264779988/264779988]

Tue, 13 Aug 2013 14:08:56 +0200: converting /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/i386/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/i386/dist-root.tar.gz
Tue, 13 Aug 2013 14:08:56 +0200: extracting *.img from /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/i386/dist.tar.gz
precise-ephemeral-maas-i386.img
Tue, 13 Aug 2013 14:09:22 +0200: copying contents of precise-ephemeral-maas-i386.img in /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/i386/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/i386/dist-root.tar.gz
Tue, 13 Aug 2013 14:10:00 +0200: finished. wrote to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/i386/dist-root.tar.gz
precise/armhf: updating [maas-precise-12.04-armhf-ephemeral-20121008]
--2013-08-13 14:10:17--  https://maas.ubuntu.com/images/ephemeral/releases/precise/release-20121008/precise-ephemeral-maas-armhf.tar.gz
Resolving maas.ubuntu.com (maas.ubuntu.com)... 91.189.90.19, 91.189.89.122
Connecting to maas.ubuntu.com (maas.ubuntu.com)|91.189.90.19|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 200228463 (191M) [application/x-gzip]
Saving to: ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/armhf/dist.tar.gz’

     0K ........ ........ ........ ........ ........ ........  1% 1.52M 2m3s
  3072K ........ ........ ........ ........ ........ ........  3% 2.07M 1m45s
  6144K ........ ........ ........ ........ ........ ........  4% 2.59M 93s
  9216K ........ ........ ........ ........ ........ ........  6% 3.21M 82s
 12288K ........ ........ ........ ........ ........ ........  7% 4.54M 72s
 15360K ........ ........ ........ ........ ........ ........  9% 5.19M 65s
 18432K ........ ........ ........ ........ ........ ........ 10% 6.47M 58s
 21504K ........ ........ ........ ........ ........ ........ 12% 7.71M 53s
 24576K ........ ........ ........ ........ ........ ........ 14% 9.07M 48s
 27648K ........ ........ ........ ........ ........ ........ 15% 7.42M 45s
 30720K ........ ........ ........ ........ ........ ........ 17% 6.95M 42s
 33792K ........ ........ ........ ........ ........ ........ 18% 7.13M 40s
 36864K ........ ........ ........ ........ ........ ........ 20% 7.48M 37s
 39936K ........ ........ ........ ........ ........ ........ 21% 7.96M 35s
 43008K ........ ........ ........ ........ ........ ........ 23% 8.06M 34s
 46080K ........ ........ ........ ........ ........ ........ 25% 8.32M 32s
 49152K ........ ........ ........ ........ ........ ........ 26% 8.74M 30s
 52224K ........ ........ ........ ........ ........ ........ 28% 8.99M 29s
 55296K ........ ........ ........ ........ ........ ........ 29% 9.05M 28s
 58368K ........ ........ ........ ........ ........ ........ 31% 9.16M 26s
 61440K ........ ........ ........ ........ ........ ........ 32% 9.19M 25s
 64512K ........ ........ ........ ........ ........ ........ 34% 9.19M 24s
 67584K ........ ........ ........ ........ ........ ........ 36% 9.26M 23s
 70656K ........ ........ ........ ........ ........ ........ 37% 8.89M 22s
 73728K ........ ........ ........ ........ ........ ........ 39% 9.24M 21s
 76800K ........ ........ ........ ........ ........ ........ 40% 9.22M 20s
 79872K ........ ........ ........ ........ ........ ........ 42% 9.03M 19s
 82944K ........ ........ ........ ........ ........ ........ 43% 9.26M 19s
 86016K ........ ........ ........ ........ ........ ........ 45% 8.99M 18s
 89088K ........ ........ ........ ........ ........ ........ 47% 9.29M 17s
 92160K ........ ........ ........ ........ ........ ........ 48% 9.20M 16s
 95232K ........ ........ ........ ........ ........ ........ 50% 9.43M 16s
 98304K ........ ........ ........ ........ ........ ........ 51% 9.27M 15s
101376K ........ ........ ........ ........ ........ ........ 53% 9.60M 14s
104448K ........ ........ ........ ........ ........ ........ 54% 9.80M 14s
107520K ........ ........ ........ ........ ........ ........ 56% 9.88M 13s
110592K ........ ........ ........ ........ ........ ........ 58% 10.2M 13s
113664K ........ ........ ........ ........ ........ ........ 59% 10.6M 12s
116736K ........ ........ ........ ........ ........ ........ 61% 11.0M 11s
119808K ........ ........ ........ ........ ........ ........ 62% 11.1M 11s
122880K ........ ........ ........ ........ ........ ........ 64% 11.1M 10s
125952K ........ ........ ........ ........ ........ ........ 65% 11.1M 10s
129024K ........ ........ ........ ........ ........ ........ 67% 10.2M 9s
132096K ........ ........ ........ ........ ........ ........ 69% 8.07M 9s
135168K ........ ........ ........ ........ ........ ........ 70% 9.03M 8s
138240K ........ ........ ........ ........ ........ ........ 72% 9.36M 8s
141312K ........ ........ ........ ........ ........ ........ 73% 10.1M 7s
144384K ........ ........ ........ ........ ........ ........ 75% 10.1M 7s
147456K ........ ........ ........ ........ ........ ........ 76% 10.4M 6s
150528K ........ ........ ........ ........ ........ ........ 78% 8.22M 6s
153600K ........ ........ ........ ........ ........ ........ 80% 5.61M 5s
156672K ........ ........ ........ ........ ........ ........ 81% 6.70M 5s
159744K ........ ........ ........ ........ ........ ........ 83% 6.96M 5s
162816K ........ ........ ........ ........ ........ ........ 84% 7.17M 4s
165888K ........ ........ ........ ........ ........ ........ 86% 7.10M 4s
168960K ........ ........ ........ ........ ........ ........ 87% 7.29M 3s
172032K ........ ........ ........ ........ ........ ........ 89% 7.21M 3s
175104K ........ ........ ........ ........ ........ ........ 91% 7.22M 2s
178176K ........ ........ ........ ........ ........ ........ 92% 7.24M 2s
181248K ........ ........ ........ ........ ........ ........ 94% 7.49M 2s
184320K ........ ........ ........ ........ ........ ........ 95% 7.64M 1s
187392K ........ ........ ........ ........ ........ ........ 97% 7.77M 1s
190464K ........ ........ ........ ........ ........ ........ 98% 7.83M 0s
193536K ........ ........ ........ .......                   100% 7.68M=27s

2013-08-13 14:10:44 (7.03 MB/s) - ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/armhf/dist.tar.gz’ saved [200228463/200228463]

Tue, 13 Aug 2013 14:10:58 +0200: converting /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/armhf/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/armhf/dist-root.tar.gz
Tue, 13 Aug 2013 14:10:58 +0200: extracting *.img from /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/armhf/dist.tar.gz
precise-ephemeral-maas-armhf.img
Tue, 13 Aug 2013 14:11:23 +0200: copying contents of precise-ephemeral-maas-armhf.img in /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/armhf/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/armhf/dist-root.tar.gz
Tue, 13 Aug 2013 14:11:52 +0200: finished. wrote to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/precise/armhf/dist-root.tar.gz
quantal/amd64: updating [maas-quantal-12.10-amd64-ephemeral-20121017]
--2013-08-13 14:12:05--  https://maas.ubuntu.com/images/ephemeral/releases/quantal/release-20121017/quantal-ephemeral-maas-amd64.tar.gz
Resolving maas.ubuntu.com (maas.ubuntu.com)... 91.189.90.19, 91.189.89.122
Connecting to maas.ubuntu.com (maas.ubuntu.com)|91.189.90.19|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 291203883 (278M) [application/x-gzip]
Saving to: ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/amd64/dist.tar.gz’

     0K ........ ........ ........ ........ ........ ........  1% 1.26M 3m39s
  3072K ........ ........ ........ ........ ........ ........  2% 1.52M 3m17s
  6144K ........ ........ ........ ........ ........ ........  3% 2.13M 2m52s
  9216K ........ ........ ........ ........ ........ ........  4% 2.49M 2m34s
 12288K ........ ........ ........ ........ ........ ........  5% 2.62M 2m22s
 15360K ........ ........ ........ ........ ........ ........  6% 2.67M 2m13s
 18432K ........ ........ ........ ........ ........ ........  7% 3.42M 2m4s
 21504K ........ ........ ........ ........ ........ ........  8% 4.57M 1m54s
 24576K ........ ........ ........ ........ ........ ........  9% 5.26M 1m45s
 27648K ........ ........ ........ ........ ........ ........ 10% 6.46M 98s
 30720K ........ ........ ........ ........ ........ ........ 11% 7.66M 90s
 33792K ........ ........ ........ ........ ........ ........ 12% 8.90M 84s
 36864K ........ ........ ........ ........ ........ ........ 14% 10.3M 79s
 39936K ........ ........ ........ ........ ........ ........ 15% 10.9M 74s
 43008K ........ ........ ........ ........ ........ ........ 16% 10.5M 69s
 46080K ........ ........ ........ ........ ........ ........ 17% 8.39M 66s
 49152K ........ ........ ........ ........ ........ ........ 18% 8.70M 63s
 52224K ........ ........ ........ ........ ........ ........ 19% 9.33M 60s
 55296K ........ ........ ........ ........ ........ ........ 20% 9.79M 57s
 58368K ........ ........ ........ ........ ........ ........ 21% 9.67M 55s
 61440K ........ ........ ........ ........ ........ ........ 22% 9.99M 52s
 64512K ........ ........ ........ ........ ........ ........ 23% 10.2M 50s
 67584K ........ ........ ........ ........ ........ ........ 24% 10.7M 48s
 70656K ........ ........ ........ ........ ........ ........ 25% 10.9M 46s
 73728K ........ ........ ........ ........ ........ ........ 27% 10.9M 44s
 76800K ........ ........ ........ ........ ........ ........ 28% 11.0M 43s
 79872K ........ ........ ........ ........ ........ ........ 29% 10.9M 41s
 82944K ........ ........ ........ ........ ........ ........ 30% 11.1M 40s
 86016K ........ ........ ........ ........ ........ ........ 31% 11.1M 38s
 89088K ........ ........ ........ ........ ........ ........ 32% 11.2M 37s
 92160K ........ ........ ........ ........ ........ ........ 33% 10.9M 36s
 95232K ........ ........ ........ ........ ........ ........ 34% 11.1M 35s
 98304K ........ ........ ........ ........ ........ ........ 35% 11.1M 34s
101376K ........ ........ ........ ........ ........ ........ 36% 11.0M 33s
104448K ........ ........ ........ ........ ........ ........ 37% 11.3M 32s
107520K ........ ........ ........ ........ ........ ........ 38% 11.0M 31s
110592K ........ ........ ........ ........ ........ ........ 39% 11.1M 30s
113664K ........ ........ ........ ........ ........ ........ 41% 9.09M 29s
116736K ........ ........ ........ ........ ........ ........ 42% 8.10M 28s
119808K ........ ........ ........ ........ ........ ........ 43% 9.21M 27s
122880K ........ ........ ........ ........ ........ ........ 44% 9.31M 26s
125952K ........ ........ ........ ........ ........ ........ 45% 9.95M 26s
129024K ........ ........ ........ ........ ........ ........ 46% 10.2M 25s
132096K ........ ........ ........ ........ ........ ........ 47% 10.3M 24s
135168K ........ ........ ........ ........ ........ ........ 48% 10.5M 24s
138240K ........ ........ ........ ........ ........ ........ 49% 10.7M 23s
141312K ........ ........ ........ ........ ........ ........ 50% 10.9M 22s
144384K ........ ........ ........ ........ ........ ........ 51% 11.1M 21s
147456K ........ ........ ........ ........ ........ ........ 52% 9.57M 21s
150528K ........ ........ ........ ........ ........ ........ 54% 7.22M 20s
153600K ........ ........ ........ ........ ........ ........ 55% 7.26M 20s
156672K ........ ........ ........ ........ ........ ........ 56% 5.47M 19s
159744K ........ ........ ........ ........ ........ ........ 57% 5.16M 19s
162816K ........ ........ ........ ........ ........ ........ 58% 5.23M 19s
165888K ........ ........ ........ ........ ........ ........ 59% 5.38M 18s
168960K ........ ........ ........ ........ ........ ........ 60% 5.36M 18s
172032K ........ ........ ........ ........ ........ ........ 61% 5.40M 17s
175104K ........ ........ ........ ........ ........ ........ 62% 5.43M 17s
178176K ........ ........ ........ ........ ........ ........ 63% 5.51M 16s
181248K ........ ........ ........ ........ ........ ........ 64% 4.72M 16s
184320K ........ ........ ........ ........ ........ ........ 65% 2.38M 16s
187392K ........ ........ ........ ........ ........ ........ 66% 4.05M 15s
190464K ........ ........ ........ ........ ........ ........ 68% 4.06M 15s
193536K ........ ........ ........ ........ ........ ........ 69% 4.35M 15s
196608K ........ ........ ........ ........ ........ ........ 70% 4.89M 14s
199680K ........ ........ ........ ........ ........ ........ 71% 4.98M 14s
202752K ........ ........ ........ ........ ........ ........ 72% 5.06M 13s
205824K ........ ........ ........ ........ ........ ........ 73% 5.16M 13s
208896K ........ ........ ........ ........ ........ ........ 74% 5.17M 12s
211968K ........ ........ ........ ........ ........ ........ 75% 5.36M 12s
215040K ........ ........ ........ ........ ........ ........ 76% 5.33M 11s
218112K ........ ........ ........ ........ ........ ........ 77% 5.49M 11s
221184K ........ ........ ........ ........ ........ ........ 78% 6.72M 10s
224256K ........ ........ ........ ........ ........ ........ 79% 7.41M 10s
227328K ........ ........ ........ ........ ........ ........ 81% 8.10M 9s
230400K ........ ........ ........ ........ ........ ........ 82% 7.80M 8s
233472K ........ ........ ........ ........ ........ ........ 83% 6.49M 8s
236544K ........ ........ ........ ........ ........ ........ 84% 7.21M 7s
239616K ........ ........ ........ ........ ........ ........ 85% 7.70M 7s
242688K ........ ........ ........ ........ ........ ........ 86% 7.80M 6s
245760K ........ ........ ........ ........ ........ ........ 87% 8.18M 6s
248832K ........ ........ ........ ........ ........ ........ 88% 8.19M 5s
251904K ........ ........ ........ ........ ........ ........ 89% 8.68M 5s
254976K ........ ........ ........ ........ ........ ........ 90% 6.49M 4s
258048K ........ ........ ........ ........ ........ ........ 91% 5.10M 4s
261120K ........ ........ ........ ........ ........ ........ 92% 5.31M 3s
264192K ........ ........ ........ ........ ........ ........ 93% 5.36M 3s
267264K ........ ........ ........ ........ ........ ........ 95% 5.34M 2s
270336K ........ ........ ........ ........ ........ ........ 96% 5.46M 2s
273408K ........ ........ ........ ........ ........ ........ 97% 5.48M 1s
276480K ........ ........ ........ ........ ........ ........ 98% 5.54M 1s
279552K ........ ........ ........ ........ ........ ........ 99% 6.32M 0s
282624K ........ ........ ........ ...                       100% 6.96M=47s

2013-08-13 14:12:52 (5.93 MB/s) - ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/amd64/dist.tar.gz’ saved [291203883/291203883]

Tue, 13 Aug 2013 14:13:24 +0200: converting /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/amd64/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/amd64/dist-root.tar.gz
Tue, 13 Aug 2013 14:13:24 +0200: extracting *.img from /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/amd64/dist.tar.gz
quantal-ephemeral-maas-amd64.img
Tue, 13 Aug 2013 14:13:56 +0200: copying contents of quantal-ephemeral-maas-amd64.img in /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/amd64/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/amd64/dist-root.tar.gz
Tue, 13 Aug 2013 14:14:42 +0200: finished. wrote to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/amd64/dist-root.tar.gz
quantal/i386: updating [maas-quantal-12.10-i386-ephemeral-20121017]
--2013-08-13 14:15:00--  https://maas.ubuntu.com/images/ephemeral/releases/quantal/release-20121017/quantal-ephemeral-maas-i386.tar.gz
Resolving maas.ubuntu.com (maas.ubuntu.com)... 91.189.90.19, 91.189.89.122
Connecting to maas.ubuntu.com (maas.ubuntu.com)|91.189.90.19|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 296554192 (283M) [application/x-gzip]
Saving to: ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/i386/dist.tar.gz’

     0K ........ ........ ........ ........ ........ ........  1% 2.25M 2m4s
  3072K ........ ........ ........ ........ ........ ........  2% 2.65M 1m54s
  6144K ........ ........ ........ ........ ........ ........  3% 2.77M 1m48s
  9216K ........ ........ ........ ........ ........ ........  4% 3.32M 1m40s
 12288K ........ ........ ........ ........ ........ ........  5% 4.13M 92s
 15360K ........ ........ ........ ........ ........ ........  6% 4.54M 86s
 18432K ........ ........ ........ ........ ........ ........  7% 2.31M 89s
 21504K ........ ........ ........ ........ ........ ........  8% 3.74M 86s
 24576K ........ ........ ........ ........ ........ ........  9% 3.85M 83s
 27648K ........ ........ ........ ........ ........ ........ 10% 3.92M 80s
 30720K ........ ........ ........ ........ ........ ........ 11% 3.95M 78s
 33792K ........ ........ ........ ........ ........ ........ 12% 4.18M 75s
 36864K ........ ........ ........ ........ ........ ........ 13% 4.22M 73s
 39936K ........ ........ ........ ........ ........ ........ 14% 4.71M 71s
 43008K ........ ........ ........ ........ ........ ........ 15% 4.70M 68s
 46080K ........ ........ ........ ........ ........ ........ 16% 4.78M 66s
 49152K ........ ........ ........ ........ ........ ........ 18% 4.92M 64s
 52224K ........ ........ ........ ........ ........ ........ 19% 5.17M 63s
 55296K ........ ........ ........ ........ ........ ........ 20% 5.55M 61s
 58368K ........ ........ ........ ........ ........ ........ 21% 6.79M 58s
 61440K ........ ........ ........ ........ ........ ........ 22% 7.55M 56s
 64512K ........ ........ ........ ........ ........ ........ 23% 8.28M 54s
 67584K ........ ........ ........ ........ ........ ........ 24% 9.79M 52s
 70656K ........ ........ ........ ........ ........ ........ 25% 10.4M 50s
 73728K ........ ........ ........ ........ ........ ........ 26% 11.1M 48s
 76800K ........ ........ ........ ........ ........ ........ 27% 11.2M 46s
 79872K ........ ........ ........ ........ ........ ........ 28% 8.75M 45s
 82944K ........ ........ ........ ........ ........ ........ 29% 8.23M 43s
 86016K ........ ........ ........ ........ ........ ........ 30% 9.75M 42s
 89088K ........ ........ ........ ........ ........ ........ 31% 9.75M 41s
 92160K ........ ........ ........ ........ ........ ........ 32% 10.1M 39s
 95232K ........ ........ ........ ........ ........ ........ 33% 10.4M 38s
 98304K ........ ........ ........ ........ ........ ........ 35% 10.7M 37s
101376K ........ ........ ........ ........ ........ ........ 36% 10.9M 36s
104448K ........ ........ ........ ........ ........ ........ 37% 10.9M 35s
107520K ........ ........ ........ ........ ........ ........ 38% 11.1M 33s
110592K ........ ........ ........ ........ ........ ........ 39% 11.1M 32s
113664K ........ ........ ........ ........ ........ ........ 40% 11.0M 31s
116736K ........ ........ ........ ........ ........ ........ 41% 11.1M 30s
119808K ........ ........ ........ ........ ........ ........ 42% 10.9M 29s
122880K ........ ........ ........ ........ ........ ........ 43% 11.2M 29s
125952K ........ ........ ........ ........ ........ ........ 44% 8.37M 28s
129024K ........ ........ ........ ........ ........ ........ 45% 8.34M 27s
132096K ........ ........ ........ ........ ........ ........ 46% 9.05M 26s
135168K ........ ........ ........ ........ ........ ........ 47% 9.18M 26s
138240K ........ ........ ........ ........ ........ ........ 48% 9.22M 25s
141312K ........ ........ ........ ........ ........ ........ 49% 9.31M 24s
144384K ........ ........ ........ ........ ........ ........ 50% 9.80M 23s
147456K ........ ........ ........ ........ ........ ........ 51% 9.48M 23s
150528K ........ ........ ........ ........ ........ ........ 53% 9.76M 22s
153600K ........ ........ ........ ........ ........ ........ 54% 9.91M 21s
156672K ........ ........ ........ ........ ........ ........ 55% 1.45M 22s
159744K ........ ........ ........ ........ ........ ........ 56% 1.37M 23s
162816K ........ ........ ........ ........ ........ ........ 57% 2.12M 23s
165888K ........ ........ ........ ........ ........ ........ 58% 2.07M 23s
168960K ........ ........ ........ ........ ........ ........ 59% 4.31M 23s
172032K ........ ........ ........ ........ ........ ........ 60% 5.15M 22s
175104K ........ ........ ........ ........ ........ ........ 61% 6.16M 21s
178176K ........ ........ ........ ........ ........ ........ 62% 7.49M 21s
181248K ........ ........ ........ ........ ........ ........ 63% 8.79M 20s
184320K ........ ........ ........ ........ ........ ........ 64% 10.0M 19s
187392K ........ ........ ........ ........ ........ ........ 65% 11.0M 18s
190464K ........ ........ ........ ........ ........ ........ 66% 10.8M 18s
193536K ........ ........ ........ ........ ........ ........ 67% 8.58M 17s
196608K ........ ........ ........ ........ ........ ........ 68% 9.29M 16s
199680K ........ ........ ........ ........ ........ ........ 70% 9.83M 16s
202752K ........ ........ ........ ........ ........ ........ 71% 10.1M 15s
205824K ........ ........ ........ ........ ........ ........ 72% 10.3M 14s
208896K ........ ........ ........ ........ ........ ........ 73% 10.8M 14s
211968K ........ ........ ........ ........ ........ ........ 74% 10.8M 13s
215040K ........ ........ ........ ........ ........ ........ 75% 11.0M 12s
218112K ........ ........ ........ ........ ........ ........ 76% 11.1M 12s
221184K ........ ........ ........ ........ ........ ........ 77% 11.2M 11s
224256K ........ ........ ........ ........ ........ ........ 78% 11.1M 11s
227328K ........ ........ ........ ........ ........ ........ 79% 11.0M 10s
230400K ........ ........ ........ ........ ........ ........ 80% 11.1M 9s
233472K ........ ........ ........ ........ ........ ........ 81% 11.2M 9s
236544K ........ ........ ........ ........ ........ ........ 82% 10.1M 8s
239616K ........ ........ ........ ........ ........ ........ 83% 9.02M 8s
242688K ........ ........ ........ ........ ........ ........ 84% 8.39M 7s
245760K ........ ........ ........ ........ ........ ........ 85% 9.07M 7s
248832K ........ ........ ........ ........ ........ ........ 86% 9.25M 6s
251904K ........ ........ ........ ........ ........ ........ 88% 9.35M 6s
254976K ........ ........ ........ ........ ........ ........ 89% 9.37M 5s
258048K ........ ........ ........ ........ ........ ........ 90% 9.78M 5s
261120K ........ ........ ........ ........ ........ ........ 91% 9.89M 4s
264192K ........ ........ ........ ........ ........ ........ 92% 9.87M 4s
267264K ........ ........ ........ ........ ........ ........ 93% 9.92M 3s
270336K ........ ........ ........ ........ ........ ........ 94% 9.83M 3s
273408K ........ ........ ........ ........ ........ ........ 95% 9.86M 2s
276480K ........ ........ ........ ........ ........ ........ 96% 9.79M 2s
279552K ........ ........ ........ ........ ........ ........ 97% 10.0M 1s
282624K ........ ........ ........ ........ ........ ........ 98% 6.34M 1s
285696K ........ ........ ........ ........ ........ ........ 99% 5.55M 0s
288768K ........ .....                                       100% 7.19M=46s

2013-08-13 14:15:46 (6.20 MB/s) - ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/i386/dist.tar.gz’ saved [296554192/296554192]

Tue, 13 Aug 2013 14:16:17 +0200: converting /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/i386/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/i386/dist-root.tar.gz
Tue, 13 Aug 2013 14:16:17 +0200: extracting *.img from /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/i386/dist.tar.gz
quantal-ephemeral-maas-i386.img
Tue, 13 Aug 2013 14:16:48 +0200: copying contents of quantal-ephemeral-maas-i386.img in /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/i386/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/i386/dist-root.tar.gz
Tue, 13 Aug 2013 14:17:35 +0200: finished. wrote to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/i386/dist-root.tar.gz
quantal/armhf: updating [maas-quantal-12.10-armhf-ephemeral-20121017]
--2013-08-13 14:17:51--  https://maas.ubuntu.com/images/ephemeral/releases/quantal/release-20121017/quantal-ephemeral-maas-armhf.tar.gz
Resolving maas.ubuntu.com (maas.ubuntu.com)... 91.189.90.19, 91.189.89.122
Connecting to maas.ubuntu.com (maas.ubuntu.com)|91.189.90.19|:443... connected.
HTTP request sent, awaiting response... 200 OK
Length: 251417816 (240M) [application/x-gzip]
Saving to: ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist.tar.gz’

     0K ........ ........ ........ ........ ........ ........  1% 1.13M 3m30s
  3072K ........ ........ ........ ........ ........ ........  2% 1.85M 2m47s
  6144K ........ ........ ........ ........ ........ ........  3% 2.57M 2m20s
  9216K ........ ........ ........ ........ ........ ........  5% 2.63M 2m5s
 12288K ........ ........ ........ ........ ........ ........  6% 2.68M 1m56s
 15360K ........ ........ ........ ........ ........ ........  7% 2.98M 1m47s
 18432K ........ ........ ........ ........ ........ ........  8% 4.40M 98s
 21504K ........ ........ ........ ........ ........ ........ 10% 4.97M 90s
 24576K ........ ........ ........ ........ ........ ........ 11% 6.34M 83s
 27648K ........ ........ ........ ........ ........ ........ 12% 7.39M 76s
 30720K ........ ........ ........ ........ ........ ........ 13% 9.23M 70s
 33792K ........ ........ ........ ........ ........ ........ 15% 10.2M 65s
 36864K ........ ........ ........ ........ ........ ........ 16% 10.8M 61s
 39936K ........ ........ ........ ........ ........ ........ 17% 10.7M 57s
 43008K ........ ........ ........ ........ ........ ........ 18% 8.35M 54s
 46080K ........ ........ ........ ........ ........ ........ 20% 8.67M 51s
 49152K ........ ........ ........ ........ ........ ........ 21% 8.25M 49s
 52224K ........ ........ ........ ........ ........ ........ 22% 7.73M 46s
 55296K ........ ........ ........ ........ ........ ........ 23% 7.98M 45s
 58368K ........ ........ ........ ........ ........ ........ 25% 7.91M 43s
 61440K ........ ........ ........ ........ ........ ........ 26% 8.05M 41s
 64512K ........ ........ ........ ........ ........ ........ 27% 8.14M 40s
 67584K ........ ........ ........ ........ ........ ........ 28% 8.32M 38s
 70656K ........ ........ ........ ........ ........ ........ 30% 8.64M 37s
 73728K ........ ........ ........ ........ ........ ........ 31% 8.97M 35s
 76800K ........ ........ ........ ........ ........ ........ 32% 9.16M 34s
 79872K ........ ........ ........ ........ ........ ........ 33% 9.29M 33s
 82944K ........ ........ ........ ........ ........ ........ 35% 9.28M 32s
 86016K ........ ........ ........ ........ ........ ........ 36% 9.56M 30s
 89088K ........ ........ ........ ........ ........ ........ 37% 9.64M 29s
 92160K ........ ........ ........ ........ ........ ........ 38% 9.57M 28s
 95232K ........ ........ ........ ........ ........ ........ 40% 10.7M 27s
 98304K ........ ........ ........ ........ ........ ........ 41% 10.8M 26s
101376K ........ ........ ........ ........ ........ ........ 42% 10.9M 25s
104448K ........ ........ ........ ........ ........ ........ 43% 11.1M 24s
107520K ........ ........ ........ ........ ........ ........ 45% 10.4M 24s
110592K ........ ........ ........ ........ ........ ........ 46% 9.11M 23s
113664K ........ ........ ........ ........ ........ ........ 47% 9.27M 22s
116736K ........ ........ ........ ........ ........ ........ 48% 9.48M 21s
119808K ........ ........ ........ ........ ........ ........ 50% 9.89M 21s
122880K ........ ........ ........ ........ ........ ........ 51% 10.5M 20s
125952K ........ ........ ........ ........ ........ ........ 52% 10.7M 19s
129024K ........ ........ ........ ........ ........ ........ 53% 10.9M 18s
132096K ........ ........ ........ ........ ........ ........ 55% 11.0M 18s
135168K ........ ........ ........ ........ ........ ........ 56% 11.1M 17s
138240K ........ ........ ........ ........ ........ ........ 57% 11.0M 16s
141312K ........ ........ ........ ........ ........ ........ 58% 11.2M 16s
144384K ........ ........ ........ ........ ........ ........ 60% 11.1M 15s
147456K ........ ........ ........ ........ ........ ........ 61% 9.59M 15s
150528K ........ ........ ........ ........ ........ ........ 62% 8.01M 14s
153600K ........ ........ ........ ........ ........ ........ 63% 5.64M 14s
156672K ........ ........ ........ ........ ........ ........ 65% 5.20M 13s
159744K ........ ........ ........ ........ ........ ........ 66% 2.98M 13s
162816K ........ ........ ........ ........ ........ ........ 67% 4.09M 13s
165888K ........ ........ ........ ........ ........ ........ 68% 4.08M 12s
168960K ........ ........ ........ ........ ........ ........ 70% 4.41M 12s
172032K ........ ........ ........ ........ ........ ........ 71% 4.88M 11s
175104K ........ ........ ........ ........ ........ ........ 72% 4.91M 11s
178176K ........ ........ ........ ........ ........ ........ 73% 1.41M 11s
181248K ........ ........ ........ ........ ........ ........ 75% 1.56M 11s
184320K ........ ........ ........ ........ ........ ........ 76% 2.28M 11s
187392K ........ ........ ........ ........ ........ ........ 77% 2.67M 10s
190464K ........ ........ ........ ........ ........ ........ 78% 2.94M 10s
193536K ........ ........ ........ ........ ........ ........ 80% 4.43M 9s
196608K ........ ........ ........ ........ ........ ........ 81% 5.14M 9s
199680K ........ ........ ........ ........ ........ ........ 82% 6.51M 8s
202752K ........ ........ ........ ........ ........ ........ 83% 7.83M 7s
205824K ........ ........ ........ ........ ........ ........ 85% 9.10M 7s
208896K ........ ........ ........ ........ ........ ........ 86% 10.2M 6s
211968K ........ ........ ........ ........ ........ ........ 87% 11.2M 6s
215040K ........ ........ ........ ........ ........ ........ 88% 10.4M 5s
218112K ........ ........ ........ ........ ........ ........ 90% 8.97M 4s
221184K ........ ........ ........ ........ ........ ........ 91% 9.09M 4s
224256K ........ ........ ........ ........ ........ ........ 92% 9.59M 3s
227328K ........ ........ ........ ........ ........ ........ 93% 10.1M 3s
230400K ........ ........ ........ ........ ........ ........ 95% 10.4M 2s
233472K ........ ........ ........ ........ ........ ........ 96% 10.7M 2s
236544K ........ ........ ........ ........ ........ ........ 97% 10.8M 1s
239616K ........ ........ ........ ........ ........ ........ 98% 11.0M 0s
242688K ........ ........ ........ ........ ........ ....    100% 11.2M=42s

2013-08-13 14:18:34 (5.65 MB/s) - ‘/var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist.tar.gz’ saved [251417816/251417816]

Tue, 13 Aug 2013 14:19:01 +0200: converting /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist-root.tar.gz
Tue, 13 Aug 2013 14:19:01 +0200: extracting *.img from /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist.tar.gz
quantal-ephemeral-maas-armhf.img
Tue, 13 Aug 2013 14:19:30 +0200: copying contents of quantal-ephemeral-maas-armhf.img in /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist.tar.gz to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist-root.tar.gz
Tue, 13 Aug 2013 14:20:02 +0200: finished. wrote to /var/lib/maas/ephemeral/.working/maas-import-ephemerals.AjwDJW/quantal/armhf/dist-root.tar.gz
oadmin@OSCIED-MAAS-Master:~$ 

