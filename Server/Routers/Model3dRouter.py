from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import grpc
from Requests.create_model_request import Create3dModelRequest
from Requests.response import BaseReponse
import model3d_pb2_grpc
import model3d_pb2 
from typing import List
from Repositories.model_3d_repository import Model3dRepository, Model3dEntity
import json

router = APIRouter(
    prefix="/model3d",
    tags=["model3d"]
)

def stream_create_model_responses(prompts: List[str], title: str):
    # Set any gRPC options here if needed
    with grpc.insecure_channel("localhost:50090") as channel:
        stub = model3d_pb2_grpc.GenModel3dServiceStub(channel)

        request = model3d_pb2.Model3dGenRequest(
            prompts=prompts,
            title=title
        )

        for response in stub.GenModel3d(request):
            print(f"[{response.stage}] {response.progress}% - {response.message}")
            if response.status == 2: #finish
                #add to database
                repository = Model3dRepository()
                entities = [
                    Model3dEntity(title=title, prompt=prompt, path=path)
                    for prompt, path in zip(prompts, list(response.path))
                ]
                repository.insert_many(entities)
            yield json.dumps({
                "stage": response.stage,
                "progress": response.progress,
                "message": response.message,
                "status": response.status,
                "paths": list(response.path),
            }) + "\n"

@router.post("/create-3d-models")
async def create_3d_model(request: Create3dModelRequest):
    try:
        return StreamingResponse(stream_create_model_responses(prompts=request.prompts, title=request.title))
    except Exception as e:
        return BaseReponse(content={"result": "failed"}, status_code=500);    