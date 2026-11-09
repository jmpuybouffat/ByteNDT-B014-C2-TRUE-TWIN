from pathlib import Path
import json,re,gzip,base64
p=Path('/workspace/LSB941-C2-PUBLICATION/assets/SCENE_C2_SYNCHRONISEE.html');s=p.read_text();jd=json.JSONDecoder()
for key in ['DATA','C2_REGISTRATION','CONTACT','BEAM3D']:
 m=re.search(r'const '+key+r'\s*=',s);d,n=jd.raw_decode(s[m.end():]);raw=json.dumps(d,separators=(',',':')).encode();gz=base64.b64encode(gzip.compress(raw,6,mtime=0)).decode();s=s[:m.end()]+"await unpackC2('"+gz+"')"+s[m.end()+n:]
loader="""\nasync function unpackC2(b64){const bytes=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));const stream=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'));return JSON.parse(await new Response(stream).text())}\nwindow.C2AssetsReady=false;\n"""
s=s.replace('<script>\nconst DATA=', '<script type="module">'+loader+'const DATA=',1)
s=s.replace("if(m?.type==='C2_HELLO'){parent.postMessage", "if(m?.type==='C2_HELLO'){if(!window.C2AssetsReady)return;parent.postMessage")
s=s.replace("parent.postMessage({type:'C2_SCENE_READY'},'*');", "if(window.C2AssetsReady)parent.postMessage({type:'C2_SCENE_READY'},'*');")
s=s.replace('</script></html>',"window.C2AssetsReady=true;parent.postMessage({type:'C2_SCENE_READY'},'*');\n</script></html>")
p.write_text(s);print('Compressed browser scene',p.stat().st_size,flush=True)
