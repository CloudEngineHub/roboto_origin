import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import numpy as np
import time
import argparse
# from multiprocessing import shared_memory, Value, Array, Lock
from threading import Lock  # 使用 threading.Lock
import threading
import logging_mp
logging_mp.basicConfig(level=logging_mp.DEBUG)
logger_mp = logging_mp.getLogger(__name__)
import os 
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from televuer import TeleVuerWrapper
from teleop.robot_control.robot_arm_ik import Atom_23_ArmIK
from teleop.utils.episode_writer import EpisodeWriter
from sshkeyboard import listen_keyboard, stop_listening


# state transition
start_signal = False
running = True
should_toggle_recording = False
is_recording = False
should_send_commands = False  # 新增状态变量，用来控制是否发送命令

def on_press(key):
    global running, start_signal, should_toggle_recording,should_send_commands
    if key == 'r':
        start_signal = True
        logger_mp.info("Program start signal received.")
    elif key == 'q':
        stop_listening()
        running = False
    elif key == 's':
        should_toggle_recording = True
        logger_mp.info("Program start signal record.")
    elif key == 'a':  # 按下 'a' 键时，设置 should_send_commands 为 True
        should_send_commands = True
        logger_mp.info("Program start signal commands.")
    else:
        logger_mp.info(f"{key} was pressed, but no action is defined for this key.")

listen_keyboard_thread = threading.Thread(target=listen_keyboard, kwargs={"on_press": on_press, "until": None, "sequential": False,}, daemon=True)
listen_keyboard_thread.start()

class ArmController(Node):
    def __init__(self):
        super().__init__('arm_controller')
        self.lock = Lock()

        # 发布器
        self.left_arm_pub = self.create_publisher(JointState, '/joint_command_left_arm', 10)
        self.right_arm_pub = self.create_publisher(JointState, '/joint_command_right_arm', 10)

        # # 订阅器
        self.left_arm_sub = self.create_subscription(JointState, '/joint_states_left_arm', self.left_arm_callback, 10)
        self.right_arm_sub = self.create_subscription(JointState, '/joint_states_right_arm', self.right_arm_callback, 10)
        logger_mp.debug("Left arm subscription created.")
        logger_mp.debug("Right arm subscription created.")

        # 用于存储接收到的关节状态
        self.left_arm_states = None
        self.right_arm_states = None

    def left_arm_callback(self, msg):
        with self.lock:
            self.left_arm_states = msg
            logger_mp.debug(f"Left Arm State: {self.left_arm_states}")

    def right_arm_callback(self, msg):
        with self.lock:
            self.right_arm_states = msg
            logger_mp.debug(f"Right Arm State: {self.right_arm_states}")


    def send_commands(self, sol_q, sol_tauff):

        # logger_mp.debug(f"sol_q: {sol_q}, sol_tau: {sol_tauff}")

        # 左臂消息
        left_msg = JointState()
        left_msg.header.stamp = self.get_clock().now().to_msg()
        left_msg.name = ["left_motor0", "left_motor1", "left_motor2", "left_motor3", "left_motor4"]
        sol_q[4] = 0.0  # 将左臂最后一个关节位置设为0
        left_msg.position = sol_q[:5].tolist()   
        left_msg.velocity = [0.0] * 5            # 速度设为0
        sol_tauff[4] = 0.0  # 将左臂最后一个关节力矩设为0
        left_msg.effort = sol_tauff[:5].tolist() 
        self.left_arm_pub.publish(left_msg)

        # 右臂消息
        right_msg = JointState()
        right_msg.header.stamp = self.get_clock().now().to_msg()
        right_msg.name = ["right_motor0", "right_motor1", "right_motor2", "right_motor3", "right_motor4"]
        sol_q[9] = 0.0  # 将右臂最后一个关节位置设为0
        right_msg.position = sol_q[5:].tolist()   
        right_msg.velocity = [0.0] * 5            # 速度设为0
        sol_tauff[9] = 0.0  # 将右臂最后一个关节力矩设为0
        right_msg.effort = sol_tauff[5:].tolist() 
        self.right_arm_pub.publish(right_msg)

    def get_current_dual_arm_q(self):
        with self.lock:
            if self.left_arm_states is None or self.right_arm_states is None:
                self.get_logger().debug("Joint states not received yet.")
                return np.zeros(10)  # 或 raise Exception / return None，根据你需求
            try:
                # 提取左臂和右臂的关节位置
                left_q = [0.0] * 5
                right_q = [0.0] * 5
                for i, name in enumerate(self.left_arm_states.name):
                    if name.startswith("left_motor"):
                        idx = int(name.replace("left_motor", ""))
                        if idx < 5:
                            left_q[idx] = self.left_arm_states.position[i]
                for i, name in enumerate(self.right_arm_states.name):
                    if name.startswith("right_motor"):
                        idx = int(name.replace("right_motor", ""))
                        if idx < 5:
                            right_q[idx] = self.right_arm_states.position[i]
                logger_mp.debug(f"Left Arm Q: {left_q}, Right Arm Q: {right_q}")
                return np.array(left_q + right_q)
            except Exception as e:
                self.get_logger().error(f"Error parsing joint states: {e}")
                return np.zeros(10)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--task_dir', type = str, default = './utils/data', help = 'path to save data')
    parser.add_argument('--frequency', type = float, default = 30.0, help = 'save data\'s frequency')
    parser.add_argument('--xr-mode', type=str, choices=['hand', 'controller'], default='controller', help='Select XR device tracking source')

    parser.add_argument('--record', action = 'store_true', help = 'Enable data recording')
    parser.add_argument('--headless', action='store_true', help='Enable headless mode (no display)')

    args = parser.parse_args()
    logger_mp.info(f"args: {args}")
    
    # 初始化ROS2
    rclpy.init()
    arm_controller = ArmController()

    # television: obtain hand pose data from the XR device and transmit the robot's head camera image to the XR device.
    tv_wrapper = TeleVuerWrapper(use_hand_tracking=args.xr_mode == 'hand', return_state_data=True, return_hand_rot_data = False)

    # arm
    arm_ik = Atom_23_ArmIK(Visualization = True)


    if args.record and args.headless:
        recorder = EpisodeWriter(task_dir = args.task_dir, frequency = args.frequency, rerun_log = False)
    elif args.record and not args.headless:
        recorder = EpisodeWriter(task_dir = args.task_dir, frequency = args.frequency, rerun_log = True)

    try:
        logger_mp.info("Please enter the start signal (enter 'r' to start the subsequent program)")
        while not start_signal:
            time.sleep(0.01)
        # arm_ctrl.speed_gradual_max()
        while running:
            start_time = time.time()
    
            if args.record and should_toggle_recording:
                should_toggle_recording = False
                if not is_recording:
                    if recorder.create_episode():
                        is_recording = True
                    else:
                        logger_mp.error("Failed to create episode. Recording not started.")
                else:
                    is_recording = False
                    recorder.save_episode()

            # get input data
            tele_data = tv_wrapper.get_motion_state_data()

            # get current robot state data.
            current_lr_arm_q = arm_controller.get_current_dual_arm_q()

            # solve ik using motor data and wrist pose, then use ik results to control arms.
            time_ik_start = time.time()
            sol_q, sol_tauff  = arm_ik.solve_ik(tele_data.left_arm_pose, tele_data.right_arm_pose, current_lr_arm_q)
            #sol_q, sol_tauff  = arm_ik.solve_ik(tele_data.left_arm_pose, tele_data.right_arm_pose)
            # sol_q, sol_tauff  = arm_ik.solve_ik(tele_data.left_arm_pose, tele_data.right_arm_pose, current_lr_arm_q, current_lr_arm_dq)

            time_ik_end = time.time()
            # logger_mp.debug(f"ik:\t{round(time_ik_end - time_ik_start, 6)}")

            # 如果按下 'a' 键，就执行 arm_controller.send_commands
            if should_send_commands:
                arm_controller.send_commands(sol_q, sol_tauff)

            # record data
            if args.record:
                # dex hand or gripper
                left_ee_state = []
                right_ee_state = []
                left_hand_action = []
                right_hand_action = []
                current_body_state = []
                current_body_action = []

                # arm state and action 
                left_arm_state  = current_lr_arm_q[:5]
                right_arm_state = current_lr_arm_q[-5:]
                left_arm_action = sol_q[:5]
                right_arm_action = sol_q[-5:]
                if is_recording:
                    states = {
                        "left_arm": {                                                                    
                            "qpos":   left_arm_state.tolist(),    # numpy.array -> list
                            "qvel":   [],                          
                            "torque": [],                        
                        }, 
                        "right_arm": {                                                                    
                            "qpos":   right_arm_state.tolist(),       
                            "qvel":   [],                          
                            "torque": [],                         
                        },                        
                        "left_ee": {                                                                    
                            "qpos":   left_ee_state,           
                            "qvel":   [],                           
                            "torque": [],                          
                        }, 
                        "right_ee": {                                                                    
                            "qpos":   right_ee_state,       
                            "qvel":   [],                           
                            "torque": [],  
                        }, 
                        "body": {
                            "qpos": current_body_state,
                        }, 
                    }
                    actions = {
                        "left_arm": {                                   
                            "qpos":   left_arm_action.tolist(),       
                            "qvel":   [],       
                            "torque": [],      
                        }, 
                        "right_arm": {                                   
                            "qpos":   right_arm_action.tolist(),       
                            "qvel":   [],       
                            "torque": [],       
                        },                         
                        "left_ee": {                                   
                            "qpos":   left_hand_action,       
                            "qvel":   [],       
                            "torque": [],       
                        }, 
                        "right_ee": {                                   
                            "qpos":   right_hand_action,       
                            "qvel":   [],       
                            "torque": [], 
                        }, 
                        "body": {
                            "qpos": current_body_action,
                        }, 
                    }
                    
                    recorder.add_item(states=states, actions=actions)

            rclpy.spin_once(arm_controller)  # 传递节点对象
            time_ik_end = time.time()
            # logger_mp.debug(f"ik:\t{round(time_ik_end - time_ik_start, 6)}")
        
            current_time = time.time()
            time_elapsed = current_time - start_time
            sleep_time = max(0, (1 / args.frequency) - time_elapsed)
            time.sleep(sleep_time)
            # logger_mp.debug(f"main process sleep: {sleep_time}")

    except KeyboardInterrupt:
        logger_mp.info("KeyboardInterrupt, exiting program...")
    finally:


        if args.record:
            recorder.close()

        # 关闭ROS2节点
        if 'arm_controller' in locals():
            arm_controller.destroy_node()
            
        rclpy.shutdown()

        listen_keyboard_thread.join()
        logger_mp.info("Finally, exiting program...")
        exit(0)
