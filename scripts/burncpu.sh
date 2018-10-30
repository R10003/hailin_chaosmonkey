#!/bin/bash
# Script for BurnCpu Chaos Monkey

cat << EOF > /tmp/infiniteburn.sh
#!/bin/bash
while true;
    do openssl speed;
done
EOF
chmod 774 /tmp/infiniteburn.sh
# 32 parallel 100% CPU tasks should hit even the biggest EC2 instances
for((i=1;i<=$2;i++));
do
    nohup timeout $1 /bin/bash /tmp/infiniteburn.sh &
done