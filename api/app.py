from fastapi import FastAPI, WebSocket
from api.routes import router
from api.websocket import websocket_endpoint

app = FastAPI()
app.include_router(router)


@app.websocket("/ws")
async def ws(ws: WebSocket):
    await websocket_endpoint(ws)
