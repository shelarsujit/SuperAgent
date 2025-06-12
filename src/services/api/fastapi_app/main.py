from fastapi import FastAPI, WebSocket
from .routes import router
from ..websocket_handler import handle_websocket

app = FastAPI(title="SuperAgent API")

# Include standard HTTP routes
app.include_router(router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time interaction with the RouterAgent."""
    await handle_websocket(websocket)
