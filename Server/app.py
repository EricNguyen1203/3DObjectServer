from fastapi import FastAPI
from Routers import Model3dRouter, Image360Router, AudioRouter, LLMRouter, RoomRouter

app = FastAPI()
app.include_router(Model3dRouter.router)
app.include_router(Image360Router.router)
app.include_router(AudioRouter.router)
app.include_router(LLMRouter.router)
app.include_router(RoomRouter.router)
