from pathlib import Path
import pickle,json,numpy as np,base64
p=Path(__file__).parent;d=pickle.load((p/'REFERENCE_CALCULEE_C2.pkl').open('rb'));D=json.loads((p/'DONNEES_REJEU_C2_AFFICHEES.json').read_text());scan=d['scan'];pa=d['pa'];allxyz=[];alldb=[];alls=[];counts=[]
for k in range(199):
 idx=np.flatnonzero(scan['encoded_db'][k]>=D['parameters']['cloud_display_threshold_db'])
 if idx.size>260:idx=idx[np.linspace(0,idx.size-1,260).astype(int)]
 laws=scan['winning_law'][k,idx];rr=scan['range_axis'][idx];xyz=pa[k][None,:]+rr[:,None]*scan['law_beams'][k,laws];allxyz.extend(xyz.tolist());alldb.extend(scan['encoded_db'][k,idx].tolist());alls.extend([k+1]*len(idx));counts.append(len(allxyz))
X=np.array(allxyz);B=np.array(alldb);S=np.array(alls)
for k,fr in enumerate(D['frames']):
 n=counts[k];ids=np.arange(n)if n<=12000 else np.linspace(0,n-1,12000).astype(int)
 for key,actual in [('cloud_xyz',X[ids]),('cloud_db',B[ids]),('cloud_shot',S[ids])]:assert np.array_equal(np.array(fr[key]),actual),(k,key);del fr[key]
 fr['cloud_count']=n
 if n>12000:fr['cloud_indices_u16']=base64.b64encode(ids.astype('<u2').tobytes()).decode()
D['cloud_bank']={'xyz':allxyz,'db':alldb,'shot':alls};(p/'DONNEES_REJEU_C2_COMPACT.json').write_text(json.dumps(D,separators=(',',':'),allow_nan=False));print('Compact exact source cloud',len(X),'points; all199 snapshots equal original',flush=True)
