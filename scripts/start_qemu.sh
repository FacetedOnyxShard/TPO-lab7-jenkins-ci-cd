#!/bin/bash

FIND_FILE_CMD="find ./romulus -name "*.static.mtd""
IMAGE=$($FIND_FILE_CMD)

mkdir -p ./tmp

qemu-system-arm -m 256 -M romulus-bmc \
-nographic -drive file=$IMAGE,format=raw,if=mtd \
-net nic \
-net user,hostfwd=tcp::2222-:22,hostfwd=tcp::2443-:443,hostfwd=udp::2623-:623,hostname=qemu \
> ./tmp/qemu.log 2>&1 &
