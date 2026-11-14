"""Lector de encabezados ASA 2.0 (RAII-UNAM / CIRES). Solo lectura."""
import re, os, sys, json
import pandas as pd

KEYS = {
 'NOMBRE DEL ARCHIVO':'archivo_hdr','CLAVE DE LA ESTACION':'estacion',
 'COORDENADAS DE LA ESTACION':'coord_est','COORDENADAS DEL EPICENTRO':'coord_epi',
 'FECHA DEL SISMO':'fecha','HORA EPICENTRO':'hora_origen','MAGNITUD(ES)':'magnitudes',
 'PROFUNDIDAD FOCAL':'prof','ORIENTACION C1-C6':'orient','VEL. DE MUESTREO, C1-C6':'fs',
 'FREC. NAT. DE SENSORES, C1-C6':'fn','AMORTIGUAMIENTO DE SENSORES, C1-C6':'amort',
 'INTERVALO DE MUESTREO, C1-C6':'dt','HORA DE LA PRIMERA MUESTRA':'hora_primera',
 'NUM. TOTAL DE MUESTRAS, C1-C6':'nmuestras','ACEL. MAX.':'pga','UNIDADES DE LOS DATOS':'unidades',
 'FORMATO DATOS':'formato','MEMORIA DE PREEVENTO':'preevento','NUMERO DE CANALES':'ncanales',
 'FUENTE':'fuente_epi','EXACTITUD DEL TIEMPO':'exactitud_t',
}

def leer_encabezado(path):
    with open(path,'rb') as f: raw=f.read(20000)
    txt=raw.decode('latin1')
    i=txt.find('DATOS DE ACELERACION')
    hdr=txt[:i if i>0 else len(txt)]
    lines=hdr.replace('\r','').split('\n')
    out={}; last=None; calidad=[]; incal=False
    for ln in lines:
        if ln.startswith('CALIDAD DEL ACELEROGRAMA'): incal=True; continue
        if incal:
            if ln.startswith('====') or ln.startswith('COMENTARIOS'): incal=False
            elif ln.strip(): calidad.append(ln.strip())
            continue
        if ':' not in ln: continue
        k,v=ln.split(':',1); k=k.strip(); v=v.strip()
        if k=='' and last:   # continuación
            out[last]=out[last]+' | '+v; continue
        last=None
        for key,name in KEYS.items():
            if k.startswith(key):
                if name=='pga' and ('EN LA MUESTRA' in k or 'C7-C12' in k): break
                if 'C7-C12' in k: break
                if name in out: break
                out[name]=v; last=name; break
    out['calidad']=' '.join(calidad)
    out['bytes_hdr']=i
    return out

NUM=r'[-+]?\d+(?:\.\d+)?'
def parse_coord(s):
    """'16.775 LAT. N | 99.835 LONG. W' -> (lat, lon) con lon oeste negativa."""
    if not s: return (None,None,'sin_coord')
    lat=lon=None; nota=[]
    m=re.search(r'('+NUM+r')\s*LAT\.?\s*([NS])?',s,re.I)
    if m:
        lat=float(m.group(1));
        if (m.group(2) or 'N').upper()=='S': lat=-abs(lat)
    m=re.search(r'('+NUM+r')\s*LON[G]?\.?\s*([EW])?',s,re.I)
    if m:
        v=float(m.group(1)); hemi=(m.group(2) or 'W').upper()
        lon=abs(v) if hemi=='E' else -abs(v)
        if v<0: nota.append('lon_negativa_en_hdr')
    return (lat,lon,';'.join(nota))

def parse_mags(s):
    """Devuelve lista [(tipo, valor)]"""
    if not s: return []
    res=[]
    for t,v in re.findall(r'([A-Za-z]{1,3})\s*=\s*('+NUM+')',s):
        res.append((t,float(v)))
    return res

def slash_list(s):
    if not s: return []
    return [x.strip() for x in s.split('/') if x.strip()]

if __name__=='__main__':
    base=sys.argv[1]; rows=[]
    for grupo in ['Temblores_1964-1999','Temblores_2000-2020']:
        d=os.path.join(base,grupo)
        for fn in sorted(os.listdir(d)):
            h=leer_encabezado(os.path.join(d,fn)); h['grupo']=grupo; h['archivo']=fn
            rows.append(h)
    pd.DataFrame(rows).to_csv(sys.argv[2],index=False)
    print(len(rows))
