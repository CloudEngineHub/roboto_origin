# websocket_client.py
import asyncio
import websockets

async def send_heartbeat(websocket, interval=30):
    while True:
        try:
            await websocket.ping()
            await asyncio.sleep(interval)
        except Exception:
            break

async def client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # 启动心跳协程
        asyncio.create_task(send_heartbeat(websocket, interval=30))
        while True:
            msg = input("请输入要发送的内容（exit退出）：")
            if msg.lower() == "exit":
                break
            await websocket.send(msg)
            reply = await websocket.recv()
            print(f"收到服务端回复: {reply}")

if __name__ == "__main__":
    asyncio.run(client())