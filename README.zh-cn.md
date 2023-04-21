# Snapmaker Cura Plugin

**注意: 请先卸载 Snapmaker J1 Plugin, 再安装 Snapmaker Plugin。**

功能特性:

- 增加 Snapmaker J1 & Snapmaker Artsian & Snapmaker 2.0 双挤出模块 机型和打印质量配置。 
- 增加 Snapmaker 材料（包括 Breakaway 支撑材料)。
- 支持导出 Snapmaker 设备可识别的 G-code 文件。
- 检测联网的 Snapmaker 设备，并传输 G-code 到设备上。

## 安装 Cura 5

在安装插件之前，确保安装 [Cura 5.0](https://ultimaker.com/software/ultimaker-cura) 以上版本。

初次启动 Cura 时，引导流程会要求用户添加一个打印机，这时候我们还未安装插件，可以先选择添加离线的打印机 Ultimaker S5 来跳过引导流程。

## 安装插件 (Marketplace)

在Cura的市场中搜索 "Snapmaker插件"（位于Cura窗口的右上角），然后安装。

## 安装插件 (拖拽安装 curapackage 安装包)

- 在 [Releases](https://github.com/Snapmaker/SnapmakerCuraPlugin/releases) 中点击 `SnapmakerCuraPlugin-{版本号}.curapackage` 下载最新的插件。
- 拖拽下载的 .curapackage 安装包到 Cura 里。
- 重启 Cura。

## 安装插件 (手动安装 zip 压缩文件)

- 在 [Releases](https://github.com/Snapmaker/SnapmakerCuraPlugin/releases) 中点击 `Source code (zip)` 下载最新的插件。
- 解压 zip 文件，并且将文件夹重命名为 "SnapmakerCuraPlugin" (去掉最后的版本号标识)。
- 在 Cura 的菜单中，「帮助」>「显示配置文件夹」，将 "SnapmakerCuraPlugin" 文件夹复制到「plugins」文件夹中。
- 重启 Cura。

## 添加 Snapmaker 打印机

在应用程序菜单中, **设置** > **打印机** > **添加打印机...**

<img width="744" alt="Add Snapmaker printer" src="https://user-images.githubusercontent.com/3749551/208425647-c568fbbd-d910-426d-b2e7-7fcf4d4c5489.png">

## 使用 Snapmaker 材料

安装插件后，可以在软件中添加 Snapmaker 打印机。添加之后，在软件的主页面选择 Snapmaker 打印机，可见到两个打印头的配置。

我们在Snapmaker品牌下预先定义了几种材料，包括PLA、ABS、PETG、TPU、PVA和Breakaway。

预先定义的材料通常具有由制造商调整好的打印温度和回缩参数。您可以将它们分配给挤出机并直接使用。

以分 Breakaway 材料为例，你可以点击挤出机选择器，在挤出机对话框中，选择材料 > Snapmaker > Breakaway > Breakaway Support来使用它。

## 通过网络打印机打印
让您的模型切片，您可以将G代码导出到本地文件，或者将其发送到联网的 Snapmaker 机器上。
<img width="744" alt="Print via network printer" src="https://user-images.githubusercontent.com/3749551/208425792-13a6bf7d-a1e9-408a-a6ec-f1e3f019cc20.png">
