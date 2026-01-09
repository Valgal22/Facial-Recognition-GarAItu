import base64
import cv2
import numpy as np

def decode_image_from_request(req):
    """
    Soporta:
      - multipart/form-data: field 'file'
      - JSON: {"image_b64": "..."}
    Devuelve imagen BGR o None
    """
    image = None

    # Support 'file' (standard) or 'image' (Node-RED/User)
    print("DEBUG: decode_image_from_request entered")
    print(f"DEBUG: req.files keys: {list(req.files.keys())}")
    
    file_storage = req.files.get('file') or req.files.get('image')

    if file_storage:
        print("DEBUG: Found file_storage, reading...")
        data = file_storage.read()
        print(f"DEBUG: Read {len(data)} bytes")
        nparr = np.frombuffer(data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        print(f"DEBUG: Decoded image shape: {image.shape if image is not None else 'None'}")

    else:
        js = req.get_json(silent=True) or {}
        b64 = js.get("image_b64", "")
        if b64:
            if b64.startswith("data:image"):
                _, b64 = b64.split(",", 1)
            data = base64.b64decode(b64)
            nparr = np.frombuffer(data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    return image
