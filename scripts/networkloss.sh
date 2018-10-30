#!/bin/bash
# Script for NetworkLoss Chaos Monkey

# Drops 7% of packets, with 25% correlation with previous packet loss
# 7% is high, but it isn't high enough that TCP will fail entirely
netdev=`ip addr |grep 'state UP'|awk '{print $2}'`
tc qdisc add dev $netdev root netem loss $2%
sleep $1
tc qd del dev $netdev root netem


# tc qd show

