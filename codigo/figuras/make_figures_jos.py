"""Journal of Seismology figures for the merged SASTREMORS manuscript.

All panels are regenerated from the source data (legacy tre-data matrices, audit tables,
trigger table, metric CSVs and the extracted traces), in English, as vector PDF.
Usage: python -I figuras_jos.py <thesis_dir> <outputs_dir> <signals_npz> <dest_dir>
"""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, sosfilt

THESIS, OUT, NPZ, DEST = map(Path, sys.argv[1:5])
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
                     'font.size': 8, 'axes.titlesize': 8, 'axes.labelsize': 8, 'legend.fontsize': 7,
                     'xtick.labelsize': 7, 'ytick.labelsize': 7, 'axes.linewidth': 0.6,
                     'lines.linewidth': 0.9, 'pdf.fonttype': 42,
                     'axes.spines.top': False, 'axes.spines.right': False})
META = {'Creator': None, 'Producer': None, 'CreationDate': None}
MM = 1 / 25.4
COL, FULL = 84 * MM, 174 * MM
C_NEG, C_POS = '#8a8a8a', '#c0392b'          # no alert / alert
C_OLD, C_NEW = '#1f5f9e', '#d98c1f'          # 1964-1999 / 2000-2020


def save(fig, name):
    fig.savefig(DEST / name, metadata=META)
    plt.close(fig)
    print('wrote', name)


# ------------------------------------------------------------------ data
mats = {p: np.loadtxt(THESIS / f'Datos_{p.replace("-", "_")}.dat') for p in ('1964-1999', '2000-2020')}
with open(OUT / 'inventario_paso_1.tsv', encoding='utf-8-sig', newline='') as f:
    links = list(csv.DictReader(f, delimiter='\t'))
assert len(links) == 7562


def year(row):
    raw = row['fecha_original'].strip()
    m = re.search(r'(1[89]\d\d|20\d\d)', raw)
    if m:
        return int(m.group(1))
    yy = int(re.split(r'[/\- ]', raw)[-1])
    return (2000 if row['periodo'] == '2000-2020' else 1900) + yy


years = Counter()
bad = 0
for r in links:
    try:
        years[(year(r), int(float(r['etiqueta'])))] += 1
    except (ValueError, IndexError):
        bad += 1
print('records without parseable year:', bad)

# ------------------------------------------------------------------ Fig: data overview
fig, ax = plt.subplots(2, 2, figsize=(FULL, 112 * MM), layout='constrained')
a = ax[0, 0]
ys = np.arange(1964, 2021)
neg = np.array([years[(y, 0)] for y in ys]); pos = np.array([years[(y, 1)] for y in ys])
a.bar(ys, neg, width=0.85, color=C_NEG, label='No alert (0)')
a.bar(ys, pos, width=0.85, bottom=neg, color=C_POS, label='Alert (1)')
a.axvline(1999.5, color='k', lw=0.6, ls='--')
a.text(1999, a.get_ylim()[1] * 0.93, '1964–1999 ', ha='right', fontsize=7)
a.text(2000, a.get_ylim()[1] * 0.93, ' 2000–2020', ha='left', fontsize=7)
a.set_xlabel('Year of event'); a.set_ylabel('Accelerograms'); a.legend(frameon=False, loc='upper left')
a.set_title('(a) Archive composition', loc='left')

a = ax[0, 1]
for p, mk, col in (('1964-1999', 'o', C_OLD), ('2000-2020', '^', C_NEW)):
    m = mats[p]
    a.scatter(m[:, 11], m[:, 1], s=2.5, marker=mk, facecolors='none', edgecolors=col, linewidths=0.4,
              alpha=0.6, label=p, rasterized=True)
# rule boundary: alert if (M>5 & D<=250) | (M>5.5 & D<=350) | (M>6)
bx = [5.0, 5.0, 5.5, 5.5, 6.0, 6.0]; by = [5, 250, 250, 350, 350, 20000]
a.plot(bx, by, color='k', lw=1.0)
a.text(7.0, 20, 'alert', fontsize=7); a.text(3.0, 2000, 'no alert', fontsize=7)
a.set_yscale('log'); a.set_xlim(0, 8.5); a.set_ylim(5, 20000)
a.set_xlabel('Catalogue magnitude $M$'); a.set_ylabel('Distance $D$ to reference point (km)')
a.legend(frameon=False, loc='upper left', markerscale=3)
a.set_title('(b) Records in the labelling plane (Eq. 5)', loc='left')

a = ax[1, 0]
bins = np.arange(0, 525, 12.5)
for p, col in (('1964-1999', C_OLD), ('2000-2020', C_NEW)):
    a.hist(mats[p][:, 2], bins=bins, color=col, alpha=0.55, label=p, weights=np.full(len(mats[p]), 100 / len(mats[p])))
a.set_xlabel('Sensor natural frequency, channel 1 (Hz)'); a.set_ylabel('Records (%)')
a.legend(frameon=False); a.set_title('(c) Instrument attribute', loc='left')

a = ax[1, 1]
bins = np.arange(0, 225, 7.5)
for p, col in (('1964-1999', C_OLD), ('2000-2020', C_NEW)):
    a.hist(mats[p][:, 0], bins=bins, color=col, alpha=0.55, label=p, weights=np.full(len(mats[p]), 100 / len(mats[p])))
a.set_xlabel('Focal depth (km)'); a.set_ylabel('Records (%)')
a.legend(frameon=False); a.set_title('(d) Event attribute', loc='left')
save(fig, 'Fig1.pdf')

# ------------------------------------------------------------------ Fig: trigger examples
sig = np.load(NPZ)
trig = {}
with open(OUT / 'disparos_paso_2.tsv', encoding='utf-8-sig', newline='') as f:
    for r in csv.DictReader(f, delimiter='\t'):
        trig[r['archivo'].split('/')[-1]] = float(r['disparo_s']) if r['disparo_s'] else None
ref = {}
with open(OUT / 'llegadas_onda_p.csv', encoding='utf-8-sig', newline='') as f:
    for r in csv.DictReader(f):
        ref[r['archivo']] = (float(r['intervalo_min_s']), float(r['intervalo_max_s']))


def ratio(trace, hz):
    short, long_ = round(hz * .25), round(hz * 2)
    x = sosfilt(butter(2, [1, 10], btype='bandpass', fs=hz, output='sos'), trace - trace[0])
    e = np.r_[0., np.cumsum(x ** 2)]
    ends = np.arange(short + long_, len(e))
    rec = (e[ends] - e[ends - short]) / short
    bg = (e[ends - short] - e[ends - short - long_]) / long_
    return (ends - 1) / hz, rec / np.maximum(bg, np.finfo(float).eps)


examples = [('1964-02', '(a) Trigger within the reference P interval'),
            ('1964-01', '(b) Early trigger on pre-event noise')]
fig, ax = plt.subplots(2, 2, figsize=(FULL, 78 * MM), layout='constrained', sharex='col',
                       gridspec_kw={'height_ratios': [1.4, 1]})
for j, (key, title) in enumerate(examples):
    name = str(sig[key + '_name']); hz = float(sig[key + '_hz']); s = sig[key]
    t = np.arange(len(s)) / hz
    lo, hi = ref[name]; tg = trig[name]
    a = ax[0, j]
    a.plot(t, s - np.median(s[:int(hz)]), color='#135268', lw=0.4)
    a.axvspan(lo, hi, color='#2e8b57', alpha=0.35, lw=0, label='reference P interval')
    a.axvline(tg, color=C_POS, lw=0.9, ls='--', label='automatic trigger')
    a.axvspan(tg, tg + 3, color=C_POS, alpha=0.10, lw=0, label='3-s feature window')
    a.set_ylabel('Vertical accel. (gal)'); a.set_title(f'{title}: {name}, {hz:g} Hz', loc='left')
    if j == 0:
        a.legend(frameon=False, loc='upper right')
    tr, rr = ratio(s, hz)
    b = ax[1, j]
    b.semilogy(tr, rr, color='#444444', lw=0.5)
    b.axhline(4, color=C_POS, lw=0.6, ls=':')
    b.axvline(tg, color=C_POS, lw=0.9, ls='--')
    b.axvspan(lo, hi, color='#2e8b57', alpha=0.35, lw=0)
    b.set_ylabel('STA/LTA'); b.set_xlabel('Time since first sample (s)')
    b.set_xlim(0, t[-1])
save(fig, 'Fig4.pdf')

# ------------------------------------------------------------------ Fig: operating points
def rows(path):
    with open(OUT / path, encoding='utf-8-sig') as f:
        return [r for r in csv.DictReader(f) if r.get('estado', 'ok') == 'ok']


fig, a = plt.subplots(figsize=(COL, 80 * MM), layout='constrained')
a.plot([0, 1], [0, 1], color='#999999', lw=0.6, ls='--')
screen = rows('metricas_algoritmos_paso_4.csv') + rows('metricas_bpnn_paso_4.csv') + rows('metricas_variantes_paso_4.csv')
pts = [(float(r['tasa_falsas_alarmas']), float(r['sensibilidad'])) for r in screen if r['ventana_s'] == '3']
with open(OUT / 'metricas_c45_paso_4.csv', encoding='utf-8-sig') as f:
    pts += [(float(r['tasa_falsas_alarmas']), float(r['sensibilidad'])) for r in csv.DictReader(f) if r['ventana_s'] == '3']
a.scatter(*zip(*pts), s=10, marker='o', facecolors='none', edgecolors='#777777', linewidths=0.6,
          label=f'Exp. 2, vertical features ({len(pts)} models)')
tc = {r['modelo']: r for r in rows('metricas_tres_componentes.csv') if r['ventana_s'] == '3'}
for k, mk in (('AdaBoost tres componentes', 's'), ('C4.5 tres componentes', 'D')):
    r = tc[k]
    a.scatter(float(r['tasa_falsas_alarmas']), float(r['sensibilidad']), s=18, marker=mk, color=C_NEW,
              label='Exp. 2, three-comp., ' + ('AdaBoostM1' if k.startswith('Ada') else 'legacy tree'))
cat = {'Legacy tree': (688, 18, 3, 2778), 'BP-ANN': (651, 55, 56, 2725), 'Decision tables': (678, 28, 165, 2616),
       'Naive Bayes': (456, 250, 715, 2066), '$k$-NN': (423, 283, 1048, 1733)}
first = True
for n, (tp, fn, fp, tn) in cat.items():
    x, y = fp / (fp + tn), tp / (tp + fn)
    a.scatter(x, y, s=14, marker='^', color=C_OLD, label='Exp. 1, catalogue attributes' if first else None)
    place = {'Legacy tree': (0.16, 0.985), 'Decision tables': (0.16, 0.925), 'BP-ANN': (0.16, 0.865)}
    if n in place:
        a.annotate(n, (x, y), xytext=place[n], textcoords='data', fontsize=6, color=C_OLD, va='center',
                   arrowprops=dict(arrowstyle='-', color=C_OLD, lw=0.4, shrinkA=0, shrinkB=2))
    else:
        a.annotate(n, (x, y), xytext=(4, -2), textcoords='offset points', fontsize=6, color=C_OLD)
    first = False
a.scatter(0, 1, s=22, marker='*', color='k', label='Eq. 5 applied directly', zorder=5)
a.set_xlim(-0.02, 1.0); a.set_ylim(0, 1.03)
a.set_xlabel('False-alarm rate'); a.set_ylabel('Sensitivity')
a.legend(frameon=False, loc='lower right', fontsize=6)
save(fig, 'Fig6.pdf')

# ------------------------------------------------------------------ Fig: paired gain
with open(OUT / 'incertidumbre_tres_componentes.csv', encoding='utf-8-sig') as f:
    unc = list(csv.DictReader(f))
fig, a = plt.subplots(figsize=(COL, 58 * MM), layout='constrained')
for k, (lab, col, mk, dx) in {'AdaBoost': ('AdaBoostM1', C_NEW, 's', -0.06),
                              'C4.5': ('Legacy tree', C_OLD, 'D', 0.06)}.items():
    rr = sorted((r for r in unc if r['modelo'] == k), key=lambda r: int(r['ventana_s']))
    x = np.array([int(r['ventana_s']) for r in rr]) + dx
    y = np.array([float(r['diferencia_pp']) for r in rr])
    lo = y - np.array([float(r['ic95_min_pp']) for r in rr]); hi = np.array([float(r['ic95_max_pp']) for r in rr]) - y
    a.errorbar(x, y, yerr=[lo, hi], fmt=mk + '-', color=col, ms=4, capsize=2.5, lw=0.9, label=lab)
a.axhline(0, color='#999999', lw=0.6, ls='--')
a.set_xticks([1, 2, 3]); a.set_xlabel('Window after trigger (s)')
a.set_ylabel('Gain in balanced accuracy (pp)'); a.legend(frameon=False, loc='upper left')
save(fig, 'Fig7.pdf')
