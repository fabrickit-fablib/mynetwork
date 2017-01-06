# coding: utf-8

from fabkit import *  # noqa
from fablib.base import SimpleBase


class MyNetwork(SimpleBase):
    def __init__(self):
        self.data_key = 'mynetwork'
        self.data = {
            'version': '1.0.0'
        }

        self.packages = {
            'CentOS .*': [
                'epel-release',
                'bird',
                'bird6',
                'tcpdump',
                'lsof',
                'wget',
            ]
        }

        self.services = {
            'CentOS .*': []
        }

    def setup(self):
        data = self.init()

        sudo('setenforce 0')
        filer.Editor('/etc/selinux/config').s('SELINUX=enforcing', 'SELINUX=disable')
        Service('firewalld').stop().disable()

        self.install_packages()

        self.create_simple_network()

    def create_simple_network(self):
        sudo('ip netns list | grep server  || ip netns add server')
        sudo('ip netns list | grep gateway || ip netns add gateway')
        sudo('ip netns list | grep client  || ip netns add client')
        sudo('ip netns exec gateway sysctl net.ipv4.ip_forward=1')

        with api.warn_only():
            result = sudo('ip netns exec server ip a | grep svr-veth')
            if result.return_code != 0:
                sudo('ip link add svr-veth type veth peer name svrgw-veth')
                sudo('ip link set svr-veth netns server')
                sudo('ip netns exec server ip addr add dev svr-veth 192.168.100.2/24')
                sudo('ip netns exec server ip link set svr-veth up')
                sudo('ip netns exec server route add default gw 192.168.100.1')

            result = sudo('ip netns exec client ip a | grep cli-veth')
            if result.return_code != 0:
                sudo('ip link add cli-veth type veth peer name cligw-veth')
                sudo('ip link set cli-veth netns client')
                sudo('ip netns exec client ip add add dev cli-veth 10.0.100.2/24')
                sudo('ip netns exec client ip link set cli-veth up')
                sudo('ip netns exec client route add default gw 10.0.100.1')

            result = sudo('ip netns exec gateway ip a | grep svrgw-veth')
            if result.return_code != 0:
                sudo('ip link set svrgw-veth netns gateway')
                sudo('ip netns exec gateway ip addr add dev svrgw-veth 192.168.100.1/24')
                sudo('ip netns exec gateway ip link set svrgw-veth up')

            result = sudo('ip netns exec gateway ip a | grep cligw-veth')
            if result.return_code != 0:
                sudo('ip link set cligw-veth netns gateway')
                sudo('ip netns exec gateway ip addr add dev cligw-veth 10.0.100.1/24')
                sudo('ip netns exec gateway ip link set cligw-veth up')
