"""Ejecuta solo el bloque de la Figura 7 de make_figures_jos.py, sin modificarlo.
Uso: python generar_fig7.py <carpeta_con_incertidumbre_tres_componentes.csv> <carpeta_destino>"""
import sys
from pathlib import Path
src = (Path(__file__).parent / 'make_figures_jos.py').read_text(encoding='utf-8')
pre = src[:src.index('# ------------------------------------------------------------------ data')]
fig7 = src[src.index('# ------------------------------------------------------------------ Fig: paired gain'):]
pre = pre.replace('THESIS, OUT, NPZ, DEST = map(Path, sys.argv[1:5])', 'OUT, DEST = map(Path, sys.argv[1:3])')
# Si Arial no está instalada (Linux), usa Liberation Sans, que tiene las mismas métricas.
pre += "\nplt.rcParams['font.sans-serif'] = ['Arial', 'Liberation Sans', 'Helvetica', 'DejaVu Sans']\n"
exec(compile(pre + fig7, 'make_figures_jos.py[Fig7]', 'exec'))
