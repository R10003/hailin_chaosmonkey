#!/bin/bash
# Script for BurnIO Chaos Monkey

cat << EOF > /tmp/loopburnio.sh
#!/bin/bash
while true;
do
    dd if=/dev/urandom of=$2 bs=1M count=1024 iflag=fullblock
done
EOF

nohup timeout $1 /bin/bash /tmp/loopburnio.sh &
sleep $1
sleep 2
rm -rf $2