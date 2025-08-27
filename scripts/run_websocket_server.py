"""
Run the FastAPI WebSocket server for the Agriculture Systems Dashboard
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.api.websocket_server:app", host="0.0.0.0", port=8000, reload=True)
