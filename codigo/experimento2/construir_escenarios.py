import pandas as pd,numpy as np
from collections import Counter
R=pd.read_pickle('caracteristicas_todas.pkl')
x=pd.read_csv('../disparador_v2/cruce_v2.csv')
o=pd.read_csv('../codex/outputs/outputs/caracteristicas_tres_componentes.csv',encoding='utf-8-sig')
exc=set(pd.read_csv('../codex/outputs/outputs/exclusiones_paso_4.csv',encoding='utf-8-sig').archivo)
o=o[~o.archivo.isin(exc)].copy(); o['arch']=o.archivo.str.split('/').str[-1]
F=['pico_abs_gal','rms_gal','integral_acel_cuadrada_gal2_s','media_abs_gal','pico_a_pico_gal','pico_h_menor','pico_h_mayor','integral_h_menor','integral_h_mayor','integral_tres','log_relacion_potencia']
lab=dict(zip(x.archivo,x.etiqueta_final))
def guardar(df,nombre):
    df=df[['periodo','archivo','ventana_s','etiqueta']+F]; df.to_csv(f'matlab/escenario_{nombre}.csv',index=False)
    for t in (3,):
        s=df[df.ventana_s==t]; print(nombre,{p:(len(g),int(g.etiqueta.sum())) for p,g in s.groupby('periodo')})
# E0/E1
e0=o.rename(columns={'etiqueta_historica':'etiqueta'}); guardar(e0,'E0_original_etiqueta_historica')
e1=e0.copy(); e1['etiqueta']=e1.arch.map(lab); assert e1.etiqueta.notna().all(); e1['etiqueta']=e1.etiqueta.astype(int); guardar(e1,'E1_original_etiqueta_final')
print('cambios E1 vs E0 (3 s):',Counter(zip(e0[e0.ventana_s==3].etiqueta,e1[e1.ventana_s==3].etiqueta)))
# Elegibilidad comun para E2/E3
base=x[~x.estado_original.isin(['senal_o_frecuencia_no_utilizable','inicio_incompleto_declarado'])]
base=base[~(base.grupo+'/'+base.archivo).isin(exc) & base.etiqueta_final.notna()]
def filas(sub,clave):
    out=[]
    for _,r in sub.iterrows():
        st=R[r.archivo].get(clave)
        if st is None or st[0]!='utilizable': continue
        for f in st[1]: out.append(dict(periodo=r.grupo.split('_')[1],archivo=r.grupo+'/'+r.archivo,etiqueta=int(r.etiqueta_final),**f))
    return pd.DataFrame(out)
def ok(a,c): s=R[a].get(c); return s is not None and s[0]=='utilizable'
s2=base[base.t_corregido.notna() & base.t_original.notna()]
s2=s2[[ok(a,'corregido') and ok(a,'original') for a in s2.archivo]]
guardar(filas(s2,'corregido'),'E2_disparo_corregido'); guardar(filas(s2,'original'),'E2c_control_disparo_original')
s3=base[(base.snr_ref>=10)&(base.t_ref>=2.75)&base.t_original.notna()]
s3=s3[[ok(a,'referencia') and ok(a,'original') for a in s3.archivo]]
guardar(filas(s3,'referencia'),'E3_onda_P_referencia'); guardar(filas(s3,'original'),'E3c_control_disparo_original')
print('motivos no utilizable corregido:',Counter(R[a]['corregido'][0] for a in base.archivo if 'corregido' in R[a]))
