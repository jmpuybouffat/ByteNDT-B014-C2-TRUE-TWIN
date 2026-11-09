from pathlib import Path
import re
root=Path('/workspace/LSB941-C2-PUBLICATION');p=root/'assets/00_OUVRIR_CYCLE_C2_FR_EN.html';s=p.read_text();assert 'C2_PLAYBACK_R2'not in s
# Prevent an apparently active Play control before the heavy scene is ready.
s,n=re.subn(r'(<button\b[^>]*\bid="play")',r'\1 disabled',s,count=1);assert n==1
addon=r'''
// C2_PLAYBACK_R2: acknowledged start, readiness gating and retry without duplicate starts.
let playbackRequestId=0,playbackRetry=null;
const originalPlaybackRefresh=refreshText;
refreshText=function(){originalPlaybackRefresh();$('play').disabled=!sceneReady;if(!sceneReady)$('play').textContent=lang==='fr'?'Chargement de la vue…':'Loading view…'};
const originalPlaybackStop=stop;stop=function(){clearInterval(playbackRetry);playbackRetry=null;originalPlaybackStop()};
function requestGlide(){clearInterval(playbackRetry);const id=++playbackRequestId;let attempts=0;const send=()=>{if(!playing||id!==playbackRequestId){clearInterval(playbackRetry);return}if(++attempts>6){stop();$('status').textContent=lang==='fr'?'La vue ne répond pas. Rechargez la page puis relancez Lecture.':'The view is not responding. Reload the page, then press Play.';return}$('scene').contentWindow.postMessage({type:'C2_GLIDE_PLAY',requestId:id,shot:current,stepDuration:+$('speed').value},'*')};send();playbackRetry=setInterval(send,500)}
$('play').onclick=async()=>{if(!sceneReady)return;if(playing){stop();return}if(current>=199)await go(1);playing=true;refreshText();requestGlide()};
window.addEventListener('message',e=>{if(e.source!==$('scene').contentWindow)return;if(e.data?.type==='C2_SCENE_READY'){sceneReady=true;refreshText()}else if(e.data?.type==='C2_GLIDE_STARTED'&&e.data.requestId===playbackRequestId){clearInterval(playbackRetry);playbackRetry=null}});
const r2mark=document.createElement('p');r2mark.style='font-size:12px;color:#48657a;margin:6px 0 0';r2mark.textContent='C2 · R2 · Play';document.querySelector('header')?.append(r2mark);refreshText();
'''
i=s.rindex('</script>');s=s[:i]+addon+s[i:];s=s.replace('après le tir 41.','après le tir 199.').replace('after shot 41.','after shot 199.');p.write_text(s)
p=root/'assets/SCENE_C2_SYNCHRONISEE.html';s=p.read_text();a=s.index('function startGlide(');b=s.index("window.addEventListener('message'",a)
s=s[:a]+'''function glideProgress(elapsed,duration){const t=Math.max(0,Math.min(duration,elapsed)),a=Math.min(600,duration/3),span=duration-a;const ramp=x=>(x-a/Math.PI*Math.sin(Math.PI*x/a))*.5/span;if(t<a)return ramp(t);if(t>duration-a)return 1-ramp(duration-t);return (t-a*.5)/span}
function startGlide(m){const phase=Math.abs(glidePhase-(m.shot-1))<1?glidePhase:m.shot-1;glideJob={requestId:m.requestId,start:performance.now(),phase,stepDuration:m.stepDuration||600,lastAcquired:m.shot,startDistance:distanceAtPhase(phase),duration:Math.max(1,(198-phase)*(m.stepDuration||600))};motionJob=null}
'''+s[b:]
old="if(m?.type==='C2_GLIDE_PLAY')startGlide(m);";new="if(m?.type==='C2_GLIDE_PLAY'){if(!glideJob||glideJob.requestId!==m.requestId)startGlide(m);parent.postMessage({type:'C2_GLIDE_STARTED',requestId:m.requestId},'*');}";assert old in s;s=s.replace(old,new,1)
old='e=tau*tau*tau*(10+tau*(-15+6*tau))';assert old in s;s=s.replace(old,'e=glideProgress(time-job.start,job.duration)',1);p.write_text(s)
p=root/'app.py';s=p.read_text().replace('GORGE-INTRADOS-R1','GORGE-INTRADOS-R2').replace('199 positions · R1','199 positions · R2').replace('C2_FR_EN_R1.zip','C2_FR_EN_R2.zip');p.write_text(s)
p=root/'DEPLOIEMENT_C2_FR_EN.md';p.write_text(p.read_text().replace('R1','R2'))
print('C2 R2: ready/acknowledged Play, bounded start/arrival ramp. Source arrays and contacts untouched.')
