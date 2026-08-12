# License Scope and Inventory / 许可证范围与清单

This file records the license boundaries of `roboparty_deploy`. It does not replace the complete license text in this repository or its dependencies.

本文记录 `roboparty_deploy` 的许可证边界，不替代本仓库及各依赖中的完整许可证文本。

## Repository License / 仓库许可证

Unless otherwise stated, original content authored by RoboParty in this repository is licensed under the GNU General Public License v3.0 only (`GPL-3.0-only`). See [LICENSE](LICENSE).

除另有说明外，本仓库中由 RoboParty 创作的原创内容采用 GNU General Public License v3.0 only（`GPL-3.0-only`），完整条款见 [LICENSE](LICENSE)。

The root license does not relicense Git submodules, packaged binaries, or third-party material. Their copyright notices and license terms must be retained.

根许可证不会对 Git 子模块、已打包二进制文件或第三方资料重新授权；必须保留其版权声明和许可证条款。

## Git Submodules / Git 子模块

| Path | Source | Detected license | Notes |
| --- | --- | --- | --- |
| `src/inference` | [Roboparty/roboparty_inference](https://github.com/Roboparty/roboparty_inference) | GPL-3.0 | Separate source repository and license |
| `src/motors` | [Roboparty/roboparty_motors](https://github.com/Roboparty/roboparty_motors) | GPL-3.0 | Separate source repository and license |
| `src/imu` | [Roboparty/roboparty_imu](https://github.com/Roboparty/roboparty_imu) | GPL-3.0 | Separate source repository and license |
| `tools/create_ap` | [Roboparty/create_ap](https://github.com/Roboparty/create_ap) | BSD-2-Clause | Preserve the upstream copyright and BSD license |
| `src/camera` | [Roboparty/roboparty_camera](https://github.com/Roboparty/roboparty_camera) | GPL-3.0-only | Separate source repository and license |

## Other Distributed Material / 其他分发内容

Files under `assets/`, including Linux kernel packages and configuration material, may originate from third parties or generated distributions. They are not relicensed by this repository-level GPLv3 declaration. Confirm their source, license, notices, and redistribution rights before publishing a release archive or image.

`assets/` 下的 Linux 内核软件包、配置资料等文件可能来自第三方或生成发行物，不会因仓库级 GPLv3 声明而被重新授权。发布压缩包或镜像前，应确认其来源、许可证、通知及再分发权利。

## Contributions / 贡献

Contributions to RoboParty-authored files are accepted under `GPL-3.0-only` unless the target file or component states another license. Contributions to a Git submodule must follow that source repository's contribution and license terms.

对 RoboParty 原创文件的贡献默认采用 `GPL-3.0-only`，目标文件或组件另有说明的除外。对子模块的贡献应遵循对应源仓库的贡献规则和许可证。
