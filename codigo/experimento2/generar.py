import pandas as pd,numpy as np,os,sys
from multiprocessing import Pool
from caracteristicas import calcular
from senales import leer_senal
x=pd.read_csv('../disparador_v2/cruce_v2.csv')
cr=pd.read_csv('../auditoria_v2/encabezados_crudos.csv')[['archivo','fs']]
x=x.merge(cr,on='archivo',how='left')
def rates(s): 
    try: return [float(v) for v in str(s).split('/') if v.strip()]
    except: return []
def proc(r):
    try: X,o=leer_senal(os.path.join('../datos_completos',r['grupo'],r['archivo']))
    except Exception as e: return r['archivo'],{}
    hz=r['fs_x'] if 'fs_x' in r else r['fs']; res={}
    for nombre,t in [('original',r['t_original']),('corregido',r['t_corregido']),('referencia',r['t_ref'])]:
        if pd.isna(t) or pd.isna(hz): continue
        idx=int(round(t*hz)) if nombre!='referencia' else int(round(t*hz))-1
        res[nombre]=calcular(X,o,hz,idx,rates(r['fs_y']))
    return r['archivo'],res
if __name__=='__main__':
    with Pool(2) as P: R=dict(P.map(proc,[r for _,r in x.iterrows()],chunksize=40))
    pd.to_pickle(R,'caracteristicas_todas.pkl'); print(len(R))
