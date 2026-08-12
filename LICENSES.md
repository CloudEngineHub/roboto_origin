# License scope / 许可证范围

`roboto_origin` is a snapshot aggregation repository. It contains material under several licenses. The root [`LICENSE`](LICENSE) does not replace a license or copyright notice stored in a module, subdirectory, or individual file.

`roboto_origin` 是一个快照聚合仓库，仓库内容采用多种许可证。根目录的 [`LICENSE`](LICENSE) 不会替代模块、子目录或文件中已有的许可证及版权声明。

Third-party sources, notices and unresolved binary provenance are listed in [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

第三方来源、版权通知以及来源待确认的二进制文件见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

## Scope map / 范围说明

| Path | License scope |
| --- | --- |
| Repository-root files, `.github/`, and `assets/` | RoboParty-authored material without a more specific notice is licensed under `GPL-3.0-only`. The root license grants no rights in third-party material. / 其中由 RoboParty 创作且没有单独声明的内容采用 `GPL-3.0-only`。根许可证不授权第三方资料。 |
| `modules/roboparty_deploy/` | RoboParty-authored material is `GPL-3.0-only`; embedded components and binaries retain their own terms. See [`modules/roboparty_deploy/LICENSES.md`](modules/roboparty_deploy/LICENSES.md). / RoboParty 原创内容采用 `GPL-3.0-only`；内含组件和二进制文件沿用各自条款。 |
| `modules/roboparty_firmware/` | The module-level default is `GPL-3.0`; nested projects and third-party files with their own notices are exceptions. For example, `orangepi-build` carries `GPL-2.0`. / 模块默认采用 `GPL-3.0`；有单独声明的内嵌项目和第三方文件除外，例如 `orangepi-build` 采用 `GPL-2.0`。 |
| `modules/roboparty_navigation/` | The module-level default is `GPL-3.0`; nested components with their own license files retain those licenses, including BSD-licensed utility code. / 模块默认采用 `GPL-3.0`；带有单独许可证的内嵌组件沿用原许可证，其中包括 BSD 许可的工具代码。 |
| `modules/roboparty_train/` | The module README declares `BSD-3-Clause`. The bundled `robolab` and `rsl_rl` snapshots carry separate `BSD-3-Clause` license files and dependency notices. / 模块 README 声明采用 `BSD-3-Clause`；其中 `robolab`、`rsl_rl` 快照各自带有 `BSD-3-Clause` 许可证及依赖声明。 |
| `modules/roboparty_xr_teleop/` | The combined work and RoboParty-owned material are `GPL-3.0-only`. Unitree-derived code retains its copyright and Apache License 2.0 notice. See [`modules/roboparty_xr_teleop/LICENSES.md`](modules/roboparty_xr_teleop/LICENSES.md). / 组合作品及 RoboParty 所有内容采用 `GPL-3.0-only`；源自 Unitree 的代码保留原版权和 `Apache-2.0` 声明。 |
| `modules/rpo_hardware/` | Hardware design, software, documentation, and third-party material are licensed separately. See [`modules/rpo_hardware/LICENSES.md`](modules/rpo_hardware/LICENSES.md). / 硬件设计、软件、文档和第三方资料分别授权，详见该目录的 LICENSES.md。 |
| `modules/rpo_appearance/` | `CERN-OHL-W-2.0`. See [`modules/rpo_appearance/LICENSE`](modules/rpo_appearance/LICENSE). / 采用 `CERN-OHL-W-2.0`。 |
| `modules/rpo_description/` | `CERN-OHL-W-2.0`. See [`modules/rpo_description/LICENSE`](modules/rpo_description/LICENSE). / 采用 `CERN-OHL-W-2.0`。 |

## Rules / 使用规则

- A license notice in a file or a nearer directory overrides the module or repository default.
- Third-party material keeps its original copyright and license terms. Its presence in this repository does not relicense it.
- If a file's origin or license cannot be identified, do not redistribute it until the rights are confirmed.
- Open-source licenses do not grant rights to RoboParty names, logos, or product marks.

- 文件或下级目录中的许可证声明优先于模块或仓库默认规则。
- 第三方资料沿用原版权和许可证；进入本仓库不等于被重新授权。
- 无法确认来源或许可证的文件，在权利确认前不应再分发。
- 开源许可证不授权 RoboParty 的名称、Logo 或产品标识。
