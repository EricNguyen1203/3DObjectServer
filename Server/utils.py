import io
import os
import zipfile
import aiofiles


async def create_zip(folder_root_path: str, files: list[str]) -> io.BytesIO:
    if not check_files(folder_root_path):
        return None
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename in files:
            file_path = os.path.join(folder_root_path, filename)
            if os.path.exists(file_path):
                async with aiofiles.open(file_path, "rb") as f:
                    file_data = await f.read()
                    zip_file.writestr(filename, file_data)

    zip_buffer.seek(0)
    return zip_buffer


def check_files(folder_path):
    if not os.path.isdir(folder_path):
        print("Folder does not exist.")
        return False

    required_files = {"mesh.obj", "texture.png", "texture.mtl"}
    existing_files = set(os.listdir(folder_path))

    missing_files = required_files - existing_files
    if not missing_files:
        print("All required files are present.")
        return True
    else:
        print("Missing files:", ", ".join(missing_files))
        return False
