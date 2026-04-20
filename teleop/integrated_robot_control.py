import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import numpy as np
import time
import argparse
import threading
import logging_mp
import os
import sys
import json
import glob
import shutil
import cv2
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

# 从原始脚本中导入所需的库
from sshkeyboard import listen_keyboard, stop_listening
from televuer import TeleVuerWrapper
from teleop.robot_control.robot_arm_ik import Atom_23_ArmIK
from teleop.utils.episode_writer import EpisodeWriter

# --- 配置与常量 ---

ATOM_CONFIG = RobotConfig(
    motors=[
        "left_joint_0", "left_joint_1", "left_joint_2", "left_joint_3", "left_joint_4",
        "right_joint_0", "right_joint_1", "right_joint_2", "right_joint_3", "right_joint_4"
    ],
    cameras=[],  # 没有相机
    camera_to_image_key={},  # 空映射
    json_state_data_name=["left_arm", "right_arm"],
    json_action_data_name=["left_arm", "right_arm"]
)

ROBOT_CONFIGS = {
    "ATOM": ATOM_CONFIG, 
}

# --- 全局状态管理 ---
# 使用线程安全的字典来管理全局状态
global_state = {
    'running': True,
    'start_signal': False,
    'should_toggle_recording': False,
    'is_recording': False,
    'should_send_commands': False,
    'should_replay': False,
    'paused': False,
    'lock': threading.Lock()
}

# --- 录制防抖逻辑 ---
LAST_RECORD_TRIGGER_TIME = 0
RECORD_DEBOUNCE_INTERVAL = 1.0 # 防抖间隔增加到1秒

# --- 日志设置 ---
logging_mp.basicConfig(level=logging_mp.INFO)
logger_mp = logging_mp.getLogger(__name__)


# --- 键盘输入处理 ---
def on_press(key):
    global global_state
    with global_state['lock']:
        if key == 'r':
            global_state['start_signal'] = True
            logger_mp.info("程序启动信号已接收。")
        elif key == 'q':
            global_state['running'] = False
            stop_listening()
            logger_mp.info("退出信号已接收，正在关闭。")
        elif key == 's':
            global_state['should_toggle_recording'] = True
            logger_mp.info("切换录制状态信号已接收。")
        elif key == 'a':
            global_state['should_send_commands'] = True
            logger_mp.info("遥操作指令已启用。")
        elif key == 'p': # 用于暂停回放
            global_state['paused'] = not global_state['paused']
            status = "暂停" if global_state['paused'] else "恢复"
            logger_mp.info(f"回放已 {status}。")

# --- 机械臂控制器 (ROS2 节点) ---
class ArmController(Node):
    def __init__(self):
        super().__init__('arm_controller')
        self.lock = threading.Lock()
        self.left_arm_pub = self.create_publisher(JointState, '/joint_command_left_arm', 10)
        self.right_arm_pub = self.create_publisher(JointState, '/joint_command_right_arm', 10)
        self.left_arm_sub = self.create_subscription(JointState, '/joint_states_left_arm', self.left_arm_callback, 10)
        self.right_arm_sub = self.create_subscription(JointState, '/joint_states_right_arm', self.right_arm_callback, 10)
        self.left_arm_states = None
        self.right_arm_states = None

    def left_arm_callback(self, msg):
        with self.lock:
            self.left_arm_states = msg

    def right_arm_callback(self, msg):
        with self.lock:
            self.right_arm_states = msg

    def send_commands(self, sol_q, sol_tauff=None):
        if sol_tauff is None:
            sol_tauff = np.zeros(10)

        if len(sol_q) != 10 or len(sol_tauff) != 10:
            logger_mp.error(f"无效的指令维度。期望10，实际q={len(sol_q)}, tauff={len(sol_tauff)}")
            return

        # 左臂
        left_msg = JointState()
        left_msg.header.stamp = self.get_clock().now().to_msg()
        left_msg.name = ["left_motor0", "left_motor1", "left_motor2", "left_motor3", "left_motor4"]
        left_q = list(sol_q[:5])
        left_tau = list(sol_tauff[:5])
        left_q[4] = 0.0  # 末端关节固定
        left_tau[4] = 0.0
        left_msg.position = left_q
        left_msg.velocity = [0.0] * 5
        left_msg.effort = left_tau
        self.left_arm_pub.publish(left_msg)

        # 右臂
        right_msg = JointState()
        right_msg.header.stamp = self.get_clock().now().to_msg()
        right_msg.name = ["right_motor0", "right_motor1", "right_motor2", "right_motor3", "right_motor4"]
        right_q = list(sol_q[5:])
        right_tau = list(sol_tauff[5:])
        right_q[4] = 0.0 # 末端关节固定
        right_tau[4] = 0.0
        right_msg.position = right_q
        right_msg.velocity = [0.0] * 5
        right_msg.effort = right_tau
        self.right_arm_pub.publish(right_msg)

    def get_current_dual_arm_q(self):
        with self.lock:
            if self.left_arm_states is None or self.right_arm_states is None:
                return np.zeros(10)
            try:
                def parse_arm_q(states, prefix):
                    q_dict = {f"{prefix}{i}": 0.0 for i in range(5)}
                    for i, name in enumerate(states.name):
                        if name in q_dict:
                            q_dict[name] = states.position[i]
                    return [q_dict[f"{prefix}{i}"] for i in range(5)]

                left_q = parse_arm_q(self.left_arm_states, "left_motor")
                right_q = parse_arm_q(self.right_arm_states, "right_motor")
                return np.array(left_q + right_q)
            except Exception as e:
                self.get_logger().error(f"解析关节状态时出错: {e}")
                return np.zeros(10)


# --- 数据转换逻辑 (来自 convert_unitree_json_to_lerobot.py) ---
class JsonDatasetReader:
    def __init__(self, data_dir: Path, robot_type: str):
        self.data_dir = data_dir
        self.robot_type = robot_type
        self.episode_paths = sorted(glob.glob(os.path.join(self.data_dir, "*", "")))
        if not self.episode_paths:
             raise FileNotFoundError(f"在 {self.data_dir} 中未找到任何 episode 目录")
        self.config = ROBOT_CONFIGS[robot_type]

    def __len__(self):
        return len(self.episode_paths)

    def _extract_data(self, episode_data: Dict, key: str, parts: List[str]) -> np.ndarray:
        result = []
        for sample_data in episode_data["data"]:
            data_array = np.array([], dtype=np.float32)
            for part in parts:
                qpos = np.array(sample_data[key][part]["qpos"], dtype=np.float32)
                data_array = np.concatenate([data_array, qpos])
            result.append(data_array)
        return np.array(result)

    def get_item(self, index: int) -> Dict:
        episode_path = self.episode_paths[index]
        json_path = os.path.join(episode_path, "data.json")
        with open(json_path, "r", encoding="utf-8") as f:
            episode_data = json.load(f)

        action = self._extract_data(episode_data, "actions", self.config['json_action_data_name'])
        state = self._extract_data(episode_data, "states", self.config['json_state_data_name'])

        # 这是一个简化的图像解析器。如果不需要处理图像，可以保持为空。
        # 如果有图像，需要在此处使用原始脚本中的图像处理逻辑。
        # images = defaultdict(list)

        return {"state": state, "action": action, "cameras": images, "episode_length": len(state)}

def run_conversion(repo_id: str, raw_dir: Path, robot_type: str):
    logger_mp.info(f"开始转换为 '{raw_dir}' 中的数据")
    logger_mp.info(f"目标 LeRobot 数据集 repo_id: '{repo_id}'")
    
    # 定义 LeRobot 数据集特征
    motors = ROBOT_CONFIGS[robot_type]['motors']
    features = {
        "observation.state": {"dtype": "float32", "shape": (len(motors),)},
        "action": {"dtype": "float32", "shape": (len(motors),)},
    }
    
    # 创建一个空的 LeRobot 数据集
    # 数据集将被创建在默认缓存位置或指定的根目录
    dataset_path = Path(os.path.expanduser('~/.cache/huggingface/lerobot')) / repo_id
    if dataset_path.exists():
        logger_mp.warning(f"正在删除已存在的旧数据集: {dataset_path}")
        shutil.rmtree(dataset_path)

    dataset = LeRobotDataset.create(repo_id=repo_id, features=features)
    
    # 填充数据集
    json_reader = JsonDatasetReader(raw_dir, robot_type)
    for i in range(len(json_reader)):
        episode = json_reader.get_item(i)
        for frame_idx in range(episode['episode_length']):
            frame = {
                "observation.state": episode['state'][frame_idx],
                "action": episode['action'][frame_idx],
            }
            dataset.add_frame(frame)
        dataset.save_episode()
    
    logger_mp.info(f"数据转换完成。LeRobot 数据集保存在: {dataset.root}")
    return dataset.root, len(json_reader) - 1 # 返回路径和最后一个 episode 的索引

# --- 回放逻辑 (来自 replay.py) ---
def execute_replay(repo_id: str, root: Path, episode_idx: int, fps: float, arm_controller: ArmController):
    global global_state
    logger_mp.info(f"准备从 '{repo_id}' 以 {fps} FPS 回放 episode {episode_idx}。")

    try:
        dataset = LeRobotDataset(repo_id, root=root)
        episode_data = dataset.hf_dataset.filter(lambda example: example["episode_index"] == episode_idx)
        actions = episode_data["action"]
        num_frames = len(actions)
        if num_frames == 0:
            logger_mp.error(f"Episode {episode_idx} 不包含任何动作，无法回放。")
            return
    except Exception as e:
        logger_mp.error(f"加载用于回放的数据集失败: {e}")
        return

    logger_mp.info(f"开始回放 {num_frames} 帧。按 'p' 键暂停/恢复。")
    frame_interval = 1.0 / fps
    start_time = time.perf_counter()

    for idx in range(num_frames):
        with global_state['lock']:
            if not global_state['running']:
                logger_mp.info("回放被用户终止。")
                break
            while global_state['paused']:
                time.sleep(0.1)

        target_time = start_time + idx * frame_interval
        sleep_time = target_time - time.perf_counter()
        if sleep_time > 0:
            time.sleep(sleep_time)

        action = np.array(actions[idx])
        arm_controller.send_commands(action)

        if idx % int(fps) == 0: # 每秒记录一次日志
             logger_mp.info(f"回放进度: 帧 {idx + 1}/{num_frames}")

    logger_mp.info("回放结束。")
    with global_state['lock']:
        global_state['should_replay'] = False

# --- 主应用程序 ---
def main(args):
    global global_state, LAST_RECORD_TRIGGER_TIME

    # 初始化 ROS2
    rclpy.init()
    arm_controller = ArmController()
    spin_thread = threading.Thread(target=rclpy.spin, args=(arm_controller,), daemon=True)
    spin_thread.start()

    # 初始化 XR 和 IK
    tv_wrapper = TeleVuerWrapper(use_hand_tracking=args.xr_mode == 'hand', return_state_data=True)
    arm_ik = Atom_23_ArmIK(Visualization=not args.headless)

    # 初始化录制器
    # 将原始数据保存到子目录中，以与转换后的数据分开
    raw_data_dir = os.path.join(args.task_dir, "raw")
    recorder = EpisodeWriter(task_dir=raw_data_dir, frequency=args.frequency, rerun_log=not args.headless)
    
    last_episode_path = None
    last_episode_idx = -1

    # 启动键盘监听
    listen_keyboard_thread = threading.Thread(target=listen_keyboard, kwargs={"on_press": on_press}, daemon=True)
    listen_keyboard_thread.start()

    logger_mp.info("系统初始化完成。请按键盘 'r' 键启动。")
    while not global_state['start_signal'] and global_state['running']:
        time.sleep(0.1)
        
    logger_mp.info("主循环已启动。'a' 控制, 's' 录制, 'q' 退出。")
    logger_mp.info("XR 控制器: 右手柄 'A' 控制, 左手柄 'A' 录制, 左手柄 'B' 回放。")

    try:
        while global_state['running']:
            start_time = time.time()
            
            # 非阻塞地检查ROS2回调
            rclpy.spin_once(arm_controller, timeout_sec=0.001)

            # 获取 XR 数据
            tele_data = tv_wrapper.get_motion_state_data()
            
            # --- 处理状态与输入 ---
            with global_state['lock']:
                # 录制逻辑
                if global_state['should_toggle_recording'] or tele_data.tele_state.left_aButton:
                    current_time = time.time()
                    if current_time - LAST_RECORD_TRIGGER_TIME > RECORD_DEBOUNCE_INTERVAL:
                        LAST_RECORD_TRIGGER_TIME = current_time
                        if not global_state['is_recording']:
                            if recorder.create_episode():
                                global_state['is_recording'] = True
                                logger_mp.info("录制已开始。")
                        else:
                            global_state['is_recording'] = False
                            saved_path = recorder.save_episode()
                            logger_mp.info(f"录制已停止。数据保存在 {saved_path}")
                            
                            # --- 自动转换 ---
                            try:
                                last_episode_path, last_episode_idx = run_conversion(
                                    repo_id=args.repo_id,
                                    raw_dir=Path(raw_data_dir),
                                    robot_type=DEFAULT_ROBOT_TYPE
                                )
                            except Exception as e:
                                logger_mp.error(f"自动数据转换失败: {e}")

                    global_state['should_toggle_recording'] = False

                # 遥操作控制逻辑
                if tele_data.tele_state.right_aButton:
                    global_state['should_send_commands'] = True
                if tele_data.tele_state.right_bButton:
                    global_state['should_send_commands'] = False
                
                # 回放触发逻辑
                if tele_data.tele_state.left_bButton:
                    if last_episode_path and last_episode_idx != -1:
                        if not global_state.get('replay_thread') or not global_state['replay_thread'].is_alive():
                            logger_mp.info("控制器触发回放。")
                            replay_thread = threading.Thread(
                                target=execute_replay,
                                args=(args.repo_id, Path(last_episode_path), last_episode_idx, args.fps, arm_controller),
                                daemon=True
                            )
                            global_state['replay_thread'] = replay_thread
                            replay_thread.start()
                        else:
                            logger_mp.warning("回放已在进行中。")
                    else:
                        logger_mp.warning("尚未录制和转换任何数据，无法回放。")

            # --- 核心IK与机器人指令 ---
            current_lr_arm_q = arm_controller.get_current_dual_arm_q()
            sol_q, sol_tauff = arm_ik.solve_ik(
                tele_data.left_arm_pose, 
                tele_data.right_arm_pose, 
                current_lr_arm_motor_q=current_lr_arm_q
            )
            
            if global_state['should_send_commands']:
                arm_controller.send_commands(sol_q, sol_tauff)

            # --- 数据录制帧 ---
            if global_state['is_recording']:
                # 简化的用于录制的状态/动作结构
                states = {"left_arm": {"qpos": current_lr_arm_q[:5].tolist()}, "right_arm": {"qpos": current_lr_arm_q[5:].tolist()}}
                actions = {"left_arm": {"qpos": sol_q[:5].tolist()}, "right_arm": {"qpos": sol_q[5:].tolist()}}
                recorder.add_item(states=states, actions=actions)

            # 维持频率
            time_elapsed = time.time() - start_time
            sleep_time = max(0, (1 / args.frequency) - time_elapsed)
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        logger_mp.info("检测到 KeyboardInterrupt，正在关闭程序。")
    finally:
        # 清理并关闭
        global_state['running'] = False
        if listen_keyboard_thread.is_alive():
            stop_listening() # 这应该能让线程退出
        
        arm_controller.destroy_node()
        rclpy.shutdown()
        
        if spin_thread.is_alive():
            spin_thread.join()
        if listen_keyboard_thread.is_alive():
            listen_keyboard_thread.join()
        
        logger_mp.info("程序已干净地退出。")
        sys.exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="集成的机器人控制、录制与回放系统")
    
    # 来自 xr_Control_Atom.py 的参数
    parser.add_argument('--frequency', type=float, default=30.0, help='操作频率 (Hz)。')
    parser.add_argument('--xr-mode', type=str, choices=['hand', 'controller'], default='controller', help='XR 设备的追踪源。')
    parser.add_argument('--task-dir', type=str, default='./recorded_data', help='保存数据的路径。')
    parser.add_argument('--headless', action='store_true', help='启用无头模式 (无可视化)。')

    # 来自 convert_unitree_json_to_lerobot.py & replay.py 的参数
    parser.add_argument('--repo-id', type=str, default='MyAtomSkills', help='用于转换后 LeRobot 数据集的仓库ID。')
    parser.add_argument('--fps', type=float, default=30.0, help='回放帧率 (Hz)。')

    args = parser.parse_args()
    logger_mp.info(f"程序启动，配置参数: {args}")
    
    # 如果目录不存在，则创建它
    os.makedirs(args.task_dir, exist_ok=True)
    os.makedirs(os.path.join(args.task_dir, "raw"), exist_ok=True)
    
    main(args)