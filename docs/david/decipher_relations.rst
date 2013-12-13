========================
State machine of a charm
========================

-----------------------
Step-by step deployment
-----------------------

One unit connected to a requirer after the started state.

::
    juju deploy oscied-storage storage
    juju deploy oscied-publisher publisher

unit storage/0 : install, config changed, start

::
    juju add-relation publisher storage

unit storage/0: storage joined

::
    juju remove-relation publisher storage

unit storage/0: storage departed, config changed

::
    juju add-relation publisher storage

unit storage/0: storage joined

::
    juju add-unit storage

==== ================
Unit State
==== ================
1    install
1    config changed
1    start
1    peer joined
0    peer joined
0    peer changed
1    peer changed
1    storage joined
1    peer changed
0    peer changed
==== ================

::
    juju remove-relation publisher storage

==== ================
Unit State
==== ================
1    storage departed
0    storage departed
0    config changed
1    config changed
==== ================

----------------
Bunch deployment
----------------

Two storage units deployed at the same time // the requirer.

The logging method::

    def relations_decipher(self, hook_name):
        self.info(u'{0} {1}'.format(hook_name, self.name))
        self.info(u'LIST "{0}"'.format(self.relation_list()))
        for relation in (u'peer', u'storage'):
            for rel_id in self.relation_ids(relation):
                    self.info(u'LIST FOR RELID {0} = {1}'.format(rel_id, self.relation_list(rel_id)))


::
    juju deploy oscied-storage -n 2 storage
    juju deploy oscied-publisher publisher
    juju add-relation publisher storage


Remark: err = error: no relation name specified

==== ================  =============  ========================  ============================
Unit State             list default   list(id) id in ids[peer]  list(id) id in ids[storage]
==== ================  =============  ========================  ============================
1    install           err            []                        []
1    config changed    err            []                        []
1    start             err            []                        []
0    install           err            []                        []
0    config changed    err            []                        []
0    start             err            []                        []
1    peer joined       [storage/0]    [peer:0] -> [storage/0]   [storage:1] -> []
0    peer joined       [storage/1]    [peer:0] -> [storage/1]   [storage:1] -> []
0    peer changed      [storage/1]    [peer:0] -> [storage/1]   [storage:1] -> []
1    peer changed      [storage/0]    [peer:0] -> [storage/0]   [storage:1] -> []
1    storage joined    [publisher/0]  [peer:0] -> [storage/0]   [storage:1] -> [publisher/0]
0    storage joined    [publisher/0]  [peer:0] -> [storage/1]   [storage:1] -> [publisher/0]
==== ================  =============  =======================   ============================

The log
=======

With some cleanup.

::
    in the rest of the log replaced by replaced by "..." :
    oscied-storage/1: [DEBUG] Execute unit-get private-address
    oscied-storage/1: [DEBUG] Execute unit-get public-address
    oscied-storage/1: [DEBUG] Using juju True, reason: Life is good !
    oscied-storage/1: [DEBUG] Load metadatas from file metadata.yaml


    oscied-storage/1: [HOOK] Execute StorageHooks hook install
    oscied-storage/1: [INFO] INSTALL oscied-storage/1
    oscied-storage/1: [DEBUG] Execute relation-list --format json
    oscied-storage/1: [DEBUG] Attempt 1 out of 1: Failed
    oscied-storage/1: [INFO] LIST "{u'process': <subprocess.Popen object at 0x1d4afd0>, u'returncode': 2, u'stderr': 'error: no relation id specified\n', u'stdout': ''}"
    oscied-storage/1: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/1: [DEBUG] Execute relation-ids --format json storage
    oscied-storage/1: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/1: [HOOK] Exiting StorageHooks hook install

    ...
    oscied-storage/1: [HOOK] Execute StorageHooks hook config-changed
    oscied-storage/1: [INFO] CONFIG CHANGED oscied-storage/1
    oscied-storage/1: [DEBUG] Execute relation-list --format json
    oscied-storage/1: [DEBUG] Attempt 1 out of 1: Failed
    oscied-storage/1: [INFO] LIST "{u'process': <subprocess.Popen object at 0x2671290>, u'returncode': 2, u'stderr': 'error: no relation id specified\n', u'stdout': ''}"
    oscied-storage/1: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/1: [DEBUG] Execute relation-ids --format json storage
    oscied-storage/1: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/1: [HOOK] Exiting StorageHooks hook config-changed

    ...
    oscied-storage/1: [HOOK] Execute StorageHooks hook start
    oscied-storage/1: [INFO] START oscied-storage/1
    oscied-storage/1: [DEBUG] Execute relation-list --format json
    oscied-storage/1: [DEBUG] Attempt 1 out of 1: Failed
    oscied-storage/1: [INFO] LIST "{u'process': <subprocess.Popen object at 0x2f34350>, u'returncode': 2, u'stderr': 'error: no relation id specified\n', u'stdout': ''}"
    oscied-storage/1: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/1: [DEBUG] Execute relation-ids --format json storage
    oscied-storage/1: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/1: [HOOK] Exiting StorageHooks hook start

    ...
    oscied-publisher/0: [HOOK] Execute PublisherHooks hook install
    oscied-publisher/0: [INFO] Uninstall prerequisities, unregister service and load default configuration
    oscied-publisher/0: [INFO] Stop the publisher worker
    oscied-publisher/0: [DEBUG] Execute service publisher stop
    oscied-publisher/0: [DEBUG] Attempt 1 out of 1: Failed

    ...
    oscied-storage/0: [HOOK] Execute StorageHooks hook install
    oscied-storage/0: [INFO] INSTALL oscied-storage/0
    oscied-storage/0: [DEBUG] Execute relation-list --format json
    oscied-storage/0: [DEBUG] Attempt 1 out of 1: Failed
    oscied-storage/0: [INFO] LIST "{u'process': <subprocess.Popen object at 0x2ba7fd0>, u'returncode': 2, u'stderr': 'error: no relation id specified\n', u'stdout': ''}"
    oscied-storage/0: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/0: [DEBUG] Execute relation-ids --format json storage
    oscied-storage/0: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/0: [HOOK] Exiting StorageHooks hook install

    ...
    oscied-storage/0: [HOOK] Execute StorageHooks hook config-changed
    oscied-storage/0: [INFO] CONFIG CHANGED oscied-storage/0
    oscied-storage/0: [DEBUG] Execute relation-list --format json
    oscied-storage/0: [DEBUG] Attempt 1 out of 1: Failed
    oscied-storage/0: [INFO] LIST "{u'process': <subprocess.Popen object at 0x1dd9290>, u'returncode': 2, u'stderr': 'error: no relation id specified\n', u'stdout': ''}"
    oscied-storage/0: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/0: [DEBUG] Execute relation-ids --format json storage
    oscied-storage/0: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/0: [HOOK] Exiting StorageHooks hook config-changed

    ...
    oscied-storage/0: [HOOK] Execute StorageHooks hook start
    oscied-storage/0: [INFO] START oscied-storage/0
    oscied-storage/0: [DEBUG] Execute relation-list --format json
    oscied-storage/0: [DEBUG] Attempt 1 out of 1: Failed
    oscied-storage/0: [INFO] LIST "{u'process': <subprocess.Popen object at 0x21fc350>, u'returncode': 2, u'stderr': 'error: no relation id specified\n', u'stdout': ''}"
    oscied-storage/0: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/0: [DEBUG] Execute relation-ids --format json storage
    oscied-storage/0: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/0: [HOOK] Exiting StorageHooks hook start

    ...
    oscied-storage/1 peer:0: [HOOK] Execute StorageHooks hook peer-relation-joined
    oscied-storage/1 peer:0: [INFO] PEER RELATION JOINED oscied-storage/1
    oscied-storage/1 peer:0: [DEBUG] Execute relation-list --format json
    oscied-storage/1 peer:0: [INFO] LIST "[u'oscied-storage/0']"
    oscied-storage/1 peer:0: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/1 peer:0: [DEBUG] Execute relation-list --format json -r peer:0
    oscied-storage/1 peer:0: [INFO] LIST FOR RELID peer:0 = [u'oscied-storage/0']
    oscied-storage/1 peer:0: [DEBUG] Execute relation-ids --format json storage
    oscied-storage/1 peer:0: [DEBUG] Execute relation-list --format json -r storage:1
    oscied-storage/1 peer:0: [INFO] LIST FOR RELID storage:1 = []
    oscied-storage/1 peer:0: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/1 peer:0: [HOOK] Exiting StorageHooks hook peer-relation-joined


    oscied-publisher/0: [DEBUG] Execute service apache2 stop
    oscied-publisher/0: [DEBUG] Attempt 1 out of 1: Failed
    oscied-publisher/0: [INFO] Unregister shared storage
    oscied-publisher/0: [REMARK] Shared storage already unmounted !
    oscied-publisher/0: [INFO] Unregister the Orchestrator
    oscied-publisher/0: [DEBUG] Execute update-rc.d -f publisher remove
    oscied-publisher/0: [INFO] Generate locales if missing
    oscied-publisher/0: [DEBUG] Execute locale-gen fr_CH.UTF-8
    oscied-publisher/0: [DEBUG] Execute dpkg-reconfigure locales
    oscied-publisher/0: [INFO] Upgrade system and install prerequisites
    oscied-publisher/0: [DEBUG] Execute apt-add-repository -y ppa:jon-severinsson/ffmpeg
    oscied-publisher/0: [DEBUG] Execute apt-get -y update
    oscied-publisher/0: [DEBUG] Execute apt-get -y -f install
    oscied-publisher/0: [DEBUG] Execute apt-get -y upgrade

    ...
    oscied-storage/0 peer:0: [HOOK] Execute StorageHooks hook peer-relation-joined
    oscied-storage/0 peer:0: [INFO] PEER RELATION JOINED oscied-storage/0
    oscied-storage/0 peer:0: [DEBUG] Execute relation-list --format json
    oscied-storage/0 peer:0: [INFO] LIST "[u'oscied-storage/1']"
    oscied-storage/0 peer:0: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/0 peer:0: [DEBUG] Execute relation-list --format json -r peer:0
    oscied-storage/0 peer:0: [INFO] LIST FOR RELID peer:0 = [u'oscied-storage/1']
    oscied-storage/0 peer:0: [DEBUG] Execute relation-ids --format json storage
    oscied-storage/0 peer:0: [DEBUG] Execute relation-list --format json -r storage:1
    oscied-storage/0 peer:0: [INFO] LIST FOR RELID storage:1 = []
    oscied-storage/0 peer:0: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/0 peer:0: [HOOK] Exiting StorageHooks hook peer-relation-joined

    ...
    oscied-storage/0 peer:0: [HOOK] Execute StorageHooks hook peer-relation-changed
    oscied-storage/0 peer:0: [INFO] PEER RELATION CHANGED oscied-storage/0
    oscied-storage/0 peer:0: [DEBUG] Execute relation-list --format json
    oscied-storage/0 peer:0: [INFO] LIST "[u'oscied-storage/1']"
    oscied-storage/0 peer:0: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/0 peer:0: [DEBUG] Execute relation-list --format json -r peer:0
    oscied-storage/0 peer:0: [INFO] LIST FOR RELID peer:0 = [u'oscied-storage/1']
    oscied-storage/0 peer:0: [DEBUG] Execute relation-ids --format json storage
    oscied-storage/0 peer:0: [DEBUG] Execute relation-list --format json -r storage:1
    oscied-storage/0 peer:0: [INFO] LIST FOR RELID storage:1 = []
    oscied-storage/0 peer:0: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/0 peer:0: [HOOK] Exiting StorageHooks hook peer-relation-changed

    ...
    oscied-storage/1 peer:0: [HOOK] Execute StorageHooks hook peer-relation-changed
    oscied-storage/1 peer:0: [INFO] PEER RELATION CHANGED oscied-storage/1
    oscied-storage/1 peer:0: [DEBUG] Execute relation-list --format json
    oscied-storage/1 peer:0: [INFO] LIST "[u'oscied-storage/0']"
    oscied-storage/1 peer:0: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/1 peer:0: [DEBUG] Execute relation-list --format json -r peer:0
    oscied-storage/1 peer:0: [INFO] LIST FOR RELID storage:1 = []
    oscied-storage/1 peer:0: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/1 peer:0: [HOOK] Exiting StorageHooks hook peer-relation-changed

    oscied-publisher/0: [DEBUG] Execute apt-get -y install glusterfs-client nfs-common ntp make apache2 apache2-threaded-dev
    oscied-publisher/0: [INFO] Restart network time protocol service
    oscied-publisher/0: [DEBUG] Execute service ntp restart

    ...
    oscied-storage/1 storage:1: [HOOK] Execute StorageHooks hook storage-relation-joined
    oscied-storage/1 storage:1: [INFO] STORAGE RELATION JOINED oscied-storage/1
    oscied-storage/1 storage:1: [DEBUG] Execute relation-list --format json
    oscied-storage/1 storage:1: [INFO] LIST "[u'oscied-publisher/0']"
    oscied-storage/1 storage:1: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/1 storage:1: [DEBUG] Execute relation-list --format json -r peer:0
    oscied-storage/1 storage:1: [INFO] LIST FOR RELID peer:0 = [u'oscied-storage/0']
    oscied-storage/1 storage:1: [DEBUG] Execute relation-ids --format json storage
    oscied-storage/1 storage:1: [DEBUG] Execute relation-list --format json -r storage:1
    oscied-storage/1 storage:1: [INFO] LIST FOR RELID storage:1 = [u'oscied-publisher/0']
    oscied-storage/1 storage:1: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/1 storage:1: [HOOK] Exiting StorageHooks hook storage-relation-joined

    oscied-publisher/0: [INFO] Expose Apache 2 service
    oscied-publisher/0: [DEBUG] Execute open-port 80/TCP
    oscied-publisher/0: [DEBUG] Save (updated) local configuration {'storage_mount_max_retry': 5, 'storage_options': u'', 'verbose': False, 'publish_uri': u'http://ip-172-31-16-198.eu-west-1.compute.internal', 'celery_init_template_file': u'templates/celeryd.init.template', 'apache_config_file': u'/etc/apache2/apache2.conf', 'celery_config_file': u'celeryconfig.py', 'site_ssl_file': u'/etc/apache2/sites-available/default-ssl', 'storage_path': u'/mnt/storage', 'storage_mountpoint': u'', 'proxy_ips': [], '_json_filename': u'local_config.json', 'mod_streaming_installed': False, 'storage_address': u'', 'site_template_file': u'templates/default.template', 'hosts_file': u'/etc/hosts', 'storage_mount_sleep_delay': 5, 'storage_nat_address': u'', 'storage_fstype': u'', 'www_root_path': u'/mnt', 'site_file': u'/etc/apache2/sites-available/default', 'celery_default_template_file': u'templates/celeryd.default.template', 'celery_config_template_file': u'templates/celeryconfig.py.template', 'site_ssl_template_file': u'templates/default-ssl.template', 'api_nat_socket': u''}
    oscied-publisher/0: [HOOK] Exiting PublisherHooks hook install

    ...
    oscied-publisher/0: [HOOK] Execute PublisherHooks hook config-changed
    oscied-publisher/0: [INFO] Configure Apache 2
    oscied-publisher/0: [INFO] Disable Apache H.264 streaming module
    oscied-publisher/0: [REMARK] File /etc/apache2/sites-available/default successfully generated !
    oscied-publisher/0: [REMARK] File /etc/apache2/sites-available/default-ssl successfully generated !
    oscied-publisher/0: [DEBUG] Save (updated) local configuration {'storage_mount_max_retry': 5, 'storage_options': u'', 'verbose': False, 'publish_uri': u'http://ip-172-31-16-198.eu-west-1.compute.internal', 'celery_init_template_file': u'templates/celeryd.init.template', 'apache_config_file': u'/etc/apache2/apache2.conf', 'celery_config_file': u'celeryconfig.py', 'site_ssl_file': u'/etc/apache2/sites-available/default-ssl', 'storage_path': u'/mnt/storage', 'storage_mountpoint': u'', 'proxy_ips': [], '_json_filename': u'local_config.json', 'mod_streaming_installed': False, 'storage_address': u'', 'site_template_file': u'templates/default.template', 'hosts_file': u'/etc/hosts', 'storage_mount_sleep_delay': 5, 'storage_nat_address': u'', 'storage_fstype': u'', 'www_root_path': u'/mnt', 'site_file': u'/etc/apache2/sites-available/default', 'celery_default_template_file': u'templates/celeryd.default.template', 'celery_config_template_file': u'templates/celeryconfig.py.template', 'site_ssl_template_file': u'templates/default-ssl.template', 'api_nat_socket': u''}
    oscied-publisher/0: [HOOK] Exiting PublisherHooks hook config-changed

    ...
    oscied-publisher/0: [HOOK] Execute PublisherHooks hook start
    oscied-publisher/0: [REMARK] Do not start publisher daemon : No shared storage !
    oscied-publisher/0: [DEBUG] Save (updated) local configuration {'storage_mount_max_retry': 5, 'storage_options': u'', 'verbose': False, 'publish_uri': u'http://ip-172-31-16-198.eu-west-1.compute.internal', 'celery_init_template_file': u'templates/celeryd.init.template', 'apache_config_file': u'/etc/apache2/apache2.conf', 'celery_config_file': u'celeryconfig.py', 'site_ssl_file': u'/etc/apache2/sites-available/default-ssl', 'storage_path': u'/mnt/storage', 'storage_mountpoint': u'', 'proxy_ips': [], '_json_filename': u'local_config.json', 'mod_streaming_installed': False, 'storage_address': u'', 'site_template_file': u'templates/default.template', 'hosts_file': u'/etc/hosts', 'storage_mount_sleep_delay': 5, 'storage_nat_address': u'', 'storage_fstype': u'', 'www_root_path': u'/mnt', 'site_file': u'/etc/apache2/sites-available/default', 'celery_default_template_file': u'templates/celeryd.default.template', 'celery_config_template_file': u'templates/celeryconfig.py.template', 'site_ssl_template_file': u'templates/default-ssl.template', 'api_nat_socket': u''}
    oscied-publisher/0: [HOOK] Exiting PublisherHooks hook start

    ...
    oscied-publisher/0 storage:1: [HOOK] Execute PublisherHooks hook storage-relation-joined
    oscied-publisher/0 storage:1: [DEBUG] Save (updated) local configuration {'storage_mount_max_retry': 5, 'storage_options': u'', 'verbose': False, 'publish_uri': u'http://ip-172-31-16-198.eu-west-1.compute.internal', 'celery_init_template_file': u'templates/celeryd.init.template', 'apache_config_file': u'/etc/apache2/apache2.conf', 'celery_config_file': u'celeryconfig.py', 'site_ssl_file': u'/etc/apache2/sites-available/default-ssl', 'storage_path': u'/mnt/storage', 'storage_mountpoint': u'', 'proxy_ips': [], '_json_filename': u'local_config.json', 'mod_streaming_installed': False, 'storage_address': u'', 'site_template_file': u'templates/default.template', 'hosts_file': u'/etc/hosts', 'storage_mount_sleep_delay': 5, 'storage_nat_address': u'', 'storage_fstype': u'', 'www_root_path': u'/mnt', 'site_file': u'/etc/apache2/sites-available/default', 'celery_default_template_file': u'templates/celeryd.default.template', 'celery_config_template_file': u'templates/celeryconfig.py.template', 'site_ssl_template_file': u'templates/default-ssl.template', 'api_nat_socket': u''}
    oscied-publisher/0 storage:1: [HOOK] Exiting PublisherHooks hook storage-relation-joined

    ...
    oscied-publisher/0 storage:1: [HOOK] Execute PublisherHooks hook storage-relation-changed
    oscied-publisher/0 storage:1: [DEBUG] Execute relation-get private-address
    oscied-publisher/0 storage:1: [DEBUG] Execute relation-get fstype
    oscied-publisher/0 storage:1: [DEBUG] Execute relation-get mountpoint
    oscied-publisher/0 storage:1: [DEBUG] Execute relation-get options
    oscied-publisher/0 storage:1: [DEBUG] Storage address is ip-172-31-18-17.eu-west-1.compute.internal, fstype: , mountpoint: , options:
    oscied-publisher/0 storage:1: [REMARK] Waiting for complete setup !
    oscied-publisher/0 storage:1: [DEBUG] Save (updated) local configuration {'storage_mount_max_retry': 5, 'storage_options': u'', 'verbose': False, 'publish_uri': u'http://ip-172-31-16-198.eu-west-1.compute.internal', 'celery_init_template_file': u'templates/celeryd.init.template', 'apache_config_file': u'/etc/apache2/apache2.conf', 'celery_config_file': u'celeryconfig.py', 'site_ssl_file': u'/etc/apache2/sites-available/default-ssl', 'storage_path': u'/mnt/storage', 'storage_mountpoint': u'', 'proxy_ips': [], '_json_filename': u'local_config.json', 'mod_streaming_installed': False, 'storage_address': u'', 'site_template_file': u'templates/default.template', 'hosts_file': u'/etc/hosts', 'storage_mount_sleep_delay': 5, 'storage_nat_address': u'', 'storage_fstype': u'', 'www_root_path': u'/mnt', 'site_file': u'/etc/apache2/sites-available/default', 'celery_default_template_file': u'templates/celeryd.default.template', 'celery_config_template_file': u'templates/celeryconfig.py.template', 'site_ssl_template_file': u'templates/default-ssl.template', 'api_nat_socket': u''}
    oscied-publisher/0 storage:1: [HOOK] Exiting PublisherHooks hook storage-relation-changed

    ...
    oscied-storage/0 storage:1: [HOOK] Execute StorageHooks hook storage-relation-joined
    oscied-storage/0 storage:1: [INFO] STORAGE RELATION JOINED oscied-storage/0
    oscied-storage/0 storage:1: [DEBUG] Execute relation-list --format json
    oscied-storage/0 storage:1: [INFO] LIST "[u'oscied-publisher/0']"
    oscied-storage/0 storage:1: [DEBUG] Execute relation-ids --format json peer
    oscied-storage/0 storage:1: [DEBUG] Execute relation-list --format json -r peer:0
    oscied-storage/0 storage:1: [INFO] LIST FOR RELID peer:0 = [u'oscied-storage/1']
    oscied-storage/0 storage:1: [DEBUG] Execute relation-ids --format json storage
    oscied-storage/0 storage:1: [DEBUG] Execute relation-list --format json -r storage:1
    oscied-storage/0 storage:1: [INFO] LIST FOR RELID storage:1 = [u'oscied-publisher/0']
    oscied-storage/0 storage:1: [DEBUG] Save (updated) local configuration {'volume_flag': False, 'allowed_ips': [], 'verbose': True, '_json_filename': u'local_config.json'}
    oscied-storage/0 storage:1: [HOOK] Exiting StorageHooks hook storage-relation-joined

    ...
    oscied-publisher/0 storage:1: [HOOK] Execute PublisherHooks hook storage-relation-joined
    oscied-publisher/0 storage:1: [DEBUG] Save (updated) local configuration {'storage_mount_max_retry': 5, 'storage_options': u'', 'verbose': False, 'publish_uri': u'http://ip-172-31-16-198.eu-west-1.compute.internal', 'celery_init_template_file': u'templates/celeryd.init.template', 'apache_config_file': u'/etc/apache2/apache2.conf', 'celery_config_file': u'celeryconfig.py', 'site_ssl_file': u'/etc/apache2/sites-available/default-ssl', 'storage_path': u'/mnt/storage', 'storage_mountpoint': u'', 'proxy_ips': [], '_json_filename': u'local_config.json', 'mod_streaming_installed': False, 'storage_address': u'', 'site_template_file': u'templates/default.template', 'hosts_file': u'/etc/hosts', 'storage_mount_sleep_delay': 5, 'storage_nat_address': u'', 'storage_fstype': u'', 'www_root_path': u'/mnt', 'site_file': u'/etc/apache2/sites-available/default', 'celery_default_template_file': u'templates/celeryd.default.template', 'celery_config_template_file': u'templates/celeryconfig.py.template', 'site_ssl_template_file': u'templates/default-ssl.template', 'api_nat_socket': u''}
    oscied-publisher/0 storage:1: [HOOK] Exiting PublisherHooks hook storage-relation-joined

    ...
    oscied-publisher/0 storage:1: [HOOK] Execute PublisherHooks hook storage-relation-changed
    oscied-publisher/0 storage:1: [DEBUG] Execute relation-get private-address
    oscied-publisher/0 storage:1: [DEBUG] Execute relation-get fstype
    oscied-publisher/0 storage:1: [DEBUG] Execute relation-get mountpoint
    oscied-publisher/0 storage:1: [DEBUG] Execute relation-get options
    oscied-publisher/0 storage:1: [DEBUG] Storage address is ip-172-31-28-67.eu-west-1.compute.internal, fstype: , mountpoint: , options:
    oscied-publisher/0 storage:1: [REMARK] Waiting for complete setup !
    oscied-publisher/0 storage:1: [DEBUG] Save (updated) local configuration {'storage_mount_max_retry': 5, 'storage_options': u'', 'verbose': False, 'publish_uri': u'http://ip-172-31-16-198.eu-west-1.compute.internal', 'celery_init_template_file': u'templates/celeryd.init.template', 'apache_config_file': u'/etc/apache2/apache2.conf', 'celery_config_file': u'celeryconfig.py', 'site_ssl_file': u'/etc/apache2/sites-available/default-ssl', 'storage_path': u'/mnt/storage', 'storage_mountpoint': u'', 'proxy_ips': [], '_json_filename': u'local_config.json', 'mod_streaming_installed': False, 'storage_address': u'', 'site_template_file': u'templates/default.template', 'hosts_file': u'/etc/hosts', 'storage_mount_sleep_delay': 5, 'storage_nat_address': u'', 'storage_fstype': u'', 'www_root_path': u'/mnt', 'site_file': u'/etc/apache2/sites-available/default', 'celery_default_template_file': u'templates/celeryd.default.template', 'celery_config_template_file': u'templates/celeryconfig.py.template', 'site_ssl_template_file': u'templates/default-ssl.template', 'api_nat_socket': u''}
    oscied-publisher/0 storage:1: [HOOK] Exiting PublisherHooks hook storage-relation-changed
