from concurrent.futures import ThreadPoolExecutor
from cloudinary.uploader import upload


def image_upload(file, file_name):
    pool = ThreadPoolExecutor(4)
    pool.submit(set_image_upload, file, file_name)


def set_image_upload(file, file_name: str):
    try:
        return upload(file, public_id=file_name)

    except:
        return None
