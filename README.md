# SVS Subwoofer Home Assistant Integration

A custom Home Assistant integration for controlling SVS subwoofers via Bluetooth. Only tested with SB-1000 Pro subwoofer, other models may or may not work.

Works with ESPHome Bluetooth proxies.

## Important Note

**The subwoofer can only maintain one Bluetooth connection at a time.** If the SVS mobile app is connected to your subwoofer, Home Assistant will fail to connect. Similarly, if Home Assistant is connected, the mobile app will not be able to connect. Make sure to disconnect the mobile app before adding the integration, and to disable the device in Home Assistant before attempting to use the SVS app.

## Features

- Volume control with native Home Assistant media player interface
- Standby mode selection (Auto On, Trigger, On)
- Real-time state updates via Bluetooth notifications
- Additional attributes exposed (phase, polarity, filters, etc.)
- Automatic device discovery via Bluetooth
- ESPHome Bluetooth proxy support

## Installation

1. Copy the `custom_components/svs_subwoofer` directory to your Home Assistant `config/custom_components/` directory

2. Restart Home Assistant

3. Go to Settings > Devices & Services > Add Integration

4. Search for "SVS Subwoofer"

5. Select your subwoofer from the discovered devices

## Usage

Once installed, your SVS subwoofer appears as a media player entity:

### Volume Control

- Use the media player card in Home Assistant UI
- Adjust volume from -60 dB to 0 dB
- Volume slider automatically converts between Home Assistant (0.0-1.0) and SVS (-60 to 0 dB) ranges

### Power Control

- Turn On: Sets subwoofer to "ON" mode (always active)
- Turn Off: Sets subwoofer to "AUTO ON" mode (power-saving)

### Additional Attributes

The media player exposes additional attributes accessible in automations and templates:

- `phase`: Phase adjustment (0-180 degrees)
- `polarity`: Polarity setting (+ or -)
- `standby_mode`: Current standby mode (auto_on, trigger, or on)
- `low_pass_filter`: Low pass filter state (on/off)
- `low_pass_filter_freq`: Low pass filter frequency (Hz)
- `room_gain`: Room gain compensation (on/off)
- `volume_db`: Volume in dB (easier for automations)

### Example Automation

```yaml
automation:
  - alias: "Movie Mode - Boost Subwoofer"
    trigger:
      - platform: state
        entity_id: media_player.living_room_tv
        to: "playing"
    condition:
      - condition: state
        entity_id: input_select.media_scene
        state: "Movie"
    action:
      - service: media_player.volume_set
        target:
          entity_id: media_player.svs_subwoofer
        data:
          volume_level: 0.75 # -15 dB

  - alias: "Night Mode - Lower Subwoofer"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: media_player.volume_set
        target:
          entity_id: media_player.svs_subwoofer
        data:
          volume_level: 0.5 # -30 dB
```

### Template Examples

```yaml
# Display volume in dB
sensor:
  - platform: template
    sensors:
      subwoofer_volume_db:
        friendly_name: "Subwoofer Volume"
        value_template: "{{ state_attr('media_player.svs_subwoofer', 'volume_db') }}"
        unit_of_measurement: "dB"

# Check if low pass filter is enabled
binary_sensor:
  - platform: template
    sensors:
      subwoofer_lpf_enabled:
        friendly_name: "Subwoofer LPF"
        value_template: "{{ state_attr('media_player.svs_subwoofer', 'low_pass_filter') == 'on' }}"
```

## Credits

Based on [pySVS](https://github.com/logon84/pySVS) by [logon84](https://github.com/logon84).

## License

This integration inherits the license from the original pySVS project.
