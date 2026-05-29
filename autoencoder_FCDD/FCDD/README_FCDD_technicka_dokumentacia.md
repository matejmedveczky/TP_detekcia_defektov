# Technická dokumentácia FCDD experimentov

Tento README dokument slúži ako technická dokumentácia k FCDD riešeniu pre detekciu defektov na podložkách. Popisuje, kde sa nachádzajú jednotlivé časti kódu, ako pipeline funguje, ako sa spúšťajú experimenty a aké výstupy sa generujú.

Dokumentácia sa vzťahuje na tri experimentálne notebooky:

| Experiment | Notebook | Dataset | Výstupný priečinok |
|---|---|---|---|
| 1.8 | `FCDD_1.8_supervisor_report.ipynb` | kovové podložky, polar unwrap | `runs/fcdd_polar_reflect_v1` |
| 1.9 | `FCDD_1.9_TP26_plastic_FIX.ipynb` | plastové podložky, RGB | `runs/fcdd_tp26_plastic_reflect_v1` |
| 2.0 | `FCDD_2.0_TP26_depthmaps.ipynb` | depthmapy plastových podložiek | `runs/fcdd_tp26_depthmap_v1` |

---

## 1. Cieľ riešenia

Cieľom riešenia je detekovať defektné podložky pomocou FCDD prístupu. FCDD je fully convolutional prístup k detekcii anomálií. Model je trénovaný hlavne na dobrých vzorkách a pri vyhodnotení vytvára anomálovú mapu, z ktorej sa vypočíta image-level skóre.

Výsledkom sú dva typy výstupu:

1. **Klasifikácia obrázka** na `good` alebo `anomaly`.
2. **Lokalizácia podozrivej oblasti** pomocou heatmapy.

Keďže podložky majú kruhový tvar, vstup sa pred modelom transformuje do polar unwrap reprezentácie. Kruhový prstenec sa tým rozvinie do obdĺžnikového obrazu.

---

## 2. Očakávaná štruktúra dát

Všetky datasety sú uložené v priečinku:

```text
C:\Users\Jakub\Desktop\skola new\Tímový projekt\dataset_splits
```

### 2.1 Experiment 1.8

Experiment 1.8 používa pôvodný dataset pre FCDD:

```text
dataset_splits/
└── ae_fcdd/
    ├── train/
    ├── val/
    └── test/
```

V jednotlivých splitoch sa očakávajú triedy `good` a `anomaly`.

### 2.2 Experiment 1.9

Experiment 1.9 používa dataset plastových podložiek:

```text
dataset_splits/
└── TP26_plastic_classification_v2_x3/
    ├── train/
    │   ├── good/
    │   └── bad/
    ├── valid/
    │   ├── good/
    │   └── bad/
    └── test/
        ├── good/
        └── bad/
```

Notebook si z tohto datasetu automaticky vytvorí FCDD-ready štruktúru:

```text
dataset_splits/
└── TP26_plastic_fcdd_ready/
    ├── train/
    │   ├── good/
    │   └── anomaly/
    ├── val/
    │   ├── good/
    │   └── anomaly/
    └── test/
        ├── good/
        └── anomaly/
```

Premapovanie je:

```text
good -> good
bad  -> anomaly
valid -> val
```

### 2.3 Experiment 2.0

Experiment 2.0 používa depthmapy:

```text
dataset_splits/
└── TP26_depthmap_classification/
    ├── train/
    │   ├── good/
    │   └── bad/
    ├── valid/
    │   ├── good/
    │   └── bad/
    └── test/
        ├── good/
        └── bad/
```

Notebook si vytvorí:

```text
dataset_splits/
└── TP26_depthmap_fcdd_ready/
    ├── train/
    │   ├── good/
    │   └── anomaly/
    ├── val/
    │   ├── good/
    │   └── anomaly/
    └── test/
        ├── good/
        └── anomaly/
```

---

## 3. Základná logika pipeline

Pipeline je rovnaká vo všetkých troch experimentoch:

```text
vstupný obrázok
        ↓
segmentácia kruhovej podložky
        ↓
odhad stredu, vnútorného a vonkajšieho polomeru
        ↓
polar unwrap prstenca
        ↓
uloženie predspracovaného vstupu do cache
        ↓
trénovanie alebo načítanie FCDD modelu
        ↓
výpočet anomaly heatmapy
        ↓
výpočet image-level anomaly score
        ↓
určenie thresholdu na validačnej množine
        ↓
vyhodnotenie testovacej množiny
        ↓
export grafov, metrík a heatmáp
```

---

## 4. Polar unwrap

Keďže podložka je kruhová, model by sa pri klasickom RGB obrázku musel učiť defekty na zakrivenom prstenci. Preto sa používa transformácia do polar unwrap priestoru.

Vstupný kruhový prstenec sa rozvinie do obdĺžnika:

```text
horizontálna os = uhol okolo podložky
vertikálna os = radiálny smer medzi vnútorným a vonkajším okrajom
```

Použité rozmery polar obrazu:

```text
radial_bins = 128
angular_bins = 512
```

Teda model dostáva vstup približne:

```text
RGB experimenty:       3 × 128 × 512
Depthmap experiment:   1 × 128 × 512
```

---

## 5. Cache predspracovania

Aby sa polar unwrap nepočítal pri každom tréningovom behu odznova, predspracované dáta sa ukladajú do cache.

Použité cache priečinky:

| Experiment | Cache |
|---|---|
| 1.8 | `dataset_splits/ae_fcdd_polar_cache_reflect_v1` |
| 1.9 | `dataset_splits/TP26_plastic_polar_cache_reflect_v1` |
| 2.0 | `dataset_splits/TP26_depthmap_polar_cache_v1` |

V cache sa ukladajú hlavne:

```text
*.npy   predspracovaný polar unwrap obraz
*.json  metadáta o geometrii podložky
```

Metadáta obsahujú napríklad informáciu o strede podložky, vnútornom a vonkajšom polomere. Tieto údaje sa neskôr používajú pri spätnom premietnutí heatmapy na pôvodný obrázok.

---

## 6. Hlavné časti notebookov

Notebooky sú štruktúrované veľmi podobne. Najdôležitejšie časti sú:

### 6.1 Konfigurácia experimentu

Nachádza sa v úvodnej bunke notebooku v slovníku `CFG`.

Príklad hlavných parametrov:

```python
CFG = {
    "data_root": ...,
    "cache_root": ...,
    "out_dir": ...,
    "radial_bins": 128,
    "angular_bins": 512,
    "batch_size": 8,
    "epochs": 24,
    "lr": 1e-4,
    "base_channels": 32,
    "grayscale": False,
    "topk_ratio": 0.0045,
    "score_smooth_kernel": 3,
}
```

Dôležité parametre:

| Parameter | Význam |
|---|---|
| `data_root` | cesta k FCDD-ready datasetu |
| `cache_root` | cesta k predspracovanej polar cache |
| `out_dir` | priečinok, kam sa ukladajú výsledky experimentu |
| `radial_bins` | počet pixelov v radiálnom smere po unwrape |
| `angular_bins` | počet pixelov v uhlovom smere po unwrape |
| `batch_size` | veľkosť batchu |
| `epochs` | počet epoch tréningu |
| `lr` | learning rate |
| `base_channels` | základný počet kanálov v FCDD sieti |
| `grayscale` | či sa vstup prevedie na jeden kanál |
| `topk_ratio` | aká časť najaktívnejších pixelov heatmapy sa použije pri image-level skóre |
| `score_smooth_kernel` | smoothing použitý pri výpočte skóre |

---

## 7. Hlavné funkcie v kóde

### 7.1 `prepare_tp26_fcdd_dataset`

Používa sa v experimentoch 1.9 a 2.0.

Úloha:

```text
- pripraví dataset do formátu, ktorý očakáva FCDD notebook,
- premenuje valid na val,
- premenuje bad na anomaly,
- ponechá good ako good.
```

Používa sa len pri datasetoch, ktoré pôvodne nemajú presnú FCDD štruktúru.

---

### 7.2 `build_polar_cache`

Táto funkcia pripravuje predspracované vstupy pre model.

Úloha:

```text
- prejde všetky obrázky v train/val/test,
- načíta obrázok,
- odhadne geometriu podložky,
- rozvinie prstenec do polar unwrap reprezentácie,
- aplikuje voliteľné potlačenie odleskov a high-pass úpravu,
- uloží výsledok do cache ako .npy,
- uloží metadáta ako .json.
```

Táto časť je výpočtovo dôležitá, pretože určuje, aký vstup bude model reálne vidieť.

---

### 7.3 `estimate_washer_geometry`

Funkcia odhaduje geometriu podložky.

Úloha:

```text
- nájde oblasť podložky na obrázku,
- odhadne stred objektu,
- odhadne vnútorný a vonkajší polomer,
- vytvorí masku prstenca.
```

Výsledok sa používa pri polar unwrape aj pri spätnom premietnutí heatmapy.

---

### 7.4 `unwrap_annulus`

Táto funkcia transformuje kruhový prstenec do obdĺžnikového polar obrazu.

Úloha:

```text
- vezme pôvodný obrázok a geometriu podložky,
- pre každý radiálny a uhlový krok vypočíta zodpovedajúci pixel v pôvodnom obraze,
- vytvorí polar unwrap obraz veľkosti 128 × 512.
```

---

### 7.5 `wrap_heatmap_to_original`

Táto funkcia robí opačnú operáciu ako `unwrap_annulus`.

Úloha:

```text
- vezme heatmapu v polar unwrap priestore,
- premietne ju späť na pôvodný kruhový tvar podložky,
- vytvorí heatmapu použiteľnú na overlay nad pôvodným obrázkom.
```

Používa sa pri vizualizácii lokalizácie defektu.

---

### 7.6 `CachedPolarTrainDataset`

Dataset pre tréning.

Úloha:

```text
- načítava predspracované .npy súbory z cache,
- používa iba dobré vzorky,
- aplikuje jednoduché augmentácie, napríklad horizontálny posun v polar priestore.
```

Tréning FCDD je založený na tom, že model sa učí reprezentáciu dobrých vzoriek.

---

### 7.7 `CachedPolarEvalDataset`

Dataset pre validáciu a testovanie.

Úloha:

```text
- načítava good aj anomaly vzorky,
- vracia vstupný tensor, label, cestu k obrázku a cestu k metadátam,
- používa sa na výpočet metrík a heatmáp.
```

---

### 7.8 `FCDDPolarNet`

Toto je hlavná neurónová sieť.

Charakteristika:

```text
- plne konvolučná sieť,
- vstupom je polar unwrap obraz,
- výstupom je anomálová mapa,
- používa kruhové správanie v uhlovom smere pomocou CircularWidthConv.
```

`CircularWidthConv` pomáha najmä preto, že horizontálna os polar unwrap obrazu predstavuje uhol. Ľavý a pravý okraj obrazu na seba nadväzujú.

---

### 7.9 `masked_topk_score`

Táto funkcia prevádza heatmapu na jedno image-level skóre.

Úloha:

```text
- vezme anomaly heatmapu,
- aplikuje maskovanie okrajov a stredu,
- prípadne heatmapu vyhladí,
- vyberie top-k najaktívnejších pixelov,
- z ich hodnôt vypočíta finálne anomaly score.
```

Vyššie skóre znamená vyššiu pravdepodobnosť defektu.

---

### 7.10 `calibrate_threshold_from_val`

Táto funkcia určuje threshold na validačnej množine.

Úloha:

```text
- vypočíta skóre pre validačné obrázky,
- skúša rôzne thresholdy,
- vyberie threshold podľa validačných metrík.
```

Threshold potom rozhoduje:

```text
score >= threshold  -> anomaly
score < threshold   -> good
```

---

### 7.11 `evaluate_with_confusion`

Funkcia vyhodnocuje model na validačnej alebo testovacej množine.

Počíta:

```text
TN, FP, FN, TP
accuracy
balanced accuracy
recall
specificity
AUC
```

Confusion matrix sa ukladá aj ako obrázok.

---

### 7.12 `save_heatmaps`

Funkcia generuje vizualizačné heatmapy.

Úloha:

```text
- vypočíta modelovú anomaly heatmapu,
- porovná ju s referenciou dobrých vzoriek,
- vytvorí hybridnú heatmapu,
- premietne heatmapu späť na pôvodný obrázok,
- uloží panel s pôvodným obrázkom, heatmapou a overlayom.
```

Výstupy sa ukladajú do výstupného priečinka experimentu.

---

### 7.13 `generate_supervisor_report`

Funkcia generuje finálne výstupy pre školiteľa.

Ukladá:

```text
supervisor_report/
├── metrics_summary.csv
├── thresholds_summary.json
├── val_scores_defect_sensitive.csv
├── test_scores_defect_sensitive.csv
├── val_score_histogram.png
├── test_score_histogram.png
├── val_threshold_sweep.csv
├── val_threshold_sweep.png
├── training_loss.png
├── validation_metrics.png
├── test_balanced_confusion_matrix.png
├── test_defect_sensitive_confusion_matrix.png
├── heatmap_examples_categories/
│   ├── TP_grid.png
│   ├── TN_grid.png
│   ├── FP_grid.png
│   ├── FN_grid.png
│   └── selected_heatmap_examples.csv
└── documentation_notes.md
```

Ak niektorá kategória neexistuje, napríklad ak nie je žiadny FN prípad, príslušný grid sa nevytvorí. Toto nie je chyba.

---

## 8. Tréning modelu

Model sa trénuje na dobrých vzorkách. Pri trénovaní sa minimalizuje chyba na reprezentácii dobrých podložiek. Ak model neskôr dostane defektný obrázok, lokálne oblasti s defektom by mali vytvoriť vyššiu odozvu v anomaly heatmape.

Spustenie tréningu je riadené parametrom:

```python
"only_export_heatmaps": False
```

Ak je hodnota `False`, notebook:

```text
- vytvorí alebo načíta cache,
- natrénuje model,
- uloží najlepší checkpoint,
- vyhodnotí test,
- vygeneruje heatmapy.
```

Najlepší checkpoint sa ukladá ako:

```text
best_fcdd_polar_cached.pt
```

---

## 9. Export z existujúceho checkpointu

Ak už model existuje a netreba ho trénovať odznova, používa sa:

```python
"only_export_heatmaps": True
```

Vtedy notebook:

```text
- načíta checkpoint best_fcdd_polar_cached.pt,
- nevykoná nový tréning,
- len prepočíta skóre, heatmapy a report.
```

Toto sa používalo napríklad pri dodatočnom generovaní výstupov pre školiteľa.

---

## 10. Thresholdy a metriky

V reportoch sa používajú dva režimy:

### 10.1 Balanced threshold

Balanced threshold je prah vybraný tak, aby dával rozumný kompromis medzi detekciou defektov a počtom falošných pozitívnych detekcií.

Vhodný je na objektívne porovnanie modelov.

### 10.2 Defect-sensitive threshold

Defect-sensitive threshold je prah nastavený tak, aby zachytil viac defektov. Zvyčajne má vyšší recall, ale môže mať viac false positives.

V kontexte kontroly kvality dáva tento režim praktický zmysel, pretože je lepšie poslať podozrivý dobrý kus na manuálnu kontrolu, než pustiť defektný kus ďalej.

---

## 11. Význam metrík

Použité metriky:

| Metrika | Význam |
|---|---|
| `TP` | defektný kus správne označený ako defektný |
| `TN` | dobrý kus správne označený ako dobrý |
| `FP` | dobrý kus nesprávne označený ako defektný |
| `FN` | defektný kus nesprávne označený ako dobrý |
| `Precision` | podiel správnych defektných predikcií zo všetkých predikovaných defektov |
| `Recall` | podiel zachytených defektov zo všetkých skutočných defektov |
| `F1` | harmonický priemer precision a recall |
| `Accuracy` | celkový podiel správnych predikcií |
| `Balanced accuracy` | priemer recall pre triedu good a triedu anomaly |
| `AUC` | schopnosť modelu separovať good a anomaly naprieč thresholdmi |

Výpočty:

```text
Precision = TP / (TP + FP)
Recall    = TP / (TP + FN)
F1        = 2 * Precision * Recall / (Precision + Recall)
```

---

## 12. Výstupy experimentov

Každý experiment generuje výstupy do svojho `out_dir` priečinka.

### 12.1 Hlavné súbory v `out_dir`

```text
run_config.json
history.json
best_fcdd_polar_cached.pt
test_confusion_matrix.png
```

### 12.2 Priečinok `supervisor_report`

Tento priečinok je najdôležitejší pre dokumentáciu a prezentáciu výsledkov.

Obsahuje:

```text
training_loss.png
validation_metrics.png
val_score_histogram.png
test_score_histogram.png
val_threshold_sweep.png
metrics_summary.csv
thresholds_summary.json
test_balanced_confusion_matrix.png
test_defect_sensitive_confusion_matrix.png
heatmap_examples_categories/
documentation_notes.md
```

---

## 13. Interpretácia obrázkov v reporte

### 13.1 `training_loss.png`

Ukazuje priebeh tréningovej chyby počas epoch. Klesajúca krivka znamená, že model sa postupne učí reprezentáciu dobrých vzoriek.

### 13.2 `validation_metrics.png`

Ukazuje vývoj validačných metrík počas trénovania. Pomáha určiť, v ktorej epoche bol checkpoint najlepší.

### 13.3 `val_score_histogram.png` a `test_score_histogram.png`

Histogramy ukazujú rozdelenie anomaly score pre triedy `good` a `anomaly`.

Dobrá separácia znamená, že good vzorky majú nižšie skóre a anomaly vzorky vyššie skóre. Ak sa histogramy výrazne prekrývajú, dataset je pre model náročnejší.

### 13.4 `val_threshold_sweep.png`

Ukazuje, ako sa menia metriky pri rôznych thresholdoch. Používa sa na vysvetlenie rozdielu medzi balanced a defect-sensitive režimom.

### 13.5 Confusion matrix obrázky

Confusion matrix ukazuje počty `TN`, `FP`, `FN` a `TP`.

Pri defect-sensitive nastavení je typické, že rastie `TP` a klesá `FN`, ale zároveň môže narásť `FP`.

### 13.6 `TP_grid.png`, `TN_grid.png`, `FP_grid.png`, `FN_grid.png`

Tieto gridy ukazujú príklady konkrétnych rozhodnutí modelu:

| Grid | Význam |
|---|---|
| `TP_grid.png` | defektné vzorky správne označené ako defektné |
| `TN_grid.png` | dobré vzorky správne označené ako dobré |
| `FP_grid.png` | dobré vzorky nesprávne označené ako defektné |
| `FN_grid.png` | defektné vzorky nesprávne označené ako dobré |

Tieto obrázky sú dôležité najmä na vizuálnu kontrolu, či heatmapa reaguje na skutočný defekt alebo na textúru, okraj, odlesk či šum.

---

## 14. Konfigurácie použitých experimentov

### 14.1 Experiment 1.8

```text
out_dir: runs/fcdd_polar_reflect_v1
radial_bins: 128
angular_bins: 512
batch_size: 8
epochs: 24
learning rate: 1e-4
base_channels: 32
grayscale: False
suppress_reflections: True
topk_ratio: 0.0045
score_smooth_kernel: 3
```

### 14.2 Experiment 1.9

```text
out_dir: runs/fcdd_tp26_plastic_reflect_v1
raw dataset: TP26_plastic_classification_v2_x3
prepared dataset: TP26_plastic_fcdd_ready
radial_bins: 128
angular_bins: 512
batch_size: 8
epochs: 24
learning rate: 1e-4
base_channels: 32
grayscale: False
suppress_reflections: True
topk_ratio: 0.0045
score_smooth_kernel: 3
```

Pri dodatočnom re-score experimente sa skúšalo aj:

```text
topk_ratio: 0.015
score_smooth_kernel: 5
```

### 14.3 Experiment 2.0

```text
out_dir: runs/fcdd_tp26_depthmap_v1
raw dataset: TP26_depthmap_classification
prepared dataset: TP26_depthmap_fcdd_ready
radial_bins: 128
angular_bins: 512
batch_size: 8
epochs: 24
learning rate: 1e-4
base_channels: 32
grayscale: True
suppress_reflections: False
topk_ratio: 0.015
score_smooth_kernel: 5
```

Pri depthmapách sa nepoužíva potlačenie odleskov, pretože vstup nie je RGB fotografia, ale mapa hĺbky.

---

## 15. Ako spustiť experiment

### 15.1 Prvý tréning

1. Otvoriť príslušný notebook.
2. Skontrolovať cesty v úvodnej bunke.
3. Nastaviť:

```python
"only_export_heatmaps": False
```

4. Spustiť všetky bunky zhora nadol.
5. Po skončení tréningu spustiť časť `Supervisor report exports`.

### 15.2 Len pregenerovanie reportu

Ak už existuje checkpoint:

1. Otvoriť notebook.
2. Nastaviť:

```python
"only_export_heatmaps": True
```

3. Spustiť bunky s konfiguráciou a definíciami funkcií.
4. Spustiť hlavnú bunku experimentu.
5. Spustiť `Supervisor report exports`.

---

## 16. Časté problémy

### 16.1 Chýba cesta k datasetu

Ak notebook vypíše `FileNotFoundError`, treba skontrolovať cestu:

```python
DATASET_SPLITS_ROOT = Path(r"C:\Users\Jakub\Desktop\skola new\Tímový projekt\dataset_splits")
```

Ak je projekt na inom počítači alebo v inom používateľskom účte, treba upraviť túto cestu.

### 16.2 Chýba `heatmap_limit_per_class`

Ak sa objaví chyba:

```text
AttributeError: 'types.SimpleNamespace' object has no attribute 'heatmap_limit_per_class'
```

treba do `CFG` doplniť:

```python
"heatmap_limit_per_class": 60
```

### 16.3 Nevznikol `FN_grid.png`

Nie je to automaticky chyba. Znamená to, že pri danom thresholde neexistoval žiadny false negative prípad.

### 16.4 Výsledky sa nezmenili po úprave parametrov

Treba skontrolovať `thresholds_summary.json`, či sa tam naozaj uložili nové hodnoty, napríklad:

```json
"topk_ratio": 0.015,
"smooth_kernel": 5
```

Ak je tam stará hodnota, daný beh nepoužil očakávaný config.

---

## 17. Odporúčaný spôsob odovzdania

Do repozitára alebo odovzdávacieho priečinka odporúčam priložiť:

```text
README.md
FCDD_1.8_supervisor_report.ipynb
FCDD_1.9_TP26_plastic_FIX.ipynb
FCDD_2.0_TP26_depthmaps.ipynb
runs/
└── jednotlivé supervisor_report priečinky
```

Pre školiteľa sú najdôležitejšie najmä:

```text
metrics_summary.csv
thresholds_summary.json
training_loss.png
validation_metrics.png
val_score_histogram.png
test_score_histogram.png
val_threshold_sweep.png
confusion_matrix obrázky
TP/TN/FP/FN heatmap gridy
```

---

## 18. Stručné zhrnutie

Kód implementuje FCDD pipeline pre anomálovú detekciu na kruhových podložkách. Vstupné obrázky sa najprv transformujú do polar unwrap reprezentácie, ktorá zjednodušuje učenie defektov na kruhovom prstenci. Model následne generuje anomaly heatmapu a z nej sa počíta image-level skóre. Threshold sa určuje z validačnej množiny a výsledky sa exportujú vo forme metrík, histogramov, confusion matrices a vizualizačných heatmáp.

Experimenty 1.8, 1.9 a 2.0 používajú rovnakú základnú pipeline, ale líšia sa typom vstupných dát. Experiment 1.8 slúži ako hlavný výsledok na pôvodných dátach, experiment 1.9 overuje pipeline na plastových RGB dátach a experiment 2.0 overuje využitie depthmap reprezentácie.
