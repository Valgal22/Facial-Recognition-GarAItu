import onnxruntime as ort
import numpy as np
import cv2

class ONNXFaceDetector:
    def __init__(self, model_path):
        self.session = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name
        self.output_names = [o.name for o in self.session.get_outputs()]

    def preprocess(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        h, w, _ = image.shape

        target = 224
        scale = min(target / w, target / h)
        nw, nh = int(w * scale), int(h * scale)

        resized = cv2.resize(image, (nw, nh))
        canvas = np.full((target, target, 3), 128, dtype=np.uint8)

        dx, dy = (target - nw) // 2, (target - nh) // 2
        canvas[dy:dy+nh, dx:dx+nw] = resized

        x = canvas.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        std  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        x = (x - mean) / std

        x = np.transpose(x, (2, 0, 1))
        x = np.expand_dims(x, 0)
        return x, (scale, dx, dy)

    def detect(self, image, thresh=0.5):
        x, (scale, dx, dy) = self.preprocess(image)
        out = self.session.run(
            self.output_names,
            {self.input_name: x}
        )

        score = float(out[0][0][0])
        bbox  = out[1][0]  # cx,cy,w,h normalized

        if score < thresh:
            return None

        t = 224
        cx, cy, bw, bh = bbox
        cx, cy, bw, bh = cx*t, cy*t, bw*t, bh*t

        x1 = int((cx - bw/2 - dx) / scale)
        y1 = int((cy - bh/2 - dy) / scale)
        x2 = int((cx + bw/2 - dx) / scale)
        y2 = int((cy + bh/2 - dy) / scale)

        h, w, _ = image.shape
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)

        return {
            "bbox": [x1, y1, x2, y2],
            "score": score
        }
