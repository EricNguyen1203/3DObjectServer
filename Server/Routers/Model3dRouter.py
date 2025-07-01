from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import grpc
from Requests.create_model_request import *
from Requests.response import BaseReponse, JSONResponse
import model3d_pb2_grpc
import model3d_pb2 
from typing import Dict, List, Tuple
from Repositories.model_3d_repository import Model3dRepository, Model3dEntity
from Repositories.dialogue_repository import *
from Models.dialogue_entity import *
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
dialouge_repository = DialogueRepository()


def stream_create_model_responses(
    character_descs: List[Tuple[str, str]],
    title: str,
    room_id: str,
    index: int,
    scene: str,
):
    paths = []
    prompts = []
    character_names = []
    gen_character_names = []
    print(f"load {len(character_descs)}")
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
            gen_character_names.append(character_name)

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

                filter = Model3dEntity(
                    title=title,
                    room_id=room_id,
                    index=index,
                ).to_dict()
                entities = repository.load_many(filter)
                res = [
                    entity
                    for entity in entities
                    if entity["_character_name"] in gen_character_names
                ]
                print(len(res_paths))
                yield json.dumps(
                    {
                        "stage": response.stage,
                        "progress": response.progress,
                        "message": response.message,
                        "status": response.status,
                        "entities": res,
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
        print(character_descs)

    try:
        return StreamingResponse(
            stream_create_model_responses(
                character_descs=character_descs,
                title=request.title,
                room_id=request.room_id,
                index=request.index,
                scene=request.story,
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


# update position and model scale
@router.post("/update-3d-model")
async def update_3d_model(request: Update3dModelRequest):
    try:
        entities = repository.load_many(
            Model3dEntity(
                title=request.title, room_id=request.room_id, index=request.index
            ).to_dict()
        )
        if entities is None or len(entities) == 0:
            return JSONResponse(
                content={"code": 4, "message": "Not Found model", "data": None},
                status_code=400,
            )
        character_map = {character.name: character for character in request.characters}
        print(character_map)
        bulk_updates = []
        for entity in entities:
            name = entity.get("_character_name")
            if name in character_map:
                matched = character_map[name]

                # Optional: check if values actually changed
                if (
                    entity.get("_position") != matched.position
                    or entity.get("_scale") != matched.scale
                ):
                    bulk_updates.append(
                        {
                            "filter": {"_id": ObjectId(entity["_id"])},
                            "update": {
                                "$set": {
                                    "_position": matched.position,
                                    "_scale": matched.scale,
                                    "_rotation": matched.rotation,
                                }
                            },
                        }
                    )
        print(len(bulk_updates))
        if bulk_updates:
            repository.bulk_update(bulk_updates)  # You must implement this in your repo

        return JSONResponse(
            content={
                "code": 0,
                "message": f"Updated {len(bulk_updates)} model(s) successfully",
                "data": "Success",
            }
        )

    except Exception as e:
        print(e)
        return JSONResponse(
            content={
                "code": 5,
                "message": f"{e}",
                "data": "Failed",
            },
            status_code=500,
        )


@router.post("/delete")
async def delete_3d_model(request: Delete3dModelRequest):
    try:
        entity = character_desc_repository.load_one(
            CharacterDescriptionEntity(
                title=request.title,
                room_id=request.room_id,
                index=request.index,
            ).to_dict()
        )
        if entity is None:
            return JSONResponse(
                content={"code": 4, "message": "Not Found model", "data": None},
                status_code=400,
            )
        character_updates = [
            (character_name, desc)
            for character_name, desc in entity["_descriptions"]
            if character_name != request.character_name
        ]
        id = ObjectId(entity["_id"])
        character_desc_repository.update_one(
            {"_id": id}, {"$set": {"_descriptions": character_updates}}
        )

        return JSONResponse(
            content={
                "code": 0,
                "message": f"Delete model(s) successfully",
                "data": "Success",
            }
        )

    except Exception as e:
        print(e)
        return JSONResponse(
            content={
                "code": 5,
                "message": f"{e}",
                "data": "Failed",
            },
            status_code=500,
        )
