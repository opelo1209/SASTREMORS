import numpy as np
from scipy.signal import butter, lfilter, sosfilt
def bp(x,fs,f1=1,f2=10,orden=2):
    sos=butter(orden,[f1,min(f2,0.45*fs)],btype='band',fs=fs,output='sos'); return sosfilt(sos,x)
def sta_lta(y2,fs,sta=0.25,lta=2.0):
    """STA = media de y^2 en los últimos sta s; LTA = media en los lta s que preceden a la ventana STA (causal)."""
    ns,nl=int(round(sta*fs)),int(round(lta*fs)); c=np.r_[0,np.cumsum(y2)]
    n=len(y2); r=np.full(n,np.nan); i=np.arange(ns+nl-1,n)
    S=(c[i+1]-c[i+1-ns])/ns; L=(c[i+1-ns]-c[i+1-ns-nl])/nl
    r[i]=S/np.maximum(L,1e-20); return r
def disparo_legado(z,fs,umbral=4,dur=0.10):
    """Reproduce la sección 4.2: Butterworth causal 2º orden 1–10 Hz, STA 0.25 s / LTA 2 s, ratio>=umbral durante 0.10 s."""
    y=bp(z,fs); r=sta_lta(y**2,fs); k=int(round(dur*fs))
    ok=np.nan_to_num(r)>=umbral
    run=np.convolve(ok.astype(int),np.ones(k,int),'full')[:len(ok)]
    j=np.where(run>=k)[0]
    return (int(j[0]) if len(j) else None), r
def aic_pick(z,i0,i1):
    """Picado AIC (Maeda 1985) no causal en z[i0:i1]."""
    x=z[i0:i1]-np.mean(z[i0:i1]); n=len(x)
    if n<20: return None
    k=np.arange(1,n-1); c=np.cumsum(x**2); 
    v1=np.array([np.var(x[:j]) for j in k]) if n<2000 else None
    # versión vectorizada
    s1=np.cumsum(x); s2=np.cumsum(x**2)
    m1=s1[k-1]/k; var1=s2[k-1]/k-m1**2
    m2=(s1[-1]-s1[k-1])/(n-k); var2=(s2[-1]-s2[k-1])/(n-k)-m2**2
    a=k*np.log(np.maximum(var1,1e-20))+(n-k-1)*np.log(np.maximum(var2,1e-20))
    return i0+int(k[np.argmin(a)])

def referencia_P(z,fs):
    """Inicio de referencia NO causal (solo para evaluar, nunca como disparador):
    1) filtro 1–10 Hz de fase cero; 2) tiempo t5 en que la energía acumulada llega al 5 %;
    3) AIC en [t5-20 s, t5+1 s]; 4) AIC refinado en ±1.5 s. Devuelve (índice, calidad=SNR en dB)."""
    from scipy.signal import sosfiltfilt
    sos=butter(2,[1,min(10,0.45*fs)],btype='band',fs=fs,output='sos'); y=sosfiltfilt(sos,z-np.mean(z[:max(10,int(fs))]))
    e=np.cumsum(y**2); 
    if e[-1]<=0: return None,np.nan
    i5=int(np.searchsorted(e,0.05*e[-1]))
    a=aic_pick(y,max(0,i5-int(20*fs)),min(len(y),i5+int(1*fs)))
    if a is None: return None,np.nan
    b=aic_pick(y,max(0,a-int(1.5*fs)),min(len(y),a+int(1.5*fs))) or a
    pre=y[max(0,b-int(2*fs)):b]; pos=y[b:b+int(2*fs)]
    snr=10*np.log10(np.mean(pos**2)/max(np.mean(pre**2),1e-20)) if len(pre)>10 and len(pos)>10 else np.nan
    return b,snr

def disparo_corregido(z,fs,umbral=4.0,dur=0.10,sta=0.25,lta=2.0,arranque=True,despike=True,piso=True,confirmar=0.0,piso_abs=0.02,k_q=3.0):
    """Disparador causal corregido. Cambios respecto al legado:
    arranque : el filtro se inicializa en estado estacionario con la primera muestra (evita el transitorio del
               desplazamiento DC) y no se permite disparar antes de sta+lta+0.5 s.
    despike  : mediana causal de 3 muestras (retardo de 1 muestra) para eliminar picos de una sola muestra.
    piso     : LTA efectivo = max(LTA, (max(piso_abs, k_q*paso_de_cuantizacion))^2); el paso se estima solo con
               muestras anteriores (primer segundo), evita razones enormes en trazas casi constantes.
    confirmar: si >0, exige que la razón siga >= umbral/2 durante 'confirmar' s; el disparo se emite al confirmar."""
    from scipy.signal import sosfilt_zi
    x=np.asarray(z,float)
    if despike:
        xp=np.r_[x[0],x[0],x]; x=np.median(np.c_[xp[:-2],xp[1:-1],xp[2:]],axis=1)
    sos=butter(2,[1,min(10,0.45*fs)],btype='band',fs=fs,output='sos')
    if arranque:
        zi=sosfilt_zi(sos)*x[0]; y,_=sosfilt(sos,x,zi=zi)
    else: y=sosfilt(sos,x)
    ns,nl=int(round(sta*fs)),int(round(lta*fs)); c=np.r_[0,np.cumsum(y**2)]; n=len(y)
    i=np.arange(ns+nl-1,n); S=(c[i+1]-c[i+1-ns])/ns; L=(c[i+1-ns]-c[i+1-ns-nl])/nl
    if piso:
        u=np.unique(np.round(x[:max(int(fs),10)],6)); q=np.min(np.diff(u)) if len(u)>1 else 0.0
        L=np.maximum(L,max(piso_abs,k_q*q)**2*0.1)
    r=np.full(n,np.nan); r[i]=S/np.maximum(L,1e-20)
    i0=ns+nl-1+(int(0.5*fs) if arranque else 0)
    ok=np.nan_to_num(r)>=umbral; ok[:i0]=False
    k=max(1,int(round(dur*fs))); run=np.convolve(ok.astype(int),np.ones(k,int),'full')[:n]
    cand=np.where(run>=k)[0]
    if not len(cand): return None
    if confirmar<=0: return int(cand[0])
    kc=int(round(confirmar*fs)); ok2=np.nan_to_num(r)>=umbral/2
    # recorrer candidatos hasta uno confirmado
    j=0
    while j<len(cand):
        t=cand[j]
        if t+kc<n and ok2[t:t+kc].all(): return int(t+kc)
        # saltar al siguiente candidato después del fallo
        nxt=np.searchsorted(cand,t+kc); j=max(j+1,nxt)
    return None

def referencia_P2(z,fs,snr_min=6.0,max_iter=6):
    """Referencia NO causal v2. Parte de referencia_P y busca hacia atrás una llegada más temprana:
    AIC en [b-60 s, b-0.5 s]; se acepta si la energía 1–10 Hz de los 2 s posteriores supera en >= snr_min dB
    a la de los 2 s anteriores y la energía se mantiene elevada hasta b (mediana de RMS por segundo
    >= 2 veces el ruido previo), lo que descarta picos aislados. Devuelve (índice, SNR, n_retrocesos)."""
    from scipy.signal import sosfiltfilt
    b,snr=referencia_P(z,fs)
    if b is None: return None,np.nan,0
    sos=butter(2,[1,min(10,0.45*fs)],btype='band',fs=fs,output='sos'); y=sosfiltfilt(sos,z-np.mean(z[:max(10,int(fs))]))
    n2=int(2*fs); it=0
    while it<max_iter:
        i0=max(0,b-int(60*fs)); i1=b-int(0.5*fs)
        if i1-i0<int(3*fs): break
        a=aic_pick(y,i0,i1)
        if a is None or a<n2: break
        pre=np.mean(y[a-n2:a]**2); pos=np.mean(y[a:a+n2]**2)
        s=10*np.log10(pos/max(pre,1e-20))
        seg=y[a:b]; 
        if len(seg)<int(fs): break
        rms=np.sqrt(np.mean(seg[:len(seg)//int(fs)*int(fs)].reshape(-1,int(fs))**2,axis=1))
        if s>=snr_min and np.median(rms)>=2*np.sqrt(pre):
            b=a; snr=s; it+=1
        else: break
    return b,snr,it
