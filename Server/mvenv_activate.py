import os
import subprocess
import sys
import venv
from pathlib import Path
from typing import Union

StrOrFilePath = Union[str, Path]

# print(requests.get("http://127.0.0.1:8000/").json())

# prompt = "a red doll"
# # response = requests.post("http://127.0.0.1:8000/create-model3D", json={"prompt": prompt})
# response = requests.post("http://127.0.0.1:8000/get-model3D-bytes", json={"prompt": prompt})
# # response = requests.post("http://3.27.152.131/get-model3D-bytes", json={"prompt": prompt})
# # response = requests.get("http://3.27.152.131/")

# # print(response.json())


# response.raise_for_status()

# print (response.status_code)
# if response.status_code != 204:
#     print(response.json())
#     image = base64.b64decode(response.json()["texture"]) 
#     with open("texture.png", "wb") as file:
#         file.write(image)
# else:
#     print("No response")


class ExtendedEnvBuilder(venv.EnvBuilder):
    def __init__(self, *args, **kwargs):
        self.nodist = kwargs.pop('nodist', False)
        self.nopip = kwargs.pop('nopip', False)
        self.progress = kwargs.pop('progress', None)
        self.verbose = kwargs.pop('verbose', False)
        super().__init__(*args, **kwargs)
    
    def install_reqs(self, venv_path: StrOrFilePath):
        req_file = Path("requirements.txt")
        venv_path = Path(venv_path)
        if not req_file.exists():
            print("[WARN] requirements.txt not found. Skipping dependencies installation.")
            return
        
        python_exec = venv_path / ("Scripts" if os.name == "nt" else "bin") / "python"
        print(f"Installing dependencies from {req_file}...")
        print(f"Ensuring pip is installed in {venv_path}...")
        subprocess.check_call([str(python_exec), "-m", "ensurepip", "--default-pip"])
        subprocess.check_call([str(python_exec), "-m", "pip", "install", "-r", str(req_file)])

    def activate_venv(self, filepath: StrOrFilePath):
        venv_path = Path(filepath)
        if not venv_path.exists():
            print(f"Virtual environment not found at {venv_path}")
            self.create(filepath)

        if os.name == "nt":  # Windows
            activate_script = venv_path / "Scripts" / "activate"
            command = f'cmd.exe /K "{activate_script}"'  # Opens a new shell with venv activated
        else:  # macOS/Linux
            activate_script = venv_path / "bin" / "activate"
            command = f'bash --rcfile <(echo "source {activate_script}") -i'

        if not activate_script.exists():
            raise FileNotFoundError(f"Activation script not found at {activate_script}")
    
        print(f"Activating virtual environment at: {venv_path}")
        subprocess.run(command, shell=True, executable="/bin/bash" if os.name != "nt" else None)

    
    

builder = ExtendedEnvBuilder()
builder.install_reqs("./myenv")