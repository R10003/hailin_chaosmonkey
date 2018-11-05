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
        cmd = './burnio.sh %d /burn_io> burnio.log 2>&1 &' % time
        self.login_node_exec_cmd(cmd)

    def burn_data_io(self, time, percent):
        time = int(time)
        percent = int(percent)
        cmd = './burnio.sh %d /data/burn_io> burnio.log 2>&1 &' % time
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

    def eat_mem(self, time, percent):
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
        eat_block = int(percent / 100.0 * available_mem)

        # eat_block单位为M,i为有几个1G，即为执行次数
        i = eat_block / 1000
        j = 0
        ratio = 10000
        # 执行一次eatMemory.o占用ratio*0.1M内存，这里为1G
        while j < i:
            if j == 0:
                cmd = 'echo total:%s > eatMemory.log' % i
                self.login_node_exec_cmd(cmd)
            cmd = 'echo num:%s >> eatMemory.log' % j
            self.login_node_exec_cmd(cmd)
            cmd = './eatMemory.o %d %d >> eatMemory.log 2>&1 &' % (time, ratio)
            self.login_node_exec_cmd(cmd)
            j += 1

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
        stdin, stdout, stderr = ssh.exec_command('cd /chaos/scripts ; %s ' % cmd)
        stdout_read = stdout.read()
        stderr_read = stderr.read()
        return stdout_read, stderr_read

    def kill_para(self, para):
        cmd = '%s | grep -v grep ;echo $?' % para
        exec_out, exec_err = self.login_node_exec_cmd(cmd)
        exec_out = exec_out.strip()

        # 返回码为0,说明有这个服务在
        if exec_out[-1] == '0':
            cmd = '''%s | grep -v grep |awk {'print "kill -9 " $2'}|sh''' % para
            self.login_node_exec_cmd(cmd)
        else:
            print '%s has not process %s' % (self.node, para)


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


def do(func, cofig_time, config_percent):
    do_time = get_config(config_path, 'chaosmonkey', cofig_time)
    do_percent = get_config(config_path, 'chaosmonkey', config_percent)
    if do_time == '':
        do_time = random.randint(10, 3600)
    if do_percent == '':
        do_percent = random.randint(10, 100)

    func(do_time, do_percent)


def do_appoint():
    node_string = get_config(config_path, 'chaosmonkey', 'node_list')
    node_list = re.split(',', node_string)
    node_num = len(node_list)
    node_user = get_config(config_path, 'chaosmonkey', 'node_user')
    node_password = get_config(config_path, 'chaosmonkey', 'node_password')
    is_random_kill_apps = get_config(config_path, 'chaosmonkey', 'is_random_kill_apps')
    is_all_random = get_config(config_path, 'chaosmonkey', 'is_all_random')
    apps_string = get_config(config_path, 'chaosmonkey', 'apps_list')
    apps_list = re.split(',', apps_string)

    for i in range(node_num):
        chaos = ChaosMonkey(node_list[i], node_user, node_password)
        actions_func = {'is_burn_cpu': chaos.burn_cpu, 'is_burn_mem': chaos.burn_mem, 'is_eat_mem': chaos.eat_mem,
                        'is_burn_io': chaos.burn_io, 'is_burn_data_io': chaos.burn_data_io,
                        'is_net_loss': chaos.net_loss, 'is_net_delay': chaos.net_latency}
        print time.strftime('%Y.%m.%d %H:%M', time.localtime(time.time()))
        print 'node:%s' % node_list[i]

        for key in actions:
            if is_all_random:
                actions[key] = random.randint(0, 1)
            else:
                actions[key] = get_config(config_path, 'chaosmonkey', key)
            print '%s:%s' % (key, actions[key])
        # print '=' * 60

        for key in actions:
            if actions[key]:
                do(actions_func[key], actions_time[key], actions_percent[key])

        for app in apps_list:
            app = app.strip()
            if is_random_kill_apps:
                kill_or_not = random.randint(0, 1)
                if kill_or_not:
                    try:
                        parameter = apps_func[app]
                        chaos.kill_para(parameter)
                    except KeyError:
                        print 'app %s is not exist ' % app

            else:
                kill_or_not = 1
                try:
                    parameter = apps_func[app]
                    chaos.kill_para(parameter)
                except KeyError:
                    print 'app %s is not exist ' % app

            print 'kill %s:%s' % (app, kill_or_not)
        print '=' * 60


if __name__ == "__main__":
    config_path = u'/chaos/chaosconfig.ini'

    actions = {'is_burn_cpu': '', 'is_eat_mem': '', 'is_burn_io': '', 'is_burn_data_io': '',
               'is_net_loss': '', 'is_net_delay': ''}

    actions_time = {'is_burn_cpu': 'burn_cpu_time', 'is_burn_mem': 'burn_mem_time', 'is_eat_mem': 'eat_mem_time',
                    'is_burn_io': 'burn_io_time', 'is_burn_data_io': 'burn_data_io_time',
                    'is_net_loss': 'net_loss_time', 'is_net_delay': 'net_delay_run_time'}

    actions_percent = {'is_burn_cpu': 'burn_cpu_percent', 'is_burn_mem': 'burn_mem_percent',
                       'is_eat_mem': 'eat_mem_percent', 'is_burn_io': 'burn_io_percent',
                       'is_burn_data_io': 'burn_data_io_percent', 'is_net_loss': 'net_loss_percent',
                       'is_net_delay': 'net_delay_time'}

    apps_func = {
        'mysqld': 'ps -ef|grep mysqld|grep port',
        'mysqld_safe': 'ps -ef|grep mysqld_safe',
        'flume_agent': 'ps -ef|grep flume_agent',
        'hbase_master': 'ps -ef|grep HBase_Master',
        'hbase_regionserver': 'ps -ef|grep HBase_RegionServer',
        'hdfs_datanode': 'ps -ef|grep HDFS_DataNode',
        'hdfs_namenode': 'ps -ef|grep HDFS_NameNode',
        'hdfs_journalnode': 'ps -ef|grep HDFS_JournalNode',
        'hdfs_failovercontroller': 'ps -ef|grep HDFS-FAILOVERCONTROLLER',
        'hive_metastore': 'ps -ef|grep Hive_hive-metastore',
        'impala-statestore': 'ps -ef|grep impala-STATESTORE',
        'impala-catalogserver': 'ps -ef |grep impala-CATALOGSERVER',
        'impala_daemon': 'ps -ef|grep impala-IMPALAD',
        'kafka_broker': 'ps -ef|grep KAFKA_BROKER',
        'oozie_server': 'ps -ef|grep OOZIE_SERVER',
        'spark_history_server': 'ps -ef|grep SPARK_YARN_HISTORY_SERVER',
        'yarn_nodemanager': 'ps -ef|grep YARN_NodeManager',
        'yarn_resourcemanager': 'ps -ef|grep YARN_ResourceManager',
        'yarn_jobhistory': 'ps -ef|grep YARN_JobHistory',
        'zookeeper_server': 'ps -ef|grep zookeeper-server',
        'cloudera_hostmonitor': 'ps -ef|grep cloudera-mgmt-HOSTMONITOR',
        'cloudera_servicemonitor': 'ps -ef|grep cloudera-mgmt-SERVICEMONITOR',
        'cloudera_eventserver': 'ps -ef|grep cloudera-mgmt-EVENTSERVER',
        'cloudera_alertpublish': 'ps -ef|grep cloudera-mgmt-ALERTPUBLISHER',
        'nginx': 'ps -ef|grep nginx|grep master',
        'keepalive': 'ps -ef|grep keepalive',
        'ntpd': 'ps -ef|grep ntpd',
        'pacemaker': 'ps -ef|grep pacemaker',
        'corosync': 'ps -ef|grep corosync',
        'tomcat': 'ps -ef|grep tomcat',
        'redis': 'ps -ef|grep redis',
        'topbi': 'ps -ef | grep jackrabbit',
        'monitor.py': 'ps -ef|grep monitor.py'
    }

    do_appoint()
