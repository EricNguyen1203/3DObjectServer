from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import grpc
from Requests.create_model_request import Create3dModelRequest
from Requests.response import BaseReponse
import model3d_pb2_grpc
import model3d_pb2 
from typing import Dict, List, Tuple
from Repositories.model_3d_repository import Model3dRepository, Model3dEntity
from Controllers.llm_controller import LLMJsonParser
import json

router = APIRouter(
    prefix="/model3d",
    tags=["model3d"]
)
repository = Model3dRepository()


def stream_create_model_responses(
    character_descs: List[List[Tuple[str, str]]], title: str, room_id: str
):
    with grpc.insecure_channel("localhost:50090") as channel:
        stub = model3d_pb2_grpc.GenModel3dServiceStub(channel)
        prompts = []
        character_names = []
        number_character_in_scenes = []
        for characters in character_descs:
            number_character_in_scenes.append(len(characters))
            prompts += [desc[1] for desc in characters]
            character_names += [desc[0] for desc in characters]

        request = model3d_pb2.Model3dGenRequest(prompts=prompts, title=title)
        index = 0
        for response in stub.GenModel3d(request):
            print(f"[{response.stage}] {response.progress}% - {response.message}")
            if response.status == 2:  # Finished
                entities = []
                paths = list(response.path)

                for i in range(len(paths)):
                    if number_character_in_scenes[index] == 0:
                        index = index + 1
                    entities.append(
                        Model3dEntity(
                            title=title,
                            room_id=room_id,
                            character_name=character_names[i],
                            prompt=prompts[i],
                            path=paths[i],
                            index=index,
                        )
                    )
                    number_character_in_scenes[index] = (
                        number_character_in_scenes[index] - 1
                    )
                repository.insert_many(entities)

            yield json.dumps({
                "stage": response.stage,
                "progress": response.progress,
                "message": response.message,
                "status": response.status,
                "paths": list(response.path),
            }) + "\n"


def get_model_3d_grpc(path: str):
    with grpc.insecure_channel("localhost:50090") as channel:
        stub = model3d_pb2_grpc.GenModel3dServiceStub(channel)

        request = model3d_pb2.Model3dGetRequest(
            path = path
        )

        for response in stub.GetModel3d(request):
            yield response.data


@router.post("/create-3d-models")
async def create_3d_models(request: Create3dModelRequest):
    llm = LLMJsonParser()
    character_descs = llm.json_parse_characters(request.title, request.story)
    try:
        return StreamingResponse(
            stream_create_model_responses(
                character_descs=character_descs,
                title=request.title,
                room_id=request.room_id,
            )
        )
    except Exception as e:
        return BaseReponse(content={"result": "failed"}, status_code=500);    


@router.get("/get-3d-model")
async def get_3d_model(path: str):
    try:
        return StreamingResponse(get_model_3d_grpc(path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
