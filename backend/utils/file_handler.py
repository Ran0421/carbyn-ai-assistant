import os
import shutil

UPLOAD_DIR = "temp_uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_uploaded_file(upload_file):

    file_path = os.path.join(
        UPLOAD_DIR,
        upload_file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path