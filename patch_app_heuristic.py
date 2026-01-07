import json
import os

nb_path = r"c:\Users\ikerb\OneDrive\Escritorio\MU\3-Maila\ArtificialInteligence\Jupyter\proyecto_faces\app.ipynb"

print(f"Reading {nb_path}...")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# The replacement block (logic to expand box)
# We target the block we inserted previously
new_vis_logic = [
    "        # Desnormalizar\n",
    "        x_px = int(x * w_img)\n",
    "        y_px = int(y * h_img)\n",
    "        w_px = int(w * w_img)\n",
    "        h_px = int(h * h_img)\n",
    "        \n",
    "        # --- HEURISTIC: EXPAND BOX 20% ---\n",
    "        margin_w = int(w_px * 0.2)\n",
    "        margin_h = int(h_px * 0.2)\n",
    "        \n",
    "        x_px = max(0, x_px - margin_w // 2)\n",
    "        y_px = max(0, y_px - margin_h // 2)\n",
    "        w_px = min(w_img - x_px, w_px + margin_w)\n",
    "        h_px = min(h_img - y_px, h_px + margin_h)\n",
    "        # ---------------------------------\n",
    "        \n",
    "        # Dibujar rectangulo (BGR para OpenCV)\n",
    "        cv2.rectangle(image, (x_px, y_px), (x_px+w_px, y_px+h_px), (0, 0, 255), 2)\n"
]

modified = False

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = cell["source"]
        
        # We need to find where "x_px = int(x * w_img)" starts and where "cv2.rectangle" is
        start_idx = -1
        end_idx = -1
        
        for i, line in enumerate(source):
            if "x_px = int(x * w_img)" in line:
                start_idx = i
            if "cv2.rectangle(image" in line and start_idx != -1 and i > start_idx:
                end_idx = i
                break
        
        if start_idx != -1 and end_idx != -1:
            print(f"Expanding box logic from line {start_idx} to {end_idx}")
            # Replace lines [start_idx ... end_idx] (inclusive) with new logic
            # Note: end_idx in list slice is checking for the replacement of the rectangle call too
            # Actually, my new_vis_logic includes the rectangle call at the end.
            # So I should replace up to end_idx + 1 (exclusive) if I want to replace the rectangle line too.
            cell["source"] = source[:start_idx] + new_vis_logic + source[end_idx+1:]
            modified = True
            break

if modified:
    print("Saving patched notebook...")
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("SUCCESS: app.ipynb patched with expanded bounding box.")
else:
    print("WARNING: Could not find code block to replace.")
