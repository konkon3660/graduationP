from fastapi import FastAPI
from routers import ws_router, mjpeg_router

app = FastAPI()
app.include_router(ws_router.router)
app.include_router(mjpeg_router.router)

