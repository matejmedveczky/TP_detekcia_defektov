# FCDD polar unwrap – výsledky a dokumentačné poznámky

## Stručný popis riešenia
Model používa FCDD prístup pre detekciu anomálií. Vstupný kruhový prstenec sa najprv prevedie do polar unwrap reprezentácie, kde horizontálna os reprezentuje uhol a vertikálna os radiálnu šírku prstenca. Sieť následne generuje anomálovú mapu. Z tejto mapy sa image-level skóre počíta ako priemer najvyšších hodnôt v maskovanej oblasti.

## Threshold
- Balanced/specificity threshold: `0.091349`
- Defect-sensitive threshold: `0.088356`
- Defect-sensitive režim bol vybraný na validácii s cieľom dosiahnuť recall defektov približne `0.90` alebo vyšší, aj za cenu vyššieho počtu false positives.

V praktickej kontrole kvality je vhodnejšie zachytiť viac potenciálne defektných kusov a poslať ich na manuálnu kontrolu, než pustiť defektný kus ako dobrý.

## Hlavné parametre
- `radial_bins`: `128`
- `angular_bins`: `512`
- `unwrap_margin_frac`: `0.0`
- `base_channels`: `32`
- `batch_size`: `8`
- `epochs`: `24`
- `lr`: `0.0001`
- `weight_decay`: `1e-06`
- `topk_ratio`: `0.0045`
- `score_center_trim_frac`: `0.13`
- `score_edge_min_weight`: `0.1`
- `score_smooth_kernel`: `3`
- `suppress_reflections`: `True`
- `illum_sigma_px`: `35.0`
- `illum_blend`: `0.5`
- `hp_sigma_r`: `1.5`
- `hp_sigma_t`: `14.0`
- `hp_blend`: `0.25`

## Výsledky
| split | mode | threshold | acc | bal_acc | auc | recall | specificity | TN | FP | FN | TP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| val | balanced | 0.091349 | 0.8112 | 0.7917 | 0.8527 | 0.8278 | 0.7556 | 34 | 11 | 26 | 125 |
| val | defect_sensitive | 0.088356 | 0.8571 | 0.8059 | 0.8527 | 0.9007 | 0.7111 | 32 | 13 | 15 | 136 |
| test | balanced | 0.091349 | 0.7839 | 0.8063 | 0.8781 | 0.7647 | 0.8478 | 39 | 7 | 36 | 117 |
| test | defect_sensitive | 0.088356 | 0.8090 | 0.7770 | 0.8781 | 0.8366 | 0.7174 | 33 | 13 | 25 | 128 |

## Vygenerované obrázky
- `training_loss.png` – priebeh tréningovej chyby
- `validation_metrics.png` – validačné metriky počas trénovania
- `val_score_histogram.png`, `test_score_histogram.png` – rozdelenie skóre pre good/anomaly
- `val_threshold_sweep.png` – vplyv thresholdu na recall/specificity/balanced accuracy
- `*_confusion_matrix.png` – confusion matrices pre oba režimy
- `heatmap_examples_categories/TP|TN|FP|FN` – príklady heatmáp podľa typu rozhodnutia