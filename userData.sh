#!/bin/bash
mkdir -p /home/ubuntu/mount_point ;
# Delaing volume operations to ensure it was attached by the main script
sleep 70;
# Redirecting stOut and stIn to a file
sudo mkfs -t xfs /dev/xvdh  >> /home/ubuntu/log.txt 2>&1
sudo mount /dev/xvdh  /home/ubuntu/mount_point >> /home/ubuntu/log.txt 2>&1 