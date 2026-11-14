import pandas as pd, numpy as np, os, pickle
from multiprocessing import Pool
from senales import leer_senal, canal_vertical
from disparadores import *
CFG=dict(umbral=5,dur=0.2,piso_abs=0.02,k_q=1,confirmar=0.0)
m=pd.read_csv('metadatos_disparador.csv')
def snr_causal(z,fs,j,win=3.0):
    """SNR causal de la ventana: energía 1–10 Hz en [j, j+win] frente a los 2 s previos (fondo)."""
    y=bp(z-z[0],fs); a=y[j:j+int(win*fs)]; b=y[max(0,j-int(2*fs)):j]
    return 10*np.log10(np.mean(a**2)/max(np.mean(b**2),1e-20)) if len(a)>5 and len(b)>5 else np.nan
def proc(r):
    out=dict(grupo=r['grupo'],archivo=r['archivo'])
    try:
        X,o=leer_senal(os.path.join('../datos_completos',r['grupo'],r['archivo'])); v=canal_vertical(o); fs=1/r['dt_s']
        if v is None: out['error']='sin_vertical'; return out
        z=X[:,v]; z=z[np.isfinite(z)]
        if len(z)<fs*5 or np.ptp(z)==0: out['error']='traza_corta_o_constante'; return out
        out['fs']=fs; out['dur']=len(z)/fs
        jr,snr,it=referencia_P2(z,fs); out['t_ref']=jr/fs if jr is not None else np.nan; out['snr_ref']=snr; out['retrocesos_ref']=it
        jl=disparo_legado(z,fs)[0]; jc=disparo_corregido(z,fs,**CFG)
        out['t_legado']=jl/fs if jl is not None else np.nan; out['t_corregido']=jc/fs if jc is not None else np.nan
        out['snr_ventana3_legado']=snr_causal(z,fs,jl) if jl is not None else np.nan
        out['snr_ventana3_corregido']=snr_causal(z,fs,jc) if jc is not None else np.nan
        out['ventana3_completa_corregido']=bool(jc is not None and jc+int(3*fs)<=len(z))
    except Exception as e: out['error']=repr(e)[:100]
    return out
if __name__=='__main__':
    with Pool(max(2,os.cpu_count())) as P: res=P.map(proc,[r for _,r in m.iterrows()],chunksize=25)
    d=pd.DataFrame(res)
    part=pickle.load(open('particion_ajuste.pkl','rb'))
    d['uso_en_ajuste']=np.where(d.archivo.isin(part['dev']),'desarrollo',np.where(d.grupo.str.contains('1964'),'validacion_1964_1999','prueba_2000_2020'))
    fiable=(d.snr_ref>=10)
    def cat(t,tr,f):
        if not f: return 'referencia_no_fiable'
        if tr<2.75: return 'P_antes_de_que_opere_el_detector'
        if np.isnan(t): return 'sin_disparo'
        e=t-tr
        return 'temprano' if e<-0.5 else ('tardio' if e>1 else 'correcto')
    for v in ['legado','corregido']:
        d['cat_'+v]=[cat(t,tr,f) if pd.isna(er) else 'error_lectura' for t,tr,f,er in zip(d['t_'+v],d.t_ref,fiable,d.get('error',pd.Series([np.nan]*len(d))))]
    d.to_csv('disparos_final.csv',index=False)
    print(pd.crosstab([d.grupo,d.cat_legado],d.cat_corregido,margins=True))
