import json
import random

nb_path = r"c:\Users\ikerb\OneDrive\Escritorio\MU\3-Maila\ArtificialInteligence\Jupyter\proyecto_faces\preprocess_and_train.ipynb"

print(f"Reading {nb_path}...")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# ---------------------------------------------------------
# 1. NEW FaceDataset CODE (Letterbox + Augmentation)
# ---------------------------------------------------------
new_dataset_class = [
    "class FaceDataset(Dataset):\n",
    "    def __init__(self, dataframe, transform=None, phase='train'):\n",
    "        self.data = dataframe.reset_index(drop=True)\n",
    "        self.transform = transform\n",
    "        self.phase = phase\n",
    "\n",
    "    def __len__(self):\n",
    "        return len(self.data)\n",
    "\n",
    "    def __getitem__(self, idx):\n",
    "        row = self.data.iloc[idx]\n",
    "        img_path = row['path']\n",
    "        \n",
    "        image = cv2.imread(img_path)\n",
    "        if image is None:\n",
    "            return self.__getitem__((idx + 1) % len(self))\n",
    "        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)\n",
    "        \n",
    "        h_org, w_org, _ = image.shape\n",
    "        has_face = float(row['has_face'])\n",
    "        x, y, w_box, h_box = float(row['x']), float(row['y']), float(row['w']), float(row['h'])\n",
    "        \n",
    "        # --- DATA AUGMENTATION (Train only) ---\n",
    "        if self.phase == 'train' and has_face == 1.0:\n",
    "            # Horizontal Flip\n",
    "            if random.random() > 0.5:\n",
    "                image = cv2.flip(image, 1)\n",
    "                x = w_org - x - w_box\n",
    "        \n",
    "        # --- LETTERBOX RESIZE ---\n",
    "        target_size = 224\n",
    "        scale = min(target_size / w_org, target_size / h_org)\n",
    "        nw = int(w_org * scale)\n",
    "        nh = int(h_org * scale)\n",
    "        \n",
    "        image_resized = cv2.resize(image, (nw, nh))\n",
    "        \n",
    "        # Paste into center of 224x224 gray image\n",
    "        new_image = np.full((target_size, target_size, 3), 128, dtype=np.uint8)\n",
    "        dx = (target_size - nw) // 2\n",
    "        dy = (target_size - nh) // 2\n",
    "        new_image[dy:dy+nh, dx:dx+nw] = image_resized\n",
    "        \n",
    "        # Update labels\n",
    "        if has_face == 1:\n",
    "            x = x * scale + dx\n",
    "            y = y * scale + dy\n",
    "            w_box = w_box * scale\n",
    "            h_box = h_box * scale\n",
    "            \n",
    "            # Normalize to 0-1 relative to 224x224\n",
    "            x /= target_size\n",
    "            y /= target_size\n",
    "            w_box /= target_size\n",
    "            h_box /= target_size\n",
    "        else:\n",
    "            x, y, w_box, h_box = 0.0, 0.0, 0.0, 0.0\n",
    "            \n",
    "        if self.transform:\n",
    "            new_image = self.transform(new_image)\n",
    "            \n",
    "        return new_image, torch.tensor([has_face], dtype=torch.float32), torch.tensor([x, y, w_box, h_box], dtype=torch.float32)\n"
]

# ---------------------------------------------------------
# 2. APPLY PATCHES
# ---------------------------------------------------------
modified_dataset = False
modified_loader_init = False

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = cell["source"]
        
        # Patch FaceDataset class
        if "class FaceDataset(Dataset):" in "".join(source):
            print("Found FaceDataset definition. Replacing...")
            # We want to keep FaceDetector part if it's in the same cell
            # In original file, FaceDataset ends before FaceDetector starts
            new_source = []
            skipping = False
            inserted = False
            
            for line in source:
                if "class FaceDataset(Dataset):" in line:
                    skipping = True
                    if not inserted:
                        new_source.extend(new_dataset_class)
                        inserted = True
                
                # Check for start of next class or end of FaceDataset
                if skipping and ("class FaceDetector" in line or "# --- MODELO ---" in line):
                    skipping = False
                
                if not skipping:
                    new_source.append(line)
            
            cell["source"] = new_source
            modified_dataset = True
            
        # Patch Train/Val Dataset instantiation to add phase='...'
        # Look for "train_ds = FaceDataset"
        if "train_ds = FaceDataset" in "".join(source):
            print("Found Dataset instantiation. updating to include phase...")
            new_source = []
            for line in source:
                if "train_ds = FaceDataset" in line:
                    line = line.replace("transform=transform)", "transform=transform, phase='train')")
                if "val_ds = FaceDataset" in line:
                    line = line.replace("transform=transform)", "transform=transform, phase='val')")
                new_source.append(line)
            cell["source"] = new_source
            modified_loader_init = True
            
        # Also need to import random for augmentation
        if "import cv2" in "".join(source):
            if "import random" not in "".join(source):
                 cell["source"] = ["import random\n"] + cell["source"]


if modified_dataset and modified_loader_init:
    print("Saving patched notebook...")
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=1)
    print("SUCCESS: preprocess_and_train.ipynb patched with Letterbox and Augmentation.")
else:
    print(f"WARNING: Patch incomplete. Dataset:{modified_dataset}, Loader:{modified_loader_init}")
