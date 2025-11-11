"""Media player platform for SVS Subwoofer."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STANDBY_MODES
from .coordinator import SVSCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up SVS media player from a config entry."""
    coordinator: SVSCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SVSMediaPlayer(coordinator, entry)])


class SVSMediaPlayer(CoordinatorEntity[SVSCoordinator], MediaPlayerEntity):
    """Representation of an SVS Subwoofer as a media player."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
    )

    def __init__(self, coordinator: SVSCoordinator, entry: ConfigEntry) -> None:
        """Initialize the media player."""
        super().__init__(coordinator)
        self._attr_unique_id = entry.data[CONF_ADDRESS]
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.data[CONF_ADDRESS])},
            "name": f"SVS Subwoofer {entry.data[CONF_ADDRESS][-5:]}",
            "manufacturer": "SVS",
            "model": "SB-1000 Pro",
            "connections": {("bluetooth", entry.data[CONF_ADDRESS])},
        }

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.device.is_connected and super().available

    @property
    def state(self) -> MediaPlayerState:
        """Return the state of the device."""
        standby = self.coordinator.data.get("STANDBY")
        if standby == 2:  # ON mode
            return MediaPlayerState.ON
        if standby in [0, 1]:  # AUTO ON or TRIGGER mode
            return MediaPlayerState.STANDBY
        return MediaPlayerState.OFF

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0.0 to 1.0)."""
        # Convert SVS range (-60 to 0 dB) to Home Assistant range (0.0 to 1.0)
        svs_volume = self.coordinator.data.get("VOLUME")
        if svs_volume is None:
            return None
        return (svs_volume + 60) / 60

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level (0.0 to 1.0)."""
        # Convert Home Assistant range to SVS range (-60 to 0 dB)
        svs_volume = int((volume * 60) - 60)
        await self.coordinator.device.set_volume(svs_volume)

    async def async_volume_up(self) -> None:
        """Volume up the media player."""
        current_volume = self.volume_level
        if current_volume is not None and current_volume < 1.0:
            new_volume = min(1.0, current_volume + 0.05)
            await self.async_set_volume_level(new_volume)

    async def async_volume_down(self) -> None:
        """Volume down media player."""
        current_volume = self.volume_level
        if current_volume is not None and current_volume > 0.0:
            new_volume = max(0.0, current_volume - 0.05)
            await self.async_set_volume_level(new_volume)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        data = self.coordinator.data
        attributes = {}

        if "PHASE" in data:
            attributes["phase"] = data["PHASE"]

        if "POLARITY" in data:
            attributes["polarity"] = "+" if data["POLARITY"] == 0 else "-"

        if "STANDBY" in data:
            attributes["standby_mode"] = STANDBY_MODES.get(data["STANDBY"], "unknown")

        if "LOW_PASS_FILTER_ENABLE" in data:
            attributes["low_pass_filter"] = "on" if data["LOW_PASS_FILTER_ENABLE"] else "off"

        if "LOW_PASS_FILTER_FREQ" in data:
            attributes["low_pass_filter_freq"] = data["LOW_PASS_FILTER_FREQ"]

        if "ROOM_GAIN_ENABLE" in data:
            attributes["room_gain"] = "on" if data["ROOM_GAIN_ENABLE"] else "off"

        # Add volume in dB for reference
        if "VOLUME" in data:
            attributes["volume_db"] = data["VOLUME"]

        return attributes
