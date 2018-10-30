#!/bin/bash
# Script for NetworkLatency Chaos Monkey
netdev=`ip addr |grep 'state UP'|awk '{print $2}'`
# Adds 1000ms +- 500ms of latency to each packet
tc qdisc add dev $netdev root netem  delay $2ms
sleep $1
tc qd del dev $netdev root netem


# tc qd show