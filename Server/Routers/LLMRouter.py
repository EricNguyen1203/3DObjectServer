from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from Controllers.llm_controller import LLMJsonParser
from Repositories.story_repository import *
from Models.story_entity import *

router = APIRouter(prefix="/llm", tags=["llm"])
story_repository = StoryRepository()


@router.get("/get-place")
async def get_place(title: str, room_id: str, story: str):
    try:
        content = story_repository.load_one(
            StoryEntity(title=title, room_id=room_id).to_dict()
        )
        print("story ", content)
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
            StoryEntity(title=title, room_id=room_id, descriptions=result)
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
async def get_characters(title: str, room_id: str, story: str):
    try:
        print("story ", story)
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
