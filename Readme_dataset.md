# README dataset

Tento súbor opisuje pomocné skripty použité na spracovanie pôvodných fotografií podložiek pred ich zaradením do datasetu. Skripty boli použité na automatické vyhľadanie podložky v obraze, jej orezanie, zjednotenie veľkosti a vytvorenie upravených alebo augmentovaných snímok vhodných na trénovanie modelov umelej inteligencie.

## Umiestnenie skriptov

V projekte sa nachádzajú tieto skripty:

- main_metal.py - spracovanie kovových podložiek.
- main_plast.py - spracovanie plastových podložiek.
- main_depthmap.py - spracovanie hĺbkových máp z profilometra.

Skripty pracujú s pôvodnými snímkami uloženými mimo tohto LaTeX projektu v priečinku `../originalphotos/` a výsledky ukladajú do priečinka `../augmentationphotos/`.

## Vstupné dáta

Vstupom boli originálne snímky podložiek vytvorené pomocou kamery Raspberry Pi Camera Module 3 a hĺbkové mapy získané laserovým profilometrom Micro-Epsilon scanCONTROL 2900-100. Dáta boli rozdelené podľa typu materiálu a triedy, napríklad:

../originalphotos/metal/metal_good/*.png
../originalphotos/plastic/plastic_good/*.png
../originalphotos/depthmap/depth_good/*.png

Podľa potreby bolo možné v skriptoch zmeniť vstupnú cestu aj pre iné triedy, napríklad chybné kovové alebo plastové podložky.

## Výstupné dáta

Výstupom skriptov boli upravené snímky s jednotným rozmerom `512 x 512` pixelov. Obrázky boli ukladané do priečinkov určených pre augmentované dáta, napríklad:

../augmentationphotos/metal_aug/metal_good_aug/
../augmentationphotos/plastic_aug/plastic_good_aug/
../augmentationphotos/depth_aug/depth_good_aug/

Tieto výstupy boli následne použité pri tvorbe datasetov pre klasifikáciu, detekciu defektov a vyhodnocovanie modelov.

## `main_metal.py`

Skript `main_metal.py` slúži na spracovanie kovových podložiek. Najskôr načíta pôvodnú snímku, prevedie ju do odtieňov sivej a zmenší pomocný obraz na rozmer `512 x 512`. Následne sa použije mediánový filter, adaptívne prahovanie a morfologické operácie na oddelenie podložky od pozadia.

Po nájdení kontúry sa určí stred a približný polomer podložky. Na základe týchto hodnôt sa z pôvodnej snímky vyreže oblasť so súčiastkou, ktorá sa následne zmení na rozmer `512 x 512`. Potom sa vytvorí základný výstup a ďalšie augmentované varianty:

- náhodná rotácia v rozsahu približne `20` až `300` stupňov,
- rozmazanie pomocou Gaussovho filtra,
- stmavenie snímky,
- zosvetlenie snímky.

Tieto úpravy zvyšujú variabilitu datasetu a pomáhajú modelu lepšie reagovať na rôzne natočenie, odlesky a svetelné podmienky kovových podložiek.

## `main_plast.py`

Skript `main_plast.py` spracováva plastové podložky podobným spôsobom ako kovové. Vstupná snímka sa prevedie do odtieňov sivej, zmenší sa na pracovný rozmer, vyhladí mediánovým filtrom a prahovaním sa vytvorí maska objektu. Po vyčistení okrajov a morfologickom uzatvorení sa nájde hlavná kontúra podložky.

Na základe kontúry sa vypočíta stred a veľkosť oblasti, ktorá sa má orezať. Výrez sa následne zmení na rozmer `512 x 512` a náhodne otočí. Výstupom je normalizovaný obrázok plastovej podložky, ktorý má jednotný rozmer a podobné umiestnenie objektu v obraze.

Pri plastových podložkách sa používala najmä normalizácia polohy, orezanie, zmena mierky a rotácia. Tieto úpravy pomáhajú odstrániť rozdiely spôsobené polohou podložky pri snímaní.

## `main_depthmap.py`

Skript `main_depthmap.py` je určený na spracovanie hĺbkových máp. Na rozdiel od bežných fotografií sa pri hĺbkových mapách nepracuje s farbou objektu, ale s informáciou o výškovom profile povrchu.

Postup spracovania je nasledovný:

1. načítanie hĺbkovej mapy,
2. prevod na odtiene sivej,
3. vyhladenie mediánovým filtrom,
4. prahovanie pomocou Otsu metódy,
5. rozšírenie masky dilatáciou,
6. vyhľadanie súvislých komponentov,
7. výber väčších objektov podľa plochy,
8. orezanie oblasti s podložkou,
9. odstránenie rušivého okolia pomocou masky,
10. zmena veľkosti výsledku na `512 x 512` pixelov.

Pri hĺbkových mapách sa nepoužívali zmeny jasu alebo farby, pretože tieto dáta nereprezentujú klasickú RGB fotografiu. Cieľom bolo najmä izolovať objekt, odstrániť pozadie a pripraviť jednotný vstup pre modely.

## Použité knižnice

Skripty používajú knižnice:

- `cv2` - načítanie obrázkov, filtrovanie, prahovanie, kontúry, rotácie a uloženie výsledkov,
- `glob` - vyhľadanie vstupných obrázkov podľa cesty,
- `random` - náhodný výber uhla rotácie,
- `numpy` - práca s maskami a výpočty pri hĺbkových mapách.

## Poznámky k používaniu

Pred spustením skriptov je potrebné skontrolovať, či existujú vstupné a výstupné priečinky. Ak sa spracúva iná trieda ako tá, ktorá je uvedená v skripte, treba upraviť premennú `files` a výstupnú cestu `out`. Skripty automaticky preskakujú obrázky, ktoré sa nepodarí načítať.

Výstupné snímky z týchto skriptov boli použité ako základ pre ďalšie rozdelenie datasetov na trénovaciu, validačnú a testovaciu množinu.