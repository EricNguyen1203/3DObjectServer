import requests

# print(requests.get("http://127.0.0.1:8000/").json())

prompt = "a rainy sky"
# response = requests.post("http://127.0.0.1:8000/create-model3D", json={"prompt": prompt})
response = requests.post("http://127.0.0.1:8000/get-model3D-bytes", json={"prompt": prompt})
# response = requests.post("http://13.236.5.12/get-model3D-bytes", json={"prompt": prompt})

response.raise_for_status()

if response.status_code != 204:
    print(response.json())
    image = response.json()["texture"].encode("latin1")
    with open("texture.png", "wb") as file:
        file.write(image)
else:
    print("No response")