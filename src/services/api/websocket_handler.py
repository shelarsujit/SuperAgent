from fastapi import WebSocket, WebSocketDisconnect
from src.agents.router_agent import RouterAgent

router_agent = RouterAgent(config={})

async def handle_websocket(websocket: WebSocket) -> None:
    """Receive messages over a WebSocket and respond via the RouterAgent."""
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            result = await router_agent.process_input(data)
            await websocket.send_json(result)
    except WebSocketDisconnect:
        pass
