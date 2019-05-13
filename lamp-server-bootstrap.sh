#! /bin/bash -ex
yum update -y
yum groupinstall -y "Web Server" "MySQL Database" "PHP Support"
yum install -y git wget
service httpd start
chkconfig httpd on
groupadd www
usermod -a -G www ec2-user
chown -R root:www /var/www
chmod 2775 /var/www
find /var/www -type d -exec chmod 2775 {} +
find /var/www/ -type f -exec chmod 0664 {} +
cd /var/www/html
git clone https://github.com/cordeiromarco/webresume.git

#Create a PHP page with the following commands:
echo "<?php phpinfo(); ?>" > /var/www/html/phpinfo.php
