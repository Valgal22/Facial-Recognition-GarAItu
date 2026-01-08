import math

W_SIZE   = 0.7
W_CENTER = 0.3
GAMMA    = 1.5

def _extract(face):
    if isinstance(face, dict):
        return (
            face.get("bbox"),
            face.get("confidence", 1.0),
            face.get("landmarks")
        )
    return (
        face.bbox,
        getattr(face, "confidence", 1.0),
        face.landmarks
    )

def select_primary_face(faces, image_shape):
    H, W = image_shape[:2]
    diag_half = math.sqrt(W*W + H*H) / 2.0

    best = None
    best_score = -1.0

    for f in faces:
        bbox, conf, landmarks = _extract(f)
        if bbox is None or landmarks is None:
            continue

        x1, y1, x2, y2 = bbox
        bw, bh = max(0, x2-x1), max(0, y2-y1)

        size_norm = (bw * bh) / float(W * H)

        cx, cy = x1 + bw/2.0, y1 + bh/2.0
        d = math.sqrt((cx - W/2)**2 + (cy - H/2)**2)
        d_norm = min(1.0, d / diag_half)

        center_score = 1.0 - (d_norm ** GAMMA)
        score = (W_SIZE * size_norm + W_CENTER * center_score) * conf

        if score > best_score:
            best_score = score
            best = {
                "bbox": [float(x1), float(y1), float(x2), float(y2)],
                "confidence": float(conf),
                "landmarks": landmarks,
                "primary_score": float(score)
            }

    return best
