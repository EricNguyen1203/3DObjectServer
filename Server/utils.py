import io
import os
import zipfile
import aiofiles


async def create_zip(folder_root_path: str, files: list[str]) -> io.BytesIO:
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
