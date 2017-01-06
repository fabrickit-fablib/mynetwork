# coding: utf-8

from fabkit import *  # noqa
from fablib.base import SimpleBase


class Calico(SimpleBase):
    def __init__(self):
        self.data_key = 'calico'
        self.data = {
            'version': '1.0.0'
        }

        self.packages = {
            'CentOS .*': []
        }

        self.services = {
            'CentOS .*': [
                'calico-node'
            ]
        }

    def setup(self):
        data = self.init()

        sudo('setenforce 0')
        filer.Editor('/etc/selinux/config').s('SELINUX=enforcing', 'SELINUX=disable')
        Service('firewalld').stop().disable()

        self.install_calico()
        filer.template('/etc/calico/calico.env', data=data)
        self.start_services()

    def install_calico(self):
        data = self.init()

        calicoctl_url = 'https://github.com/projectcalico/calico-containers/releases/download/v{0}/calicoctl'.format(data['version'])  # noqa
        calicoctl_path = '/usr/bin/calicoctl'
        if not filer.exists(calicoctl_path):
            with api.cd('/tmp'):
                sudo('wget {0}'.format(calicoctl_url))
                sudo('chmod 755 calicoctl')
                sudo('mv calicoctl {0}'.format(calicoctl_path))

        filer.mkdir('/etc/calico/')

        if filer.template('/lib/systemd/system/calico-node.service'):
            sudo('systemctl daemon-reload')
