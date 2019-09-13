#! /bin/bash
echo $1  ALL=\(ALL:ALL\) NOPASSWD:ALL >> /etc/sudoers
mkdir /etc/skel/.ssh
chmod 700 /etc/skel/.ssh
useradd -G admin -m --skel /etc/skel/ $1
cd /home/$1/.ssh
wget https://s3.amazonaws.com/zabbix.ipsense/public-key/$1.pub
mv $1.pub authorized_keys
chmod 600 authorized_keys
chown $1:$1 authorized_keys

