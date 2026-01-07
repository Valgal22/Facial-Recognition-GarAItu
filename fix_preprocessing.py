import json
import os

nb_path = r"c:\Users\ikerb\OneDrive\Escritorio\MU\3-Maila\ArtificialInteligence\Jupyter\proyecto_faces\app.ipynb"

print(f"Reading {nb_path}...")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# The new preprocessing lines to insert
new_preprocess_code = [
    "def preprocess_image(image):\n",
    "    \"\"\"\n",
    "    Ajusta esto según cómo fue entrenado tu modelo\n",
    "    \"\"\"\n",
    "    # 1. Convertir a RGB (OpenCV carga en BGR)\n",
    "    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)\n",
    "    \n",
    "    # 2. Resize igual que en training\n",
    "    image = cv2.resize(image, (224, 224))\n",
    "    \n",
    "    # 3. Normalización ImageNet\n",
    "    image = image.astype(np.float32) / 255.0\n",
    "    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)\n",
    "    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)\n",
    "    image = (image - mean) / std\n",
    "    \n",
    "    # 4. Transponer a CHW y añadir Batch dim\n",
    "    image = np.transpose(image, (2, 0, 1))\n",
    "    image = np.expand_dims(image, axis=0)\n",
    "    return image.astype(np.float32)\n"
]

modified = False

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = cell["source"]
        # Find start and end of the preprocess_image function
        start_idx = -1
        end_idx = -1
        
        for i, line in enumerate(source):
            if "def preprocess_image(image):" in line:
                start_idx = i
            # Find the return line to end replacement (assuming simple structure)
            if start_idx != -1 and "return image" in line and i > start_idx:
                end_idx = i
                break
        
        if start_idx != -1 and end_idx != -1:
            print(f"Found preprocess_image from line {start_idx} to {end_idx}")
            # Replace the lines
            cell["source"] = source[:start_idx] + new_preprocess_code + source[end_idx+1:]
            modified = True
            break

if modified:
    print("Saving patched notebook...")
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("SUCCESS: app.ipynb patched with correct preprocessing.")
else:
    print("WARNING: Could not find 'def preprocess_image' block to replace.")
