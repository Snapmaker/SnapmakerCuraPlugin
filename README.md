# Snapmaker J1 Cura Plugin

[Cura](https://github.com/Ultimaker/Cura) plugin that provides support for Snapmaker J1.

Features:

- Add Snapmaker J1 machine definitions and quality configurations.
- Auto detection networked Snapmaker J1, and send G-code to the machine.

## How to install (Marketplace)

Wait for approval...

## How to Install (Manually)

- Install Cura 5
- Download `SnapmakerJ1CuraPlugin` in [release](https://github.com/Snapmaker/SnapmakerJ1CuraPlugin/releases) tab.
- Unzip downloaded plugin, rename the folder name to "SnapmakerJ1CuraPlugin" (if it has a version suffix).
- Start Cura applcation. Open *Help Menu* -> *Show Configuration Folder*, copy downloaded plugin folder to `plugins` directory.
- Re-start Cura.

## Manual Scripts (for quality maintainers)

- Convert Cura profile file to quality file:
 
```Shell
python cura_profile_to_quality.py {cura profile file}
```
