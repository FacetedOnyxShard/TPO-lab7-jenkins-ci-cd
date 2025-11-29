#!/bin/bash

# FIND_FILE_CMD="find ./romulus -name "*.static.mtd""
# IMAGE=$($FIND_FILE_CMD)
# echo $IMAGE

# mkdir -p ./tmp

qemu-system-arm -m 256 -M romulus-bmc \
-nographic -drive file=./romulus/obmc-phosphor-image-romulus-20250916112422.static.mtd,format=raw,if=mtd \
-net nic \
-net user,hostfwd=tcp::2222-:22,hostfwd=tcp::2443-:443,hostfwd=udp::2623-:623,hostname=qemu \
> /dev/null
# > ./tmp/qemu.log 2>&1 &