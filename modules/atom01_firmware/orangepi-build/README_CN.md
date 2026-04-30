# Orange Pi 构建系统

**[English Documentation](README.md) | 简体中文**

一个用于创建 Orange Pi Linux 发行版镜像的综合构建系统，支持多种 SoC 和板卡变体。

## 功能特性

- 🎯 **多平台支持**：支持 13+ 款 Orange Pi 板卡，覆盖多种 SoC
- 🔧 **灵活配置**：可自定义板卡配置、引导环境和内核参数
- 📦 **包管理**：内置包管理功能，支持 aptly
- 🎨 **多种发行版**：支持 CLI、Desktop 和 Server 等多种桌面环境
- 🚀 **优化编译**：模块化脚本，提高编译效率
- 🛠️ **扩展支持**：支持为特定板卡添加自定义扩展

## 支持的板卡

| SoC | 板卡 |
|:--|:--|
| Allwinner H6 | Orange Pi 3 / 3 LTS |
| Allwinner H616 | Orange Pi Zero2 / Zero2w / Zero3 |
| Allwinner T527 | Orange Pi 4A |
| Allwinner A733 | Orange Pi 4Pro |
| Rockchip RK3399 | Orange Pi 4 / 4B / 4 LTS / 800 |
| Rockchip RK3566 | Orange Pi 3B / CM4 |
| Rockchip RK3588S | Orange Pi 5 / 5B / 5Pro / CM5 / CM5-tablet |
| Rockchip RK3588 | Orange Pi 5Plus / 5MAX / 5Ultra |
| Cix P1 | Orange Pi 6Plus |
| Starfive JH7110 | Orange Pi RV |
| Kylin X1 | Orange Pi RV2 / R2S |

## 系统要求

- **主机系统**：Ubuntu 22.04 (Jammy) 或兼容的 Debian 发行版
- **架构**：x86_64
- **权限**：需要 root/sudo 权限
- **磁盘空间**：建议 100GB+ 可用空间
- **网络**：需要访问 Ubuntu 仓库和 GitHub

## 快速开始

```bash
cd orangepi-build

# 主要构建入口
./build.sh
```

编译时选择板卡：

| 固件 | 板卡选择 |
|:--|:--|
| 01 | `robopi1` |
| 02 | `robopi2` |
| 03 | `robopi3` |

**推荐内核版本**：`current`

## 目录结构

```
.
├── build.sh                 # 主构建入口
├── scripts/                 # 构建脚本
│   ├── main.sh             # 主要编排脚本
│   ├── compilation.sh      # 核心编译逻辑
│   ├── configuration.sh    # 配置管理
│   ├── debootstrap.sh      # Root 文件系统初始化
│   ├── extensions.sh       # 扩展处理
│   ├── distributions.sh    # 发行版设置
│   └── image-helpers.sh    # 镜像工具
├── external/               # 外部资源
│   ├── cache/              # 包和源码缓存
│   ├── config/             # 板卡和系统配置
│   ├── extensions/         # 扩展脚本
└── └── packages/           # 自定义包
```

## 官方链接

- 📌 **官方网站**：[Orange Pi](http://www.orangepi.org)
- 🇨🇳 **中文官网**：[Orange Pi 中文](http://www.orangepi.cn)
- 📖 **OrangePi 5 Plus 用户手册**：[OrangePi_5_Plus_RK3588_用户手册_v2.1.pdf](OrangePi_5_Plus_RK3588_%E7%94%A8%E6%88%B7%E6%89%8B%E5%86%8C_v2.1.pdf)

（烧录系统请参考第118页）

镜像在release里面，建议使用最新镜像。

## 许可证

本项目根据 LICENSE 文件中指定的条款发行。
