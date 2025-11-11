"""DataUpdateCoordinator for SVS Subwoofer."""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from bleak.exc import BleakError

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .device import SVSDevice

_LOGGER = logging.getLogger(__name__)


class SVSCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Class to manage fetching SVS data."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: SVSDevice,
        ble_device: bluetooth.BLEDevice,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.device = device
        self.ble_device = ble_device
        self._state: dict[str, Any] = {}

        # Register callback for state updates from device
        self.device.register_callback(self._handle_state_update)

    def _handle_state_update(self, data: dict[str, Any]) -> None:
        """Handle state updates from the device."""
        _LOGGER.debug("State update received: %s", data)
        self._state.update(data)
        # Notify Home Assistant of the update
        self.async_set_updated_data(self._state)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        try:
            if not self.device.is_connected:
                _LOGGER.debug("Device not connected, attempting to reconnect")
                await self.device.connect(self.ble_device)

            # Request full settings
            await self.device.get_full_settings()

            # Return current state (updates come via notifications)
            return self._state

        except BleakError as err:
            _LOGGER.warning("Error communicating with device: %s", err)
            # Try to reconnect on next update
            try:
                await self.device.disconnect()
            except Exception:
                pass
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        await self.device.disconnect()
