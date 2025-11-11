"""SVS Subwoofer device communication."""
from __future__ import annotations

import asyncio
from binascii import crc_hqx, hexlify
import logging
from typing import Any, Callable

from bleak import BleakClient
from bleak.exc import BleakError
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

from homeassistant.components import bluetooth

from .const import CHAR_UUID, FRAME_PREAMBLE, SVS_FRAME_TYPES, SVS_PARAMS

_LOGGER = logging.getLogger(__name__)


class SVSDevice:
    """Representation of an SVS Subwoofer device."""

    def __init__(self, address: str) -> None:
        """Initialize the device."""
        self.address = address
        self._client: BleakClient | None = None
        self._callbacks: list[Callable[[dict[str, Any]], None]] = []
        self._partial_frame = b''
        self._sync = True
        self._disconnect_timer: asyncio.TimerHandle | None = None

    async def connect(self, ble_device: bluetooth.BLEDevice) -> None:
        """Connect to the device."""
        _LOGGER.debug("Connecting to SVS subwoofer at %s", self.address)

        self._client = await establish_connection(
            BleakClientWithServiceCache,
            ble_device,
            self.address,
            max_attempts=3,
        )

        # Subscribe to notifications
        await self._client.start_notify(CHAR_UUID, self._notification_handler)
        _LOGGER.info("Connected to SVS subwoofer at %s", self.address)

    async def disconnect(self) -> None:
        """Disconnect from the device."""
        if self._client and self._client.is_connected:
            await self._client.stop_notify(CHAR_UUID)
            await self._client.disconnect()
            _LOGGER.info("Disconnected from SVS subwoofer at %s", self.address)
        self._client = None

    @property
    def is_connected(self) -> bool:
        """Return True if connected to the device."""
        return self._client is not None and self._client.is_connected

    def register_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Register a callback for state updates."""
        self._callbacks.append(callback)

    def _notification_handler(self, handle: int, data: bytearray) -> None:
        """Handle notifications from the device."""
        # Build frame from fragments
        if data[0] == int.from_bytes(FRAME_PREAMBLE, 'little'):
            # Detected frame start
            if not self._sync:
                _LOGGER.warning(
                    "Frame fragment out of sync: %s",
                    hexlify(self._partial_frame).decode("utf-8")
                )
            self._partial_frame = bytes(data)
        else:
            # Detected frame fragment
            self._partial_frame = self._partial_frame + bytes(data)

        # Try to decode the frame
        decoded_frame = self._svs_decode(self._partial_frame)
        self._sync = decoded_frame["FRAME_RECOGNIZED"]

        if self._sync:
            validated_values = decoded_frame.get("VALIDATED_VALUES", {})
            if validated_values:
                _LOGGER.debug("Received: %s", validated_values)
                # Notify all callbacks
                for callback in self._callbacks:
                    callback(validated_values)

    async def get_full_settings(self) -> dict[str, Any]:
        """Request full settings from the device."""
        if not self.is_connected:
            raise BleakError("Device not connected")

        # Request all settings
        frames = [
            self._svs_encode("MEMREAD", "FULL_SETTINGS")[0],
            self._svs_encode("MEMREAD", "PRESET1NAME")[0],
            self._svs_encode("MEMREAD", "PRESET2NAME")[0],
            self._svs_encode("MEMREAD", "PRESET3NAME")[0],
        ]

        for frame in frames:
            if frame:
                await self._client.write_gatt_char(CHAR_UUID, frame)
                await asyncio.sleep(0.2)

        # Wait a bit for responses
        await asyncio.sleep(1)

        # Return empty dict - actual data comes through notifications
        return {}

    async def set_volume(self, volume: int) -> None:
        """Set volume level (-60 to 0 dB)."""
        if not self.is_connected:
            raise BleakError("Device not connected")

        frame, _ = self._svs_encode("MEMWRITE", "VOLUME", volume)
        if frame:
            await self._client.write_gatt_char(CHAR_UUID, frame)
            _LOGGER.debug("Set volume to %d dB", volume)

    async def set_standby(self, mode: int) -> None:
        """Set standby mode (0=AUTO ON, 1=TRIGGER, 2=ON)."""
        if not self.is_connected:
            raise BleakError("Device not connected")

        frame, _ = self._svs_encode("MEMWRITE", "STANDBY", mode)
        if frame:
            await self._client.write_gatt_char(CHAR_UUID, frame)
            _LOGGER.debug("Set standby mode to %d", mode)

    async def set_phase(self, phase: int) -> None:
        """Set phase (0-180 degrees)."""
        if not self.is_connected:
            raise BleakError("Device not connected")

        frame, _ = self._svs_encode("MEMWRITE", "PHASE", phase)
        if frame:
            await self._client.write_gatt_char(CHAR_UUID, frame)
            _LOGGER.debug("Set phase to %d degrees", phase)

    async def set_polarity(self, polarity: int) -> None:
        """Set polarity (0=+, 1=-)."""
        if not self.is_connected:
            raise BleakError("Device not connected")

        frame, _ = self._svs_encode("MEMWRITE", "POLARITY", polarity)
        if frame:
            await self._client.write_gatt_char(CHAR_UUID, frame)
            _LOGGER.debug("Set polarity to %d", polarity)

    def _svs_encode(self, ftype: str, param: str, data: Any = "") -> tuple[bytes, str]:
        """Encode a frame for sending to the device."""
        if ftype == "PRESETLOADSAVE" and SVS_PARAMS[param]["id"] >= 0x18:
            frame = (
                SVS_PARAMS[param]["id"].to_bytes(4, "little") +
                SVS_PARAMS[param]["offset"].to_bytes(2, "little") +
                SVS_PARAMS[param]["n_bytes"].to_bytes(2, "little")
            )
        elif ftype == "MEMWRITE" and SVS_PARAMS[param]["id"] <= 0xA and SVS_PARAMS[param]["limits_type"] != "group":
            if isinstance(data, str) and len(data) > 0 and SVS_PARAMS[param]["limits_type"] == 2:
                encoded_data = bytes(data.ljust(SVS_PARAMS[param]["n_bytes"], "\x00"), 'utf-8')[:SVS_PARAMS[param]["n_bytes"]]
            elif isinstance(data, (int, float)):
                if (SVS_PARAMS[param]["limits_type"] == 1 and data in SVS_PARAMS[param]["limits"]) or \
                   (SVS_PARAMS[param]["limits_type"] == 0 and max(SVS_PARAMS[param]["limits"]) >= data >= min(SVS_PARAMS[param]["limits"])):
                    mask = 0 if data >= 0 else 0xFFFF
                    encoded_data = ((int(10 * abs(data)) ^ mask) + (mask % 2)).to_bytes(2, 'little')
                else:
                    _LOGGER.error("Value for %s out of limits", param)
                    return (b'', "")
            else:
                _LOGGER.error("Value for %s incorrect", param)
                return (b'', "")

            frame = (
                SVS_PARAMS[param]["id"].to_bytes(4, "little") +
                SVS_PARAMS[param]["offset"].to_bytes(2, "little") +
                SVS_PARAMS[param]["n_bytes"].to_bytes(2, "little") +
                encoded_data
            )
        elif ftype == "MEMREAD" and SVS_PARAMS[param]["id"] <= 0xA:
            frame = (
                SVS_PARAMS[param]["id"].to_bytes(4, "little") +
                SVS_PARAMS[param]["offset"].to_bytes(2, "little") +
                SVS_PARAMS[param]["n_bytes"].to_bytes(2, "little")
            )
        elif ftype == "RESET" and SVS_PARAMS[param]["id"] <= 0xA:
            frame = SVS_PARAMS[param]["reset_id"].to_bytes(1, "little")
        elif ftype in ["SUB_INFO1", "SUB_INFO2", "SUB_INFO3"]:
            frame = b'\x00'
        else:
            _LOGGER.error("Unknown frame type to encode: %s", ftype)
            return (b'', "")

        frame = FRAME_PREAMBLE + SVS_FRAME_TYPES[ftype] + (len(frame) + 7).to_bytes(2, "little") + frame
        frame = frame + crc_hqx(frame, 0).to_bytes(2, 'little')
        meta = f"{ftype} {[param]} {str(data) if data else ''}"
        return (frame, meta)

    def _svs_decode(self, frame: bytes) -> dict[str, Any]:
        """Decode a frame received from the device."""
        output: dict[str, Any] = {}

        if len(frame) < 5:
            return {"FRAME_RECOGNIZED": False}

        # Validate frame
        crc_received = frame[-2:]
        crc_calculated = crc_hqx(frame[:-2], 0).to_bytes(2, 'little')
        frame_length = int.from_bytes(frame[3:5], 'little')

        recognized = (
            frame[0] == int.from_bytes(FRAME_PREAMBLE, 'little') and
            frame_length == len(frame) and
            crc_received == crc_calculated
        )

        output["FRAME_RECOGNIZED"] = recognized

        if not recognized:
            return output

        # Identify frame type
        frame_type = None
        for key, value in SVS_FRAME_TYPES.items():
            if value == frame[1:3]:
                frame_type = key
                break

        if not frame_type:
            return output

        output["FRAME_TYPE"] = frame_type
        output["VALIDATED_VALUES"] = {}

        # Parse frame based on type
        if frame_type in ["MEMWRITE", "MEMREAD", "READ_RESP"]:
            id_position = 9 if frame_type == "READ_RESP" else 5
            param_id = int.from_bytes(frame[id_position:id_position + 4], 'little')
            mem_start = int.from_bytes(frame[id_position + 4:id_position + 6], 'little')
            mem_size = int.from_bytes(frame[id_position + 6:id_position + 8], 'little')

            # Read attributes and data
            attributes = []
            for offset in range(0, mem_size, 2):
                for key, value in SVS_PARAMS.items():
                    if value["limits_type"] != "group" and value["id"] == param_id:
                        if (mem_start + offset) == value["offset"]:
                            attributes.append(key)
                            break
                        elif (mem_start + offset) >= value["offset"] and \
                             (mem_start + offset) < (value["offset"] + value["n_bytes"]):
                            break

            # Decode data
            if frame_type != "MEMREAD" and attributes:
                data_start = id_position + 8
                for attrib in attributes:
                    param_info = SVS_PARAMS[attrib]
                    data_bytes = frame[data_start:data_start + param_info["n_bytes"]]

                    if param_info["limits_type"] == 2:
                        # String type
                        value = data_bytes.decode("utf-8").rstrip('\x00')
                        output["VALIDATED_VALUES"][attrib] = value
                    else:
                        # Numeric type
                        raw_value = int.from_bytes(data_bytes, 'little')
                        mask = 0 if raw_value < 0xf000 else 0xFFFF
                        value = ((-1)**(mask % 2)) * ((raw_value - (mask % 2)) ^ mask) / 10

                        # Validate limits
                        if param_info["limits_type"] == 1:
                            check = value in param_info["limits"]
                        elif param_info["limits_type"] == 0:
                            check = max(param_info["limits"]) >= value >= min(param_info["limits"])
                        else:
                            check = False

                        if check:
                            output["VALIDATED_VALUES"][attrib] = int(value) if ".0" in str(value) else value

                    data_start += param_info["n_bytes"]

        return output
