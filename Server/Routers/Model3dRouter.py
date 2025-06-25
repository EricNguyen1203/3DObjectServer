from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import grpc
from Requests.create_model_request import Create3dModelRequest
from Requests.response import BaseReponse
import model3d_pb2_grpc
import model3d_pb2 
from typing import Dict, List, Tuple
from Repositories.model_3d_repository import Model3dRepository, Model3dEntity
from Repositories.character_desc_repository import (
    CharacterDescriptionRepository,
    CharacterDescriptionEntity,
)
from Controllers.llm_controller import LLMJsonParser
import json

router = APIRouter(
    prefix="/model3d",
    tags=["model3d"]
)
repository = Model3dRepository()
character_desc_repository = CharacterDescriptionRepository()


def stream_create_model_responses(
    character_descs: List[Tuple[str, str]], title: str, room_id: str, index: int
):
    paths = []
    prompts = []
    character_names = []

    for character_name, prompt in character_descs:
        entity = repository.load_one(
            Model3dEntity(
                title=title,
                room_id=room_id,
                character_name=character_name,
                prompt=prompt,
                index=index,
            ).to_dict()
        )
        if entity:
            paths.append(entity["_path"])
        else:
            character_names.append(character_name)
            prompts.append(prompt)

    with grpc.insecure_channel("localhost:50090") as channel:
        stub = model3d_pb2_grpc.GenModel3dServiceStub(channel)
        request = model3d_pb2.Model3dGenRequest(prompts=prompts, title=title)
        for response in stub.GenModel3d(request):
            print(f"[{response.stage}] {response.progress}% - {response.message}")
            if response.status == 2:  # Finished
                entities = []
                res_paths = list(response.path)
                paths += res_paths
                for i in range(len(prompts)):
                    entities.append(
                        Model3dEntity(
                            title=title,
                            room_id=room_id,
                            character_name=character_names[i],
                            prompt=prompts[i],
                            path=res_paths[i],
                            index=index,
                        )
                    )

                repository.insert_many(entities)
                yield json.dumps(
                    {
                        "stage": response.stage,
                        "progress": response.progress,
                        "message": response.message,
                        "status": response.status,
                        "entities": repository.load_many(
                            Model3dEntity(
                                title=title,
                                room_id=room_id,
                                index=index,
                            ).to_dict()
                        ),
                    }
                ) + "\n"
            else:
                yield json.dumps(
                    {
                        "stage": response.stage,
                        "progress": response.progress,
                        "message": response.message,
                        "status": response.status,
                        "entities": [],
                    }
                ) + "\n"


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

    content = character_desc_repository.load_one(
        CharacterDescriptionEntity(
            title=request.title, room_id=request.room_id, index=request.index
        ).to_dict()
    )
    if content is None:
        llm = LLMJsonParser()
        character_descs = llm.json_parse_characters(request.title, request.story)
        character_desc_repository.insert_one(
            CharacterDescriptionEntity(
                title=request.title,
                room_id=request.room_id,
                descriptions=character_descs,
                index=request.index,
            )
        )
    else:
        character_descs = content["_descriptions"]

    try:
        return StreamingResponse(
            stream_create_model_responses(
                character_descs=character_descs,
                title=request.title,
                room_id=request.room_id,
                index=request.index,
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
