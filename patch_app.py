import json
import os

nb_path = r"c:\Users\ikerb\OneDrive\Escritorio\MU\3-Maila\ArtificialInteligence\Jupyter\proyecto_faces\app.ipynb"

print(f"Reading {nb_path}...")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

modified = False

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        # 1. Update app.run to disable debug
        new_source = []
        for line in cell["source"]:
            if "app.run" in line and "debug=True" in line:
                print("Found app.run with debug=True. Disabling debug...")
                # Reformatted line safe for notebook
                line = '    app.run(host="0.0.0.0", port=5000, debug=False)\n'
                modified = True
            new_source.append(line)
        cell["source"] = new_source
        
        # 2. Check for the client request code and replace it
        source_text = "".join(cell["source"])
        if "requests.post" in source_text and "http://localhost:5000/detect" in source_text:
            print("Found client test cell. Clearing content...")
            cell["source"] = [
                "# El código de prueba se ha movido a test_api.py\n",
                "# Esto evita que el notebook se bloquee al ejecutar el servidor.\n",
                "# 1. Ejecuta la celda superior para iniciar el servidor.\n",
                "# 2. Abre una terminal y ejecuta: python test_api.py\n"
            ]
            cell["outputs"] = [] # Clear previous errors
            modified = True

if modified:
    print("Saving patched notebook...")
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("SUCCESS: app.ipynb patched.")
else:
    print("WARNING: No changes made. Maybe already patched?")
