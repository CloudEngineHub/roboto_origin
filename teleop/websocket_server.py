import asyncio
import websockets
from replay_Atom import replay_actions
import threading
import rclpy
from replay_Atom import ArmController

# 全局只初始化一次rclpy和ArmController
rclpy.init()
arm_controller = ArmController()

def run_replay_actions(episode):
    # 直接调用replay_actions，传入全局arm_controller
    replay_actions(
        repo_id="test",
        root="/home/ygx/.cache/huggingface/lerobot/test",
        episode=episode,
        fps=30.0,
        arm_controller=arm_controller
    )

async def echo(websocket):
    try:
        async for message in websocket:
            print(f"收到客户端消息: {message}")
            await websocket.send(f"服务端已收到: {message}")
            # 判断是否为数字，若是则回放对应episode
            if message.isdigit():
                episode = int(message)
                threading.Thread(target=run_replay_actions, args=(episode,), daemon=True).start()
    except websockets.exceptions.ConnectionClosed:
        print("客户端已断开连接。")
    except Exception as e:
        print(f"发生异常: {e}")

async def main():
    # 设置更长的ping间隔和超时时间，防止空闲断开
    async with websockets.serve(
        echo, "localhost", 8765, ping_interval=120, ping_timeout=120
    ):
        print("WebSocket 服务器已启动 ws://localhost:8765")
        await asyncio.Future()  # 永远运行

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        arm_controller.destroy_node()
        rclpy.shutdown()