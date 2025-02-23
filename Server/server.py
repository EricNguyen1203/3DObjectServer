import json
import subprocess

import paramiko
from scp import SCPClient
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import base64

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from Server import utils
from Server.controllers.llm_controller import LLMJsonParser
from Server.database import MongoDBCollections
from Server.models import ModelInfo

TEXTURE_FILE_NAME = "texture.png"
MODEL_FILE_NAME = "models.obj"
MTL_FILE_NAME = "texture.mtl"
# Load the .env file
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1"],
)


class PromptRequest(BaseModel):
    prompt: str
    model_name: str
    max_face_nums: int

class GetZipModelRequest(BaseModel):
    model_name: str


class Model3D:
    model: bytes
    texture: str
    mtl: bytes

    def __init__(self, model: bytes, texture: str, mtl: bytes):
        self.model = model
        self.texture = texture
        self.mtl = mtl

class LLMJsonParseRequest(BaseModel):
    prompt: str

# Server details
hostname = os.getenv("SERVER_HOST")
username = os.getenv("SERVER_USERNAME")
password = os.getenv("SERVER_PASSWORD")

remote_folder = os.getenv("REMOTE_PATH")
local_folder = os.getenv("LOCAL_PATH")
root_db = "thesis2025"

def create_scp_client(ssh_client):
    return SCPClient(ssh_client.get_transport())


def file_to_byte_array(file_path):
    with open(file_path, "rb") as file:
        byte_array = file.read()
    return byte_array


def create_model3D_SSH(promt: str, model_name: str):
    try:
        output = None
        error = None
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)

        scp = create_scp_client(client)

        # if os.path.exists(local_folder):
        #     os.rmdir(local_folder)
        #     os.makedirs(local_folder)

        # if not os.path.exists(local_folder):
        #     os.makedirs(local_folder)

        # activate the virtual environment name myenv
        command = f"""cd /raid/hvtham/Thesis-Triet-Thanh-k21/Hunyuan3D-1/ && source ~/miniconda3/etc/profile.d/conda.sh && conda activate esroom && python main.py --text_prompt "{promt}" --save_folder ./outputs/{model_name}/ --max_faces_num 90000 --do_texture_mapping"""

        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        print("Output:", output)
        print("Errors:", error)

        # not copy
        # obj_file = remote_folder + "mesh.obj"
        #
        # scp.get(obj_file, local_folder)

        client.close()
        return {"output": output, "error": error}
    except Exception as e:
        print("Error:", str(e))
        return {"error": str(e)}


def create_model3D_command(prompt: str, model_name: str, max_face_nums: int, desc: ModelInfo):
    folder_root = "/raid/hvtham/Thesis-Triet-Thanh-k21/Hunyuan3D-1/"
    count=0
    query={
                "model_name": model_name,
                "model_info": desc.to_json()
    }
    mongo_collection = MongoDBCollections(db_name=root_db)
    if not mongo_collection:
        return {"output": "no database connection"}

    count = len(mongo_collection.find_all("model3D", query={
        "model_name": model_name,
    }))
    print(f"creating model {query}")

    if utils.check_model_existed(os.path.join(folder_root, "outputs", f"{model_name}_{count}")):
        mongo_collection = MongoDBCollections(db_name=root_db)
        if len(mongo_collection.find_all("model3D", query=query)) > 0:
            return {"output": "already gen this object"}

    count = count + 1

    model_id = mongo_collection.insert_one(
        collection_name="model3D",
        data={
            "model_name": model_name,
            "prompt": prompt,
            "path": os.path.join(folder_root, "outputs", model_name),
            "max_face_num": max_face_nums,
        })
    if model_id is not None:
        print(f"inserted {model_id}")
    else:
        return {"output": "insert collection failed"}

    command = (f"    cd {folder_root} &&\n"
               f"    python main.py --text_prompt \"{prompt}\" --save_folder ./outputs/{model_name}_{count}/ --max_faces_num {max_face_nums} --do_texture_mapping"
               )


    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            executable="/bin/bash"  # Run in local bash shell
        )
        output, error = process.communicate()
        if utils.check_model_existed(os.path.join(folder_root, "outputs",
                                          f"{model_name}_{count}")):  # check if success avoid 500 response but gen success

            return {"output": output}

        print("Errors:", error)

        return {"output": output, "error": error}
    except Exception as e:
        return {"error": e}

#
# def get_model3D_bytes_SSH(promt: str):
#     result = Model3D(None, None, None)
#
#     try:
#         client = paramiko.SSHClient()
#         client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#         client.connect(hostname, username=username, password=password)
#
#         # promt = request.prompt
#         # command = f"""cd /raid/hvtham/Thesis-Triet-Thanh-k21/Hunyuan3D-1/ && source ~/miniconda3/etc/profile.d/conda.sh && conda activate esroom && python main.py --text_prompt "{promt}" --save_folder ./outputs/test/ --max_faces_num 90000 --do_texture_mapping --do_render"""
#
#         # stdin, stdout, stderr = client.exec_command(command)
#         # print("Output:", stdout.read().decode())
#         # print("Errors:", stderr.read().decode())
#
#         model_file = remote_folder + "mesh.obj"
#         mtl_file = remote_folder + "texture.mtl"
#         texture_file = remote_folder + "texture.png"
#
#         print("Texture file:", texture_file)
#
#         sftp_client = client.open_sftp()
#
#         with sftp_client.file(model_file, mode="rb") as file:
#             result.model = file.read()
#
#         with sftp_client.file(mtl_file, mode="rb") as file:
#             result.mtl = file.read()
#
#         with sftp_client.file(texture_file, mode="rb") as file:
#             texture_byte = file.read()
#
#         result.texture = base64.b64encode(texture_byte)
#
#         sftp_client.close()
#         client.close()
#         return result
#     except Exception as e:
#         print("Error:", str(e))
#         return result


@app.get("/")
async def root():
    return {"message": "Welcome to the 3D model generation server!"}


@app.post("/create-model3D")
async def create_model3D(request: PromptRequest):
    prompt = request.prompt
    try:
        llm = LLMJsonParser()
        res = llm.json_parse(prompt)
        res_object = json.loads(res) if res is not None else None
        model_name = res_object.get("model_name") if res_object else None
        max_face_nums = res_object.get("max_face_num") if res_object else 10000
        # Init model info
        model_info = ModelInfo()
        model_info.max_face_num = res_object.get("max_face_num") if res_object else model_info.max_face_num
        model_info.size = res_object.get("size") if res_object else model_info.size
        model_info.color = res_object.get("color") if res_object else model_info.color
        model_info.material = res_object.get("material") if res_object else model_info.material

        result = create_model3D_command(prompt, model_name, max_face_nums, model_info)

        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.post("/get-model3D-zip")
async def get_model3D_zip(request: GetZipModelRequest):
    zip_buffer = await utils.create_zip(os.path.join(remote_folder, "outputs", request.model_name), ["mesh.obj", "texture.png", "texture.mtl"])  # Zip for optimize transferring
    if not zip_buffer:
        return HTTPException(status_code=400, detail="No model gen yet")
    return StreamingResponse(zip_buffer)

@app.get("/json-parse")
async def get_model_desc(request: LLMJsonParseRequest):
    prompt=request.prompt
    llm = LLMJsonParser()
    try:
        res = llm.json_parse(prompt)
        return {"output": res}

    except Exception as e:
        print(f"Error in Parse: {e}")
        raise HTTPException(status_code=500, detail=e)

# @app.post("/get-model3D-bytes")
# async def get_model3D_bytes(request: PromptRequest):
#     prompt = request.prompt
#
#     result = get_model3D_bytes_SSH(request)
#
#     if not result.model:
#         raise HTTPException(status_code=204, detail="No model found")
#
#     if not result.texture:
#         raise HTTPException(status_code=204, detail="No texture found")
#
#     if not result.mtl:
#         raise HTTPException(status_code=204, detail="No mtl found")
#
#     return result