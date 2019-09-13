#! /bin/bash
# Run me with superuser privileges
echo 'admin	ALL=(ALL:ALL) ALL' >> /etc/sudoers
mkdir /etc/skel/.ssh
chmod 700 /etc/skel/.ssh
useradd -G admin -m --skel /etc/skel/ $1
su - $1
cd ./.ssh
wget https://s3.amazonaws.com/zabbix.ipsense/public-key/$1.pub
mv $1.pub authorized_keys
chmod 600 authorized_keys
