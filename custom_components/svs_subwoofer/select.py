"""Select platform for SVS Subwoofer."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SVSCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SVS select entities from a config entry."""
    coordinator: SVSCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SVSStandbyModeSelect(coordinator, entry)])


class SVSStandbyModeSelect(CoordinatorEntity[SVSCoordinator], SelectEntity):
    """Representation of an SVS Subwoofer standby mode select."""

    _attr_has_entity_name = True
    _attr_name = "Standby Mode"
    _attr_options = ["Auto On", "Trigger", "On"]
    _attr_icon = "mdi:power-settings"

    def __init__(self, coordinator: SVSCoordinator, entry: ConfigEntry) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.data[CONF_ADDRESS]}_standby_mode"
        self._entry = entry

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._entry.data[CONF_ADDRESS])},
            "name": f"SVS Subwoofer {self._entry.data[CONF_ADDRESS][-5:]}",
            "manufacturer": "SVS",
            "model": "SB-1000 Pro",
            "connections": {("bluetooth", self._entry.data[CONF_ADDRESS])},
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.device.is_connected and super().available

    @property
    def current_option(self) -> str | None:
        """Return the current standby mode."""
        standby_value = self.coordinator.data.get("STANDBY")
        if standby_value is None:
            return None

        # Map numeric value to display string
        mode_map = {
            0: "Auto On",
            1: "Trigger",
            2: "On",
        }
        return mode_map.get(standby_value)

    async def async_select_option(self, option: str) -> None:
        """Change the selected standby mode."""
        # Map display string to numeric value
        option_map = {
            "Auto On": 0,
            "Trigger": 1,
            "On": 2,
        }

        mode = option_map.get(option)
        if mode is not None:
            await self.coordinator.device.set_standby(mode)
