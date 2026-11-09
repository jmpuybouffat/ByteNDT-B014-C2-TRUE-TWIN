from pathlib import Path
import numpy as np,json
from scipy.signal import find_peaks
exec(Path('/workspace/C2_mecanique/build_registration.py').read_text().split('# Full observed')[0])
reg=json.load(open('/workspace/C2_mecanique/REGISTRATION_C2.json'));report=[]
for shot,phase in enumerate(np.linspace(36,1,199),1):
 i=min(39,int(phase));f=phase-i;p=oldt[i]*(1-f)+oldt[i+1]*f;n=oldt[min(40,i+1)]-oldt[max(0,i-1)];n[2]=0;n=unit(n);u=unit(np.cross(n,[0,0,1]));u*=-np.sign(u@(oldp[i]-p));dd=(tri-p)@n;pts=[[]for _ in tri]
 for a,b in [(0,1),(1,2),(2,0)]:
  ids=np.flatnonzero(dd[:,a]*dd[:,b]<0);qq=tri[ids,a]+(dd[ids,a]/(dd[ids,a]-dd[ids,b]))[:,None]*(tri[ids,b]-tri[ids,a])
  for j,q in zip(ids,qq):pts[j].append(q)
 seg=np.array([q for q in pts if len(q)==2]);h=seg@axis;x=(seg-p)@u;hs=np.unique(h[(h>-55)&(h<20)]);xx=[];qq=[]
 for z in hs:
  den=h[:,1]-h[:,0];ids=np.flatnonzero(((h[:,0]-z)*(h[:,1]-z)<=1e-13)&(abs(den)>1e-10));ff=(z-h[ids,0])/den[ids];xs=x[ids,0]+ff*(x[ids,1]-x[ids,0]);j=np.argmin(xs);xx.append(xs[j]);qq.append(seg[ids[j],0]+ff[j]*(seg[ids[j],1]-seg[ids[j],0]))
 peaks=find_peaks(xx,prominence=.2)[0];assert len(peaks)>=3
 # Identify the actual repeating fir-tree train, rather than counting a
 # possible concavity in the platform/airfoil transition as a root groove.
 ordered_low=sorted(peaks,key=lambda k:hs[k]);chains={}
 for k in ordered_low:
  candidates=[chains[j]+[k]for j in chains if 8<hs[k]-hs[j]<16 and -10<xx[k]-xx[j]<-.25]
  chains[k]=max(candidates,key=len)if candidates else[k]
 train=max(chains.values(),key=lambda chain:(len(chain),hs[chain[-1]]));assert len(train)>=4
 ordered=list(reversed(train));first=ordered[0];actual=np.array(qq[first]);target=np.array(reg['frames'][shot-1]['target']);err=np.linalg.norm(actual-target);assert err<1e-7,(shot,hs[ordered],err)
 report.append({'shot':shot,'uppermost_concave_valley_local_height_mm':float(hs[first]),'next_valley_height_mm':float(hs[ordered[1]]),'target_to_first_valley_mm':float(err)})
out={'method':'Independent full root-profile extrema; longest repeated fir-tree groove train (8–16mm height spacing, widening toward platform); uppermost concave root valley. Platform/airfoil pockets excluded by reversal of radial width progression.','positions':199,'maximum_target_to_first_valley_mm':max(r['target_to_first_valley_mm']for r in report),'numerical_target_change':False,'rendering_problem':'R2 rendered red tube without depth testing from an elevated viewpoint; projection could cover lips. R3 respects occlusion and uses a target-height viewpoint.','records':report};Path('/workspace/C2_mecanique/CONTROLE_PREMIERE_GORGE_R3.json').write_text(json.dumps(out,indent=2));print('199/199 first profile valleys match; maxerror',out['maximum_target_to_first_valley_mm'])
