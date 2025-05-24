from fastapi import FastAPI
from Routers import Model3dRouter, Image360Router

app = FastAPI()
app.include_router(Model3dRouter.router)
app.include_router(Image360Router.router)
