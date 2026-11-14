"""Lectura de series ASA 2.0 (ancho fijo según 'FORMATO DATOS')."""
import numpy as np, re
def leer_senal(path):
    raw=open(path,'rb').read().decode('latin1').replace('\r','')
    i=raw.find('DATOS DE ACELERACION'); hdr=raw[:i]; body=raw[i:].split('\n')
    m=re.search(r'FORMATO DATOS.*?:\s*(\d+)\s*F\s*(\d+)\.(\d+)',hdr)
    nc,w=(int(m[1]),int(m[2])) if m else (3,10)
    # orientaciones: línea tras CANAL-1
    k=[j for j,l in enumerate(body[:8]) if 'CANAL-1' in l][0]
    orient=body[k+1].split()
    start=k+3  # tras la segunda regla
    while start<len(body) and body[start].startswith('---'): start+=1
    vals=[]
    for l in body[start:]:
        if not l.strip(): continue
        row=[]
        for c in range(nc):
            s=l[c*w:(c+1)*w].strip()
            row.append(float(s) if s else np.nan)
        vals.append(row)
    X=np.array(vals,float)
    return X,orient
def canal_vertical(orient):
    for j,o in enumerate(orient):
        o2=o.upper().split(';')[-1]
        if re.fullmatch(r'[+-]?V',o2) or o2 in ('+V','V','-V','UP','Z'): return j
    return None
