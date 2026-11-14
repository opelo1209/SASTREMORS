import pandas as pd, numpy as np
p=pd.read_csv('encabezados.csv')
mcols=[c for c in p.columns if c.startswith('M_')]
cols=['prof','D','fn1','fn2','fn3','am1','am2','am3','pga1','pga2','pga3','M','etiqueta']
def score(m,h):
    s=0
    s+= np.isclose(m.prof,h.prof) if pd.notna(h.prof) else 0
    s+= sum(np.isclose(m['pga%d'%k],h['pga%d'%k],atol=0.011,rtol=0.002) for k in (1,2,3))
    s+= sum(np.isclose(m['fn%d'%k],h['fn%d'%k],atol=0.01) for k in (1,2,3) if pd.notna(h['fn%d'%k]))
    s+= any(np.isclose(m.M,h[c],atol=0.006) for c in mcols if pd.notna(h[c]))
    s+= np.isclose(m.D,h.D_literal,atol=0.5) or np.isclose(m.D,h.D_corr,atol=0.5)
    return s  # max 9
out=[]
for g,f in [('Temblores_1964-1999','Datos_1964_1999.dat'),('Temblores_2000-2020','Datos_2000_2020.dat')]:
    m=pd.read_csv('../datos_completos/ProgramasMary/Red_en_Matlab/'+f,sep=r'\s+',header=None,names=cols); m['fila']=np.arange(1,len(m)+1)
    h=p[p.grupo==g].reset_index(drop=True)
    j=0; W=40
    for i,mr in m.iterrows():
        best=(-1,None)
        for jj in range(max(0,j-5),min(len(h),j+W)):
            s=score(mr,h.iloc[jj])
            if s>best[0]: best=(s,jj)
            if s==9: break
        s,jj=best
        if s>=7: out.append(dict(grupo=g,fila=mr.fila,archivo=h.archivo[jj],puntaje=s)); j=jj+1
        else: out.append(dict(grupo=g,fila=mr.fila,archivo=None,puntaje=s))
e=pd.DataFrame(out); e.to_csv('empate_matriz_archivos.csv',index=False)
print(e.groupby('grupo').apply(lambda x: pd.Series({'filas':len(x),'empatadas':x.archivo.notna().sum(),'dup':x.archivo.dropna().duplicated().sum()})))
print(e.groupby(['grupo','puntaje']).size())
