#!/bin/sh
# Dynamically update the IP address to bind to in nginx.conf using eth0's current IP
echo "Nginx startup script"
ip addr show dev eth0 | grep "inet " | awk '{print $2}' | sed 's/\/.*//'
ETH0IP=`ip addr show dev eth0 | grep "inet " | awk '{print $2}' | sed 's/\/.*//'`
echo $ETH0IP
sed -i "s/##ETH0IP##/$ETH0IP/" /etc/nginx/nginx.conf
grep listen /etc/nginx/nginx.conf
nginx -g 'daemon off;'

