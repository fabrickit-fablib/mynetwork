# coding: utf-8

from fabkit import *  # noqa
from fablib.base import SimpleBase


class Bird(SimpleBase):
    def __init__(self):
        self.data_key = 'bird'
        self.data = {
            'version': '1.0.0'
        }

        self.packages = {
            'CentOS .*': [
                'epel-release',
                'bird',
                'bird6'
            ]
        }

        self.services = {
            'CentOS .*': [
                'bird'
            ]
        }

    def setup(self):
        data = self.init()

        sudo('setenforce 0')
        filer.Editor('/etc/selinux/config').s('SELINUX=enforcing', 'SELINUX=disable')
        Service('firewalld').stop().disable()

        self.install_packages()

        filer.template('/etc/bird.conf', data=data)

        self.start_services()

        sudo('birdcl show status')
