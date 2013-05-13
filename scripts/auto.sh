# Simple helper to speed-up LXC containers
sudo umount /var/lib/lxc
sudo mount -t tmpfs -o size=3072M tmpfs /var/lib/lxc

# This is a temporary utility to speed-up testing of charms
lu-importUtils ../charms/
sh juju-menu.sh overwrite
sh juju-menu.sh
