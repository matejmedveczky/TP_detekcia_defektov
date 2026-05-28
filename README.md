## Prehľad Jupyter Notebookov

Projekt bol vyvíjaný a spúšťaný prostredníctvom Jupyter notebookov, ktoré sú rozdelené podľa ich logického účelu (detekcia, klasifikácia, testovanie a práca s dátami):

| Notebook | Účel a popis |
|---|---|
| `yolo_dataset_download.ipynb` | **Príprava dát:** Pomocný skript na automatizované sťahovanie datasetov (napr. z platformy Roboflow prostredníctvom API), ich rozbalenie a prípravu adresárovej štruktúry potrebnej pre trénovanie YOLO modelov. |
| `YOLO_TP_detekcia_metal.ipynb` | **Detekcia (Kovy):** Hlavný notebook určený na trénovanie a validáciu objektovej detekcie (Object Detection s bounding boxami) zameranej špecificky na hľadanie povrchových chýb a defektov **na kovoch**. |
| `YOLO_TP_detekcia_plastic.ipynb` | **Detekcia (Plasty):** Obdoba predchádzajúceho notebooku, avšak prispôsobená a ladená na detekciu chýb a defektov **na plastových povrchoch**. |
| `YOLO_TP_klasifikacia.ipynb` | **Klasifikácia:** Notebook zameraný na trénovanie klasifikačných modelov (Image Classification). Slúži na zaradenie celého obrázka do konkrétnej kategórie (typu defektu) bez určovania presnej polohy defektu. |
| `YOLO_test.ipynb` | **Testovanie a Inferencia:** Experimentálny priestor pre načítanie natrénovaných modelov (váh `.pt`), spúšťanie inferencie na testovacích/nových obrázkoch, vizualizáciu bounding boxov a vyhodnocovanie výkonnosti modelu. |

**Odporúčaný workflow:**
1. Stiahnutie a formátovanie dát pomocou `yolo_dataset_download.ipynb`.
2. Natrénovanie modelu v príslušnom detekčnom (`...metal.ipynb` / `...plastic.ipynb`) alebo klasifikačnom (`...klasifikacia.ipynb`) notebooku.
3. Overenie výsledkov a vizualizácia predikcií v `YOLO_test.ipynb`.

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
