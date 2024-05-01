# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import abc
import dataclasses
import logging
from typing import Any, ClassVar
from uuid import UUID

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Model(metaclass=abc.ABCMeta):
    _meta: ClassVar[dict[str, Any]]

    def as_dict(
        self, ignore_associations=False, ignore_foreign_keys=False
    ) -> dict[str, Any]:
        dict_output = {}
        for field in dataclasses.fields(self):
            if not (
                ignore_associations
                and field.metadata.get('assoc')
                or ignore_foreign_keys
                and field.metadata.get('foreign_key')
            ):
                value = getattr(self, field.name)
                if dataclasses.is_dataclass(value):
                    dict_output[field.name] = value.as_dict(
                        ignore_associations=ignore_associations
                    )
                else:
                    dict_output[field.name] = value

        return dict_output


@dataclasses.dataclass
class Tenant(Model):
    uuid: UUID
    provisioning_key: str | None = dataclasses.field(default=None)

    _meta = {'primary_key': 'uuid'}


@dataclasses.dataclass
class ServiceConfiguration(Model):
    uuid: UUID
    plugin_server: str | None = dataclasses.field(default=None)
    http_proxy: str | None = dataclasses.field(default=None)
    https_proxy: str | None = dataclasses.field(default=None)
    ftp_proxy: str | None = dataclasses.field(default=None)
    locale: str | None = dataclasses.field(default=None)
    nat_enabled: bool | None = dataclasses.field(default=False)

    _meta = {'primary_key': 'uuid'}


@dataclasses.dataclass
class DeviceConfig(Model):
    id: str
    parent_id: str | None = dataclasses.field(default=None)
    label: str | None = dataclasses.field(default=None)
    deletable: bool = dataclasses.field(default=True)
    type: str | None = dataclasses.field(default=None)
    role: str | None = dataclasses.field(default=None)
    configdevice: str | None = dataclasses.field(default=None)
    transient: bool = dataclasses.field(default=False)
    registrar_main: str | None = dataclasses.field(default=None)
    registrar_main_port: int | None = dataclasses.field(default=None)
    proxy_main: str | None = dataclasses.field(default=None)
    proxy_main_port: int | None = dataclasses.field(default=None)
    proxy_outbound: str | None = dataclasses.field(default=None)
    proxy_outbound_port: int | None = dataclasses.field(default=None)
    registrar_backup: str | None = dataclasses.field(default=None)
    registrar_backup_port: int | None = dataclasses.field(default=None)
    proxy_backup: str | None = dataclasses.field(default=None)
    proxy_backup_port: int | None = dataclasses.field(default=None)

    raw_config: DeviceRawConfig | None = dataclasses.field(
        default=None, metadata={'assoc': True}
    )

    _meta = {'primary_key': 'id'}


@dataclasses.dataclass
class SIPLine(Model):
    uuid: UUID
    config_id: str = dataclasses.field(metadata={'foreign_key': True})
    position: int
    proxy_ip: str | None = dataclasses.field(default=None)
    proxy_port: int | None = dataclasses.field(default=None)
    backup_proxy_ip: str | None = dataclasses.field(default=None)
    backup_proxy_port: int | None = dataclasses.field(default=None)
    registrar_ip: str | None = dataclasses.field(default=None)
    registrar_port: int | None = dataclasses.field(default=None)
    backup_registrar_ip: str | None = dataclasses.field(default=None)
    backup_registrar_port: int | None = dataclasses.field(default=None)
    outbound_proxy_ip: str | None = dataclasses.field(default=None)
    outbound_proxy_port: int | None = dataclasses.field(default=None)
    username: str | None = dataclasses.field(default=None)
    password: str | None = dataclasses.field(default=None)
    auth_username: str | None = dataclasses.field(default=None)
    display_name: str | None = dataclasses.field(default=None)
    number: str | None = dataclasses.field(default=None)
    dtmf_mode: str | None = dataclasses.field(
        default=None
    )  # "RTP-in-band, RTP-out-of-band, SIP-INFO": enum
    srtp_mode: str | None = dataclasses.field(
        default=None
    )  # "disabled, preferred, required": enum
    voicemail: str | None = dataclasses.field(default=None)

    _meta = {'primary_key': 'uuid'}


@dataclasses.dataclass
class SCCPLine(Model):
    uuid: UUID
    config_id: str = dataclasses.field(metadata={'foreign_key': True})
    position: int
    ip: str | None = dataclasses.field(default=None)
    port: int | None = dataclasses.field(default=None)

    _meta = {'primary_key': 'uuid'}


@dataclasses.dataclass
class FunctionKey(Model):
    uuid: UUID
    config_id: str = dataclasses.field(metadata={'foreign_key': True})
    position: int
    type: str | None = dataclasses.field(default=None)  # enum "speeddial, blf, park"
    value: str | None = dataclasses.field(default=None)
    label: str | None = dataclasses.field(default=None)
    line: str | None = dataclasses.field(default=None)

    _meta = {'primary_key': 'uuid'}


@dataclasses.dataclass
class DeviceRawConfig(Model):
    config_id: str = dataclasses.field(metadata={'foreign_key': True})
    ip: str | None = dataclasses.field(default=None)
    http_port: int | None = dataclasses.field(default=None)
    http_base_url: str | None = dataclasses.field(default=None)
    tftp_port: int | None = dataclasses.field(default=None)
    dns_enabled: bool | None = dataclasses.field(default=None)
    dns_ip: str | None = dataclasses.field(default=None)
    ntp_enabled: bool | None = dataclasses.field(default=None)
    ntp_ip: str | None = dataclasses.field(default=None)
    vlan_enabled: bool | None = dataclasses.field(default=None)
    vlan_id: int | None = dataclasses.field(default=None)
    vlan_priority: int | None = dataclasses.field(default=None)
    vlan_pc_port_id: int | None = dataclasses.field(default=None)
    syslog_enabled: bool | None = dataclasses.field(default=None)
    syslog_ip: str | None = dataclasses.field(default=None)
    syslog_port: int | None = dataclasses.field(default=None)
    syslog_level: int | None = dataclasses.field(default=None)
    admin_username: str | None = dataclasses.field(default=None)
    admin_password: str | None = dataclasses.field(default=None)
    user_username: str | None = dataclasses.field(default=None)
    user_password: str | None = dataclasses.field(default=None)
    timezone: str | None = dataclasses.field(default=None)
    locale: str | None = dataclasses.field(default=None)
    protocol: str | None = dataclasses.field(default=None)  # ENUM sip,sccp
    sip_proxy_ip: str | None = dataclasses.field(default=None)
    sip_proxy_port: int | None = dataclasses.field(default=None)
    sip_backup_proxy_ip: str | None = dataclasses.field(default=None)
    sip_backup_proxy_port: int | None = dataclasses.field(default=None)
    sip_registrar_ip: str | None = dataclasses.field(default=None)
    sip_registrar_port: int | None = dataclasses.field(default=None)
    sip_backup_registrar_ip: str | None = dataclasses.field(default=None)
    sip_backup_registrar_port: int | None = dataclasses.field(default=None)
    sip_outbound_proxy_ip: str | None = dataclasses.field(default=None)
    sip_outbound_proxy_port: int | None = dataclasses.field(default=None)
    sip_dtmf_mode: str | None = dataclasses.field(default=None)
    sip_srtp_mode: str | None = dataclasses.field(default=None)
    sip_transport: str | None = dataclasses.field(default=None)
    sip_servers_root_and_intermediate_certificates: str | None = dataclasses.field(
        default=None
    )
    sip_local_root_and_intermediate_certificates: str | None = dataclasses.field(
        default=None
    )
    sip_local_certificate: str | None = dataclasses.field(default=None)
    sip_local_key: str | None = dataclasses.field(default=None)
    sip_subscribe_mwi: str | None = dataclasses.field(default=None)
    exten_dnd: str | None = dataclasses.field(default=None)
    exten_fwd_unconditional: str | None = dataclasses.field(default=None)
    exten_fwd_no_answer: str | None = dataclasses.field(default=None)
    exten_fwd_busy: str | None = dataclasses.field(default=None)
    exten_fwd_disable_all: str | None = dataclasses.field(default=None)
    exten_park: str | None = dataclasses.field(default=None)
    exten_pickup_group: str | None = dataclasses.field(default=None)
    exten_pickup_call: str | None = dataclasses.field(default=None)
    exten_voicemail: str | None = dataclasses.field(default=None)
    user_uuid: str | None = dataclasses.field(default=None)
    phonebook_ip: str | None = dataclasses.field(default=None)
    phonebook_profile: str | None = dataclasses.field(default=None)

    function_keys: dict[str, FunctionKey] | None = dataclasses.field(
        default=None, metadata={'assoc': True}
    )
    sip_lines: dict[str, SIPLine] | None = dataclasses.field(
        default=None, metadata={'assoc': True}
    )
    sccp_lines: dict[str, SCCPLine] | None = dataclasses.field(
        default=None, metadata={'assoc': True}
    )

    _meta = {'primary_key': 'config_id'}


@dataclasses.dataclass
class Device(Model):
    id: str
    tenant_uuid: UUID
    config_id: str | None = dataclasses.field(
        default=None, metadata={'foreign_key': True}
    )
    mac: str | None = dataclasses.field(default=None)
    ip: str | None = dataclasses.field(default=None)
    vendor: str | None = dataclasses.field(default=None)
    model: str | None = dataclasses.field(default=None)
    version: str | None = dataclasses.field(default=None)
    plugin: str | None = dataclasses.field(default=None)
    configured: bool = dataclasses.field(default=False)
    auto_added: bool = dataclasses.field(default=False)
    is_new: bool = dataclasses.field(default=False)

    _meta = {'primary_key': 'id'}
