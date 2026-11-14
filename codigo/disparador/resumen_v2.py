import pandas as pd,numpy as np
d=pd.read_csv('disparos_final.csv'); m=pd.read_csv('metadatos_disparador.csv')
t=pd.read_csv('../codex/outputs/outputs/disparos_paso_2.tsv',sep='\t',encoding='utf-8-sig'); t['archivo']=t.archivo.str.split('/').str[-1]
x=d.merge(m[['grupo','archivo','estacion','evento','lat_est','lon_est','etiqueta_final','etiqueta_Mmax','etiqueta_h','etiqueta_corr','revisar','M_corr','D_corr']],on=['grupo','archivo'],how='left')
x=x.merge(t[['archivo','estado','disparo_s','ventana_3s']].rename(columns={'estado':'estado_original','disparo_s':'t_original','ventana_3s':'ventana3_original'}),on='archivo',how='left')
print('registros',len(x), x.groupby('grupo').size().to_dict())
y=x[x.t_original.notna()&x.t_legado.notna()]; same=(y.t_original-y.t_legado).abs()<=1.01/y.fs
print('original real vs reconstruccion', y.groupby('grupo').apply(lambda z:((z.t_original-z.t_legado).abs()<=1.01/z.fs).mean().round(4)).to_dict(), len(y))
ev=x[(x.snr_ref>=10)&(x.t_ref>=2.75)]
def f(z,c):
    e=z[c]-z.t_ref; return [len(z), round(100*((e>=-.5)&(e<=1)).mean(),1), round(100*(e<-.5).mean(),1), round(100*(e>1).mean(),1), round(100*e.isna().mean(),1)]
rows=[]
for k,z in ev.groupby('uso_en_ajuste'):
    for c in ['t_original','t_legado','t_corregido']: rows.append([k,c,*f(z,c)])
print(pd.DataFrame(rows,columns=['conjunto','disparador','n','correcto','temprano','tardio','sin']).to_string())
print(pd.crosstab(x.cat_corregido,x.grupo)); print(pd.crosstab(x.cat_legado,x.grupo))
cd=x.lat_est.between(19.15,19.65)&x.lon_est.between(-99.35,-98.9)
for g,z in x.groupby('grupo'):
    print(g,'CDMX %.0f%%'%(100*cd[z.index].mean()),'dist mediana',round(z.dist_epi_est_km.median() if 'dist_epi_est_km' in z else np.nan,0),
     'snr_ref<10',(z.snr_ref<10).sum(),'| ventana3 snr med leg %.1f corr %.1f | <3dB leg %.0f%% corr %.0f%%'%(z.snr_ventana3_legado.median(),z.snr_ventana3_corregido.median(),100*(z.snr_ventana3_legado<3).mean(),100*(z.snr_ventana3_corregido<3).mean()))
x.to_csv('cruce_v2.csv',index=False)
