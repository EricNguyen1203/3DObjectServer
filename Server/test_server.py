import requests
import base64

# print(requests.get("http://127.0.0.1:8000/").json())

prompt = "a red doll"
# response = requests.post("http://127.0.0.1:8000/create-model3D", json={"prompt": prompt})
response = requests.post("http://127.0.0.1:8000/get-model3D-bytes", json={"prompt": prompt})
# response = requests.post("http://3.27.152.131/get-model3D-bytes", json={"prompt": prompt})
# response = requests.get("http://3.27.152.131/")

# print(response.json())


response.raise_for_status()

print (response.status_code)
if response.status_code != 204:
    print(response.json())
    image = base64.b64decode(response.json()["texture"]) 
    with open("texture.png", "wb") as file:
        file.write(image)
else:
    print("No response")