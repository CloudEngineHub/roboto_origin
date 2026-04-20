# Modified from Unitree xr_teleoperate for Atom robot teleoperation.
import argparse
import os
import sys
import threading
import time
from threading import Lock

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
        self.lock = Lock()
        self.arm_pub = self.create_publisher(JointState, "/joint_ref_states", 10)
        self.left_arm_sub = self.create_subscription(
            JointState, "/joint_states_left_arm", self.left_arm_callback, 10
        )
        self.right_arm_sub = self.create_subscription(
            JointState, "/joint_states_right_arm", self.right_arm_callback, 10
        )
        self.left_arm_states = None
        self.right_arm_states = None

    def left_arm_callback(self, msg: JointState) -> None:
        with self.lock:
            self.left_arm_states = msg

    def right_arm_callback(self, msg: JointState) -> None:
        with self.lock:
            self.right_arm_states = msg

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

        left_offset = np.array([0.18, 0.06, 0.0, 0.78, 0.0])
        right_offset = np.array([0.18, -0.06, 0.0, 0.78, 0.0])
        total_offset = np.concatenate([left_offset, right_offset])

        msg.position = (command_q - total_offset).tolist()
        msg.velocity = [0.0] * 10
        msg.effort = command_tau.tolist()
        self.arm_pub.publish(msg)

    def get_current_dual_arm_q(self) -> np.ndarray:
        with self.lock:
            if self.left_arm_states is None or self.right_arm_states is None:
                return np.zeros(10)

            def parse_arm_q(arm_states: JointState, prefix: str) -> list[float]:
                arm_q = [0.0] * 5
                for index, name in enumerate(arm_states.name):
                    if not name.startswith(prefix):
                        continue
                    joint_index = int(name.replace(prefix, ""))
                    if joint_index < 5:
                        arm_q[joint_index] = arm_states.position[index]
                return arm_q

            left_q = parse_arm_q(self.left_arm_states, "left_motor")
            right_q = parse_arm_q(self.right_arm_states, "right_motor")
            return np.array(left_q + right_q)


def main() -> int:
    global should_send_commands

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
    args = parser.parse_args()
    logger_mp.info("args: %s", args)

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
            start_time = time.time()
            rclpy.spin_once(arm_controller, timeout_sec=0.001)

            tele_data = tv_wrapper.get_motion_state_data()
            if tele_data is None:
                continue

            current_lr_arm_q = arm_controller.get_current_dual_arm_q()

            if tele_data.tele_state.right_aButton:
                should_send_commands = True
                logger_mp.info("Right controller A pressed. Command streaming enabled.")
            if tele_data.tele_state.right_bButton:
                should_send_commands = False
                logger_mp.info("Right controller B pressed. Command streaming disabled.")

            sol_q, sol_tauff = arm_ik.solve_ik(
                tele_data.left_arm_pose,
                tele_data.right_arm_pose,
                current_lr_arm_motor_q=current_lr_arm_q,
            )

            if should_send_commands:
                arm_controller.send_commands(sol_q, sol_tauff)

            sleep_time = max(0.0, (1.0 / args.frequency) - (time.time() - start_time))
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        logger_mp.info("KeyboardInterrupt received, exiting.")
    finally:
        if listen_keyboard_thread.is_alive():
            listen_keyboard_thread.join(timeout=1.0)
        arm_controller.destroy_node()
        rclpy.shutdown()

    logger_mp.info("Program exited cleanly.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
