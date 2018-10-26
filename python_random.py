# !/usr/bin/env python
# encoding: utf-8
import ConfigParser
import re
import time
from ConfigParser import NoSectionError, NoOptionError
import random
import paramiko


class ChaosMonkey(object):
    def __init__(self, node, node_user, node_password):
        self.node = node
        self.node_user = node_user
        self.node_password = node_password
        self.port = 22

    def burn_cpu(self, time, percent):
        time = int(time)
        percent = int(percent)
        cmd = 'cat /proc/cpuinfo| grep "processor"| wc -l'
        core_cpu, err = self.login_node_exec_cmd(cmd)
        if err:
            print 'exec cmd %s error:%s ' % (cmd, err)
        core_cpu = int(core_cpu)
        burn_count = int(percent / 100.0 * core_cpu)
        cmd = './burncpu.sh %d %d > burncpu.log 2>&1 &' % (time, burn_count)
        self.login_node_exec_cmd(cmd)

    def burn_io(self, time, percent):
        time = int(time)
        percent = int(percent)
        cmd = './burnio.sh %d > burnio.log 2>&1 &' % time
        self.login_node_exec_cmd(cmd)

    def burn_mem(self, time, percent):
        time = int(time)
        percent = int(percent)
        cmd = "free -m |grep Mem| awk '{print $2}'"
        total_mem, err = self.login_node_exec_cmd(cmd)
        cmd = "free -m |grep Mem| awk '{print $3}'"
        used_mem, err = self.login_node_exec_cmd(cmd)
        available_mem = int(total_mem) - int(used_mem)
        if err:
            print 'exec cmd %s error:%s ' % (cmd, err)
        available_mem = int(available_mem)
        mount_mem = int(percent / 100.0 * available_mem)
        cmd = './burnmemory.sh %d %d > burnmemory.log 2>&1 &' % (time, mount_mem)
        self.login_node_exec_cmd(cmd)

    def net_loss(self, time, percent):
        time = int(time)
        percent = int(percent)
        cmd = './networkloss.sh %d %d > networkloss.log 2>&1 &' % (time, percent)
        self.login_node_exec_cmd(cmd)

    def net_latency(self, exec_time, delay_time):
        """delay_time:ms"""
        exec_time = int(exec_time)
        delay_time = int(delay_time)
        cmd = './networklatency.sh %d %d > networklatency.log 2>&1 &' % (exec_time, delay_time)
        self.login_node_exec_cmd(cmd)

    def reboot_node(self):
        cmd = 'ip addr'
        self.login_node_exec_cmd(cmd)

    def ssh_node(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.node.strip(), self.port, self.node_user, self.node_password)
        return ssh

    def login_node_exec_cmd(self, cmd):
        ssh = self.ssh_node()
        stdin, stdout, stderr = ssh.exec_command('cd /chaos ; %s ' % cmd)
        stdout_read = stdout.read()
        stderr_read = stderr.read()
        return stdout_read, stderr_read


def get_config(path, section, key):
    value = None
    try:
        cf = ConfigParser.ConfigParser()
        cf.read(path)
        value = cf.get(section, key)
    except IOError:
        print "path %s is not exist " % path
    except NoSectionError:
        print "%s file not this section %s " % (path, section)
    except NoOptionError:
        print "%s file not this key %s " % (path, key)
    finally:
        return value


def random_choice_node(node_list):
    num = random.randint(0, len(node_list) - 1)
    node = node_list[num]
    return node


def do_random():
    node_string = get_config(config_path, 'chaosmonkey', 'node_list')
    node_list = re.split(',', node_string)
    node_num = len(node_list)
    node_user = get_config(config_path, 'chaosmonkey', 'node_user')
    node_password = get_config(config_path, 'chaosmonkey', 'node_password')
    for i in range(node_num):
        chaos = ChaosMonkey(node_list[i], node_user, node_password)
        is_burn_cpu = random.randint(0, 1)
        is_burn_mem = random.randint(0, 1)
        is_burn_io = random.randint(0, 1)
        is_net_loss = random.randint(0, 1)
        is_net_delay = random.randint(0, 1)
        print time.strftime('%Y.%m.%d %H.%M', time.localtime(time.time()))
        print 'node:%s' % node_list[i]
        print 'is_burn_cpu:%s' % is_burn_cpu
        print 'is_burn_mem:%s' % is_burn_mem
        print 'is_burn_io:%s' % is_burn_io
        print 'is_net_loss:%s' % is_net_loss
        print 'is_net_delay:%s' % is_net_delay
        print '=' * 60
        if is_burn_cpu:
            do(chaos.burn_cpu, 'burn_cpu_time', 'burn_cpu_percent')
        if is_burn_mem:
            do(chaos.burn_mem, 'burn_mem_time', 'burn_mem_percent')
        if is_burn_io:
            do(chaos.burn_io, 'burn_io_time', 'burn_io_percent')
        if is_net_loss:
            do(chaos.net_loss, 'net_loss_time', 'net_loss_percent')
        if is_net_delay:
            do(chaos.net_latency, 'net_delay_run_time', 'net_delay_time')


def do(func, cofig_time, config_percent):
    do_time = get_config(config_path, 'chaosmonkey', cofig_time)
    do_percent = get_config(config_path, 'chaosmonkey', config_percent)
    if do_time is None:
        do_time = random.randint(10, 3600)
    if do_percent is None:
        do_percent = random.randint(10, 100)

    func(do_time, do_percent)


def do_appoint():
    node_string = get_config(config_path, 'chaosmonkey', 'node_list')
    node_list = re.split(',', node_string)
    node_num = len(node_list)
    node_user = get_config(config_path, 'chaosmonkey', 'node_user')
    node_password = get_config(config_path, 'chaosmonkey', 'node_password')
    for i in range(node_num):
        chaos = ChaosMonkey(node_list[i], node_user, node_password)
        is_burn_cpu = get_config(config_path, 'chaosmonkey', 'is_burn_cpu')
        is_burn_mem = get_config(config_path, 'chaosmonkey', 'is_burn_mem')
        is_burn_io = get_config(config_path, 'chaosmonkey', 'is_burn_io')
        is_net_loss = get_config(config_path, 'chaosmonkey', 'is_net_loss')
        is_net_delay = get_config(config_path, 'chaosmonkey', 'is_net_delay')
        print time.strftime('%Y.%m.%d %H.%M', time.localtime(time.time()))
        print 'node:%s' % node_list[i]
        print 'is_burn_cpu:%s' % is_burn_cpu
        print 'is_burn_mem:%s' % is_burn_mem
        print 'is_burn_io:%s' % is_burn_io
        print 'is_net_loss:%s' % is_net_loss
        print 'is_net_delay:%s' % is_net_delay
        print '=' * 60
        if is_burn_cpu:
            do(chaos.burn_cpu, 'burn_cpu_time', 'burn_cpu_percent')
        if is_burn_mem:
            do(chaos.burn_mem, 'burn_mem_time', 'burn_mem_percent')
        if is_burn_io:
            do(chaos.burn_io, 'burn_io_time', 'burn_io_percent')
        if is_net_loss:
            do(chaos.net_loss, 'net_loss_time', 'net_loss_percent')
        if is_net_delay:
            do(chaos.net_latency, 'net_delay_run_time', 'net_delay_time')


if __name__ == "__main__":
    config_path = u'/chaos/chaosconfig.ini'
    is_all_random = get_config(config_path, 'chaosmonkey', 'is_all_random')
    if is_all_random:
        do_random()
    else:
        do_appoint()
