#!/bin/bash
instanceId=$(curl http://169.254.169.254/latest/meta-data/instance-id)
region=$(curl http://169.254.169.254/latest/dynamic/instance-identity/document | grep region | awk -F\" '{print $4}')
echo "<h1>$instanceId</h1>" " " "<h1>$region</h1>" > /var/www/html/index.html
