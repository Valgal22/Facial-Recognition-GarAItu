import numpy as np
from uniface import RetinaFace, ArcFace
from services.face_selection import select_primary_face

# ⚠️ Inicialización GLOBAL
detector = RetinaFace()
recognizer = ArcFace()

def recognize_primary_face(image):
    # --- OPTIMIZATION: Resize if too big ---
    # RetinaFace on CPU is slow on large images. 
    # Resizing to max 640px speeds it up significantly (~5x-10x).
    # --- OPTIMIZATION: Resize if too big ---
    # RetinaFace on CPU is slow on large images. 
    # Resizing to max 640px speeds it up significantly (~5x-10x).
    h, w = image.shape[:2]
    max_dim = 640
    scale = 1.0

    if max(h, w) > max_dim:
        import cv2
        scale = max_dim / float(max(h, w))
        new_w, new_h = int(w * scale), int(h * scale)
        image = cv2.resize(image, (new_w, new_h))

    try:
        faces = detector.detect(image)
        # Note: BBox and Landmarks are now in resized coordinates.
        # Since we use the same 'image' variable for ArcFace below, 
        # it is consistent. We don't need to scale back unless 
        # we wanted to return coordinates relative to original upload.
        # For embeddings, this is fine.
    except Exception as e:
        return None, f"detector_error: {str(e)}"

    if not faces:
        return None, "no_faces"

    primary = select_primary_face(faces, image.shape)
    if primary is None:
        return None, "selection_failed"

    if primary.get("landmarks") is None:
        return None, "no_landmarks"

    landmarks = np.asarray(primary["landmarks"], dtype=np.float32)

    try:
        embedding = recognizer.get_normalized_embedding(
            image,
            landmarks
        )
    except Exception as e:
        return None, f"arcface_error: {str(e)}"

    embedding = embedding.astype(np.float32)

    return {
        "embedding": embedding.flatten().tolist(),
        "primary_face": {
            "bbox": primary["bbox"],
            "detector_confidence": float(primary["confidence"]),
            "primary_score": float(primary["primary_score"])
        }
    }, None
