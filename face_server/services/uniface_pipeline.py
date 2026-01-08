import numpy as np
from uniface import RetinaFace, ArcFace
from services.face_selection import select_primary_face

detector = RetinaFace()
recognizer = ArcFace()

def recognize_primary_face(image):
    faces = detector.detect(image)
    if not faces:
        return None, "no_faces"

    primary = select_primary_face(faces, image.shape)
    if primary is None:
        return None, "selection_failed"

    landmarks = np.array(primary["landmarks"])

    embedding = recognizer.get_normalized_embedding(
        image,
        landmarks
    )

    return {
        "embedding": embedding.flatten().tolist(),
        "primary_face": {
            "bbox": primary["bbox"],
            "detector_confidence": primary["confidence"],
            "primary_score": primary["primary_score"]
        }
    }, None
