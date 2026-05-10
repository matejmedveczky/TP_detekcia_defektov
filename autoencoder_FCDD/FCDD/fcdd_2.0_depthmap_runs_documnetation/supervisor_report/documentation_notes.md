# FCDD polar unwrap – výsledky a dokumentačné poznámky

## Stručný popis riešenia
Model používa FCDD prístup pre detekciu anomálií. Vstupný kruhový prstenec sa najprv prevedie do polar unwrap reprezentácie, kde horizontálna os reprezentuje uhol a vertikálna os radiálnu šírku prstenca. Sieť následne generuje anomálovú mapu. Z tejto mapy sa image-level skóre počíta ako priemer najvyšších hodnôt v maskovanej oblasti.

## Threshold
- Balanced/specificity threshold: `0.268935`
- Defect-sensitive threshold: `0.268935`
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
- `topk_ratio`: `0.015`
- `score_center_trim_frac`: `0.13`
- `score_edge_min_weight`: `0.1`
- `score_smooth_kernel`: `5`
- `suppress_reflections`: `False`
- `illum_sigma_px`: `35.0`
- `illum_blend`: `0.5`
- `hp_sigma_r`: `1.5`
- `hp_sigma_t`: `14.0`
- `hp_blend`: `0.25`

## Výsledky
| split | mode | threshold | acc | bal_acc | auc | recall | specificity | TN | FP | FN | TP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| val | balanced | 0.268935 | 0.9375 | 0.9373 | 0.9216 | 0.9333 | 0.9412 | 16 | 1 | 1 | 14 |
| val | defect_sensitive | 0.268935 | 0.9375 | 0.9373 | 0.9216 | 0.9333 | 0.9412 | 16 | 1 | 1 | 14 |
| test | balanced | 0.268935 | 0.9333 | 0.9375 | 1.0000 | 1.0000 | 0.8750 | 7 | 1 | 0 | 7 |
| test | defect_sensitive | 0.268935 | 0.9333 | 0.9375 | 1.0000 | 1.0000 | 0.8750 | 7 | 1 | 0 | 7 |

## Vygenerované obrázky
- `training_loss.png` – priebeh tréningovej chyby
- `validation_metrics.png` – validačné metriky počas trénovania
- `val_score_histogram.png`, `test_score_histogram.png` – rozdelenie skóre pre good/anomaly
- `val_threshold_sweep.png` – vplyv thresholdu na recall/specificity/balanced accuracy
- `*_confusion_matrix.png` – confusion matrices pre oba režimy
- `heatmap_examples_categories/TP|TN|FP|FN` – príklady heatmáp podľa typu rozhodnutia