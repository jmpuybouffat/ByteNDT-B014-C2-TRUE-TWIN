from pathlib import Path
import subprocess
root=Path('/workspace/LSB941-C2-PUBLICATION');p=root/'assets/SCENE_C2_SYNCHRONISEE.html';s=subprocess.check_output(['git','show','81ce1c7:assets/SCENE_C2_SYNCHRONISEE.html'],cwd=root).decode()
# No geometry/data correction: genuine depth instead of x-ray projection.
s=s.replace('new THREE.TubeGeometry(grooveCurve,320,.65,7,false)','new THREE.TubeGeometry(grooveCurve,1980,.22,8,false)').replace('grooveLine.material.depthTest=false;','grooveLine.material.depthTest=true;grooveLine.material.polygonOffset=true;grooveLine.material.polygonOffsetFactor=-1;grooveLine.material.polygonOffsetUnits=-1;')
a=s.index('function beamCamera()');b=s.index('function clearBeamCut',a);v=s[a:b];v=v.replace('new THREE.Vector3(mean.x-c.x,mean.y-c.y,12)','new THREE.Vector3(mean.x-c.x,mean.y-c.y,0)').replace('new THREE.Vector3(0,0,30)','new THREE.Vector3(0,0,15)').replace('el=Math.asin(view.z);radius=285','el=Math.asin(-15/285);radius=285');s=s[:a]+v+s[b:];i=s.rindex('</script>');s=s[:i]+Path('/workspace/C2_mecanique/groove_inset_r3.js').read_text()+s[i:];p.write_text(s)
