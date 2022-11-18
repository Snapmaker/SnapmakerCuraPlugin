# Snapmaker J1 Cura Plugin

[Cura](https://github.com/Ultimaker/Cura) plugin that provides support for Snapmaker J1.

Features:

- Add Snapmaker J1 machine definitions and quality configurations.
- Add Snapmaker Breakaway Support material.
- Be able to export Snapmaker J1 G-code file format (with headers for J1).
- Auto detection networked Snapmaker J1, and send G-code to the machine.

## How to Install (Marketplace)

Wait for approval...

## How to Install (Manually)

- Install Cura 5.
  (When you first launch Cura, user guide may ask you to add a printer. You can add a offline printer, say "Ultimaker S5" for now.
  You will be able to add Snapmaker J1 printer with plugin installed.)
- Download `SnapmakerJ1CuraPlugin` in [release](https://github.com/Snapmaker/SnapmakerJ1CuraPlugin/releases) tab.
- Unzip downloaded plugin, rename the folder name to "SnapmakerJ1CuraPlugin" (if it has a version suffix).
- Start Cura applcation. Open *Help Menu* -> *Show Configuration Folder*, copy downloaded plugin folder to `plugins` directory.
- Re-start Cura.

## Use Snapmaker Breakaway material

After installed the plugin, created a Snapmaker J1 printer in Cura, you should
be able to see there are 2 extruders on top the window.

To use **Snapmaker Breakaway** material, tap the extruder selector, in the
extruder dialog, choose material > *Snapmaker* > *Breakaway* > *Breakaway Support*.

## Other languages

- [中文简介 README.md](./README.zh-cn.md)