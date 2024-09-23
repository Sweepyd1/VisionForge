import base64
from typing import Optional


def is_base64_image(base64_string: str) -> Optional[bytes]:
    try:
        img_data = base64.b64decode(base64_string)
        return img_data
    except:
        return None

