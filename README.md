# Atom XR 遥操作

基于 [Unitree xr_teleoperate](https://github.com/unitreerobotics/xr_teleoperate) 修改，面向 Atom 机器人与 PICO VR 的双臂遥操作。

## 环境

- Ubuntu 20.04 / 22.04
- Python 3.10
- ROS2 Python 环境
- PICO VR 设备
- Atom 机器人控制链路

## 安装

### 1. 创建环境

推荐先创建独立环境：

```bash
conda create -n atom_xr python=3.10 -y
conda activate atom_xr
```

### 2. 安装 IK 依赖

`pinocchio` 和 `casadi` 建议通过 `conda-forge` 安装：

```bash
conda install -c conda-forge pinocchio casadi numpy=1.26.4 -y
```

### 3. 安装仓库依赖

在仓库根目录执行：

```bash
pip install -r requirements.txt
```

### 4. 准备 ROS2

运行前请确认当前终端已经 source 过对应的 ROS2 环境，并且可以正常导入：

- `rclpy`
- `sensor_msgs`

## 证书配置

PICO 通过浏览器访问遥操作页面时，需要 HTTPS 证书。

在仓库根目录执行：

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.pem -out cert.pem
```

如果主机开了防火墙，请放行 `8012` 端口：

```bash
sudo ufw allow 8012
```

## 启动

在仓库根目录执行：

```bash
python teleop/xr_Control_Atom.py --xr-mode controller
```

常用参数：

- `--xr-mode {hand,controller}`：选择 XR 跟踪模式，默认 `controller`
- `--frequency`：控制频率，默认 `30`
- `--headless`：关闭 IK 可视化

## PICO 使用流程

以下流程默认：

- PICO 与运行程序的主机在同一局域网
- 主机 IP 为 `192.168.123.2`
- 使用 `controller` 模式

如果你的主机 IP 不同，请把下面 URL 中的 `192.168.123.2` 替换成实际地址。

### 1. 启动控制程序

```bash
python teleop/xr_Control_Atom.py --xr-mode controller
```

程序启动后会等待开始信号。

### 2. 在 PICO 浏览器打开页面

在 PICO 浏览器访问：

```text
https://192.168.123.2:8012/?ws=wss://192.168.123.2:8012
```

如果浏览器提示证书不安全，点击继续访问即可。

### 3. 进入 VR

进入页面后：

1. 点击 `Virtual Reality`
2. 接受浏览器和设备弹出的权限请求
3. 等待 XR 会话建立完成

终端出现连接日志后，说明 PICO 已接入成功。

### 4. 开始遥操作

终端键位：

- `r`：开始主循环
- `a`：允许发送机械臂命令
- `q`：退出程序

控制器键位：

- 右手 `A`：开始发送命令
- 右手 `B`：停止发送命令

建议先让操作者手臂接近机器人初始姿态，再开始发送控制命令。

## 运行建议

- 首次使用时，先在安全空间内做小范围动作测试
- 开始发送命令前，确认机器人周围无人靠近
- 退出前，建议先让机械臂回到较自然的位置

## 目录

```text
RPO_teleoperate/
├── assets/
│   └── Atom01_urdf/
├── teleop/
│   ├── robot_control/
│   │   └── robot_arm_ik.py
│   ├── utils/
│   │   └── weighted_moving_filter.py
│   └── xr_Control_Atom.py
├── televuer/
├── LICENSE
├── README.md
└── requirements.txt
```

## 致谢

本项目基于 [Unitree xr_teleoperate](https://github.com/unitreerobotics/xr_teleoperate) 修改实现。相关许可信息见 [LICENSE](/C:/Users/10029/Desktop/Code/RPO_teleoperate/LICENSE)。
