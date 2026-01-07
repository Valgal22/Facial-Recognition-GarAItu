import json
import os

nb_path = r"c:\Users\ikerb\OneDrive\Escritorio\MU\3-Maila\ArtificialInteligence\Jupyter\proyecto_faces\app.ipynb"

print(f"Reading {nb_path}...")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# The new detection logic
new_detect_code = [
    "    input_tensor = preprocess_image(image)\n",
    "\n",
    "    outputs = session.run(\n",
    "        output_names,\n",
    "        {input_name: input_tensor}\n",
    "    )\n",
    "\n",
    "    # --- VISUALIZACIÓN ---\n",
    "    score = outputs[0][0][0]\n",
    "    bbox = outputs[1][0] # [x, y, w, h] normalizado\n",
    "    \n",
    "    detections = [float(score)]\n",
    "    box_coords = []\n",
    "\n",
    "    if score > 0.5:\n",
    "        h_img, w_img, _ = image.shape\n",
    "        x, y, w, h = bbox\n",
    "        \n",
    "        # Desnormalizar\n",
    "        x_px = int(x * w_img)\n",
    "        y_px = int(y * h_img)\n",
    "        w_px = int(w * w_img)\n",
    "        h_px = int(h * h_img)\n",
    "        \n",
    "        # Dibujar rectangulo (BGR para OpenCV)\n",
    "        cv2.rectangle(image, (x_px, y_px), (x_px+w_px, y_px+h_px), (0, 0, 255), 2)\n",
    "        cv2.putText(image, f\"{score:.2f}\", (x_px, y_px-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)\n",
    "        \n",
    "        box_coords = [x_px, y_px, w_px, h_px]\n",
    "        \n",
    "    # Guardar imagen resultante\n",
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
        
        # We look for the block inside def detect(): that calls session.run
        # and replace everything after it until return jsonify
        
        start_idx = -1
        end_idx = -1
        
        for i, line in enumerate(source):
            if "input_tensor = preprocess_image(image)" in line:
                start_idx = i
            if "return jsonify({" in line and start_idx != -1 and i > start_idx:
                # We want to replace the whole return block too to add 'box'
                # Find the closing brace of return jsonify
                for j in range(i, len(source)):
                    if "})" in source[j]:
                        end_idx = j
                        break
                break
        
        if start_idx != -1 and end_idx != -1:
            print(f"Replacing code block from line {start_idx} to {end_idx}")
            cell["source"] = source[:start_idx] + new_detect_code + source[end_idx+1:]
            modified = True
            break

if modified:
    print("Saving patched notebook...")
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("SUCCESS: app.ipynb patched with visualization logic.")
else:
    print("WARNING: Could not find code block to replace.")
