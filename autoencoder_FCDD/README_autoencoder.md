# README – technická dokumentácia autoenkódera

Tento dokument slúži ako technická dokumentácia ku kódom pre detekciu defektov pomocou konvolučného autoenkódera. Popisuje, čo jednotlivé notebooky robia, akú štruktúru dát očakávajú, ako prebieha tréning, validácia, výber rozhodovacieho prahu a vyhodnocovanie výsledkov.

## 1. Základný princíp

Použitý prístup je založený na konvolučnom autoenkóderi. Autoenkóder sa trénuje na správnych vzorkách bez defektu. Po natrénovaní sa pre vstupný obrázok vytvorí rekonštrukcia a následne sa vypočíta rozdiel medzi pôvodným obrázkom a rekonštruovaným obrázkom.

Ako `anomaly score` sa používa MSE rekonštrukčná chyba. Ak je MSE vyššie ako rozhodovací prah, vzorka je označená ako defektná. Ak je MSE menšie alebo rovné prahu, vzorka je označená ako správna.

F1-score sa nepoužíva ako rekonštrukčná chyba. Slúži iba na výber najvhodnejšieho rozhodovacieho prahu na validačnej množine.

## 2. Prehľad notebookov

Experimenty sú rozdelené do štyroch notebookov podľa typu dát a použitého predspracovania.

| Notebook | Úloha | Vstupné dáta | Výstup modelu |
|---|---|---|---|
| `autoencoder.ipynb` | Základný autoenkóder pre kovové podložky bez dodatočného predspracovania. | `C:\ae_fcdd\train`, `C:\ae_fcdd\val`, `C:\ae_fcdd\test` | `C:\BestModel\best_autoencoder_basic.pth` |
| `autoencoder_predspracovanie.ipynb` | Vytvorenie HSV a inpainting datasetov pre kovové podložky a tréning na zvolenej verzii. | `C:\ae_fcdd` → `C:\dataset_basic_hsv` alebo `C:\dataset_basic_inpaint` | `C:\BestModel\best_autoencoder_basic_hsv.pth` alebo `C:\BestModel\best_autoencoder_basic_inpaint.pth` |
| `autoencoder_plast.ipynb` | Autoenkóder pre plastové podložky s predspracovaním odleskov priamo pri načítaní obrázka. | `C:\TP26_plastic_autoencoder_v2_x3\train`, `\valid`, `\test` | `C:\BestModel\best_autoencoder_plast.pth` |
| `autoencoder_depth_map.ipynb` | Autoenkóder pre depth mapy s potlačením extrémne tmavých a svetlých hodnôt. | `C:\TP26_depthmap_autoencoder\train`, `\val`, `\test` | `C:\BestModel\best_autoencoder_depth_map.pth` |

## 3. Očakávaná štruktúra dát

Kódy používajú absolútne cesty vo Windows. Pred spustením je potrebné skontrolovať, či dané priečinky existujú a či obsahujú očakávanú štruktúru.

Príklad štruktúry pre kovové podložky:

```text
C:\ae_fcdd\
├── train\
│   └── good\
├── val\
│   ├── good\
│   └── anomaly\
│       ├── bad1\
│       ├── bad2\
│       ├── ...
│       └── bad6\
└── test\
    ├── good\
    └── anomaly\
        ├── bad1\
        ├── bad2\
        ├── ...
        └── bad6\
```

Dôležité poznámky:

- Trénovacia množina má obsahovať iba správne obrázky bez defektu.
- Validačná a testovacia množina obsahujú triedu `good` a defektné triedy.
- Pri plastových podložkách je validačný priečinok pomenovaný `valid`, nie `val`.
- Priečinok `C:\BestModel` musí existovať pred spustením tréningu, pretože sa doň ukladajú najlepšie váhy modelov.

## 4. Použité knižnice

Notebooky sú napísané v Pythone a používajú hlavne PyTorch.

| Knižnica | Použitie |
|---|---|
| `torch`, `torch.nn`, `torch.optim` | Definícia modelu, loss funkcia, optimalizátor a tréning. |
| `torchvision.datasets.ImageFolder` | Načítanie obrázkov podľa priečinkovej štruktúry. |
| `torchvision.transforms` | Transformácie obrázkov pred vstupom do modelu. |
| `numpy` | Práca so skóre, thresholdmi a hodnotami obrazu. |
| `matplotlib` | Grafy loss funkcie, histogramy a vizualizácie rekonštrukcií. |
| `sklearn.metrics` | Confusion matrix, precision, recall a F1-score. |
| `cv2`, `PIL` | Predspracovanie obrázkov, HSV úpravy, inpainting a mediánový filter. |

Výpočtové zariadenie sa nastavuje automaticky:

```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

Ak je dostupná CUDA GPU, tréning beží na GPU. Inak sa použije CPU.

## 5. Architektúra autoenkódera

Vo všetkých experimentoch je použitá rovnaká alebo veľmi podobná architektúra konvolučného autoenkódera. Vstupom je grayscale obrázok s rozmerom `256 × 256` pixelov.

Po transformácii má vstup tvar:

```text
[B, 1, 256, 256]
```

kde:

- `B` je veľkosť batchu,
- `1` je jeden grayscale kanál,
- `256 × 256` je výška a šírka obrázka.

Encoder postupne zmenšuje priestorový rozmer obrazu a zvyšuje počet máp príznakov. Decoder robí opačný proces a rekonštruuje obraz späť na pôvodný rozmer.

| Časť | Približný výstupný tvar | Význam |
|---|---|---|
| Vstup | `[B, 1, 256, 256]` | Grayscale obrázok. |
| Conv2d 1 → 32 | `[B, 32, 128, 128]` | Prvá extrakcia príznakov a zmenšenie rozmeru na polovicu. |
| Conv2d 32 → 64 | `[B, 64, 64, 64]` | Ďalšie zmenšenie a viac máp príznakov. |
| Conv2d 64 → 128 | `[B, 128, 32, 32]` | Hlbšie príznaky obrazu. |
| Conv2d 128 → 256 | `[B, 256, 16, 16]` | Kompaktnejší opis obrazu. |
| Conv2d 256 → 512 | `[B, 512, 8, 8]` | Najmenší priestorový rozmer v encoderi. |
| Conv2d 512 → 16 | `[B, 16, 8, 8]` | Latentná reprezentácia. |
| Decoder | `[B, 1, 256, 256]` | Transponované konvolúcie obnovia rozmer obrázka. |

Parametre `kernel_size=4`, `stride=2` a `padding=1` pri konvolučných vrstvách spôsobujú zmenšenie obrazu približne na polovicu. Pri `ConvTranspose2d` s rovnakými parametrami sa rozmer naopak približne zdvojnásobuje. Posledná sigmoid vrstva udrží výstup v rozsahu 0 až 1.

## 6. Notebook `autoencoder.ipynb` – kovové podložky bez predspracovania

Tento notebook predstavuje základný experiment. Používa kovové podložky z priečinka `C:\ae_fcdd` a nepoužíva dodatočné predspracovanie odleskov.

Základné kroky:

1. Import knižníc.
2. Nastavenie parametrov experimentu (`IMG_HEIGHT`, `IMG_WIDTH`, `batch_size`, `epochs`, `learning_rate`, `patience`).
3. Definícia triedy `Autoencoder`.
4. Načítanie datasetov `train`, `val`, `test`.
5. Tréning pomocou `MSELoss`, optimalizátora Adam a scheduleru `ReduceLROnPlateau`.
6. Uloženie najlepšieho modelu podľa najnižšej validačnej chyby na good vzorkách.
7. Výpočet MSE anomaly score a výber threshold-u podľa najlepšieho F1-score.
8. Testovanie a vizualizácie výsledkov.

V tomto experimente sa obrázky iba prevedú na grayscale, zmenia na rozmer `256 × 256` a prevedú na tensor.

## 7. Notebook `autoencoder_predspracovanie.ipynb` – kovové podložky s predspracovaním

Tento notebook má dve hlavné časti:

1. vytvorenie nových predspracovaných datasetov z pôvodného datasetu `C:\ae_fcdd`,
2. tréning autoenkódera na zvolenej verzii datasetu.

Použité predspracovania:

| Funkcia | Úloha |
|---|---|
| `remove_glare_inpaint` | Vytvorí masku veľmi svetlých oblastí a pomocou inpaintingu nahradí odlesk hodnotami z okolia. |
| `remove_glare_hsv` | Obmedzí veľmi vysokú jasovú hodnotu vo farebnom priestore HSV. |
| `generate_datasets` | Prejde `train`, `val`, `test`, aplikuje HSV aj inpainting a uloží nové obrázky. |
| `show_visual_comparison` | Zobrazí porovnanie originálu, masky, inpaintingu a HSV úpravy. |

Predspracované datasety sa ukladajú do:

```text
C:\dataset_basic_hsv
C:\dataset_basic_inpaint
```

Výber datasetu na tréning sa nastavuje premennou:

```python
METHOD_TO_TRAIN = "basic_inpaint"  # alebo "basic_hsv"
```

Ak už predspracované datasety existujú, volanie `generate_datasets()` môže zostať zakomentované. Ak ešte neexistujú, treba ho odkomentovať a spustiť.

## 8. Notebook `autoencoder_plast.ipynb` – plastové podložky

Tento notebook pracuje s plastovými podložkami z priečinka:

```text
C:\TP26_plastic_autoencoder_v2_x3
```

Dôležitý rozdiel oproti ostatným datasetom je, že validačný priečinok je pomenovaný `valid`.

Predspracovanie plastových vzoriek sa vykonáva priamo v transformačnom reťazci pri načítaní obrázka. Obrázky sa neukladajú ako nový dataset. Každý obrázok sa pred vstupom do autoenkódera upraví v pamäti.

Použité kroky:

| Trieda alebo transformácia | Úloha |
|---|---|
| `ReflectionReducer` | Potláča lokálne svetlé odlesky pomocou masky, inpaintingu a obmedzenia maximálnej hodnoty jasu vo HSV. |
| `GaussianBlur` | Jemne vyhladí obraz a zníži lokálny šum. |
| `QuantizeTensor` | Zredukuje počet šedých odtieňov, napríklad na 64 úrovní. |

Poznámka: `ReflectionReducer` cielene potláča hlavne svetlé odlesky. Tmavé časti nie sú zámerne zosvetľované ani potláčané, aby sa nezmazali možné tmavé defekty.

## 9. Notebook `autoencoder_depth_map.ipynb` – depth mapy

Tento notebook pracuje s depth mapami z priečinka:

```text
C:\TP26_depthmap_autoencoder
```

Depth mapa nie je klasický farebný obraz, ale obraz hĺbkovej informácie. Pri týchto dátach môžu byť problémom extrémne tmavé alebo extrémne svetlé hodnoty.

Použité predspracovanie zabezpečuje trieda `DepthMapSoftClip`.

| Parameter | Význam |
|---|---|
| `black_floor = 15` | Dolná hranica, ktorá pomáha potlačiť extrémne čierne oblasti. |
| `white_ceiling = 240` | Horná hranica, ktorá pomáha potlačiť extrémne biele oblasti. |
| `low_percentile = 0.5` | Dolný percentil použitý pri výpočte rozsahu. |
| `high_percentile = 99.5` | Horný percentil použitý pri výpočte rozsahu. |
| `median_ksize = 3` | Veľkosť mediánového filtra na potlačenie lokálneho šumu. |

Postup:

1. obrázok sa prevedie na grayscale,
2. aplikuje sa mediánový filter,
3. vypočítajú sa percentilové hranice,
4. hodnoty mimo rozsahu sa orežú,
5. obraz sa normalizuje späť do rozsahu 0 až 255,
6. až potom sa cez `ToTensor()` prevedie do rozsahu 0 až 1 a vstupuje do autoenkódera.

## 10. Tréning a validácia

Tréning prebieha v cykle cez epochy. V každej epoche sa model prepne do režimu:

```python
model.train()
```

Následne sa spracujú batch-e z `train_loader`, vypočíta sa MSE loss a váhy sa upravia pomocou:

```python
loss.backward()
optimizer.step()
```

Po tréningovej časti epochy sa model prepne do režimu:

```python
model.eval()
```

Na správnych validačných vzorkách sa bez výpočtu gradientov vypočíta validačná rekonštrukčná chyba. Validačné dáta nemenia váhy modelu. Slúžia iba na kontrolu kvality rekonštrukcie a výber najlepších váh.

Ak sa validačná chyba zlepší, model sa uloží:

```python
if val_loss < best_val_loss:
    best_val_loss = val_loss
    best_model_wts = copy.deepcopy(model.state_dict())
    torch.save(model.state_dict(), cesta_k_modelu)
    early_stop_counter = 0
else:
    early_stop_counter += 1
```

Ak sa validačná chyba nezlepší počas počtu epoch definovaného premennou `patience`, tréning sa ukončí pomocou early stopping.

## 11. MSE anomaly score a výber threshold-u

Po tréningu sa pre každý validačný obrázok vypočíta MSE anomaly score:

```python
error_map = torch.square(reconstructions - images)
anomaly_score = error_map.mean(dim=(1, 2, 3))
```

Pre validačné dáta sa vytvorí pole skutočných tried:

```text
good = 0
defect = 1
```

Následne sa skúša viacero možných thresholdov. Pre každý threshold platí:

```text
ak MSE > threshold  → defekt
ak MSE <= threshold → good
```

Pre každú sadu predikcií sa vypočíta F1-score a vyberie sa threshold s najlepšou hodnotou F1-score.

Poznámka: F1-score nie je rekonštrukčná chyba. Slúži iba na výber prahu. Samotné rozhodovanie modelu je založené na MSE anomaly score.

## 12. Vizualizácie a interpretácia výsledkov

Notebooky vytvárajú viacero výstupov, ktoré slúžia na kontrolu výsledkov.

| Výstup | Význam |
|---|---|
| Loss graf | Zobrazuje trénovaciu MSE chybu a validačnú MSE chybu na good vzorkách. |
| Histogram MSE skóre | Ukazuje prekrytie good a defect vzoriek na validácii. Pomáha posúdiť vhodnosť threshold-u. |
| Confusion matrix | Ukazuje počet správnych a nesprávnych klasifikácií na testovacej množine. |
| `show_worst_good_images` | Zobrazuje dobré obrázky s najvyššou MSE chybou. |
| `show_false_positives` | Zobrazuje správne obrázky, ktoré boli označené ako defekt. |
| `show_anomaly_heatmaps` | Zobrazuje originál, rekonštrukciu a MSE heatmapu defektných vzoriek. |

Tieto vizualizácie sú dôležité, pretože pomáhajú odlíšiť skutočný defekt od problémov spôsobených osvetlením, tieňom, odleskom alebo šumom.

## 13. Odporúčaný postup spustenia

1. Skontrolovať, že sú nainštalované potrebné knižnice.
2. Skontrolovať, že Python prostredie vidí PyTorch a prípadne CUDA GPU.
3. Vytvoriť priečinok `C:\BestModel`, ak ešte neexistuje.
4. Skontrolovať cesty k datasetom.
5. Pri základnom experimente spustiť `autoencoder.ipynb` od prvej bunky po poslednú.
6. Pri experimente s predspracovaním najskôr podľa potreby odkomentovať `generate_datasets()` a vytvoriť `C:\dataset_basic_hsv` a `C:\dataset_basic_inpaint`.
7. V notebooku `autoencoder_predspracovanie.ipynb` nastaviť `METHOD_TO_TRAIN` na `basic_hsv` alebo `basic_inpaint`.
8. Pri plastových a depth experimentoch skontrolovať správne názvy priečinkov `train`, `valid`, `val`, `test`.
9. Po každom spustení skontrolovať loss graf, histogram MSE skóre, confusion matrix a heatmapy.

## 14. Čo upraviť pri zmene dát alebo experimentu

| Čo sa mení | Kde upraviť |
|---|---|
| Cesta k datasetu | Premenné v časti `ImageFolder`, `root_dir` alebo `BASE_SOURCE_DIR`. |
| Veľkosť vstupu | `IMG_HEIGHT` a `IMG_WIDTH`. Zmena môže vyžadovať kontrolu architektúry. |
| Počet epoch | Premenná `epochs`. |
| Learning rate | Premenná `learning_rate`. |
| Uloženie modelu | Cesta v `torch.save()` alebo premenná `save_model_name`. |
| Predspracovanie plastov | Parametre `ReflectionReducer` a `QuantizeTensor`. |
| Predspracovanie depth máp | Parametre `DepthMapSoftClip`. |
| Výber HSV/inpainting datasetu | Premenná `METHOD_TO_TRAIN` v notebooku `autoencoder_predspracovanie.ipynb`. |

## 15. Výstupy, ktoré treba kontrolovať

Po spustení notebookov vznikajú najmä tieto výstupy:

- uložené modely v `C:\BestModel`,
- graf priebehu tréningovej a validačnej chyby,
- histogram MSE anomaly score pre good a defect validačné vzorky,
- vypísaný najlepší threshold a validačné F1-score,
- porovnanie rôznych thresholdov na testovacej množine,
- confusion matrix pre testovacie dáta,
- vizualizácie originál / rekonštrukcia / MSE heatmapa,
- ukážky false positive prípadov,
- najhoršie rekonštruované good obrázky.

## 16. Poznámky k práci s Gitom

Ak má byť táto dokumentácia súčasťou tvojej vetvy v repozitári, súbor ulož ako:

```text
README.md
```

Odporúčaný postup:

```bash
git checkout <nazov-tvojej-branch>
git status
git add README.md
git commit -m "Add autoencoder README documentation"
git push
```

Ak už v koreňovom priečinku existuje hlavný tímový `README.md`, je vhodné dokumentáciu uložiť napríklad ako:

```text
README_autoencoder.md
```

alebo do priečinka s autoenkódermi ako:

```text
autoencoder/README.md
```
