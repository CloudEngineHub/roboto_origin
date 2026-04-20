import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import numpy as np
import time
import argparse
import cv2
# from multiprocessing import shared_memory, Value, Array, Lock
from threading import Lock  # 使用 threading.Lock
import threading
import logging_mp
logging_mp.basicConfig(level=logging_mp.DEBUG)
logger_mp = logging_mp.getLogger(__name__)
import os 
import sys

# 添加项目路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.path.join(PROJECT_ROOT, 'unitree_IL_lerobot/unitree_lerobot/lerobot/src'))
from lerobot.datasets.lerobot_dataset import LeRobotDataset

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

def on_press(key):
    global running, start_signal
    if key == 'r':
        start_signal = True
        logger_mp.info("Program start signal received.")
    elif key == 'q':
        stop_listening()
        running = False
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


    def send_commands(self, sol_q, sol_tauff=None):

        # logger_mp.debug(f"sol_q: {sol_q}, sol_tau: {sol_tauff}")

        if sol_tauff is None:
            sol_tauff = np.zeros(10)

        # 打印输入数据及其类型
        logger_mp.debug(f"Received sol_q: {sol_q}, Type: {type(sol_q)}")
        logger_mp.debug(f"Received sol_tauff: {sol_tauff}, Type: {type(sol_tauff)}")

        # 左臂消息
        left_msg = JointState()
        left_msg.header.stamp = self.get_clock().now().to_msg()
        left_msg.name = ["left_motor0", "left_motor1", "left_motor2", "left_motor3", "left_motor4"]
        sol_q[4] = 0.0  # 将左臂最后一个关节位置设为0
        left_msg.position = sol_q[:5].tolist()   
        left_msg.velocity = [0.0] * 5            # 速度设为0
        sol_tauff[4] = 0.0  # 将左臂最后一个关节力矩设为0
        left_msg.effort = sol_tauff[:5].tolist() 
        logger_mp.debug(f"Left Arm message: {left_msg}, Type: {type(left_msg)}")
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
        logger_mp.debug(f"Right Arm message: {right_msg}, Type: {type(right_msg)}")
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

def replay_actions(repo_id="test", 
                   root="/home/ygx/.cache/huggingface/lerobot/test/data", 
                   episode=5, 
                   fps=30.0,
                   arm_controller=None):
    """
    加载指定数据集中的动作序列并按指定频率发送控制指令
    
    参数:
        repo_id: HuggingFace数据集仓库ID
        root: 数据集存储路径
        episode: 要加载的episode索引
        fps: 每秒帧数，控制发送频率
        arm_controller: 已初始化的ArmController实例
    """
    if arm_controller is None:
        raise RuntimeError("arm_controller must be provided and initialized in main thread!")
    # 加载数据集
    dataset = LeRobotDataset(repo_id, root=root, episodes=[episode])
    actions = dataset.hf_dataset.select_columns("action")
    frame_interval = 1.0 / fps  # 每帧间隔时间
    
    print(f"开始回放 episode {episode}, 共 {dataset.num_frames} 帧, 频率: {fps}Hz")
    
    # 遍历所有帧
    for idx in range(dataset.num_frames):
        start_time = time.perf_counter()
        
        # 获取当前帧的动作数据
        action = actions[idx]["action"]
        
        # 打印当前帧的动作数据
        print(f"Frame {idx}/{dataset.num_frames}: action = {action}")
        
        # 发送控制指令
        arm_controller.send_commands(action)  # 将读取的动作数据传入控制指令发送方法
        
        # 计算执行时间并等待剩余时间
        elapsed = time.perf_counter() - start_time
        wait_time = frame_interval - elapsed
        
        if wait_time > 0:
            time.sleep(wait_time)  # 使用sleep来保持帧间隔一致

# 使用示例
if __name__ == "__main__":
    # 只允许命令行单独运行时初始化rclpy
    rclpy.init()
    arm_controller = ArmController()
    try:
        replay_actions(
            repo_id="Skill_Library",
            root="xr_teleoperate/teleop/utils/data",
            episode=0,
            fps=30.0,
            arm_controller=arm_controller
        )
    finally:
        arm_controller.destroy_node()
        rclpy.shutdown()
