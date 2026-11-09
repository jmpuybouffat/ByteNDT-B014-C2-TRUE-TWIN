from pathlib import Path
import sys,pickle,json,numpy as np,pandas as pd
sys.path.insert(0,'/workspace/C2_cycle_source');from charger_reference import ctx
src=pickle.load(open('/workspace/C2_cycle_source/REFERENCE_CALCULEE_C2.pkl','rb'));steps=ctx['build_steps'](src['pa'],src['target']);rows=pd.read_csv('/workspace/C2_cycle_source/C2_16915_LOIS_FOCALES.csv');errs=[]
for shot in range(199):
 v=np.load('/workspace/C2_beam_volume/volume_%02d.npz'%(shot+1));db=v['db'];sel=np.argsort(db.ravel())[-3:];pos=np.column_stack(np.unravel_index(sel,db.shape));local=np.array([[v['s'][i],v['u'][j],v['v'][k]]for i,j,k in pos]);q=v['origin']+local@v['basis'];li=v['winner'].ravel()[sel];g=[]
 for target,k in zip(q,li):
  row=rows.iloc[shot*85+int(k)];delay=np.array([row['delay_e%02d_us'%(j+1)]for j in range(64)]);g.append(ctx['vectorized_coherent_gain'](steps[shot]['elements'],delay,target)[0])
 actual=10*np.log10(g);assert min(g)>0;errs.extend(abs(actual-db.ravel()[sel]).tolist())
a={'source_kernel':'original vectorized_coherent_gain','positions':199,'nonzero_nodes':len(errs),'max_db_float32_difference':max(errs),'success':max(errs)<1e-5};assert a['success'];Path('/workspace/C2_beam_volume/CONTROLE_NOYAU_NON_NUL.json').write_text(json.dumps(a,indent=2));print(a)
