import pandas as pd,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, os, sys
from senales import *; from disparadores import *
d=pd.read_csv('disparos_final.csv'); m=pd.read_csv('metadatos_disparador.csv').set_index('archivo')
q=d.query(sys.argv[2]).sample(int(sys.argv[3]),random_state=int(sys.argv[4]))
fig,ax=plt.subplots(len(q),1,figsize=(14,1.9*len(q)))
for k,(_,r) in enumerate(q.iterrows()):
    X,o=leer_senal(os.path.join('../datos_completos',r.grupo,r.archivo)); z=X[:,canal_vertical(o)]; z=z[np.isfinite(z)]; fs=r.fs; t=np.arange(len(z))/fs
    lo=max(0,min(r.t_ref,r.t_corregido if np.isfinite(r.t_corregido) else r.t_ref)-8); hi=max(r.t_ref,r.t_corregido if np.isfinite(r.t_corregido) else 0)+8
    s=(t>=lo)&(t<=hi); ax[k].plot(t[s],z[s],lw=.5,c='k')
    ax[k].axvline(r.t_ref,c='b',ls='--'); 
    if np.isfinite(r.t_corregido): ax[k].axvline(r.t_corregido,c='r'); ax[k].axvspan(r.t_corregido,r.t_corregido+3,color='r',alpha=.08)
    if np.isfinite(r.t_legado) and lo<=r.t_legado<=hi: ax[k].axvline(r.t_legado,c='orange',ls=':')
    ax[k].set_title(f'{r.archivo} {r.cat_corregido} ref={r.t_ref:.2f} corr={r.t_corregido:.2f} leg={r.t_legado:.2f} SNRref={r.snr_ref:.1f}',fontsize=8,loc='left')
plt.tight_layout(); plt.savefig(sys.argv[1],dpi=75)
