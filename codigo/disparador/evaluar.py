import pandas as pd,numpy as np,sys
d=pd.read_csv('variantes.csv')
SNR=float(sys.argv[1]) if len(sys.argv)>1 else 10
print(d.error.value_counts(dropna=False).to_dict())
d=d[d.error.isna()]
V=[c for c in d.columns if c.startswith('t_') and c!='t_ref']
rows=[]
for g,x in d.groupby('grupo'):
    rel=x[x.snr_ref>=SNR]
    for v in V:
        e=rel[v]-rel.t_ref
        rows.append(dict(periodo=g[10:],variante=v[2:],n_ref=len(rel),
          sin_disparo=round(100*e.isna().mean(),1),
          temprano=round(100*(e<-0.5).mean(),1),
          correcto=round(100*e.between(-0.5,1.0).mean(),1),
          tardio=round(100*(e>1.0).mean(),1),
          mediana_err=round(e.median(),2),
          sin_disparo_todos=round(100*x[v].isna().mean(),1)))
print(f'Referencia fiable: SNR >= {SNR} dB'); print(pd.DataFrame(rows).to_string(index=False))
print(d.groupby('grupo').snr_ref.describe().round(1))
