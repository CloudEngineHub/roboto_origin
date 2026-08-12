# Third-party notices / 第三方通知

`roboto_origin` contains snapshots of RoboParty repositories, upstream source
code and prebuilt files. The root [`LICENSE`](LICENSE) applies only where the
scope map in [`LICENSES.md`](LICENSES.md) says it applies. Third-party material
keeps its original copyright and license.

`roboto_origin` 包含 RoboParty 仓库快照、上游源码和预编译文件。根目录
[`LICENSE`](LICENSE) 只适用于 [`LICENSES.md`](LICENSES.md) 指定的范围。第三方
内容沿用原版权和许可证。

## Source code with an identified license / 已确认许可证的源码

| Path | Project and source | License in this snapshot |
| --- | --- | --- |
| `modules/roboparty_deploy/src/camera/thirdparty/realsense-ros/` | [RealSense ROS](https://github.com/realsenseai/realsense-ros), commit `926f37e01f4f53186fc1817aba36713442d98b3e` | Apache-2.0; retain the bundled [`LICENSE`](modules/roboparty_deploy/src/camera/thirdparty/realsense-ros/LICENSE) and [`NOTICE.md`](modules/roboparty_deploy/src/camera/thirdparty/realsense-ros/NOTICE.md). |
| `modules/roboparty_deploy/src/inference/thirdparty/cnpy/` | [cnpy](https://github.com/rogersce/cnpy), copyright Carl Rogers | MIT; see the bundled [`LICENSE`](modules/roboparty_deploy/src/inference/thirdparty/cnpy/LICENSE). |
| `modules/roboparty_deploy/src/inference/thirdparty/yaml-cpp-0.9.0.tar.gz` | [yaml-cpp](https://github.com/jbeder/yaml-cpp), version 0.9.0, copyright Jesse Beder | MIT; the archive contains its license. |
| `modules/roboparty_deploy/tools/create_ap/` | [create_ap](https://github.com/oblique/create_ap), copyright oblique | BSD-2-Clause; see the bundled [`LICENSE`](modules/roboparty_deploy/tools/create_ap/LICENSE). |
| `modules/roboparty_navigation/nlink_parser_ros2/src/nlink_parser_ros2/src/utils/nlink_unpack/` and `protocol_extracter/` | Utility code, copyright Peter Fankhauser, Autonomous Systems Lab, ETH Zurich | BSD-3-Clause; each directory contains a `LICENSE`. |
| `modules/roboparty_train/rsl_rl/` | [rsl_rl](https://github.com/leggedrobotics/rsl_rl), ETH Zurich and NVIDIA | BSD-3-Clause; see the bundled [`LICENSE`](modules/roboparty_train/rsl_rl/LICENSE) and `licenses/dependencies/`. |
| Parkour-related files under `modules/roboparty_train/robolab/` | [InstinctLab](https://github.com/project-instinct/InstinctLab) | CC-BY-NC-4.0. This part is non-commercial and cannot be relicensed under BSD or GPL. |
| `modules/roboparty_xr_teleop/` | Modified from [Unitree xr_teleoperate](https://github.com/unitreerobotics/xr_teleoperate) | Unitree's original code retains Apache-2.0 notices. RoboParty's modifications and the combined work are distributed under GPL-3.0-only. See the module [`THIRD_PARTY_NOTICES.md`](modules/roboparty_xr_teleop/THIRD_PARTY_NOTICES.md). |
| `modules/roboparty_firmware/orangepi-build/` | Orange Pi build system snapshot | GPL-2.0 at the module root. Nested packages, cached source and vendor blobs retain their own terms. |
| `modules/roboparty_firmware/roboto_usb2can/` | Zephyr-based USB-to-CAN firmware | Files carrying an SPDX notice use Apache-2.0. Zephyr and other dependencies retain their own licenses. |
| Third-party material under `modules/rpo_hardware/` | Vendor and standard-parts models used for reference or assembly context | Not covered by the module's RoboParty licenses unless a file has its own permission. See the module [`THIRD_PARTY_NOTICES.md`](modules/rpo_hardware/THIRD_PARTY_NOTICES.md). |

## RoboParty-trained policy models / RoboParty 自训练策略模型

The nine ONNX files under
`modules/roboparty_deploy/src/inference/robots/rpo/models/` were trained by
RoboParty and are owned by RoboParty. They are retained in the public snapshot.
The release record should identify the training-code revision, configuration
and data source used for each model.

`modules/roboparty_deploy/src/inference/robots/rpo/models/` 下的 9 个 ONNX
策略模型均由 RoboParty 自主训练，版权归 RoboParty，保留在公开快照中。发布记录
应注明每个模型对应的训练代码提交、配置和数据来源。

## Prebuilt archives / 预编译压缩包

The following archives include their own license files and notices:

以下压缩包内含许可证及第三方通知：

- `modules/roboparty_deploy/src/camera/thirdparty/onnxruntime-linux-{x64,aarch64}-1.21.0.tgz`
- `modules/roboparty_deploy/src/inference/thirdparty/onnxruntime-linux-{x64,aarch64}-1.21.0.tgz`

All four are Microsoft ONNX Runtime 1.21.0, commit
`e0b66cad282043d4377cea5269083f17771b6dfc`, under MIT. Each archive contains
`LICENSE` and `ThirdPartyNotices.txt`.

四个文件均为 Microsoft ONNX Runtime 1.21.0，对应提交
`e0b66cad282043d4377cea5269083f17771b6dfc`，采用 MIT。每个压缩包都包含
`LICENSE` 和 `ThirdPartyNotices.txt`。

## Files that still need provenance records / 来源记录待补的文件

The repository does not contain enough information to assign a source and
redistribution basis to the following files:

仓库内现有信息不足以确认以下文件的来源和再分发依据：

| Path | Missing record |
| --- | --- |
| `modules/roboparty_deploy/assets/linux-{dtb,headers,image}-legacy-rockchip-rk3588_1.2.0_arm64.deb` | Download or build source, upstream source revision, package copyright file and source-code offer. |
| `modules/roboparty_train/robolab/data/motions/**` | Source dataset, creator, license and permission for the converted `.pkl`, `.npz` and `.csv` files. |
| `modules/roboparty_firmware/orangepi-build/external/cache/debs/**` | Package repository or build source and the copyright file for each cached package. This snapshot contains 102 `.deb` files in this directory. |
| Binary firmware and libraries under `modules/roboparty_firmware/orangepi-build/external/cache/` and `external/packages/` | Vendor or upstream source, exact version and redistribution terms. |
| `modules/roboparty_firmware/roboto_usb2can/scripts/libusb-1.0.dll` | Upstream build, version, license and notices shipped with the binary. |

Listing a file here records its current status; it does not grant permission
to redistribute it. A public release should include only files whose source,
license and required notices are recorded.

列入本节只表示当前状态，不构成再分发授权。公开发布时只应包含已记录来源、
许可证和所需通知的文件。
