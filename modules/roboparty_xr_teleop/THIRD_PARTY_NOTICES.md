# Third-Party Notices

This repository is distributed under `GPL-3.0-only`. It contains software
derived from third-party projects and uses third-party dependencies. Their
copyright and attribution notices remain in force.

## Unitree xr_teleoperate

Parts of this repository are based on and modified from Unitree Robotics'
`xr_teleoperate` project:

- Upstream: https://github.com/unitreerobotics/xr_teleoperate
- Copyright [2025] [HangZhou YuShu TECHNOLOGY CO.,LTD. ("Unitree Robotics")]
- Upstream license: Apache License 2.0; the full text is in
  [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt)

RoboParty modified the upstream software for RPO/Roboto robot teleoperation,
PICO XR input, ROS 2 integration, and the current asset and launch layout.
RoboParty's modifications and the combined work are distributed under
`GPL-3.0-only`. Unitree's original copyright and Apache License 2.0 notice are
retained. Source files changed from the upstream project carry a modification
notice.

## Other upstream projects and dependencies

The upstream project identifies the following projects as code bases or
dependencies on which it builds. Their own license terms continue to apply:

1. https://github.com/OpenTeleVision/TeleVision
2. https://github.com/dexsuite/dex-retargeting
3. https://github.com/vuer-ai/vuer
4. https://github.com/stack-of-tasks/pinocchio
5. https://github.com/casadi/casadi
6. https://github.com/meshcat-dev/meshcat-python
7. https://github.com/zeromq/pyzmq
8. https://github.com/Dingry/BunnyVisionPro
9. https://github.com/unitreerobotics/unitree_sdk2_python

CasADi is installed separately as described in `README.md` and is not vendored
in this repository. Its license applies to the installed version.
