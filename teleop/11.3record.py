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
logging_mp.basicConfig(level=logging_mp.INFO)
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

# -------------------------- 新增：防抖相关变量 --------------------------
LAST_RECORD_TRIGGER_TIME = 0  # 记录上次触发录制的时间（秒）
RECORD_DEBOUNCE_INTERVAL = 0.8  # 防抖间隔：0.5秒内重复触发不响应（可根据需求调整）
# ------------------------------------------------------------------------


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
        logger_mp.info("Ready to send commands.")
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

        # 订阅器
        self.left_arm_sub = self.create_subscription(JointState, '/joint_states_left_arm', self.left_arm_callback, 10)
        self.right_arm_sub = self.create_subscription(JointState, '/joint_states_right_arm', self.right_arm_callback, 10)

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
        left_msg.position = (sol_q[:5]-np.array([0.18, 0.06, 0.0, 0.78, 0.0])).tolist()
        left_msg.velocity = [0.0] * 5            # 速度设为0
        sol_tauff[4] = 0.0  # 将左臂最后一个关节力矩设为0
        left_msg.effort = sol_tauff[:5].tolist() 
        self.left_arm_pub.publish(left_msg)

        # 右臂消息
        right_msg = JointState()
        right_msg.header.stamp = self.get_clock().now().to_msg()
        right_msg.name = ["right_motor0", "right_motor1", "right_motor2", "right_motor3", "right_motor4"]
        sol_q[9] = 0.0  # 将右臂最后一个关节位置设为0
        right_msg.position = (sol_q[5:]-np.array([0.18, -0.06, 0.0, 0.78, 0.0])).tolist()
        right_msg.velocity = [0.0] * 5            # 速度设为0
        sol_tauff[9] = 0.0  # 将右臂最后一个关节力矩设为0
        right_msg.effort = sol_tauff[5:].tolist() 
        self.right_arm_pub.publish(right_msg)

    def get_current_dual_arm_q(self):
        with self.lock:
            # 检查关节状态是否存在，不存在返回零数组
            if self.left_arm_states is None or self.right_arm_states is None:
                self.get_logger().debug("Joint states not received yet.")
                return np.zeros(10)

            try:
                # 定义通用解析函数，合并左右臂重复逻辑
                def parse_arm_q(arm_states, prefix):
                    arm_q = [0.0] * 5
                    for i, name in enumerate(arm_states.name):
                        if name.startswith(prefix):
                            idx = int(name.replace(prefix, ""))
                            if idx < 5:
                                arm_q[idx] = arm_states.position[i]
                    return arm_q

                # 分别解析左右臂关节角度
                left_q = parse_arm_q(self.left_arm_states, "left_motor")
                right_q = parse_arm_q(self.right_arm_states, "right_motor")
                
                logger_mp.debug(f"Left Arm Q: {left_q}, Right Arm Q: {right_q}")
                return np.array(left_q + right_q)

            except Exception as e:
                self.get_logger().error(f"Error parsing joint states: {e}")
                return np.zeros(10)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--frequency', type = float, default = 30.0, help = 'save data\'s frequency')
    parser.add_argument('--xr-mode', type=str, choices=['hand', 'controller'], default='controller', help='Select XR device tracking source')

    parser.add_argument('--task_dir', type = str, default = './utils/data/Skill_Library', help = 'path to save data')
    parser.add_argument('--record', action = 'store_false', help = 'Enable data recording')
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

            rclpy.spin_once(arm_controller, timeout_sec=0.001)
            tele_data = tv_wrapper.get_motion_state_data()
            current_lr_arm_q = arm_controller.get_current_dual_arm_q()
            # 新增: 当右手柄的A键被按下时，也设置 should_send_commands 为 True
            # 这是对键盘 'a' 键操作的补充
            if tele_data.tele_state.right_aButton:
                should_send_commands = True
                logger_mp.info("Right controller 'A' button pressed. Ready to send commands...")

            # 当右手柄的B键被按下时，停止发送命令
            if tele_data.tele_state.right_bButton:
                should_send_commands = False
                logger_mp.info("Right controller 'B' button pressed. Stop sending commands.")
                
            # ... (代码下部分保持不变，包括 IK 和命令发送逻辑) .
            logger_mp.debug(f"Current Left Arm and Right Arm Joint Positions (current_lr_arm_q): {current_lr_arm_q}")
            # solve ik using motor data and wrist pose, then use ik results to control arms.
            time_ik_start = time.time()
            sol_q, sol_tauff = arm_ik.solve_ik(
                                                tele_data.left_arm_pose, 
                                                tele_data.right_arm_pose, 
                                                current_lr_arm_motor_q=current_lr_arm_q  # 传递当前的关节角度
                                            )
            

            # Log the solution (sol_q and sol_tauff) for debugging
            logger_mp.debug(f"sol_q (Joint Positions): {sol_q}, Type: {type(sol_q)}")
            logger_mp.debug(f"sol_tauff (Joint Torques): {sol_tauff}, Type: {type(sol_tauff)}")

            # 如果按下 'a' 键，就执行 arm_controller.send_commands
            if should_send_commands:
                arm_controller.send_commands(sol_q, sol_tauff)

            # -------------------------- 控制器左A键（原日志X键）触发录制：添加防抖 --------------------------
            if tele_data.tele_state.left_aButton:
                current_time = time.time()
                # 检查距离上次触发是否超过防抖间隔
                if current_time - LAST_RECORD_TRIGGER_TIME < RECORD_DEBOUNCE_INTERVAL:
                    logger_mp.debug(f"忽略短时间内重复的左控制器'A'键录制请求（防抖间隔{RECORD_DEBOUNCE_INTERVAL}秒）")
                    continue  # 跳过本次触发，不执行后续逻辑
                # 更新上次触发时间，避免重复响应
                LAST_RECORD_TRIGGER_TIME = current_time
                # ------------------------------------------------------------------------
                should_toggle_recording = True
                logger_mp.info("Left controller 'X' button pressed. Ready to toggle record...")

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



            time_ik_end = time.time()
            logger_mp.debug(f"ik:\t{round(time_ik_end - time_ik_start, 6)}")
        
            current_time = time.time()
            time_elapsed = current_time - start_time
            sleep_time = max(0, (1 / args.frequency) - time_elapsed)
            time.sleep(sleep_time)
            logger_mp.debug(f"main process sleep: {sleep_time}")

    except KeyboardInterrupt:
        logger_mp.info("KeyboardInterrupt, exiting program...")
    finally:
        listen_keyboard_thread.join()

        # 关闭ROS2节点
        if 'arm_controller' in locals():
            arm_controller.destroy_node()
            
        rclpy.shutdown()

        logger_mp.info("Finally, exiting program...")
        exit(0)
