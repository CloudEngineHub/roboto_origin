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
from sshkeyboard import listen_keyboard, stop_listening

# 添加项目路径
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(os.path.join(PROJECT_ROOT, 'unitree_IL_lerobot/unitree_lerobot/lerobot/src'))
from lerobot.datasets.lerobot_dataset import LeRobotDataset

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 全局状态控制
start_signal = False
running = True
paused = False
logging_mp.basicConfig(level=logging_mp.INFO)
logger_mp = logging_mp.getLogger(__name__)

def on_press(key):
    """键盘事件处理函数"""
    global running, start_signal, paused
    if key == 'r':
        start_signal = True
        paused = False
        logger_mp.info("程序开始/继续")
    elif key == 'q':
        stop_listening()
        running = False
        logger_mp.info("程序已停止")
    elif key == 'p':
        paused = not paused
        if paused:
            logger_mp.info("程序已暂停，按'r'继续")
        else:
            logger_mp.info("程序继续运行")
    else:
        logger_mp.debug(f"按键 {key} 未定义操作")

# 启动键盘监听线程
listen_keyboard_thread = threading.Thread(
    target=listen_keyboard,
    kwargs={"on_press": on_press, "until": None, "sequential": False},
    daemon=True
)
listen_keyboard_thread.start()

class ArmController(Node):
    """机械臂控制器，负责发布控制指令和订阅关节状态"""
    def __init__(self):
        super().__init__('arm_controller')
        self.lock = threading.Lock()

        # 发布器
        self.left_arm_pub = self.create_publisher(JointState, '/joint_command_left_arm', 10)
        self.right_arm_pub = self.create_publisher(JointState, '/joint_command_right_arm', 10)

        # 订阅器
        self.left_arm_sub = self.create_subscription(
            JointState, '/joint_states_left_arm', self.left_arm_callback, 10)
        self.right_arm_sub = self.create_subscription(
            JointState, '/joint_states_right_arm', self.right_arm_callback, 10)
        
        logger_mp.info("机械臂控制器初始化完成")

        # 关节状态存储
        self.left_arm_states = None
        self.right_arm_states = None

    def left_arm_callback(self, msg):
        """左臂关节状态回调"""
        with self.lock:
            self.left_arm_states = msg
            # 调试级别才打印详细状态，避免日志冗余
            logger_mp.debug(f"左臂状态更新: {[round(p, 3) for p in msg.position]}")

    def right_arm_callback(self, msg):
        """右臂关节状态回调"""
        with self.lock:
            self.right_arm_states = msg
            logger_mp.debug(f"右臂状态更新: {[round(p, 3) for p in msg.position]}")

    def send_commands(self, sol_q, sol_tauff=None):
        """发送关节控制指令"""
        if sol_tauff is None:
            sol_tauff = np.zeros(10)

        # 输入验证
        if len(sol_q) != 10:
            logger_mp.error(f"无效的动作维度: 期望10，实际{len(sol_q)}")
            return

        try:
            # 左臂消息
            left_msg = JointState()
            left_msg.header.stamp = self.get_clock().now().to_msg()
            left_msg.name = ["left_motor0", "left_motor1", "left_motor2", "left_motor3", "left_motor4"]
            sol_q[4] = 0.0  # 固定左臂最后一个关节
            left_msg.position = sol_q[:5].tolist()
            left_msg.velocity = [0.0] * 5
            sol_tauff[4] = 0.0
            left_msg.effort = sol_tauff[:5].tolist()
            self.left_arm_pub.publish(left_msg)

            # 右臂消息
            right_msg = JointState()
            right_msg.header.stamp = self.get_clock().now().to_msg()
            right_msg.name = ["right_motor0", "right_motor1", "right_motor2", "right_motor3", "right_motor4"]
            sol_q[9] = 0.0  # 固定右臂最后一个关节
            right_msg.position = sol_q[5:].tolist()
            right_msg.velocity = [0.0] * 5
            sol_tauff[9] = 0.0
            right_msg.effort = sol_tauff[5:].tolist()
            self.right_arm_pub.publish(right_msg)

            logger_mp.debug(f"发送指令: 左臂={[round(p, 3) for p in left_msg.position]}, "
                          f"右臂={[round(p, 3) for p in right_msg.position]}")
        except Exception as e:
            logger_mp.error(f"发送指令失败: {str(e)}")

    def get_current_dual_arm_q(self):
        """获取当前双臂关节状态"""
        with self.lock:
            if self.left_arm_states is None or self.right_arm_states is None:
                logger_mp.debug("尚未收到关节状态数据")
                return np.zeros(10)
            
            try:
                left_q = [0.0] * 5
                for i, name in enumerate(self.left_arm_states.name):
                    if name.startswith("left_motor"):
                        idx = int(name.replace("left_motor", ""))
                        if 0 <= idx < 5:
                            left_q[idx] = self.left_arm_states.position[i]

                right_q = [0.0] * 5
                for i, name in enumerate(self.right_arm_states.name):
                    if name.startswith("right_motor"):
                        idx = int(name.replace("right_motor", ""))
                        if 0 <= idx < 5:
                            right_q[idx] = self.right_arm_states.position[i]

                return np.array(left_q + right_q)
            except Exception as e:
                logger_mp.error(f"解析关节状态失败: {str(e)}")
                return np.zeros(10)

def replay_actions(repo_id, root, episode, fps, arm_controller):
    """回放动作序列的核心函数"""
    if arm_controller is None:
        raise RuntimeError("必须提供已初始化的ArmController实例")

    # 等待开始信号
    logger_mp.info("等待'r'键开始回放...")
    while not start_signal and running:
        time.sleep(0.1)
    if not running:
        logger_mp.info("回放被用户取消")
        return

    # 加载数据集
    try:
        dataset = LeRobotDataset(repo_id, root=root, episodes=[episode])
    except Exception as e:
        logger_mp.error(f"加载数据集失败: {str(e)}")
        return

    # 验证episode有效性
    if episode < 0 or episode >= len(dataset.episodes):
        logger_mp.error(f"无效的episode索引: {episode}，总共有{len(dataset.episodes)}个episode")
        return


    # 准备动作数据
    try:
        actions = dataset.hf_dataset.select_columns("action")
        num_frames = dataset.num_frames
        frame_interval = 1.0 / fps
        logger_mp.info(f"开始回放 episode {episode}，共{num_frames}帧，帧率{fps}Hz")
    except Exception as e:
        logger_mp.error(f"准备动作数据失败: {str(e)}")
        return

    # 回放统计信息
    stats = {
        "total_frames": num_frames,
        "delayed_frames": 0,
        "total_delay": 0.0,
        "start_time": time.perf_counter()
    }

    # 开始回放
    for idx in range(num_frames):
        # 检查暂停状态
        while paused and running:
            time.sleep(0.1)
        
        # 检查是否需要停止
        if not running:
            logger_mp.info("回放被用户终止")
            break

        # 时间控制（补偿延迟）
        target_time = stats["start_time"] + idx * frame_interval
        current_time = time.perf_counter()
        sleep_time = target_time - current_time

        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            delay = -sleep_time
            stats["delayed_frames"] += 1
            stats["total_delay"] += delay
            if delay > 0.1:  # 显著延迟才警告
                logger_mp.warning(f"帧{idx}延迟: {delay:.3f}秒")

        # 获取并发送动作
        try:
            action = actions[idx]["action"]
            current_q = arm_controller.get_current_dual_arm_q()
            
            # 打印状态对比（每10帧打印一次，避免刷屏）
            if idx % 10 == 0:
                logger_mp.info(
                    f"帧 {idx}/{num_frames}\n"
                    f"  目标: {[round(p, 3) for p in action]}\n"
                    f"  当前: {[round(p, 3) for p in current_q]}\n"
                    f"  误差: {[round(abs(t-c), 3) for t, c in zip(action, current_q)]}"
                )

            arm_controller.send_commands(action)
        except Exception as e:
            logger_mp.error(f"处理帧{idx}失败: {str(e)}")
            continue

    # 打印回放统计
    total_time = time.perf_counter() - stats["start_time"]
    logger_mp.info("\n回放统计:")
    logger_mp.info(f"  总帧数: {stats['total_frames']}")
    logger_mp.info(f"  总时间: {total_time:.2f}秒 (预期: {num_frames/fps:.2f}秒)")
    logger_mp.info(f"  延迟帧比例: {stats['delayed_frames']/stats['total_frames']*100:.1f}%")
    logger_mp.info(f"  平均延迟: {stats['total_delay']/stats['total_frames']:.3f}秒")

def main():
    """主函数：解析参数并启动回放"""
    parser = argparse.ArgumentParser(description='机械臂动作回放程序')
    parser.add_argument('--repo-id', type=str, default='Skill_Library', help='HuggingFace数据集仓库ID')
    parser.add_argument('--root', type=str, default='/home/ygx/.cache/huggingface/lerobot/Skill_Library', 
                      help='数据集存储路径')
    parser.add_argument('--episode', type=int, default=0, help='要回放的episode索引')
    parser.add_argument('--fps', type=float, default=30.0, help='回放帧率(Hz)')
    args = parser.parse_args()

    rclpy.init()
    arm_controller = ArmController()
    
    # 启动ROS回调线程
    spin_thread = threading.Thread(target=rclpy.spin, args=(arm_controller,), daemon=True)
    spin_thread.start()

    try:
        replay_actions(
            repo_id=args.repo_id,
            root=args.root,
            episode=args.episode,
            fps=args.fps,
            arm_controller=arm_controller
        )
    finally:
        # 清理资源
        stop_listening()  # 终止键盘监听
        arm_controller.destroy_node()
        rclpy.shutdown()
        spin_thread.join()
        logger_mp.info("程序退出")

if __name__ == "__main__":
    main()