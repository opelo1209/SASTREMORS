import pandas as pd,numpy as np,os,itertools,pickle
from senales import leer_senal, canal_vertical
from disparadores import *
d=pd.read_csv('variantes.csv'); m=pd.read_csv('metadatos_disparador.csv').set_index('archivo')
d=d[d.error.isna()&(d.snr_ref>=10)&(d.t_ref>=2.75)]
rng=np.random.default_rng(72)
dev=d[d.grupo=='Temblores_1964-1999'].sample(frac=0.5,random_state=72)
val=d[(d.grupo=='Temblores_1964-1999')&~d.archivo.isin(dev.archivo)]
tst=d[d.grupo=='Temblores_2000-2020']
def cargar(df):
    out=[]
    for _,r in df.iterrows():
        X,o=leer_senal(os.path.join('../datos_completos',r.grupo,r.archivo)); z=X[:,canal_vertical(o)]; z=z[np.isfinite(z)]
        out.append((z,r.fs,r.t_ref))
    return out
D=cargar(dev); print('dev',len(D))
grid=list(itertools.product([3,4,5,6,8],[0.1,0.2,0.3],[0.0,0.005,0.01,0.02,0.05],[0,1,3],[0.0,0.25]))
res=[]
for u,du,pa,kq,cf in grid:
    e=[]
    for z,fs,tr in D:
        j=disparo_corregido(z,fs,umbral=u,dur=du,piso_abs=pa,k_q=kq,confirmar=cf)
        e.append(np.nan if j is None else j/fs-tr)
    e=np.array(e)
    res.append(dict(umbral=u,dur=du,piso_abs=pa,k_q=kq,confirmar=cf,temprano=np.mean(e<-0.5),correcto=np.mean((e>=-0.5)&(e<=1)),tardio=np.mean(e>1),sin=np.mean(np.isnan(e))))
R=pd.DataFrame(res); R.to_csv('ajuste_grid.csv',index=False)
print(R.sort_values('correcto',ascending=False).head(15).round(3).to_string(index=False))
print(R[R.temprano<=0.03].sort_values('correcto',ascending=False).head(10).round(3).to_string(index=False))
pickle.dump(dict(val=list(val.archivo),tst=list(tst.archivo),dev=list(dev.archivo)),open('particion_ajuste.pkl','wb'))
