# -*- coding: utf-8 -*-
#
# Copyright © 2014 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.


import unittest

from ConfigParser import SafeConfigParser
import mock
from mock import Mock

from spacewalk_splice_tool import checkin
from spacewalk_splice_tool import constants
from spacewalk_splice_tool import utils


class SpliceToolTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(SpliceToolTest, self).__init__(*args, **kwargs)
        self._mocks = []

    def setUp(self):
        super(SpliceToolTest, self).setUp()
        self.config = self.mock_config()
        self.mock_cert_dir()
        self.mock(utils, 'get_release', 'RHEL-6.4')
        self.mock(utils, 'cfg_init', self.config)

        constants.CHANNEL_PRODUCT_ID_MAPPING_DIR = 'data'

    def tearDown(self):
        super(SpliceToolTest, self).tearDown()
        self.unmock_config()
        self.unmock_all()

    def mock(self, parent, child, return_value=None):
        self._mocks.append([parent, child, getattr(parent, child)])
        new_mock = Mock()
        if return_value is not None:
            new_mock.return_value = return_value
        setattr(parent, child, new_mock)
        return new_mock

    def unmock_all(self):
        for parent, child, child_object in self._mocks:
            setattr(parent, child, child_object)

    def mock_config(self):
        self.old_config = checkin.CONFIG
        
        defaults = {'spacewalk': {'host': 'spacewalkhost',
                                  'ssh_key_path': 'spacwealk_ssh_key_path'},
                    'main': {'socket_timeout': '300'},
                    'splice': {'hostname': 'test_hostname',
                               'port': '8888',
                               'handler': 'test_handler',
                               'splice_id_cert': 'test_cert',
                               'splice_id_key': 'test_key',
                               'splice_ca_cert': 'test_ca',
                               'splice_server_environment': 'test_sse',
                               'splice_server_hostname': 'test_ssh',
                               'splice_server_description': 'test_ssd',}
                   }

        config = SafeConfigParser(defaults)

        for section, configs in defaults.items():
            if not config.has_section(section):
                config.add_section(section)
            for key, value in configs.items():
                config.set(section, key, value)

        checkin.CONFIG = config

        return config

    def unmock_config(self):
        checkin.CONFIG = self.old_config

    def mock_cert_dir(self):
        mocked_cd = Mock()
        product_cert = Mock()
        product = Mock()
        product.configure_mock(id=69, name='Red Hat Enterprise Linux Server')
        product_cert.configure_mock(products=[product])
        mocked_cd.findByProduct.return_value = product_cert
        self.mock(checkin, 'CertificateDirectory', mocked_cd)
