from flask import Flask, request, jsonify

# --- Servicios internos ---
from services.image_io import decode_image_from_request
from services.onnx_detector import ONNXFaceDetector
from services.uniface_pipeline import recognize_primary_face

# ----------------------------------------------------
# Inicialización Flask
# ----------------------------------------------------
app = Flask(__name__)

# ----------------------------------------------------
# Inicialización modelos (UNA SOLA VEZ)
# ----------------------------------------------------
onnx_detector = ONNXFaceDetector(
    model_path="models/face_detector.onnx"
)

# ----------------------------------------------------
# Healthcheck
# ----------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify(status="ok"), 200


# ----------------------------------------------------
# /detect
# SOLO detección rápida (ONNX)
# ----------------------------------------------------
@app.route("/detect", methods=["POST"])
def detect():
    """
    Detección rápida con modelo ONNX.
    NO reconocimiento.
    """
    image = decode_image_from_request(request)
    if image is None:
        return jsonify(error="No image received"), 400

    result = onnx_detector.detect(image, thresh=0.5)

    if result is None:
        return jsonify(
            detected=False,
            reason="no_face_detected"
        ), 200

    return jsonify(
        detected=True,
        score=result["score"],
        bbox=result["bbox"]  # [x1, y1, x2, y2]
    ), 200


# ----------------------------------------------------
# /recognize
# Detecta TODAS → selecciona UNA → ArcFace
# Devuelve el embedding de la cara principal.
# ----------------------------------------------------
@app.route("/recognize", methods=["POST"])
def recognize():
    """
    Pipeline:
    1. Decode Image
    2. ONNX Detect (Early Exit)
    3. RetinaFace (Precise Detect)
    4. Select Primary Face (Largest/Central)
    5. ArcFace -> Embedding
    """
    image = decode_image_from_request(request)
    if image is None:
        return jsonify(error="No image received"), 400

    # --- Pipeline UniFace correcto ---
    result, error = recognize_primary_face(image)

    if error:
        return jsonify(
            recognized=False,
            reason=error
        ), 200

    return jsonify(
        recognized=True,
        # Devolvemos el embedding (lista de floats) para que el servidor REST compare
        embedding=result["embedding"],       
        primary_face=result["primary_face"]
    ), 200


# ----------------------------------------------------
# Main
# ----------------------------------------------------
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
