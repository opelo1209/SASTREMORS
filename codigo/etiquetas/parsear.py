import pandas as pd, numpy as np, re
from leer_asa import parse_coord, parse_mags, slash_list, NUM
d=pd.read_csv('encabezados_crudos.csv')
REF=(19.25,-99.13); R=6371.0
def dist(lat1,lon1,lat2=REF[0],lon2=REF[1],R=R):
    a=np.radians([lat1,lon1,lat2,lon2]); 
    c=np.sin(a[0])*np.sin(a[2])+np.cos(a[0])*np.cos(a[2])*np.cos(a[1]-a[3])
    return R*np.arccos(np.clip(c,-1,1))
rows=[]
for _,r in d.iterrows():
    s=str(r.coord_epi) if pd.notna(r.coord_epi) else ''
    lat,lon,nota=parse_coord(s)
    # versión "literal" que reproduciría un extractor ingenuo: lon = -valor_impreso
    m=re.search(r'('+NUM+r')\s*LON',s,re.I)
    lon_lit = -float(m.group(1)) if m else None
    mags=parse_mags(r.magnitudes if pd.notna(r.magnitudes) else '')
    md={}
    for t,v in mags: md.setdefault(t.capitalize(),v)
    pr=re.search(NUM,str(r.prof)) if pd.notna(r.prof) else None
    fs=slash_list(r.fs) if pd.notna(r.fs) else []
    fn=slash_list(r.fn); am=slash_list(r.amort) if pd.notna(r.amort) else []; pga=slash_list(r.pga)
    def f(x):
        try: return float(x)
        except: return np.nan
    rows.append(dict(grupo=r.grupo,archivo=r.archivo,estacion=r.estacion,fecha=r.fecha,hora=r.hora_origen,
      lat_epi=lat,lon_epi=lon,lon_literal=lon_lit,nota_coord=nota,
      D_corr=dist(lat,lon) if lat is not None and lon is not None else np.nan,
      D_literal=dist(lat,lon_lit) if lat is not None and lon_lit is not None else np.nan,
      prof=f(pr.group(0)) if pr else np.nan, magnitudes=r.magnitudes,
      **{('M_'+k):v for k,v in md.items()}, n_mags=len(mags),
      fs=r.fs, fn1=f(fn[0]) if fn else np.nan, fn2=f(fn[1]) if len(fn)>1 else np.nan, fn3=f(fn[2]) if len(fn)>2 else np.nan,
      am1=f(am[0]) if am else np.nan, pga1=f(pga[0]) if pga else np.nan,pga2=f(pga[1]) if len(pga)>1 else np.nan,pga3=f(pga[2]) if len(pga)>2 else np.nan,
      orient=r.orient, calidad=r.calidad, hora_primera=r.hora_primera, preevento=r.preevento))
p=pd.DataFrame(rows); p.to_csv('encabezados.csv',index=False)
print(p.groupby('grupo').size()); print(p.filter(like='M_').notna().sum())
print('nota coord:',p.nota_coord.value_counts().to_dict())
print(p.groupby(['grupo',p.nota_coord.fillna('')!='']).size())
print('D_corr>3000:',(p.D_corr>3000).groupby(p.grupo).sum().to_dict(),' D_literal>3000:',(p.D_literal>3000).groupby(p.grupo).sum().to_dict())
print(p[['D_corr']].describe())
