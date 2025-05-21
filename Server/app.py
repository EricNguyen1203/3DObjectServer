from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from Routers import Model3dRouter

app = FastAPI()
app.include_router(Model3dRouter.router)


