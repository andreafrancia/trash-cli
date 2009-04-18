#!/bin/bash
# mount-test-volume: mount the test volume in the current dir
#
# Copyright (C) 2007-2009 Andrea Francia Trivolzio(PV) Italy
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  
# 02110-1301, USA.

set -o errexit

device_image="$(dirname "$0")/test-volume.img"
mount_point="$(dirname "$0")/test-volume"

# clean up
sudo umount "$mount_point" || true
rm -fv "$device_image"

# prepare a fresh device image
dd if=/dev/zero of="$device_image" bs=$((1024*1024)) count=1 
/sbin/mke2fs -F "$device_image"

# mount
mkdir --parents "$mount_point"
sudo mount -t ext2 "$device_image" "$mount_point" -o loop
sudo chmod a+rwx "$mount_point"

echo "test-volume mounted as '$mount_point'"
