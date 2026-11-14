import pandas as pd, numpy as np, re, sys
sys.path.insert(0,'../auditoria_v2')
from leer_asa import NUM
crudo=pd.read_csv('../auditoria_v2/encabezados_crudos.csv')
et=pd.read_csv('../auditoria_v2/etiquetas_corregidas.csv')
def num(s):
    m=re.search(NUM,str(s)); return float(m.group(0)) if m else np.nan
def slash(s): return [x for x in str(s).split('/') if x.strip()] if pd.notna(s) else []
def hms(s):
    m=re.search(r'(\d{1,2}):(\d{1,2}):(\d{1,2}(?:\.\d+)?)',str(s))
    return int(m[1])*3600+int(m[2])*60+float(m[3]) if m else np.nan
def coord(s):
    nums=re.findall(NUM,str(s)); 
    return (float(nums[0]),-abs(float(nums[1]))) if len(nums)>=2 else (np.nan,np.nan)
r=crudo[['grupo','archivo','coord_est','dt','fs','hora_primera','exactitud_t','preevento','calidad','nmuestras']].copy()
r['lat_est'],r['lon_est']=zip(*r.coord_est.map(coord))
r['dt_s']=r.dt.map(lambda s: num(slash(s)[0]) if slash(s) else np.nan)
r['t_primera']=r.hora_primera.map(hms)
r['exactitud']=r.exactitud_t.map(num)
r['preevento_s']=r.preevento.map(num)
r['n']=r.nmuestras.map(lambda s: num(slash(s)[0]) if slash(s) else np.nan)
c=r.calidad.fillna('').str.upper()
r['tiempo_abs_ok']=c.str.contains('CON TIEMPO ABS') & ~c.str.contains('CARECE|SIN TIEMPO')
r['inicio_incompleto']=c.str.contains('FALTA UNA PARTE AL INICIO')
r['dudoso']=c.str.contains('INCOMPLETO EN SU PARTE INTENSA')
m=et.merge(r.drop(columns=['coord_est','dt','fs','hora_primera','exactitud_t','preevento','nmuestras']),on=['grupo','archivo'])
m['t_origen']=m.hora.map(hms)
# decisiones aprobadas: etiqueta principal = etiqueta por evento con la primera magnitud válida
m['etiqueta_final']=m.etiqueta_evento
m.to_csv('metadatos_disparador.csv',index=False)
print(len(m), m.tiempo_abs_ok.sum(), m.t_primera.notna().sum(), m.dt_s.value_counts().head().to_dict())
