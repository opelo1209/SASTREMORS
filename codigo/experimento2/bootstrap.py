import pandas as pd,numpy as np
p=pd.read_csv('predicciones_experimento2.csv'); m=pd.read_csv('metricas_experimento2.csv')
e=pd.read_csv('../../entrega_v2/etapa1_etiquetas/etiquetas_finales.csv')
e['ev']=e.fecha_iso.astype(str)+' '+e.hora.astype(str); ev=dict(zip(e.grupo+'/'+e.archivo,e.ev))
p['ev']=p.archivo.map(ev); assert p.ev.notna().all()
B=10000; rng=np.random.default_rng(72)
def prep(esc,mod,t):
    s=p[(p.escenario==esc)&(p.modelo==mod)&(p.ventana_s==t)].sort_values('archivo').reset_index(drop=True); return s
def eb_stats(y,q,g,G):
    # conteos por grupo para remuestreo rapido
    d=pd.DataFrame(dict(g=g,tp=(q==1)&(y==1),pos=y==1,tn=(q==0)&(y==0),neg=y==0)).groupby('g').sum().reindex(G).fillna(0).values
    return d
def eb(c): return (c[...,0]/c[...,1]+c[...,2]/c[...,3])/2
def boot(pares):
    """pares: lista de (y,q,grupos) que comparten el mismo conjunto de eventos; devuelve EB puntual y remuestreos"""
    G=sorted(set().union(*[set(g) for _,_,g in pares])); n=len(G)
    idx=rng.integers(0,n,(B,n)); W=np.zeros((B,n)); 
    for b in range(B): W[b]=np.bincount(idx[b],minlength=n)
    out=[]
    for y,q,g in pares:
        c=eb_stats(y,q,g,G); out.append((eb(c.sum(0)),eb(W@c)))
    return out,n
rows=[]
def comp(nombre,A,Bc,mismos=True):
    for t in (1,2,3):
        for mod in ['C4.5 vertical','C4.5 tres componentes','AdaBoost vertical','AdaBoost tres componentes']:
            a=prep(A,mod,t); b=prep(Bc,mod,t)
            if mismos: assert (a.archivo.values==b.archivo.values).all()
            (r,n)=boot([(a.etiqueta.values,a.prediccion.values,a.ev.values),(b.etiqueta.values,b.prediccion.values,b.ev.values)])
            (ea,ba),(eb_,bb)=r; d=(ba-bb)*100
            rows.append(dict(comparacion=nombre,ventana_s=t,modelo=mod,eventos=n,EB_A=ea,EB_B=eb_,diferencia_pp=(ea-eb_)*100,
                ic95_min_pp=np.percentile(d,2.5),ic95_max_pp=np.percentile(d,97.5),EB_A_ic95=f'{np.percentile(ba,2.5):.4f}-{np.percentile(ba,97.5):.4f}'))
# verificacion del metodo con el manuscrito: tres componentes menos vertical, E0
for t in (1,2,3):
    for fam in ['C4.5','AdaBoost']:
        a=prep('E0_original_etiqueta_historica',fam+' tres componentes',t); b=prep('E0_original_etiqueta_historica',fam+' vertical',t)
        (r,n)=boot([(a.etiqueta.values,a.prediccion.values,a.ev.values),(b.etiqueta.values,b.prediccion.values,b.ev.values)])
        d=(r[0][1]-r[1][1])*100; print('verif',fam,t,n,round((r[0][0]-r[1][0])*100,3),np.round(np.percentile(d,[2.5,97.5]),2))
comp('E1 - E0 (efecto etiquetas)','E1_original_etiqueta_final','E0_original_etiqueta_historica')
comp('E2 - E2c (disparador corregido vs original)','E2_disparo_corregido','E2c_control_disparo_original')
comp('E3 - E3c (onda P vs disparador original)','E3_onda_P_referencia','E3c_control_disparo_original')
# ganancia tres componentes - vertical en cada escenario
for esc in m.escenario.unique():
    for t in (1,2,3):
        for fam in ['C4.5','AdaBoost']:
            a=prep(esc,fam+' tres componentes',t); b=prep(esc,fam+' vertical',t)
            (r,n)=boot([(a.etiqueta.values,a.prediccion.values,a.ev.values),(b.etiqueta.values,b.prediccion.values,b.ev.values)])
            d=(r[0][1]-r[1][1])*100
            rows.append(dict(comparacion='tres componentes - vertical, '+esc,ventana_s=t,modelo=fam,eventos=n,EB_A=r[0][0],EB_B=r[1][0],
                diferencia_pp=(r[0][0]-r[1][0])*100,ic95_min_pp=np.percentile(d,2.5),ic95_max_pp=np.percentile(d,97.5),EB_A_ic95=f'{np.percentile(r[0][1],2.5):.4f}-{np.percentile(r[0][1],97.5):.4f}'))
pd.DataFrame(rows).to_csv('incertidumbre_experimento2.csv',index=False,float_format='%.4f')
