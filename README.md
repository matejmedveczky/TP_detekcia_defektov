# YOLO - Detekcia a Klasifikácia Defektov

## Štruktúra dát

Dáta a modely v tomto priečinku sú organizované nasledovne:

- **`datasets/`** - Spracované a pripravené datasety pre trénovanie (napr. štruktúra pre klasifikáciu: `datasets/TP26/train/trieda/`).
- **`TP26_*/`** (napr. `TP26_detection_v2-1`, `TP26_plastic_v1-1`, `TP26_depthmap_detection`) - Datasety stiahnuté z Roboflow vo formáte YOLO (obsahujú `train/`, `valid/`, `test/` zložky a `data.yaml`).
- **`runs/`** - Výstupy z trénovania a vyhodnocovania modelov. Obsahuje váhy modelov (`*.pt`), grafy a výsledky:
  - `runs/detect/` - Výstupy pre detekciu objektov.
  - `runs/classify/` - Výstupy pre klasifikáciu.

---

## Popis súborov (`.ipynb`)

### 1. Sťahovanie datasetov
- **`yolo_dataset_download.ipynb`** / **`yolo_dataset_v2_download.ipynb`** / **`YOLO_dataset_plastic_download.ipynb`**
  - Obsahujú kód na stiahnutie príslušných datasetov z Roboflow prostredníctvom API.

### 2. Príprava a Trénovanie Detekcie
- **`YOLO_TP_dataset_v2.ipynb`**, **`YOLO_TP_dataset_plastic.ipynb`**, **`YOLO_TP_dataset_depthmap.ipynb`**
  - Notebooky zamerané na základné trénovanie detekčných modelov s ohľadom na rôzne typy datasetov (kovový, plasty, hĺbkové mapy).
- **`YOLO_TP_detekcia_metal.ipynb`**, **`YOLO_TP_detekcia_plastic.ipynb`**
  - Obsahujú plný cyklus pre prácu s detekciou na konkrétnom type podložky. Zahŕňajú **trénovanie modelov** (napr. `yolo11s` a `yolo11n`) so špecifickými hyperparametrami a datasetmi (`TP26_detection_v2-3` / `TP26_plastic_v1-3`), ako aj následnú inferenciu a evaluáciu na testovacích sadách.

### 3. Klasifikácia
- **`YOLO_TP_klasifikacia.ipynb`**
  - Konvertuje detekčný formát (všetky obrázky v jednom priečinku) do klasifikačného (obrázky rozdelené do zložiek podľa tried). 
  - Následne trénuje a testuje YOLOv11 klasifikačný model (`yolo11n-cls.pt`).

### 4. Testovanie a Prídavné experimenty
- **`YOLO_test.ipynb`**
  - Všeobecné experimenty a testovanie modelov zbežným spôsobom.

---

## Základné ukážky kódov

### 1. Trénovanie detekčného modelu
Tento kód načíta predtrénovaný model a spustí trénovanie na datasete definovanom v `data.yaml`.
```python
from ultralytics import YOLO

# Načítanie základného modelu
model = YOLO('yolo11n.pt') 

# Spustenie trénovania
results = model.train(
    data='TP26_detection_v2-1/data.yaml', 
    epochs=50, 
    imgsz=640,
    project='detectTP',
    name='train_v2'
)
```

### 2. Trénovanie klasifikačného modelu
Pri klasifikácii si model vyžaduje, aby bola cesta nasmerovaná priamo na priečinok so štruktúrou rozčlenenou podľa tried.
```python
from ultralytics import YOLO

# Načítanie klasifikačného modelu
model = YOLO("yolo11n-cls.pt", task="classify")

# Trénovanie
results = model.train(
    data="datasets/TP26", # Priečinok musí obsahovať zložky ako train/bad1, train/good atď.
    epochs=10,
    imgsz=224,
    project="classifyTP",
    name="train"
)
```

### 3. Predikcia a vyhodnotenie (Inferencia)
Ako použiť už natrénovaný model (`best.pt`) na predikciu pre konkrétny obrázok.
```python
from ultralytics import YOLO

# Načítanie nášho natrénovaného modelu
model = YOLO("runs/detect/detectTP/train_v2/weights/best.pt")

# Spustenie predikcie pre obrázok
results = model.predict("TP26_detection_v2-1/valid/images/sample.jpg", conf=0.5)

# Zobrazenie výsledkov
for result in results:
    result.show()  # Vyskakovacie okno s detekciami
    # result.save(filename='result.jpg') # Uloženie výsledku
```

### 4. Reštrukturalizácia dát (príprava na klasifikáciu z predpôn)
Príklad z klasifikačného notebooku na vytvorenie kategórií pomocou predpôn súborov:
```python
import shutil
from pathlib import Path

# Predpokladajme, že obrázky "bad1_*.jpg" a "good_*.jpg" sú v jednom priečinku
src_path = Path("TP26_detection_v2-1/train/images")
dst_path = Path("datasets/TP26/train")

for img_file in src_path.glob("*.jpg"):
    # Zisti triedu z názvu (napr. bad1_001.jpg -> bad1)
    class_name = img_file.stem.split('_')[0] 
    
    # Vytvor priečinok a prekopíruj
    class_dir = dst_path / class_name
    class_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(img_file, class_dir / img_file.name)
```


## Návod na git
### Klonovanie
```bash
cd lokalny priecinok
git clone https://github.com/MatejMedveczky/TP_detekcia_defektov.git
cd TP_detekcia_defektov
git switch -c VHODNY_NAZOV_BRANCH //priezvisko, pripadne nazov ulohy
```
### Prvý commit
```bash
git add .
git commit -m "POPIS ZMENY"
git push -u origin <VHODNY_NAZOV_BRANCH>
```
### Dalšie commity
Skontroluj či si v správnej branchi
```bash
git add .
git commit -m "POPIS ZMENY"
git push
```
