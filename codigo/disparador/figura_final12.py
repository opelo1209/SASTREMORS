import pandas as pd,numpy as np,matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, os, sys
from senales import *; from disparadores import *
d=pd.read_csv('disparos_final.csv').set_index('archivo')
L=sys.argv[2].split(',')
fig,ax=plt.subplots(len(L),2,figsize=(15,2.4*len(L)),gridspec_kw=dict(width_ratios=[3,1.3]))
for k,a in enumerate(L):
    r=d.loc[a]; X,o=leer_senal(os.path.join('../datos_completos',r.grupo,a)); z=X[:,canal_vertical(o)]; z=z[np.isfinite(z)]; fs=r.fs; t=np.arange(len(z))/fs
    for j,axx in enumerate(ax[k]):
        axx.plot(t,z,lw=.5,c='k')
        if np.isfinite(r.t_legado): axx.axvline(r.t_legado,c='orange',lw=1.3,ls=':',label='disparo original')
        if np.isfinite(r.t_corregido): axx.axvline(r.t_corregido,c='r',lw=1.3,label='disparo corregido'); axx.axvspan(r.t_corregido,r.t_corregido+3,color='r',alpha=.08)
        if np.isfinite(r.t_ref): axx.axvline(r.t_ref,c='b',ls='--',lw=1.2,label='referencia P (no causal)')
        axx.tick_params(labelsize=8)
    c=r.t_ref if np.isfinite(r.t_ref) else 5
    ax[k,1].set_xlim(c-4,c+5)
    ax[k,0].set_title(f'{a} | {fs:.0f} Hz | original {r.t_legado:.2f} s | corregido {r.t_corregido:.2f} s | ref. {r.t_ref:.2f} s (SNR {r.snr_ref:.0f} dB) | {r.cat_corregido.replace("_"," ")}',fontsize=9,loc='left')
    ax[k,1].set_title('acercamiento a la referencia',fontsize=8,loc='left')
ax[0,0].legend(fontsize=7,loc='upper right',ncol=3); ax[-1,0].set_xlabel('Segundos desde la primera muestra'); 
plt.suptitle(sys.argv[3],fontsize=11); plt.tight_layout(); plt.savefig(sys.argv[1],dpi=90)
