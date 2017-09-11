from concurrent.futures import ThreadPoolExecutor
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url


def image_upload(file, file_name=None):
    pool = ThreadPoolExecutor(4)
    pool.submit(set_image_upload, file, file_name)


def set_image_upload(file, file_name=None):
    try:
        return upload(file, public_id=file_name)

    except:
        return None


def get_url(public_id, sizes):
    url, _ = cloudinary_url(
            public_id,
            format="png",
            width=sizes.get('width'),
            height=sizes.get('height'),
            crop='fill',
            secure=True)
    return url
