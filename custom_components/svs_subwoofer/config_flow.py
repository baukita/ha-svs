"""Config flow for SVS Subwoofer integration."""
from __future__ import annotations

import logging
from typing import Any

from bleak.exc import BleakError
import voluptuous as vol

from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothServiceInfoBleak
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN, SERVICE_UUID
from .device import SVSDevice

_LOGGER = logging.getLogger(__name__)


class SVSConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SVS Subwoofer."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle the Bluetooth discovery step."""
        _LOGGER.debug("Discovered SVS Subwoofer: %s", discovery_info.address)
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self._discovery_info = discovery_info

        # Try to connect to validate the device
        device = SVSDevice(discovery_info.address)
        ble_device = bluetooth.async_ble_device_from_address(
            self.hass, discovery_info.address, connectable=True
        )

        if not ble_device:
            return self.async_abort(reason="no_devices_found")

        try:
            await device.connect(ble_device)
            await device.disconnect()
        except BleakError as err:
            _LOGGER.warning("Could not connect to device: %s", err)
            return self.async_abort(reason="cannot_connect")

        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"SVS Subwoofer {self._discovery_info.address[-5:]}",
                data={CONF_ADDRESS: self._discovery_info.address},
            )

        self._set_confirm_only()
        return self.async_show_form(
            step_id="confirm",
            description_placeholders={
                "name": f"SVS Subwoofer {self._discovery_info.address[-5:]}"
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step to pick discovered device."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()

            # Validate connection
            ble_device = bluetooth.async_ble_device_from_address(
                self.hass, address, connectable=True
            )

            if not ble_device:
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_ADDRESS): str,
                        }
                    ),
                    errors={"base": "no_devices_found"},
                )

            device = SVSDevice(address)
            try:
                await device.connect(ble_device)
                await device.disconnect()
            except BleakError:
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema(
                        {
                            vol.Required(CONF_ADDRESS): str,
                        }
                    ),
                    errors={"base": "cannot_connect"},
                )

            return self.async_create_entry(
                title=f"SVS Subwoofer {address[-5:]}",
                data={CONF_ADDRESS: address},
            )

        # Check for discovered devices
        current_addresses = self._async_current_ids()
        discovered = bluetooth.async_discovered_service_info(
            self.hass, connectable=True
        )

        for service_info in discovered:
            if (
                service_info.address not in current_addresses
                and service_info.address not in self._discovered_devices
                and SERVICE_UUID.lower() in [s.lower() for s in service_info.service_uuids]
            ):
                self._discovered_devices[service_info.address] = service_info

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        # Show device selection
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ADDRESS): vol.In(
                        {
                            address: f"SVS Subwoofer {address}"
                            for address in self._discovered_devices
                        }
                    ),
                }
            ),
        )
