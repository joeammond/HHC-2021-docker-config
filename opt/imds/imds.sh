#!/bin/sh
# Configure networking
ip addr add 169.254.169.254/32 dev lo

# Start EC2 metadata-mock instance
/opt/imds/ec2-metadata -c /opt/imds/config.json

