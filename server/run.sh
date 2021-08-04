#!/bin/sh

# Assign an IP address to local loopback
ifconfig lo 127.0.0.1

# Add a hosts record, pointing API endpoint to local loopback
echo "127.0.0.1   kms.ap-northeast-1.amazonaws.com" >> /etc/hosts

# Set library path to app directory for libnsm.so
#pip3 install aws_encryption_sdk
echo "HELLO"
cat /proc/sys/kernel/random/entropy_avail
rngd -r /dev/urandom
sleep 10
cat /proc/sys/kernel/random/entropy_avail
aws-encryption-cli --version
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/app

aws-encryption-cli --version
# Run traffic forwarder in background and start the server
nohup python3 /app/traffic-forwarder.py 443 3 8000 &
echo "TRAFFIC-FORWARDER"
python3 /app/server.py
echo "SERVER"

#python3 /app/run.py



