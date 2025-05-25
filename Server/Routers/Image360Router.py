import json
import grpc
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import image_360_pb2
import image_360_pb2_grpc
from Requests.create_image360_request import CreateImage360Request

router = APIRouter(prefix="/image360", tags=["image360"])


def streaming_image_360(prompt: str, title: str):
    with grpc.insecure_channel("localhost:50081") as channel:
        stub = image_360_pb2_grpc.Image360ServiceStub(channel)

        # Prepare request
        request = image_360_pb2.CreateImage360Request(prompt=prompt, title=title)

        # Collect streamed responses
        final_path = ""
        for response in stub.Create360Image(request):
            yield json.dumps(
                {
                    "progress": response.progress,
                    "status": response.status,
                    "path": response.path,
                }
            ) + "\n"


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
        return StreamingResponse(
            streaming_image_360(prompt=req.prompt, title=req.title),
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
