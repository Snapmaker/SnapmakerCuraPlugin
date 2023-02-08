# Snapmaker Cura Plugin

[Cura](https://github.com/Ultimaker/Cura) plugin that provides support for Snapmaker J1 & Snapmaker Artisan.

Features:

- Add machine definitions and quality profiles for Snapmaker 3D printers (Snapmaker J1 & Snapmaker Artisan).
- Add Snapmaker branded materials (including Breakaway Support material).
- Be able to export Snapmaker favoured G-code file format (with informative headers).
- Detect networked printers, and send G-code to the machine.

## Before installing the plugin

Before installing the plugin, make sure you have Cura >= 5 installed.

When you first launch Cura, user guide may ask you to add a printer. You can add a offline printer, say "Ultimaker S5" for now.

You will be able to add Snapmaker J1 printer with plugin installed.

## How to Install (Marketplace)

~~Search "Snapmaker Plugin" in Cura's marketplace (on top right corner of Cura window), and install.~~

(Wait for plugin approval by Ultimaker Team)

## How to Install (Drag and Drop, curapackage release)

- Download `SnapmakerPlugin-{latest version}.curapackage` in [latest release](https://github.com/Snapmaker/SnapmakerJ1CuraPlugin/releases) tab.
- Drag and drop downloaded ".curapackage" file into Cura window.
- Re-start Cura.

## How to Install (Manually, zip release)

- Download `Source code (zip)` in [latest release](https://github.com/Snapmaker/SnapmakerJ1CuraPlugin/releases).
- Unzip downloaded plugin, rename the folder name to "SnapmakerJ1CuraPlugin" (if it has a version suffix).
- Start Cura applcation. Open *Help Menu* -> *Show Configuration Folder*, copy downloaded plugin folder to `plugins` directory.
- Re-start Cura.

## Add Snapmaker J1 printer

Navigate through application menu, **Settings** > **Printers** > **Add Printer...**

In the popup window "Add Printer", select "Add a non-networked printer". Scroll down the available printers to find `Snapmaker` brand, check "Snapmaker J1" option and click "Add". A new "Snapmaker J1" printer should be added successfully.

<img width="744" alt="Add Snapmaker J1 printer" src="https://user-images.githubusercontent.com/3749551/208425647-c568fbbd-d910-426d-b2e7-7fcf4d4c5489.png">

Note that there are several ways in Cura to add a printer, we only cover one in our documentation.

## Use Snapmaker materials

We pre-defined several material under the brand `Snapmaker`, including PLA, ABS, PETG, TPU, PVA and Breakaway.

Pre-defined materials usually has printing temperatures and retraction parameters well tuned by the manufacturer. You can assign them to extruder and use them directly.

Take **Breakaway** material for example, you can tap the extruder selector, in the extruder dialog, choose **Material** > **Snapmaker** > **Breakaway** > **Breakaway Support** to use it.

## Print via network printer

Have your models sliced, you can either export the G-code to local file, or send it to a networked Snapmaker J1:

<img width="360" alt="image" src="https://user-images.githubusercontent.com/3749551/208425792-13a6bf7d-a1e9-408a-a6ec-f1e3f019cc20.png">

## Other languages

- [中文简介 README.md](./README.zh-cn.md)
