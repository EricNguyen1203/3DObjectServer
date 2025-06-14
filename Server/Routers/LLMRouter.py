
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from Controllers.llm_controller import LLMJsonParser

router = APIRouter(prefix="/llm", tags=["llm"])

@router.get("/get-place")
async def get_place(title: str, story: str):
    try:
        llm = LLMJsonParser()
        result = []

        result = llm.json_parse_story(title=title, prompt=story)
                
        return JSONResponse(status_code=200, content={"places": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
