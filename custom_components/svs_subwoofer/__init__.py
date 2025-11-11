"""The SVS Subwoofer integration."""
from __future__ import annotations

import logging

from bleak.exc import BleakError

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .coordinator import SVSCoordinator
from .device import SVSDevice

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.MEDIA_PLAYER, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SVS Subwoofer from a config entry."""
    address = entry.data[CONF_ADDRESS]

    # Get BLE device from Home Assistant's Bluetooth integration
    # This works transparently with ESPHome proxies
    ble_device = bluetooth.async_ble_device_from_address(
        hass, address, connectable=True
    )

    if not ble_device:
        raise ConfigEntryNotReady(
            f"Could not find SVS Subwoofer with address {address}"
        )

    # Create device instance
    device = SVSDevice(address)

    try:
        await device.connect(ble_device)
    except BleakError as err:
        raise ConfigEntryNotReady(
            f"Could not connect to SVS Subwoofer: {err}"
        ) from err

    # Create coordinator
    coordinator = SVSCoordinator(hass, device, ble_device)

    # Perform initial data fetch
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: SVSCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    return unload_ok
