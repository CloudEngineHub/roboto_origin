# atom01_firmware - ROBOTO_ORIGIN 固件模块

ROBOTO_ORIGIN 人形机器人的固件及板卡镜像构建系统。

## 概述

本模块包含机器人嵌入式系统所需的固件组件和板卡镜像构建系统。

## 子模块

| 模块 | 说明 |
|------|------|
| [roboto_usb2can](./roboto_usb2can) | USB 转 CAN 适配器固件 - 提供主机与机器人 CAN 总线之间的通信接口 |
| [orangepi-build](./orangepi-build) | OrangePi 板卡镜像构建系统 - 为 RK 系列板卡编译定制 Linux 镜像 |
| [x5-rdk-gen](./x5-rdk-gen) | RP0 X5 镜像构建系统 - 为 X5 平台生成固件镜像 |

## 快速开始

```bash
# 克隆仓库（含子模块）
git clone --recursive https://github.com/Roboparty/atom01_firmware.git

# 或克隆后初始化子模块
git submodule update --init --recursive
```

镜像文件都在每个子模块的 release 里面。

## 目录结构

```
atom01_firmware/
├── roboto_usb2can/      # USB2CAN 固件源码
├── orangepi-build/      # OrangePi 构建系统
│   └── external/cache/sources/bms_daemon/  # BMS 守护进程（嵌套）
├── x5-rdk-gen/          # X5 RDK 生成器
├── readme.md            # 英文文档
└── readme_cn.md         # 中文文档
```

## 关联仓库

- **[Atom01_hardware](https://github.com/Roboparty/Atom01_hardware)** - 硬件设计文件
- **[atom01_deploy](https://github.com/Roboparty/atom01_deploy)** - ROS2 部署框架
- **[atom01_train](https://github.com/Roboparty/atom01_train)** - RL 训练环境
- **[atom01_description](https://github.com/Roboparty/atom01_description)** - URDF 模型文件

## 许可证

本项目采用 GNU 通用公共许可证第三版 (GPLv3) 授权。

## 贡献指南

请参阅主仓库 [roboto_origin](https://github.com/Roboparty/roboto_origin) 了解贡献指南。
