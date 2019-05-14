#! /bin/bash -ex

#Install LAMP server and update 
yum update -y
yum groupinstall -y "Web Server" "MySQL Database" "PHP Support"
yum install -y git wget

#Start HTTPD
service httpd start
chkconfig httpd on

#Define WWW group and add users
groupadd www
usermod -a -G www ec2-user
chown -R root:www /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} +
find /var/www/ -type f -exec chmod 0664 {} +

#Disable SElinux
sed -i 's/enforcing/disabled/g' /etc/selinux/config /etc/selinux/config

#Disable Firewalld
service firewalld stop
chkconfig firewalld off

#Create a PHP page with the following commands:
echo "<?php phpinfo(); ?>" > /var/www/html/phpinfo.php

#create a default web page 
cp /usr/share/httpd/noindex/index.html /var/www/html/index.html

