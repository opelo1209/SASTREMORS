import pandas as pd, numpy as np
p=pd.read_csv('encabezados.csv'); e=pd.read_csv('empate_matriz_archivos.csv')
cols=['prof','D','fn1','fn2','fn3','am1','am2','am3','pga1','pga2','pga3','M','etiqueta']
ms=[]
for g,f in [('Temblores_1964-1999','Datos_1964_1999.dat'),('Temblores_2000-2020','Datos_2000_2020.dat')]:
    m=pd.read_csv('../datos_completos/ProgramasMary/Red_en_Matlab/'+f,sep=r'\s+',header=None,names=cols); m['fila']=np.arange(1,len(m)+1); m['grupo']=g; ms.append(m)
m=pd.concat(ms).add_suffix('_h').rename(columns={'fila_h':'fila','grupo_h':'grupo'})
x=e.merge(m,on=['grupo','fila']).merge(p,on=['grupo','archivo'],how='left')
x.to_pickle('x.pkl')
xm=x[x.archivo.notna()]
print('D_h == D_literal:',np.isclose(xm.D_h,xm.D_literal,atol=0.5).mean(), ' == D_corr:',np.isclose(xm.D_h,xm.D_corr,atol=0.5).mean())
bad=xm[~np.isclose(xm.D_h,xm.D_literal,atol=0.5)]
print('D no reproducido:',len(bad)); print(bad[['archivo','D_h','D_literal','D_corr','lat_epi','lon_epi']].head(10))
mc=[c for c in p.columns if c.startswith('M_')]
for c in mc: print(c, 'igual a M_h:', np.isclose(xm.M_h,xm[c],atol=0.006).sum(),'de',xm[c].notna().sum())
# regla: primer magnitud listada?
first=xm.magnitudes.str.extract(r'=\s*([-+]?\d+(?:\.\d+)?)')[0].astype(float)
print('M_h == primera magnitud:',np.isclose(xm.M_h,first,atol=0.006).sum(),'/',len(xm))
mx=xm[mc].max(axis=1); print('M_h == max:',np.isclose(xm.M_h,mx,atol=0.006).sum())
print('M_h==0:',(xm.M_h==0).sum(), ' de ellos con alguna magnitud en hdr:',((xm.M_h==0)&xm[mc].notna().any(axis=1)).sum())
