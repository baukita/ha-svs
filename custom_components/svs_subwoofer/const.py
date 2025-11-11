"""Constants for the SVS Subwoofer integration."""
from typing import Final

DOMAIN: Final = "svs_subwoofer"
PLATFORMS: Final = ["media_player", "select"]

# Bluetooth characteristic UUID for SVS subwoofer
CHAR_UUID: Final = "6409d79d-cd28-479c-a639-92f9e1948b43"
SERVICE_UUID: Final = "1fee6acf-a826-4e37-9635-4d8a01642c5d"

# Frame constants
FRAME_PREAMBLE: Final = b'\xaa'

SVS_FRAME_TYPES: Final = {
    "PRESETLOADSAVE": b'\x07\x04',
    "MEMWRITE": b'\xf0\x1f',
    "MEMREAD": b'\xf1\x1f',
    "READ_RESP": b'\xf2\x00',
    "RESET": b'\xf3\x1f',
    "SUB_INFO1": b'\xf4\x1f',
    "SUB_INFO1_RESP": b'\xf5\x00',
    "SUB_INFO2": b'\xfc\x1f',
    "SUB_INFO2_RESP": b'\xfd\x00',
    "SUB_INFO3": b'\xfe\x1f',
    "SUB_INFO3_RESP": b'\xff\x00'
}

SVS_PARAMS: Final = {
    "FULL_SETTINGS": {"id": 4, "offset": 0x0, "limits": [None], "limits_type": "group", "n_bytes": 52, "reset_id": -1},
    "DISPLAY": {"id": 4, "offset": 0x0, "limits": [0, 1, 2], "limits_type": 1, "n_bytes": 2, "reset_id": 0},
    "DISPLAY_TIMEOUT": {"id": 4, "offset": 0x2, "limits": [0, 10, 20, 30, 40, 50, 60], "limits_type": 1, "n_bytes": 2, "reset_id": 1},
    "STANDBY": {"id": 4, "offset": 0x4, "limits": [0, 1, 2], "limits_type": 1, "n_bytes": 2, "reset_id": 2},
    "BRIGHTNESS": {"id": 4, "offset": 0x6, "limits": [0, 1, 2, 3, 4, 5, 6, 7], "limits_type": 1, "n_bytes": 2, "reset_id": 14},
    "LOW_PASS_FILTER_ALL_SETTINGS": {"id": 4, "offset": 0x8, "limits": [None], "limits_type": "group", "n_bytes": 6, "reset_id": 3},
    "LOW_PASS_FILTER_ENABLE": {"id": 4, "offset": 0x8, "limits": [0, 1], "limits_type": 1, "n_bytes": 2, "reset_id": 3},
    "LOW_PASS_FILTER_FREQ": {"id": 4, "offset": 0xa, "limits": [30, 200], "limits_type": 0, "n_bytes": 2, "reset_id": 3},
    "LOW_PASS_FILTER_SLOPE": {"id": 4, "offset": 0xc, "limits": [6, 12, 18, 24], "limits_type": 1, "n_bytes": 2, "reset_id": 3},
    "PEQ1_ALL_SETTINGS": {"id": 4, "offset": 0xe, "limits": [None], "limits_type": "group", "n_bytes": 8, "reset_id": 5},
    "PEQ1_ENABLE": {"id": 4, "offset": 0xe, "limits": [0, 1], "limits_type": 1, "n_bytes": 2, "reset_id": 5},
    "PEQ1_FREQ": {"id": 4, "offset": 0x10, "limits": [20, 200], "limits_type": 0, "n_bytes": 2, "reset_id": 5},
    "PEQ1_BOOST": {"id": 4, "offset": 0x12, "limits": [-12.0, 6.0], "limits_type": 0, "n_bytes": 2, "reset_id": 5},
    "PEQ1_QFACTOR": {"id": 4, "offset": 0x14, "limits": [0.2, 10.0], "limits_type": 0, "n_bytes": 2, "reset_id": 5},
    "PEQ2_ALL_SETTINGS": {"id": 4, "offset": 0x16, "limits": [None], "limits_type": "group", "n_bytes": 8, "reset_id": 5},
    "PEQ2_ENABLE": {"id": 4, "offset": 0x16, "limits": [0, 1], "limits_type": 1, "n_bytes": 2, "reset_id": 5},
    "PEQ2_FREQ": {"id": 4, "offset": 0x18, "limits": [20, 200], "limits_type": 0, "n_bytes": 2, "reset_id": 5},
    "PEQ2_BOOST": {"id": 4, "offset": 0x1a, "limits": [-12.0, 6.0], "limits_type": 0, "n_bytes": 2, "reset_id": 5},
    "PEQ2_QFACTOR": {"id": 4, "offset": 0x1c, "limits": [0.2, 10.0], "limits_type": 0, "n_bytes": 2, "reset_id": 5},
    "PEQ3_ALL_SETTINGS": {"id": 4, "offset": 0x1e, "limits": [None], "limits_type": "group", "n_bytes": 8, "reset_id": 5},
    "PEQ3_ENABLE": {"id": 4, "offset": 0x1e, "limits": [0, 1], "limits_type": 1, "n_bytes": 2, "reset_id": 5},
    "PEQ3_FREQ": {"id": 4, "offset": 0x20, "limits": [20, 200], "limits_type": 0, "n_bytes": 2, "reset_id": 5},
    "PEQ3_BOOST": {"id": 4, "offset": 0x22, "limits": [-12.0, 6.0], "limits_type": 0, "n_bytes": 2, "reset_id": 5},
    "PEQ3_QFACTOR": {"id": 4, "offset": 0x24, "limits": [0.2, 10.0], "limits_type": 0, "n_bytes": 2, "reset_id": 5},
    "ROOM_GAIN_ALL_SETTINGS": {"id": 4, "offset": 0x26, "limits": [None], "limits_type": "group", "n_bytes": 6, "reset_id": 8},
    "ROOM_GAIN_ENABLE": {"id": 4, "offset": 0x26, "limits": [0, 1], "limits_type": 1, "n_bytes": 2, "reset_id": 8},
    "ROOM_GAIN_FREQ": {"id": 4, "offset": 0x28, "limits": [25, 31, 40], "limits_type": 1, "n_bytes": 2, "reset_id": 8},
    "ROOM_GAIN_SLOPE": {"id": 4, "offset": 0x2a, "limits": [6, 12], "limits_type": 1, "n_bytes": 2, "reset_id": 8},
    "VOLUME": {"id": 4, "offset": 0x2c, "limits": [-60, 0], "limits_type": 0, "n_bytes": 2, "reset_id": 12},
    "PHASE": {"id": 4, "offset": 0x2e, "limits": [0, 180], "limits_type": 0, "n_bytes": 2, "reset_id": 9},
    "POLARITY": {"id": 4, "offset": 0x30, "limits": [0, 1], "limits_type": 1, "n_bytes": 2, "reset_id": 10},
    "PORTTUNING": {"id": 4, "offset": 0x32, "limits": [20, 30], "limits_type": 1, "n_bytes": 2, "reset_id": 11},
    "PRESET1NAME": {"id": 8, "offset": 0x0, "limits": [""], "limits_type": 2, "n_bytes": 8, "reset_id": 13},
    "PRESET2NAME": {"id": 9, "offset": 0x0, "limits": [""], "limits_type": 2, "n_bytes": 8, "reset_id": 13},
    "PRESET3NAME": {"id": 0xA, "offset": 0x0, "limits": [""], "limits_type": 2, "n_bytes": 8, "reset_id": 13},
    "PRESET1LOAD": {"id": 0x18, "offset": 0x1, "limits": [None], "limits_type": -1, "n_bytes": 0, "reset_id": -1},
    "PRESET2LOAD": {"id": 0x19, "offset": 0x1, "limits": [None], "limits_type": -1, "n_bytes": 0, "reset_id": -1},
    "PRESET3LOAD": {"id": 0x1A, "offset": 0x1, "limits": [None], "limits_type": -1, "n_bytes": 0, "reset_id": -1},
    "PRESET4LOAD": {"id": 0x1B, "offset": 0x1, "limits": [None], "limits_type": -1, "n_bytes": 0, "reset_id": -1},
    "PRESET1SAVE": {"id": 0x1C, "offset": 0x1, "limits": [None], "limits_type": -1, "n_bytes": 0, "reset_id": -1},
    "PRESET2SAVE": {"id": 0x1D, "offset": 0x1, "limits": [None], "limits_type": -1, "n_bytes": 0, "reset_id": -1},
    "PRESET3SAVE": {"id": 0x1E, "offset": 0x1, "limits": [None], "limits_type": -1, "n_bytes": 0, "reset_id": -1}
}

# Standby mode mapping
STANDBY_MODES: Final = {
    0: "auto_on",
    1: "trigger",
    2: "on"
}
