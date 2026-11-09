exec(open('/workspace/C1_contact_coupe/export_contact.py').read().split('pa=np.array')[0])
from scipy.interpolate import PchipInterpolator
reg=json.load(open('/workspace/C2_mecanique/REGISTRATION_C2.json'));F=reg['frames'];x=np.arange(199);P=np.array([f['contact']for f in F]);Q=np.array([f['target']for f in F]);NN=np.array([f['normal']for f in F]);ip=PchipInterpolator(x,P,axis=0);iq=PchipInterpolator(x,Q,axis=0)
unique,inv=np.unique(np.round(tri.reshape(-1,3),5),axis=0,return_inverse=True);fi=inv.reshape(-1,3);vn=np.zeros_like(unique);area=np.cross(E1,E2)
for j in range(3):np.add.at(vn,fi[:,j],area)
vn/=np.maximum(np.linalg.norm(vn,axis=1)[:,None],1e-20)
def normal_at(p,j):
 a=E1[j];b=E2[j];v=p-A[j];ab=a@b;den=(a@a)*(b@b)-ab*ab;aa=((b@b)*(v@a)-ab*(v@b))/den;bb=((a@a)*(v@b)-ab*(v@a))/den;return unit(vn[fi[j,0]]*(1-aa-bb)+vn[fi[j,1]]*aa+vn[fi[j,2]]*bb)
motion=[];prevn=None;preva=None;maxerr=0.;footmissing=[]
for k,phase in enumerate(np.linspace(0,198,1981)):
 i=min(197,int(phase));f=phase-i;nn=unit(NN[i]*(1-f)+NN[i+1]*f);p=ip(phase);h=hits(p+nn*5,-nn);h=[v for v in h if v[0]<10];assert h,(phase,'no skin');_,face,p=min(h,key=lambda a:np.linalg.norm(a[2]-p));n=normal_at(p,face);q=iq(phase);d=unit(q-p);angle=float(np.degrees(np.arccos(np.clip(-n@d,-1,1))));maxerr=max(maxerr,abs(angle-55));origin=(np.array(F[i]['origin'])*(1-f)+np.array(F[i+1]['origin'])*f)
 if prevn is None:
  tan=ip.derivative()(phase);along=unit(tan-n*(tan@n));across=unit(np.cross(along,n))
 else:
  kk=np.cross(prevn,n);cs=np.clip(prevn@n,-1,1);ss=np.linalg.norm(kk);ax=kk/max(ss,1e-20);across=preva*cs+np.cross(ax,preva)*ss+ax*(ax@preva)*(1-cs);across=unit(across-n*(across@n))
 along=unit(np.cross(n,across));prevn=n;preva=across;grid=[];gf=[]
 for yy in np.linspace(-12.5,12.5,5):
  for xx in np.linspace(-12.5,12.5,5):
   des=p+xx*across+yy*along;hh=hits(des+n*50,-n);hh=[v for v in hh if abs(v[0]-50)<30]
   if not hh:footmissing.append([float(phase),float(xx),float(yy)]);grid.append(None);gf.append(None)
   else:_,ff,pp=min(hh,key=lambda h:abs(h[0]-50));grid.append(pp.tolist());gf.append(ff)
 motion.append({'phase':float(phase),'shot':int(phase)+1,'origin':origin.tolist(),'target':q.tolist(),'contact':p.tolist(),'normal':n.tolist(),'across':across.tolist(),'along':along.tolist(),'contact_triangle':int(face),'footprint':grid,'footprint_triangles':gf,'incidence_deg':angle})
 if k%400==0:print('contact',k,'/1980',flush=True)
assert maxerr<=2,('angle tolerance',maxerr)
rows=list(csv.DictReader(open('/workspace/C2_cycle_source/C2_16915_LOIS_FOCALES.csv')));frames=[]
for i in range(199):
 m=dict(motion[10*i]);r=F[i];R=np.array(r['R']);origin=np.array(r['origin']);rays=[]
 for row in rows[i*85:(i+1)*85]:
  dr=R@np.array([float(row['beam_ux']),float(row['beam_uy']),float(row['beam_uz'])]);rays.append({'entry':m['contact'],'dir':dr.tolist(),'end':(origin+dr*r['source_range_mm']).tolist(),'sector':float(row['sector_deg']),'skew':float(row['skew_deg'])})
 m.update(rays=rays,plane_normal=unit(np.cross(np.array(m['target'])-origin,np.array(m['across']))).tolist(),section=[]);frames.append(m)
P=np.array([m['contact']for m in motion]);ip=PchipInterpolator(np.arange(1981)/10,P,axis=0);coef=ip.c.transpose(1,0,2)*np.array([.001,.01,.1,1])[None,:,None];dense=[]
for phase in np.linspace(0,198,7921):
 k=min(1979,int(phase*10));f=phase*10-k;nn=unit(np.array(motion[k]['normal'])*(1-f)+np.array(motion[k+1]['normal'])*f);p=ip(phase);hh=hits(p+3*nn,-nn);hh=[h for h in hh if h[0]<6];assert hh;dense.append(min(hh,key=lambda h:np.linalg.norm(h[2]-p))[2].tolist())
arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(dense,axis=0),axis=1))];out={'description':'C2 actual original mesh contact; physical first intrados groove; source per-shot acoustic rigid registration; mechanical footprint not manufacturing validation.','frames':frames,'motion':motion,'cubic_contact':coef.tolist(),'display_contact_path':dense,'contact_arc_lengths':arc.tolist()};Path('/workspace/C2_mecanique/CONTACT_C2.json').write_text(json.dumps(out,separators=(',',':')))
rot=[]
for a,b in zip(motion,motion[1:]):
 R0=np.column_stack([a['across'],a['along'],a['normal']]);R1=np.column_stack([b['across'],b['along'],b['normal']]);rot.append(float(np.degrees(np.arccos(np.clip((np.trace(R0.T@R1)-1)/2,-1,1)))))
audit={'poses':199,'intermediate_poses':1981,'surface_path_points':7921,'max_incidence_error_deg':maxerr,'allowed_incidence_error_user_deg':2,'max_support_increment_deg':max(rot),'missing_footprint_samples':len(footmissing),'mechanical_parameter_interval':[36,1],'full_mesh_groove_extent_verified':False,'source_results_unchanged':True,'publication_ready':False};Path('/workspace/C2_mecanique/CONTROLE_CONTACT_C2.json').write_text(json.dumps(audit,indent=2));print(audit,flush=True)
