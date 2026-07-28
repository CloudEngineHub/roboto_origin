# Licensing and third-party notices

Unless stated otherwise below, original source code and configuration authored
for this repository are licensed under the GNU General Public License,
version 3 only (`GPL-3.0-only`). See [`LICENSE`](LICENSE) for the complete
license text.

The repository also contains or references third-party components. Their
original licenses and copyright notices continue to apply:

| Path | Component | Version / revision | License |
| --- | --- | --- | --- |
| `thirdparty/realsense-ros` | [RealSense ROS](https://github.com/realsenseai/realsense-ros) | `926f37e01f4f53186fc1817aba36713442d98b3e` | [Apache-2.0](https://github.com/realsenseai/realsense-ros/blob/926f37e01f4f53186fc1817aba36713442d98b3e/LICENSE) |
| `thirdparty/onnxruntime-linux-aarch64-1.21.0.tgz` | [ONNX Runtime](https://github.com/microsoft/onnxruntime) | `v1.21.0`, Linux aarch64 binary archive | [MIT](https://github.com/microsoft/onnxruntime/blob/v1.21.0/LICENSE) |
| `thirdparty/onnxruntime-linux-x64-1.21.0.tgz` | [ONNX Runtime](https://github.com/microsoft/onnxruntime) | `v1.21.0`, Linux x64 binary archive | [MIT](https://github.com/microsoft/onnxruntime/blob/v1.21.0/LICENSE) |

## Model artifact

`models/encoder.onnx` is a model artifact rather than source code. Its training
provenance, underlying model terms, and dataset permissions must be confirmed
before redistribution. The repository-level GPL declaration applies only to
rights held by the repository's copyright holders and does not replace any
third-party terms that may apply to the model.

## 中文说明

除上表另有说明外，本仓库原创的源代码与配置文件采用
GNU GPL 第 3 版且仅限该版本（`GPL-3.0-only`）。第三方组件继续适用其
原有许可证及版权声明，仓库根许可证不会覆盖或替换这些条款。

`models/encoder.onnx` 属于模型产物而非源代码。对外再分发前，维护者须确认
其训练来源、基础模型条款以及数据集权限。
