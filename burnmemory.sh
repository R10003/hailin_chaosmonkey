#!/bin/bash


mkdir /tmp/memory
mount -t tmpfs -o size=$2M tmpfs /tmp/memory
dd if=/dev/zero of=/tmp/memory/block &

sleep $1

ps -ef|grep "dd if=/dev/zero of=/tmp/memory/block"|grep -v grep |awk '{print "kill -9 " $2}'|sh
echo $?

sleep 3
rm -rf /tmp/memory/block
sleep 3
umount /tmp/memory

sleep 10
rm -rf  /tmp/memory
