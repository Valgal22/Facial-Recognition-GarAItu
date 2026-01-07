import json
import os

nb_path = r"c:\Users\ikerb\OneDrive\Escritorio\MU\3-Maila\ArtificialInteligence\Jupyter\proyecto_faces\app.ipynb"

print(f"Reading {nb_path}...")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

modified = False

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        new_source = []
        for line in cell["source"]:
            if "cv2.resize" in line and "(640, 640)" in line:
                print(f"Found wrong dimensions: {line.strip()}")
                line = line.replace("(640, 640)", "(224, 224)")
                print(f"Replaced with:        {line.strip()}")
                modified = True
            new_source.append(line)
        cell["source"] = new_source

if modified:
    print("Saving patched notebook...")
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("SUCCESS: app.ipynb patched to use (224, 224).")
else:
    print("WARNING: Target line was not found. It might have been already changed.")
