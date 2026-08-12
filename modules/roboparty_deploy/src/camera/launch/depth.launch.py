# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2025-2026 Luo1imasi

"""Depth pipeline launch: RealSense camera + depth_node (encoder / debug vis).

Starts the camera first (rs_launch.py), then depth_node for preprocess,
encoder.onnx, and optional crop/downsample debug topics — independent of policy.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os
import re

NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def launch_setup(context, *args, **kwargs):
    policy = LaunchConfiguration("policy").perform(context)
    start_camera_arg = LaunchConfiguration("start_camera").perform(context).strip().lower()
    realsense_config_arg = LaunchConfiguration("realsense_config").perform(context).strip()

    if not NAME_PATTERN.fullmatch(policy):
        raise ValueError(f"Invalid policy name: {policy}")
    if start_camera_arg in ("", "true", "1"):
        start_camera = True
    elif start_camera_arg in ("false", "0"):
        start_camera = False
    else:
        raise ValueError(
            f"Invalid start_camera={start_camera_arg!r}; expected true/false"
        )

    policy_file = policy if policy.endswith(".yaml") else f"{policy}.yaml"
    camera_share = get_package_share_directory("camera")
    depth_config = os.path.join(camera_share, "configs", policy_file)
    depth_model_dir = os.path.join(camera_share, "models")
    realsense_config = (
        realsense_config_arg
        if realsense_config_arg
        else os.path.join(camera_share, "configs", "realsense_d435i.yaml")
    )

    if not os.path.isfile(depth_config):
        raise FileNotFoundError(f"Depth config not found: {depth_config}")

    actions = []

    if start_camera:
        if not os.path.isfile(realsense_config):
            raise FileNotFoundError(f"RealSense config not found: {realsense_config}")
        realsense_share = get_package_share_directory("realsense2_camera")
        actions.append(
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(realsense_share, "launch", "rs_launch.py")
                ),
                launch_arguments={"config_file": realsense_config}.items(),
            )
        )

    actions.append(
        Node(
            package="camera",
            executable="depth_node",
            name="depth_node",
            parameters=[
                depth_config,
                {"model_dir": depth_model_dir},
            ],
            output="screen",
        )
    )
    return actions


def generate_launch_description():
    return LaunchDescription(
        [
            DeclareLaunchArgument("policy", default_value="parkour"),
            DeclareLaunchArgument(
                "start_camera",
                default_value="true",
                description="true: also launch RealSense via rs_launch.py",
            ),
            DeclareLaunchArgument(
                "realsense_config",
                default_value="",
                description="Optional path to RealSense yaml; empty uses camera/configs/realsense_d435i.yaml",
            ),
            OpaqueFunction(function=launch_setup),
        ]
    )
