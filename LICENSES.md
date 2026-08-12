# Licensing Scope

This file explains the licensing boundaries of the `roboto_origin` aggregation repository. It does not replace any license text or change the license of any existing material.

## Aggregation layer

Unless a file states otherwise, RoboParty-authored aggregation-layer material outside `modules/` is provided under GNU General Public License version 3, as set out in the root [LICENSE](LICENSE) file.

## Module snapshots and third-party material

The directories under `modules/` are synchronized snapshots of separate repositories. Each snapshot and any third-party material within it remain subject to their own applicable copyright notices and license terms. Inclusion in this aggregation repository does not transfer ownership and does not relicense that material under the root `LICENSE`.

| Snapshot path | Source repository |
| --- | --- |
| `modules/roboparty_deploy` | [Roboparty/roboparty_deploy](https://github.com/Roboparty/roboparty_deploy) |
| `modules/roboparty_firmware` | [Roboparty/roboparty_firmware](https://github.com/Roboparty/roboparty_firmware) |
| `modules/roboparty_navigation` | [Roboparty/roboparty_navigation](https://github.com/Roboparty/roboparty_navigation) |
| `modules/roboparty_train` | [Roboparty/roboparty_train](https://github.com/Roboparty/roboparty_train) |
| `modules/roboparty_xr_teleop` | [Roboparty/roboparty_xr_teleop](https://github.com/Roboparty/roboparty_xr_teleop) |
| `modules/rpo_appearance` | [Roboparty/rpo_appearance](https://github.com/Roboparty/rpo_appearance) |
| `modules/rpo_description` | [Roboparty/rpo_description](https://github.com/Roboparty/rpo_description) |
| `modules/rpo_hardware` | [Roboparty/rpo_hardware](https://github.com/Roboparty/rpo_hardware) |

Within a module snapshot, the most specific file- or directory-level license notice takes precedence. If a snapshot does not contain sufficient license information, do not infer that the root GPL applies; consult the source repository before redistribution.

## Contributions

New contributions made directly to the aggregation layer are accepted under GNU GPL version 3 unless the target file states otherwise. Module-level contributions must be made to the corresponding source repository and follow that repository's applicable contribution and license terms.

This policy applies prospectively to new contributions and does not relicense existing module snapshots or third-party material.

---

# 许可证适用范围

本文说明 `roboto_origin` 聚合仓库中的许可证边界。本文不替代任何许可证正文，也不改变任何现有内容的许可证。

## 聚合层

除非具体文件另有说明，位于 `modules/` 之外、由 RoboParty 创作的聚合层内容，按根目录 [LICENSE](LICENSE) 所载的 GNU 通用公共许可证第 3 版提供。

## 模块快照和第三方内容

`modules/` 下的目录是独立仓库的同步快照。每个快照及其中的第三方内容，继续适用其各自的版权声明和许可证条款。将这些内容收录到本聚合仓库不表示所有权转移，也不会使其被根目录 `LICENSE` 重新许可。

各快照的来源仓库见上表。模块快照内应以适用范围最具体的文件级或目录级许可证声明为准。如果快照中没有充分的许可证信息，不应推定根目录 GPL 自动适用；再分发前应查阅对应的来源仓库。

## 贡献

直接提交到聚合层的新贡献，除非目标文件另有说明，按 GNU GPL 第 3 版接收。模块级贡献必须提交到对应的来源仓库，并遵循该仓库适用的贡献规则和许可证条款。

本规则仅面向未来的新贡献，不会对现有模块快照或第三方内容进行重新许可。