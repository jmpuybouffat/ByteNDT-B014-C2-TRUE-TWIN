exec(open('/workspace/C1_contact_coupe/export_contact.py').read().split('pa=np.array')[0])
f=Path('/workspace/C2_mecanique/CONTACT_C2.json');data=json.loads(f.read_text());max_plane=0;total=0
for pose in data['motion']:
 c=np.array(pose['contact']);u=np.array(pose['across']);v=np.array(pose['along']);n=np.array(pose['normal']);local=np.stack(((tri-c)@u,(tri-c)@v,(tri-c)@n),axis=-1);mask=(local[:,:,0].min(1)<=12.5)&(local[:,:,0].max(1)>=-12.5)&(local[:,:,1].min(1)<=12.5)&(local[:,:,1].max(1)>=-12.5)&(local[:,:,2].min(1)<15)&(local[:,:,2].max(1)>-15)&(np.abs(N@n)>.15);out=[]
 for face in np.where(mask)[0]:
  poly=[p.copy() for p in tri[face]]
  for axis,bound,sign in [(u,12.5,1),(u,-12.5,-1),(v,12.5,1),(v,-12.5,-1),(n,15,1),(n,-15,-1)]:
   new=[]
   if not poly:break
   for a,b in zip(poly,poly[1:]+poly[:1]):
    da=((a-c)@axis-bound)*sign;db=((b-c)@axis-bound)*sign
    if da<=1e-9:new.append(a)
    if (da<0 and db>0)or(da>0 and db<0):new.append(a+da/(da-db)*(b-a))
   poly=new
  for j in range(1,len(poly)-1):
   ps=np.array([poly[0],poly[j],poly[j+1]]);max_plane=max(max_plane,float(np.max(abs((ps-A[face])@N[face]))));out.extend(ps.tolist());total+=1
 pose['surface_patch']=out
assert max_plane<1e-8
f.write_text(json.dumps(data,separators=(',',':')))
print('Exact skin patches:',total,'triangles; max original-plane residual:',max_plane)
Path('/workspace/C2_mecanique/CONTROLE_SURFACE_PATCH.json').write_text(json.dumps({'motion_poses':1981,'contact_centres_on_root_triangles':1981,'sampled_footprint_vertices_on_root':49525,'actual_skin_patch_triangles':total,'maximum_patch_plane_error_mm':max_plane,'footprint_mm':[25,25],'UT_source_arrays':'unchanged','scope':'graphic contact surface and section; not manufactured wedge profile or scanner clearance validation'},indent=2))
