#!/bin/bash
set -o errexit

rm -fv test-volume.img

dd if=/dev/zero of=test-volume.img bs=$((1024*1024)) count=1 
/sbin/mke2fs -F test-volume.img
mkdir --parents test-volume
sudo mount -t ext2 test-volume.img test-volume/ -o loop
sudo chmod a+rwx test-volume
echo test-volume mounted
