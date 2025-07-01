from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from Controllers.llm_controller import LLMJsonParser
from Repositories.story_repository import *
from Repositories.character_desc_repository import *
from Repositories.dialogue_repository import *
from Models.story_entity import *
from Models.dialogue_entity import *

router = APIRouter(prefix="/llm", tags=["llm"])
story_repository = StoryRepository()
character_desc_repository = CharacterDescriptionRepository()
dialouge_repository = DialogueRepository()

@router.get("/get-place")
async def get_place(title: str, room_id: str, story: str):
    try:
        filter = StoryEntity(title=title, room_id=room_id).to_dict()
        scenes = [s.strip() for s in story.split("\n") if s.strip()]
        content = story_repository.load_one(filter)
        if content is not None:
            if not content.get("_story") or content.get("_story") is None:
                story_repository.update_one(filter, {"$set": {"_story": scenes}})
            return JSONResponse(
                status_code=200,
                content={
                    "code": 0,
                    "message": "Split Success",
                    "data": content["_descriptions"],
                },
            )

        llm = LLMJsonParser()
        result = []

        attempt = 5
        while attempt > 0:
            attempt = attempt - 1
            if result is None or len(result) == 0:
                result = llm.json_parse_story(title=title, prompt=story)
            else:
                break
        if result is None or len(result) == 0:
            return JSONResponse(
                status_code=500,
                content={
                    "code": 4005,
                    "message": "LLM could not gen model",
                    "data": [],
                },
            )
        story_repository.insert_one(
            StoryEntity(title=title, room_id=room_id, descriptions=result, story=scenes)
        )
        return JSONResponse(
            status_code=200,
            content={"code": 0, "message": "Split Success", "data": result},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 4005,
                "message": str(e),
                "data": [],
            },
        )


@router.get("/get-character")
async def get_characters(title: str, room_id: str, story: str, index: int):
    try:
        content = character_desc_repository.load_one(
            CharacterDescriptionEntity(
                title=title, room_id=room_id, index=index
            ).to_dict()
        )
        if content is not None:
            return JSONResponse(
                status_code=200,
                content={
                    "code": 0,
                    "message": "Split Success",
                    "data": content["_descriptions"],
                },
            )

        llm = LLMJsonParser()
        result = []

        attempt = 5
        while attempt > 0:
            attempt = attempt - 1
            if result is None or len(result) == 0:
                result = llm.json_parse_characters(title=title, story=story)
                print(result)
            else:
                break
        if result is None or len(result) == 0:
            return JSONResponse(
                status_code=500,
                content={
                    "code": 4005,
                    "message": "LLM could not gen model",
                    "data": [],
                },
            )
        character_desc_repository.insert_one(
            CharacterDescriptionEntity(
                title=title, room_id=room_id, descriptions=result, index=index
            )
        )
        return JSONResponse(
            status_code=200,
            content={"code": 0, "message": "Split Success", "data": result},
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 4005,
                "message": str(e),
                "data": [],
            },
        )


@router.get("/get-character-dialogues")
async def get_dialogues(title: str, room_id: str, index: int):
    try:
        dialouges = dialouge_repository.load_one(
            DialogueEntity(title=title, room_id=room_id, index=index).to_dict()
        )
        if dialouges is not None:
            return JSONResponse(
                status_code=200,
                content={
                    "code": 0,
                    "message": "Success",
                    "data": dialouges["_character_dialouges"],
                },
            )
        story = story_repository.load_one(
            StoryEntity(
                title=title,
                room_id=room_id,
            ).to_dict()
        )
        if story is None or len(story["_story"]) == 0 or index >= len(story["_story"]):
            return JSONResponse(
                status_code=400,
                content={"code": 1, "message": "Not Found", "data": None},
            )

        character_entity = character_desc_repository.load_one(
            CharacterDescriptionEntity(
                title=title, room_id=room_id, index=index
            ).to_dict()
        )
        if character_entity is None:
            return JSONResponse(
                status_code=400,
                content={
                    "code": 1,
                    "message": "Not Found character in scene",
                    "data": None,
                },
            )
        character_names = [
            character_name for character_name, desc in character_entity["_descriptions"]
        ]

        if len(character_names) == 0:
            return JSONResponse(
                status_code=400,
                content={
                    "code": 1,
                    "message": "Not Found character in scene",
                    "data": None,
                },
            )
        llm = LLMJsonParser()
        jsonList = llm.json_parse_dialouges(
            title=title,
            scene_content=story["_story"],
            characters_in_scene=character_names,
        )
        character_dialouges = [CharacterDialogue(character_name=character_name, dialogues=dialogues) for character_name, dialogues in jsonList]
        if character_dialouges is None:
            return JSONResponse(
                status_code=500,
                content={
                    "code": 5,
                    "message": "Error occur when generate dialouges",
                    "data": None,
                },
            )
        dialouge_repository.insert_one(
            DialogueEntity(
                title=title,
                room_id=room_id,
                index=index,
                character_dialouges=character_dialouges,
            )
        )
        return JSONResponse(
            status_code=200,
            content={"code": 0, "message": "Success", "data": character_dialouges},
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "code": 5,
                "message": f"Error occur when generate dialouges {e}",
                "data": None,
            },
        )
