"""Características de tres componentes (misma definición que generar_tres_componentes.py del análisis original)
para un índice de inicio arbitrario. 'idx' es el índice base 0 del disparo: la ventana empieza en idx+1."""
import numpy as np, re, sys
sys.path.insert(0,'../disparador_v2')
from senales import leer_senal
H=re.compile(r'^[NS]\d+(?:\.\d+)?[EW]$')
def ejes(orient):
    ax=[o.upper().split(';')[-1] for o in orient]
    v=[i for i,a in enumerate(ax) if a.lstrip('+-')=='V']; h=[i for i,a in enumerate(ax) if H.match(a)]
    return ax,v,h
def ortogonales(ax,h):
    b=[]
    for i in h:
        a=ax[i]; ang=float(a[1:-1]); b.append(((0 if a[0]=='N' else 180)+(ang if (a[0],a[-1]) in [('N','E'),('S','W')] else -ang))%180)
    return abs(abs(b[0]-b[1])-90)<=5
def calcular(X,orient,hz,idx,rates):
    ax,v,h=ejes(orient)
    if X.shape[1]!=3 or len(ax)!=3 or len(v)!=1 or len(h)!=2: return 'orientacion_no_confirmada',None
    if len(rates)<3 or any(abs(r-hz)>1e-6 for r in rates[:3]): return 'frecuencias_no_confirmadas',None
    if not ortogonales(ax,h): return 'horizontales_no_ortogonales',None
    end=idx+1; start=end-round(.25*hz)-round(2*hz); stop=end+round(3*hz)
    if start<0 or stop>len(X): return 'segmento_incompleto',None
    s=X[start:stop]
    if not np.isfinite(s).all(): return 'segmento_incompleto',None
    if np.any(np.ptp(s[-round(3*hz):],axis=0)==0): return 'canal_constante_en_3s',None
    bg=s[:round(2*hz)]; off=bg.mean(axis=0); pw=np.mean((bg-off)**2); vi=v[0]
    out=[]
    for sec in (1,2,3):
        w=s[end-start:end-start+round(sec*hz)]-off; z=w[:,vi]; q=z**2; hh=w[:,h]
        pk=sorted(np.max(np.abs(hh),axis=0)); en=sorted(np.sum(hh**2,axis=0)/hz)
        out.append(dict(ventana_s=sec,muestras=round(sec*hz),pico_abs_gal=np.max(np.abs(z)),rms_gal=np.sqrt(np.mean(q)),
            integral_acel_cuadrada_gal2_s=np.sum(q)/hz,media_abs_gal=np.mean(np.abs(z)),pico_a_pico_gal=np.ptp(z),
            pico_h_menor=pk[0],pico_h_mayor=pk[1],integral_h_menor=en[0],integral_h_mayor=en[1],
            integral_tres=np.sum(w**2)/hz,log_relacion_potencia=np.log1p(np.mean(w**2)/max(pw,1e-12))))
    return 'utilizable',out
