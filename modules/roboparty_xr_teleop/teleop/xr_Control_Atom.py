# Modified from Unitree xr_teleoperate for Atom robot teleoperation.
import argparse
import os
import sys
import threading
import time

import logging_mp
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from sshkeyboard import listen_keyboard, stop_listening


logging_mp.basicConfig(level=logging_mp.INFO)
logger_mp = logging_mp.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from televuer import TeleVuerWrapper
from teleop.robot_control.robot_arm_ik import Atom_23_ArmIK


start_signal = False
running = True
should_send_commands = False


def on_press(key: str) -> None:
    global running, should_send_commands, start_signal
    if key == "r":
        start_signal = True
        logger_mp.info("Start signal received.")
    elif key == "q":
        stop_listening()
        running = False
    elif key == "a":
        should_send_commands = True
        logger_mp.info("Ready to send commands.")
    else:
        logger_mp.info("%s was pressed, but no action is defined.", key)


listen_keyboard_thread = threading.Thread(
    target=listen_keyboard,
    kwargs={"on_press": on_press, "until": None, "sequential": False},
    daemon=True,
)
listen_keyboard_thread.start()


class ArmController(Node):
    def __init__(self) -> None:
        super().__init__("arm_controller")
        self.arm_pub = self.create_publisher(JointState, "/joint_ref_states", 10)

    def send_commands(self, sol_q: np.ndarray, sol_tauff: np.ndarray) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = [
            "left_motor0",
            "left_motor1",
            "left_motor2",
            "left_motor3",
            "left_motor4",
            "right_motor0",
            "right_motor1",
            "right_motor2",
            "right_motor3",
            "right_motor4",
        ]

        command_q = sol_q.copy()
        command_tau = sol_tauff.copy()
        command_q[4] = 0.0
        command_q[9] = 0.0
        command_tau[4] = 0.0
        command_tau[9] = 0.0

        msg.position = command_q.tolist()
        msg.velocity = [0.0] * 10
        msg.effort = command_tau.tolist()
        self.arm_pub.publish(msg)


def main() -> int:
    global running, should_send_commands

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--frequency",
        type=float,
        default=30.0,
        help="Control loop frequency in Hz.",
    )
    parser.add_argument(
        "--xr-mode",
        type=str,
        choices=["hand", "controller"],
        default="controller",
        help="Select XR tracking source.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Disable IK visualization.",
    )
    parser.add_argument(
        "--profile-loop",
        action="store_true",
        help="Log control-loop timing statistics.",
    )
    args = parser.parse_args()
    logger_mp.info("args: %s", args)
    last_debug_log_time = 0.0
    last_profile_log_time = 0.0
    profile_stats = {
        "loop_count": 0,
        "motion_total": 0.0,
        "ik_total": 0.0,
        "send_total": 0.0,
        "loop_total": 0.0,
        "iter_total": 0,
        "iter_max": 0,
        "hit_max_count": 0,
    }
    arm_controller = None
    tv_wrapper = None

    rclpy.init()
    arm_controller = ArmController()
    tv_wrapper = TeleVuerWrapper(
        use_hand_tracking=args.xr_mode == "hand",
        return_state_data=True,
        return_hand_rot_data=False,
    )
    arm_ik = Atom_23_ArmIK(Visualization=not args.headless)

    try:
        logger_mp.info("Press 'r' to start teleoperation, 'a' to arm commands, and 'q' to quit.")
        while not start_signal and running:
            time.sleep(0.01)

        while running:
            if not rclpy.ok():
                logger_mp.info("ROS context is no longer valid. Exiting main loop.")
                break

            start_time = time.time()
            motion_start_time = time.time()

            tele_data = tv_wrapper.get_motion_state_data()
            motion_duration = time.time() - motion_start_time
            if tele_data is None:
                continue

            if tele_data.tele_state.right_aButton:
                should_send_commands = True
                logger_mp.info("Right controller A pressed. Command streaming enabled.")
            if tele_data.tele_state.right_bButton:
                should_send_commands = False
                logger_mp.info("Right controller B pressed. Command streaming disabled.")

            ik_start_time = time.time()
            sol_q, sol_tauff = arm_ik.solve_ik(
                tele_data.left_arm_pose,
                tele_data.right_arm_pose,
            )
            ik_duration = time.time() - ik_start_time

            if time.time() - last_debug_log_time >= 0.5:
                logger_mp.info(
                    "IK result q=%s tau=%s should_send=%s",
                    np.round(sol_q, 4).tolist(),
                    np.round(sol_tauff, 4).tolist(),
                    should_send_commands,
                )
                last_debug_log_time = time.time()

            send_duration = 0.0
            if should_send_commands:
                send_start_time = time.time()
                arm_controller.send_commands(sol_q, sol_tauff)
                send_duration = time.time() - send_start_time

            loop_duration = time.time() - start_time

            if args.profile_loop:
                iter_count = int(arm_ik.last_solver_stats.get("iter_count", 0))
                profile_stats["loop_count"] += 1
                profile_stats["motion_total"] += motion_duration
                profile_stats["ik_total"] += ik_duration
                profile_stats["send_total"] += send_duration
                profile_stats["loop_total"] += loop_duration
                profile_stats["iter_total"] += iter_count
                profile_stats["iter_max"] = max(profile_stats["iter_max"], iter_count)
                if iter_count >= arm_ik.max_iter:
                    profile_stats["hit_max_count"] += 1

                if time.time() - last_profile_log_time >= 1.0:
                    loop_count = profile_stats["loop_count"]
                    avg_motion_ms = profile_stats["motion_total"] / loop_count * 1000.0
                    avg_ik_ms = profile_stats["ik_total"] / loop_count * 1000.0
                    avg_send_ms = profile_stats["send_total"] / loop_count * 1000.0
                    avg_loop_ms = profile_stats["loop_total"] / loop_count * 1000.0
                    avg_hz = loop_count / profile_stats["loop_total"] if profile_stats["loop_total"] > 0.0 else 0.0
                    avg_iter = profile_stats["iter_total"] / loop_count
                    logger_mp.info(
                        (
                            "Loop timing avg over %d iters: motion=%.2f ms, "
                            "ik=%.2f ms, send=%.2f ms, loop=%.2f ms, rate=%.2f Hz, "
                            "ipopt_iter_avg=%.2f, ipopt_iter_max=%d, "
                            "ipopt_hit_max=%d/%d, ipopt_last_status=%s"
                        ),
                        loop_count,
                        avg_motion_ms,
                        avg_ik_ms,
                        avg_send_ms,
                        avg_loop_ms,
                        avg_hz,
                        avg_iter,
                        profile_stats["iter_max"],
                        profile_stats["hit_max_count"],
                        loop_count,
                        arm_ik.last_solver_stats.get("return_status", "UNKNOWN"),
                    )
                    profile_stats = {
                        "loop_count": 0,
                        "motion_total": 0.0,
                        "ik_total": 0.0,
                        "send_total": 0.0,
                        "loop_total": 0.0,
                        "iter_total": 0,
                        "iter_max": 0,
                        "hit_max_count": 0,
                    }
                    last_profile_log_time = time.time()

            sleep_time = max(0.0, (1.0 / args.frequency) - (time.time() - start_time))
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        logger_mp.info("KeyboardInterrupt received, exiting.")
    finally:
        stop_listening()
        if listen_keyboard_thread.is_alive():
            listen_keyboard_thread.join(timeout=1.0)

        if tv_wrapper is not None:
            tv_wrapper.shutdown()

        if arm_controller is not None:
            arm_controller.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()

    logger_mp.info("Program exited cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
