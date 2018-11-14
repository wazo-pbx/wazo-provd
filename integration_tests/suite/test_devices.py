# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_provd_client import Client
from wazo_provd_client.exceptions import ProvdError
from hamcrest import assert_that, has_key, has_entry, has_length, is_, equal_to, calling, raises, is_not, empty
from .helpers import fixtures
from .helpers.base import BaseIntegrationTest
from .helpers.wait_strategy import NoWaitStrategy


class TestDevices(BaseIntegrationTest):
    asset = 'base'
    wait_strategy = NoWaitStrategy()

    def setUp(self):
        self._client = Client(
            'localhost', https=False,
            port=self.service_port(8666, 'provd'), prefix='/provd'
        )

    def tearDown(self):
        pass

    def _add_device(self, ip, mac, plugin='', id_=None):
        device = {'ip': ip, 'mac': mac, 'plugin': plugin}
        if id_:
            device.update({'id': id_})
        return self._client.devices.create(device)

    def test_list(self):
        results = self._client.devices.list()
        assert_that(results, has_key('devices'))

    def test_add(self):
        result_add = self._add_device('10.10.10.10', '00:11:22:33:44:55', id_='1234abcdef1234')
        assert_that(result_add, has_entry('id', '1234abcdef1234'))

    def test_add_errors(self):
        assert_that(
            calling(self._add_device).with_args('10.0.1.xx', '00:11:22:33:44:55'),
            raises(ProvdError, pattern='normalized')
        )
        assert_that(
            calling(self._add_device).with_args('10.0.1.1', '00:11:22:33:44:55', id_='*&!"/invalid _'),
            raises(ProvdError)
        )

    def test_update(self):
        with fixtures.Device(self._client) as device:
            new_info = {'id': device['id'], 'ip': '5.6.7.8', 'mac': 'aa:bb:cc:dd:ee:ff'}
            self._client.devices.update(new_info)

            result = self._client.devices.get(device['id'])
            assert_that(result['device']['ip'], is_(equal_to('5.6.7.8')))

    def test_update_errors(self):
        with fixtures.Device(self._client) as device:
            assert_that(
                calling(self._client.devices.update).with_args(
                    {'ip': '1.2.3.4', 'mac': '00:11:22:33:44:55'}
                ),
                raises(ProvdError, pattern='resource')
            )
            assert_that(
                calling(self._client.devices.update).with_args(
                    {'id': device['id'], 'ip': '10.0.1.1', 'mac': '00:11:22:33:44:xx'}
                ),
                raises(ProvdError, pattern='normalized')
            )

    def test_synchronize(self):
        with fixtures.Device(self._client) as device:
            self._client.devices.synchronize(device['id'])

    def test_get(self):
        with fixtures.Device(self._client) as device:
            result = self._client.devices.get(device['id'])
            assert_that(result['device']['ip'], is_(equal_to(device['ip'])))

    def test_get_errors(self):
        assert_that(
            calling(self._client.devices.get).with_args('unknown_id'),
            raises(ProvdError, pattern='resource')
        )

    def test_delete(self):
        with fixtures.Device(self._client, delete_on_exit=False) as device:
            self._client.devices.delete(device['id'])
            assert_that(
                calling(self._client.devices.get).with_args(device['id']),
                raises(ProvdError, pattern='resource')
            )

    def test_delete_errors(self):
        assert_that(
            calling(self._client.devices.delete).with_args('unknown_id'),
            raises(ProvdError, pattern='resource')
        )

    def test_reconfigure(self):
        with fixtures.Device(self._client) as device:
            self._client.devices.reconfigure(device['id'])

    def test_reconfigure_errors(self):
        assert_that(
            calling(self._client.devices.reconfigure).with_args('unknown_id'),
            raises(ProvdError, pattern='invalid')
        )

    def test_dhcp(self):
        self._client.devices.create_from_dhcp(
            {'ip': '10.10.0.1', 'mac': 'ab:bc:cd:de:ff:01', 'op': 'commit', 'options': []}
        )
        find_results = self._client.devices.list(search={'mac': 'ab:bc:cd:de:ff:01'})
        assert_that(find_results, has_key('devices'))
        assert_that(find_results['devices'], is_not(empty()))
        assert_that(find_results['devices'][0], has_entry('ip', '10.10.0.1'))

    def test_dhcp_errors(self):
        assert_that(
            calling(self._client.devices.create_from_dhcp).with_args(
                {'ip': '10.10.0.1', 'mac': 'ab:bc:cd:de:ff:01', 'op': 'commit'}
            ),
            raises(ProvdError)
        )
