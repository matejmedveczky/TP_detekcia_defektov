# CNN - Detekcia a Klasifikácia Defektov

## Štruktúra dát
Dáta a modely v tomto priečinku sú organizované nasledovne:

* **`classification/`** - Spracované a pripravené datasety pre trénovanie, validáciu a testovanie. Obsahuje `train/`, `val/` a `test/` zložky, v ktorých sú obrázky rozdelené do podzložiek podľa jednotlivých tried. Dataset pre kovové podložky.
* **`models/`** - Výstupy z trénovania. Obsahuje uložené váhy natrénovaných modelov.
* **`TP26_plastic_v1/`** - Spracované a pripravené datasety pre trénovanie, validáciu a testovanie. Obsahuje `train/`, `val/` a `test/` zložky, v ktorých sú obrázky rozdelené do podzložiek podľa jednotlivých tried. Dataset pre plastové podložky.
* **`data/`** - Spracované a pripravené datasety pre trénovanie, validáciu a testovanie. Obsahuje `train/`, `val/` a `test/` zložky, v ktorých sú obrázky rozdelené do podzložiek podľa jednotlivých tried. Dataset pre depth mapu.
## Popis súborov (.ipynb / .py)

### 1. Príprava a Trénovanie Klasifikácie
* **`cnn_defect_classification.ipynb`**
  Obsahuje plný cyklus pre prácu s klasifikáciou defektov. Zahŕňa:
  * Načítanie dát a aplikáciu augmentácií (rotácie, prevrátenia, zmena veľkosti na 224x224).
  * Trénovanie modelu založeného na architektúre **ResNet18** s využitím transfer learningu v prostredí PyTorch.
  * Následnú inferenciu a evaluáciu na testovacích sadách (výpočet presnosti, generovanie matice zámien a classification reportu).
  * Vizualizáciu aktivačných máp pomocou techniky **Grad-CAM**, ktorá formou heatmapy ukazuje, na aké časti obrázka sa model pri rozhodovaní sústredil.

---

## Základné ukážky kódov

### 1. Načítanie dát a augmentácia
Tento kód načíta obrázky zo štruktúry priečinkov a aplikuje na ne transformácie potrebné pre trénovanie (zmena veľkosti, prevrátenie, rotácia).

```python
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

IMG_SIZE = 224
BATCH_SIZE = 32

# Definovanie augmentácií pre trénovacie dáta
train_tf = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ToTensor()
])

# Načítanie datasetu z priečinkov
train_ds = datasets.ImageFolder("classification/train", transform=train_tf)
train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
```
### 2. Inicializácia a prispôsobenie modelu (ResNet18)
Načítanie predtrénovaného modelu a úprava jeho poslednej vrstvy tak, aby zodpovedala nášmu počtu tried.
```python
import torchvision.models as models
from torch import nn

# Načítanie základného modelu s predtrénovanými váhami
model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)

# Zistenie počtu tried z datasetu a úprava poslednej (Fully Connected) vrstvy
class_names = train_ds.classes
num_classes = len(class_names)

in_features = model.fc.in_features
model.fc = nn.Linear(in_features, num_classes)

# Presun modelu na GPU (ak je dostupné)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
```
### 3. Vizualizácia rozhodovania modelu (Grad-CAM)
Po natrénovaní modelu je možné použiť Grad-CAM na zistenie, na aké pixely sa model zameral.
```python
# Zameranie sa na poslednú konvolučnú vrstvu modelu ResNet
target_layer = model.layer4[-1].conv2
grad_cam = GradCAM(model, target_layer)

# Spustenie vizualizácie pre testovacie dáta
show_gradcam_n_per_class(
    model=model,
    grad_cam=grad_cam,
    loader=test_loader,
    class_names=class_names,
    n_per_class=5
)
```
### 4. Uloženie natrénovaného modelu
Po úspešnom ukončení trénovacieho cyklu sa váhy modelu uložia pre neskoršiu inferenciu.
```python
import torch
from pathlib import Path

# Vytvorenie priečinka a uloženie modelu
MODEL_DIR = Path.cwd() / "models"
MODEL_DIR.mkdir(exist_ok=True)

torch.save(model.state_dict(), MODEL_DIR / "keras_like_cnn_multiclass.pth")
```
## Návod na použitie
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
