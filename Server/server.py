import subprocess

import paramiko
from scp import SCPClient
import os
import uvicorn
import aiohttp
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import base64

from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from models import ModelInfo
import utils

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


# Server details
hostname = os.getenv("SERVER_HOST")
username = os.getenv("SERVER_USERNAME")
password = os.getenv("SERVER_PASSWORD")

remote_folder = os.getenv("REMOTE_PATH")
local_folder = os.getenv("LOCAL_PATH")


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


def create_model3D_command(prompt: str, model_name: str, max_face_nums: int):
    folder_root = "/raid/hvtham/Thesis-Triet-Thanh-k21/Hunyuan3D-1/"
    if utils.check_files(os.path.join(folder_root, "outputs", model_name)):
        return {"output": "already gen this object"}
    command = (f"    cd {folder_root} &&\n"
               f"    python main.py --text_prompt \"{prompt}\" --save_folder ./outputs/{model_name}/ --max_faces_num {max_face_nums} --do_texture_mapping"
               )
    # TODO: handle when have database, conflict model_name
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
        if utils.check_files(os.path.join(folder_root, "outputs",
                                          model_name)):  # check if success avoid 500 response but gen success
            return {"output": output}

        print("Errors:", error)

        return {"output": output, "error": error}
    except Exception as e:
        return {"error": e}


def get_model3D_bytes_SSH(promt: str):
    result = Model3D(None, None, None)

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, password=password)

        # promt = request.prompt
        # command = f"""cd /raid/hvtham/Thesis-Triet-Thanh-k21/Hunyuan3D-1/ && source ~/miniconda3/etc/profile.d/conda.sh && conda activate esroom && python main.py --text_prompt "{promt}" --save_folder ./outputs/test/ --max_faces_num 90000 --do_texture_mapping --do_render"""

        # stdin, stdout, stderr = client.exec_command(command)
        # print("Output:", stdout.read().decode())
        # print("Errors:", stderr.read().decode())

        model_file = remote_folder + "mesh.obj"
        mtl_file = remote_folder + "texture.mtl"
        texture_file = remote_folder + "texture.png"

        print("Texture file:", texture_file)

        sftp_client = client.open_sftp()

        with sftp_client.file(model_file, mode="rb") as file:
            result.model = file.read()

        with sftp_client.file(mtl_file, mode="rb") as file:
            result.mtl = file.read()

        with sftp_client.file(texture_file, mode="rb") as file:
            texture_byte = file.read()

        result.texture = base64.b64encode(texture_byte)

        sftp_client.close()
        client.close()
        return result
    except Exception as e:
        print("Error:", str(e))
        return result


@app.get("/")
async def root():
    return {"message": "Welcome to the 3D model generation server!"}


@app.post("/create-model3D")
async def create_model3D(request: PromptRequest):
    prompt = request.prompt
    model_name = request.model_name
    max_face_nums = request.max_face_nums
    result = create_model3D_command(prompt, model_name, max_face_nums)

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    return result


@app.post("/get-model3D-zip")
async def get_model3D_zip(request: GetZipModelRequest):
    zip_buffer = await utils.create_zip(os.path.join(remote_folder, "outputs", request.model_name), ["mesh.obj", "texture.png", "texture.mtl"])  # Zip for optimize transferring
    if not zip_buffer:
        return HTTPException(status_code=400, detail="No model gen yet")
    return StreamingResponse(zip_buffer)


@app.post("/get-model3D-bytes")
async def get_model3D_bytes(request: PromptRequest):
    prompt = request.prompt

    result = get_model3D_bytes_SSH(request)

    if not result.model:
        raise HTTPException(status_code=204, detail="No model found")

    if not result.texture:
        raise HTTPException(status_code=204, detail="No texture found")

    if not result.mtl:
        raise HTTPException(status_code=204, detail="No mtl found")

    return result
