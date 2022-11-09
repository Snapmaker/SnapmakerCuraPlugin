# Snapmaker J1 Cura Plugin

[Cura](https://github.com/Ultimaker/Cura) plugin that provides support for Snapmaker J1.

Features:

- Add Snapmaker J1 machine definitions and quality configurations.
- Auto detection networked Snapmaker J1, and send G-code to the machine.

## How to install (Marketplace)

TODO

## How to Install (Manually)

- Install Cura 5
- Download `SnapmakerJ1CuraPlugin` in [release](https://github.com/Snapmaker/SnapmakerJ1CuraPlugin/releases) tab.
- Start Cura applcation. Open *Help Menu* -> *Show Configuration Folder*. Copy downloaded plugin folder to `plugins` folder.
- Re-start Cura.

## Manual Scripts (for quality maintainers)

- Convert Cura profile file to quality file:
 
```Shell
python cura_profile_to_quality.py {cura profile file}
```