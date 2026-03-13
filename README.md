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
