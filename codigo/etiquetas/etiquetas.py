import pandas as pd, numpy as np, re
from leer_asa import NUM
p=pd.read_csv('encabezados.csv'); x=pd.read_pickle('x.pkl')
R=6371.0; k=6378/6371
def regla(M,D): return (((M>5.0)&(D<=250))|((M>5.5)&(D<=350))|((M>6.0)&(D>350))).astype(float)
MESES={'ENE':1,'FEB':2,'MAR':3,'ABR':4,'MAY':5,'JUN':6,'JUL':7,'AGO':8,'SEP':9,'OCT':10,'NOV':11,'DIC':12}
def fecha(s):
    s=str(s).strip()
    m=re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})',s)
    if m: return '%s-%02d-%02d'%(m[1],int(m[2]),int(m[3]))
    m=re.match(r'(\d{1,2})/([A-Z]{3})/(\d{2,4})',s.upper())
    if m:
        y=int(m[3]); y= y+2000 if y<100 and y<=30 else (y+1900 if y<100 else y)
        return '%d-%02d-%02d'%(y,MESES.get(m[2],0),int(m[1]))
    m=re.match(r'(\d{1,2}) de (\w+) de (\d{4})',s,re.I)
    if m:
        mm={'enero':1,'febrero':2,'marzo':3,'abril':4,'mayo':5,'junio':6,'julio':7,'agosto':8,'septiembre':9,'octubre':10,'noviembre':11,'diciembre':12}[m[2].lower()]
        return '%s-%02d-%02d'%(m[3],mm,int(m[1]))
    return None
def mags(s):
    s=str(s) if pd.notna(s) else ''
    out=[(t.capitalize(),float(v)) for t,v in re.findall(r'([A-Za-z]{1,2})\s*=?\s*('+NUM+')',s)]
    return out
rows=[]
for _,r in p.iterrows():
    ml=mags(r.magnitudes); val=[(t,v) for t,v in ml if v>0]
    M1=val[0][1] if val else np.nan; T1=val[0][0] if val else None
    Mmax=max(v for t,v in val) if val else np.nan
    rows.append(dict(M_corr=M1,escala_M_corr=T1,M_max=Mmax,fecha_iso=fecha(r.fecha)))
p=pd.concat([p,pd.DataFrame(rows)],axis=1)
def hnorm(h):
    m=re.match(r'\s*(\d{1,2}):(\d{1,2}):(\d{1,2})',str(h))
    return '%02d:%02d:%02d'%tuple(map(int,m.groups())) if m else '??'
p['evento']=p.fecha_iso.fillna('?')+'T'+p.hora.map(hnorm)
# 2000-2020: el nombre del archivo trae la fecha-hora del evento (EEEEyyyymmddhhmmss)
rec=p.grupo.eq('Temblores_2000-2020')&p.archivo.str.match(r'^[A-Za-z0-9]{4}\d{14}$')
p.loc[rec,'evento']=p.loc[rec,'archivo'].str[4:].map(lambda t:'%s-%s-%sT%s:%s:%s'%(t[:4],t[4:6],t[6:8],t[8:10],t[10:12],t[12:14]))
# coordenadas sin etiqueta LAT/LONG (p.ej. '16.520 | 99.330'): lat primero, lon oeste
crudo=pd.read_csv('encabezados_crudos.csv')[['grupo','archivo','coord_epi']]
p=p.merge(crudo,on=['grupo','archivo'],how='left')
for i in p.index[p.lat_epi.isna()]:
    nums=re.findall(NUM,str(p.at[i,'coord_epi']))
    if len(nums)==2:
        p.at[i,'lat_epi']=float(nums[0]); p.at[i,'lon_epi']=-abs(float(nums[1])); p.at[i,'nota_coord']='coord_sin_rotulo'
# consenso por evento: corrige epicentros atipicos (>1 grado del resto del mismo evento)
p['correccion_consenso']=''
for ev,g in p.groupby('evento'):
    if len(g)<3 or ev.endswith('??'): continue
    la,lo=g.lat_epi.median(),g.lon_epi.median()
    for i in g.index:
        if abs(p.at[i,'lat_epi']-la)>1 or abs(p.at[i,'lon_epi']-lo)>1:
            p.at[i,'correccion_consenso']='epicentro %.2f,%.2f -> %.2f,%.2f (mediana de %d registros del evento)'%(p.at[i,'lat_epi'],p.at[i,'lon_epi'],la,lo,len(g))
            p.at[i,'lat_epi'],p.at[i,'lon_epi']=la,lo
def dist(lat1,lon1,lat2=19.25,lon2=-99.13):
    l1,o1,l2,o2=[np.radians(np.asarray(v,dtype=float)) for v in (lat1,lon1,lat2,lon2)]; c=np.sin(l1)*np.sin(l2)+np.cos(l1)*np.cos(l2)*np.cos(o1-o2)
    return R*np.arccos(np.clip(c,-1,1))
p['D_corr']=dist(p.lat_epi.values,p.lon_epi.values)
# magnitud por evento (mediana de M_corr entre registros del evento)
p['M_evento']=p.groupby('evento').M_corr.transform('median')
p['n_M_distintas_evento']=p.groupby('evento').M_corr.transform('nunique')
# histórico (si se empató)
h=x[x.archivo.notna()][['grupo','archivo','fila','M_h','D_h','etiqueta_h']]
p=p.merge(h,on=['grupo','archivo'],how='left')
p['etiqueta_corr']=regla(p.M_corr,p.D_corr)
p['etiqueta_Mmax']=regla(p.M_max,p.D_corr)
p['etiqueta_corr_R6378']=regla(p.M_corr,p.D_corr*k)
p['etiqueta_evento']=regla(p.M_evento,p.groupby('evento').D_corr.transform('median'))
fuera=(p.lat_epi<5)|(p.lat_epi>35)|(p.lon_epi<-120)|(p.lon_epi>-85)
p['indeterminada']=np.where(p.M_corr.isna(),'sin_magnitud',np.where(p.lat_epi.isna()|p.lon_epi.isna(),'sin_epicentro',np.where(fuera,'epicentro_fuera_de_region','')))
p.loc[p.indeterminada!='',['etiqueta_corr','etiqueta_Mmax','etiqueta_corr_R6378','etiqueta_evento']]=np.nan
# motivo de cambio
def motivo(r):
    if pd.isna(r.etiqueta_h): return 'sin_fila_historica'
    if r.indeterminada: return 'indeterminada:'+r.indeterminada
    m=[]
    if abs(r.D_h-r.D_corr*k)>0.5: m.append('distancia(signo_longitud)' if r.nota_coord=='lon_negativa_en_hdr' else 'distancia')
    if not np.isclose(r.M_h,r.M_corr,atol=0.006): m.append('magnitud')
    if r.correccion_consenso: m.append('epicentro_atipico')
    if r.etiqueta_h!=r.etiqueta_corr: return 'CAMBIA:'+'+'.join(m)
    return 'igual'+(':'+'+'.join(m) if m else '')
p['motivo']=p.apply(motivo,axis=1)
keep=['grupo','archivo','fila','estacion','evento','fecha_iso','hora','lat_epi','lon_epi','coord_epi','nota_coord','prof','magnitudes',
 'M_h','M_corr','escala_M_corr','M_max','D_h','D_corr','etiqueta_h','etiqueta_corr','etiqueta_Mmax','etiqueta_corr_R6378','indeterminada','motivo','correccion_consenso','M_evento','n_M_distintas_evento','etiqueta_evento']
keep=list(dict.fromkeys(keep))
p[keep].to_csv('etiquetas_corregidas.csv',index=False)
print(p.motivo.value_counts())
print(pd.crosstab(p.etiqueta_h,p.etiqueta_corr,dropna=False))
for g,d in p.groupby('grupo'):
    print(g,'hist positivos',d.etiqueta_h.sum(),'/',d.etiqueta_h.notna().sum(),' corr positivos',d.etiqueta_corr.sum(),'/',d.etiqueta_corr.notna().sum())
print('Mmax vs corr difieren:',(p.etiqueta_Mmax!=p.etiqueta_corr)[p.etiqueta_corr.notna()].sum(),' R6378 vs 6371 difieren:',(p.etiqueta_corr_R6378!=p.etiqueta_corr)[p.etiqueta_corr.notna()].sum())
print('fechas no parseadas',p.fecha_iso.isna().sum())
ev=p[p.etiqueta_corr.notna()].groupby('evento').etiqueta_corr.nunique(); print('eventos',len(ev),' con etiqueta inconsistente',(ev>1).sum())
print(p[p.indeterminada!=''][['archivo','magnitudes','lat_epi','lon_epi','indeterminada']])

print('cambios evento vs registro:',(p.etiqueta_evento!=p.etiqueta_corr)[p.etiqueta_corr.notna()].sum())
print('correcciones consenso:',(p.correccion_consenso!='').sum()); print(p[p.correccion_consenso!=''][['archivo','correccion_consenso']].to_string())
# banderas de revisión adicionales
y=p.fecha_iso.str[:4].astype(float)
rev=[]
for i,r in p.iterrows():
    b=[]
    if r.grupo=='Temblores_1964-1999' and y[i]>=2000: b.append('fecha_fuera_de_periodo_nominal')
    if r.grupo=='Temblores_2000-2020' and y[i]<2000: b.append('fecha_hdr_no_coincide_con_nombre_archivo')
    if r.n_M_distintas_evento>1: b.append('magnitud_distinta_entre_registros_del_evento')
    if pd.notna(r.etiqueta_corr) and r.etiqueta_Mmax!=r.etiqueta_corr: b.append('sensible_a_escala_de_magnitud')
    if r.motivo=='sin_fila_historica': b.append('archivo_sin_fila_en_matriz_historica')
    rev.append(';'.join(b))
p['revisar']=rev
keep.append('revisar')
p[keep].to_csv('etiquetas_corregidas.csv',index=False)
print(pd.Series(';'.join(rev).split(';')).value_counts())
