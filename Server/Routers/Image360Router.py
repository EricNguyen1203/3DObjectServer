import json
from typing import List
import grpc
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import image_360_pb2
import image_360_pb2_grpc
from Repositories.image360_repository import Image360Repository
from Models.image360_entity import Image360Entity
from Requests.create_image360_request import (
    CreateImage360Request,
    CreateScene360Request,
    GetImagesRequest,
)
from Controllers.llm_controller import LLMJsonParser


router = APIRouter(prefix="/image360", tags=["image360"])
repository = Image360Repository()


def streaming_image_360(prompt: str, title: str, room_id: str, index: int):
    with grpc.insecure_channel("localhost:50081") as channel:
        stub = image_360_pb2_grpc.Image360ServiceStub(channel)

        # Prepare request
        request = image_360_pb2.CreateImage360Request(prompt=prompt, title=title)

        # Collect streamed responses
        final_path = ""
        for response in stub.Create360Image(request):
            if response.status == 2:
                id = repository.insert_one(
                    Image360Entity(
                        title=request.title,
                        prompt=request.prompt,
                        path=response.path,
                        room_id=room_id,
                        index=index,
                    )
                )

            yield json.dumps(
                {
                    "progress": response.progress,
                    "status": response.status,
                    "path": response.path,
                }
            ) + "\n"


def streaming_image_360_zip(paths: List[str]):
    with grpc.insecure_channel("localhost:50081") as channel:
        stub = image_360_pb2_grpc.Image360ServiceStub(channel)

        # Prepare request
        request = image_360_pb2.GetImagesZipRequest(paths=paths)

        # Collect streamed responses
        final_path = ""
        for response in stub.GetImagesZip(request):
            yield response.data


def get_image_360_grpc(path: str):
    try:
        with grpc.insecure_channel("localhost:50081") as channel:
            stub = image_360_pb2_grpc.Image360ServiceStub(channel)
            request = image_360_pb2.GetImage360Request(path=path)
            responses = stub.Get360Image(request)
            for response in responses:
                if response.status == 0:
                    raise Exception("Failed to retrieve image")
                elif response.status in [1, 2]:  # Data chunk or finished
                    if response.data:
                        yield response.data
    except Exception as e:
        print(f"[grpc_image_stream] Exception: {str(e)}")
        raise


@router.post("/create-image-360")
async def create_image_360(req: CreateImage360Request):
    try:
        # Connect to gRPC server
        result = repository.load_one(
            Image360Entity(
                title=f"{req.title}_{req.index}", prompt=req.prompt, room_id=req.room_id, index=req.index
            ).to_dict()
        )
        print(result)
        if result is not None:
            return StreamingResponse(
                json.dumps(
                    {
                        "progress": 100,
                        "status": 2,
                        "path": result["_path"],
                    }
                )
                + "\n",
                media_type="application/json",
            )
        return StreamingResponse(
            streaming_image_360(
                prompt=req.prompt,
                title=f"{req.title}_{req.index}",
                room_id=req.room_id,
                index=req.index,
            ),
            media_type="application/json",
        )

    except Exception as e:
        print(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get-image-360")
async def get_image_360(path: str):
    try:
        # Connect to gRPC server
        return StreamingResponse(
            get_image_360_grpc(path=path),
            media_type="image/png",
        )

    except Exception as e:
        print(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-scenes-360")
async def create_scenes(request: CreateImage360Request):
    try:
        llm = LLMJsonParser()
        results = []

        results = llm.json_parse_story(title=request.title, prompt=request.prompt)
        paths = []
        count = 0
        for result in results:
            final_path = ""
            for response in streaming_image_360(
                prompt=result, title=f"{request.title}{count}"
            ):
                data = json.loads(response)

                print(f"[{data['progress']}%] {data['status']}")

                if data["status"] == 2:
                    final_path = data["path"]

            if final_path:
                paths.append(final_path)
            count = count + 1

        return {"success": True, "image_paths": paths}

    except Exception as e:
        print(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get-images")
async def get_images(request: GetImagesRequest):
    try:
        # Connect to gRPC server
        return StreamingResponse(
            streaming_image_360_zip(request.paths), media_type="application/zip"
        )

    except Exception as e:
        print(f"Exception: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
