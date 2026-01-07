import json
import os

nb_path = r"c:\Users\ikerb\OneDrive\Escritorio\MU\3-Maila\ArtificialInteligence\Jupyter\proyecto_faces\app.ipynb"

print(f"Reading {nb_path}...")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# New preprocessing with Letterbox
# Note: We need to return the 'scale', 'dx', 'dy' so we can des-letterbox the bbox later?
# Wait, the model outputs 0-1 relative to the 224x224 canvas.
# So if we just feed the letterboxed image, the model predicts the box on the canvas.
# We then need to map that back to the original image in the 'detect' function.
# This makes it complicated because 'detect' needs 'dx', 'dy', 'scale'.
#
# SIMPLIFICATION:
# For now, let's just make sure the INPUT to the model is correct (Letterbox).
# The current 'detect' function des-normalizes based on 224x224? No, it des-normalizes based on Original Image size.
# BUT, the model output (0-1) is relative to the 224x224 *padded* image.
# So x=0.5 is center of canvas.
# If we naively multiply x * w_org, it will be wrong because of the padding.
#
# To do this correctly, we need to invert the letterbox transform on the bbox.
#
# Let's update 'preprocess_image' to return just the tensor (as before),
# BUT we also need to update 'detect' logic to handle the bbox conversion.
#
# Ideally, we should unify this. But 'preprocess_image' returns a tensor.
#
# Let's change 'preprocess_image' to return (tensor, meta_info).
# AND update 'detect' to use meta_info.

new_preprocess_code = [
    "def preprocess_image(image):\n",
    "    # 1. RGB\n",
    "    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)\n",
    "    h, w, _ = image.shape\n",
    "    \n",
    "    # 2. Letterbox\n",
    "    target_size = 224\n",
    "    scale = min(target_size / w, target_size / h)\n",
    "    nw = int(w * scale)\n",
    "    nh = int(h * scale)\n",
    "    image_resized = cv2.resize(image, (nw, nh))\n",
    "    \n",
    "    new_image = np.full((target_size, target_size, 3), 128, dtype=np.uint8)\n",
    "    dx = (target_size - nw) // 2\n",
    "    dy = (target_size - nh) // 2\n",
    "    new_image[dy:dy+nh, dx:dx+nw] = image_resized\n",
    "    \n",
    "    # 3. Normalize\n",
    "    new_image = new_image.astype(np.float32) / 255.0\n",
    "    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)\n",
    "    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)\n",
    "    new_image = (new_image - mean) / std\n",
    "    \n",
    "    # 4. Transpose\n",
    "    new_image = np.transpose(new_image, (2, 0, 1))\n",
    "    new_image = np.expand_dims(new_image, axis=0)\n",
    "    \n",
    "    return new_image.astype(np.float32), (scale, dx, dy)\n"
]

# We need to update the call site in 'detect' too
# input_tensor, meta = preprocess_image(image)
# scale, dx, dy = meta
# ...
# And the bbox mapping:
# x_on_canvas = output_x * 224
# x_on_start = x_on_canvas - dx
# x_original = x_on_start / scale
# (and same for y, w, h)

# Replacement for 'detect' function logic
new_detect_logic = [
    "    # --- Preprocessing ---\n",
    "    input_tensor, (scale, dx, dy) = preprocess_image(image)\n",
    "\n",
    "    # --- Inference ---\n",
    "    outputs = session.run(\n",
    "        output_names,\n",
    "        {input_name: input_tensor}\n",
    "    )\n",
    "\n",
    "    # --- Postprocessing ---\n",
    "    score = outputs[0][0][0]\n",
    "    bbox = outputs[1][0] # [x, y, w, h] normalized to 224x224 canvas\n",
    "    \n",
    "    detections = [float(score)]\n",
    "    box_coords = []\n",
    "\n",
    "    if score > 0.5:\n",
    "        t_size = 224\n",
    "        x_c, y_c, w_c, h_c = bbox # coords on canvas (0-1)\n",
    "        \n",
    "        # 1. Denormalize to canvas pixels\n",
    "        x_px_c = x_c * t_size\n",
    "        y_px_c = y_c * t_size\n",
    "        w_px_c = w_c * t_size\n",
    "        h_px_c = h_c * t_size\n",
    "        \n",
    "        # 2. Remove padding (dx, dy)\n",
    "        x_no_pad = x_px_c - dx\n",
    "        y_no_pad = y_px_c - dy\n",
    "        \n",
    "        # 3. Rescale to original size\n",
    "        x_final = int(x_no_pad / scale)\n",
    "        y_final = int(y_no_pad / scale)\n",
    "        w_final = int(w_px_c / scale)\n",
    "        h_final = int(h_px_c / scale)\n",
    "        \n",
    "        # --- HEURISTIC: EXPAND BOX 20% ---\n",
    "        margin_w = int(w_final * 0.2)\n",
    "        margin_h = int(h_final * 0.2)\n",
    "        \n",
    "        x_final = max(0, x_final - margin_w // 2)\n",
    "        y_final = max(0, y_final - margin_h // 2)\n",
    "        h_img, w_img, _ = image.shape\n",
    "        w_final = min(w_img - x_final, w_final + margin_w)\n",
    "        h_final = min(h_img - y_final, h_final + margin_h)\n",
    "        # ---------------------------------\n",
    "\n",
    "        cv2.rectangle(image, (x_final, y_final), (x_final+w_final, y_final+h_final), (0, 0, 255), 2)\n",
    "        cv2.putText(image, f\"{score:.2f}\", (x_final, y_final-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)\n",
    "        \n",
    "        box_coords = [x_final, y_final, w_final, h_final]\n",
    "        \n",
    "    cv2.imwrite(\"detected.jpg\", image)\n",
    "\n",
    "    return jsonify({\n",
    "        \"detections\": detections,\n",
    "        \"box\": box_coords\n",
    "    })\n"
]


modified = False

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = cell["source"]
        source_str = "".join(source)
        
        # 1. Replace preprocess_image
        if "def preprocess_image(image):" in source_str:
            print("Replacing preprocess_image...")
            # Naive replace: find start and end
            start_idx = -1
            end_idx = -1
            for i, line in enumerate(source):
                if "def preprocess_image(image):" in line:
                    start_idx = i
                if "return" in line and start_idx != -1 and i > start_idx:
                    end_idx = i
                    break
            
            if start_idx != -1 and end_idx != -1:
                cell["source"] = source[:start_idx] + new_preprocess_code + source[end_idx+1:]
                modified = True
        
        # 2. Replace detect function body (basically all of it)
        # We look for "@app.route" and then replace the function body
        if "@app.route(\"/detect\"" in source_str:
             print("Replacing detect function logic...")
             # We want to keep the headers:
             # @app.route...
             # def detect():
             #    if "image" not in request.files: ...
             #    ...
             #    image = cv2.imdecode(...)
             #
             # We replace starting from 'input_tensor = ...'
             
             start_idx = -1
             end_idx = -1
             
             for i, line in enumerate(cell["source"]): # Use revised source if preproc was in same cell? unlikely
                if "input_tensor = preprocess_image(image)" in line or "input_tensor =" in line: # Be robust
                    start_idx = i
                if "return jsonify({" in line and start_idx != -1 and i > start_idx:
                    for j in range(i, len(cell["source"])):
                        if "})" in cell["source"][j]:
                            end_idx = j
                            break
                    break
             
             if start_idx != -1 and end_idx != -1:
                 cell["source"] = cell["source"][:start_idx] + new_detect_logic + cell["source"][end_idx+1:]
                 modified = True

if modified:
    print("Saving patched notebook...")
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("SUCCESS: app.ipynb patched with Letterbox support.")
else:
    print("WARNING: Could not find blocks to replace.")
