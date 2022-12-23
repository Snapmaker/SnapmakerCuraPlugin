# Snapmaker J1 Cura Plugin

Snapmaker J1 的 [Cura](https://github.com/Ultimaker/Cura) 插件。

功能特性:

- 增加 Snapmaker J1 机型和打印质量配置。 
- 增加 Snapmaker 材料（包括 Breakaway 支撑材料)。
- 支持导出 Snapmaker J1 可识别的 G-code 文件。
- 检测联网的 Snapmaker J1 设备，并传输 G-code 到设备上。

## 安装 Cura 5

在安装插件之前，确保安装 [Cura 5.0](https://ultimaker.com/software/ultimaker-cura) 以上版本。

初次启动 Cura 时，引导流程会要求用户添加一个打印机，这时候我们还未安装插件，可以先选择添加离线的打印机 Ultimaker S5 来跳过引导流程。

## 安装插件 (Marketplace)

等待插件审核中……

## 安装插件 (拖拽安装 curapackage 安装包)

- 在 [Releases](https://github.com/Snapmaker/SnapmakerJ1CuraPlugin/releases) 中点击 `SnapmakerJ1CuraPlugin-{版本号}.curapackage` 下载最新的插件。
- 拖拽下载的 .curapackage 安装包到 Cura 里。
- 重启 Cura。

## 安装插件 (手动安装 zip 压缩文件)

- 在 [Releases](https://github.com/Snapmaker/SnapmakerJ1CuraPlugin/releases) 中点击 `Source code (zip)` 下载最新的插件。
- 解压 zip 文件，并且将文件夹重命名为 "SnapmakerJ1CuraPlugin" (去掉最后的版本号标识)。
- 在 Cura 的菜单中，「帮助」>「显示配置文件夹」，将 "SnapmakerJ1CuraPlugin" 文件夹复制到「plugins」文件夹中。
- 重启 Cura。

## 添加 Snapmaker J1 打印机

在应用程序菜单中, **设置** > **打印机** > **添加打印机...**

<img width="744" alt="Add Snapmaker J1 printer" src="https://user-images.githubusercontent.com/3749551/208425647-c568fbbd-d910-426d-b2e7-7fcf4d4c5489.png">

## 使用 Snapmaker Breakaway 支撑材料

安装插件后，可以在软件中添加 Snapmaker J1 打印机。添加之后，在软件的主页面选择 Snapmaker J1 打印机，可见到两个打印头的配置。

点击打印头配置，可以单独给左喷头或者右喷头设置使用 Snapmaker Breakaway 支撑材料。
我们已经准备好了 Snapmaker Breakaway 不同打印质量的配置，直接开始使用即可。
