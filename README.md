# Snapmaker J1 Cura Plugin

[Cura](https://github.com/Ultimaker/Cura) plugin that provides support for Snapmaker J1.

Features:

- Add Snapmaker J1 machine definitions and quality configurations.

## How to install (Marketplace)

TODO

## How to Install (Manually)

- Install Cura 5
- Download `SnapmakerJ1CuraPlugin` in [release] tab.
- Start Cura applcation. Open *Help Menu* -> *Show Configuration Folder*. Copy downloaded plugin folder to `plugins` folder.
- Re-start Cura.

## Scripts

- Import Cura profile:
 
```Shell
python -m scripts.import_curaprofile {Cura profile file} {output folder}
```

- Run checks on quality profile, and format it:

```Shell
python -m scripts.validate_machine_quality {quality file}
```