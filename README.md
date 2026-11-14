# Catalogue attributes versus early accelerograms (SASTREMORS)

Derived data and code for the manuscript "Catalogue attributes versus early accelerograms for recovering retrospective seismic-alert labels in Mexico" (submitted to Journal of Seismology).

The original accelerograms are NOT included. They are available from the strong-motion database of the Instituto de Ingenieria, UNAM (https://aplicaciones.iingen.unam.mx/AcelerogramasRSM/Inicio.aspx), under its terms of use. All tables identify records by their RAII-UNAM file name (`archivo`).

## Data (`datos/`)

| Folder | Content |
|---|---|
| `tre_data_1.0/` | Original feature matrices with the historical labels (12 attributes + label; 3,487 and 4,075 rows) |
| `etiquetas/` | Attributes recomputed from the ASA 2.0 headers (`encabezados.csv`), record-to-matrix correspondence (`empate_matriz_archivos.csv`) and corrected labels (`etiquetas_finales.csv`) |
| `disparador/` | Reference onsets and triggers of the original and corrected detectors (`cruce_v2.csv`, `disparos_final.csv`) and the tuning grid (`ajuste_grid.csv`) |
| `experimento2/` | Experiment 2 features per sample, window and configuration (`escenario_*.csv`), record-level predictions, metrics and paired bootstrap intervals |

Scenarios: E0 common sample with historical labels; E1 common sample with corrected labels; E2/E2c sample 1 with corrected/original detector; E3/E3c sample 2 with reference onset/original detector.

## Code (`codigo/`)

| Folder | Content |
|---|---|
| `etiquetas/` | ASA 2.0 reader, header parser, matching to the matrices and label audit (Python) |
| `disparador/` | Original and corrected STA/LTA detectors, reference onset and evaluation (Python and MATLAB) |
| `experimento2/` | Feature extraction and scenario building (Python), retraining in MATLAB R2021a (`ejecutar_experimento2.m`, with `c45.m` and `predict.m` from the thesis), event-grouped paired bootstrap (`bootstrap.py`, 10,000 resamples, NumPy seed 72) |
| `figuras/` | Figure script of the manuscript and Fig. 7 regeneration (`generar_fig7.py`) |

Some scripts use relative paths to the original folder layout (for example `../datos_completos/ProgramasMary/Red_en_Matlab/`); adjust them to `datos/tre_data_1.0/` and to your local copy of the RAII-UNAM records.
