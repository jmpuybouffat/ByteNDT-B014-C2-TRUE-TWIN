from pathlib import Path
import json,re,shutil,gzip,hashlib,csv,numpy as np
ROOT=Path('/workspace/LSB941-C2-PUBLICATION');A=ROOT/'assets';A.mkdir(exist_ok=True);R=ROOT/'reference_c2';R.mkdir(exist_ok=True);S=Path('/workspace/LSB941-C1-PUBLICATION/assets');P=Path(__file__).parent
JD=json.JSONDecoder()
def extract(s,key):
 m=re.search(r'const '+key+r'\s*=',s);assert m,key;d,n=JD.raw_decode(s[m.end():]);return d,m.end(),n
def put(s,key,d):
 old,i,n=extract(s,key);return s[:i]+json.dumps(d,separators=(',',':'),ensure_ascii=False,allow_nan=False)+s[i+n:]
def compact(s,key):
 d,i,n=extract(s,key);return s[:i]+'__PAYLOAD_'+key+'__'+s[i+n:],d
parent=(S/'00_OUVRIR_CYCLE_C1_FR_EN.html').read_text();child=(S/'SCENE_C1_SYNCHRONISEE.html').read_text();pp={};cc={}
for k in ['D','ANALYSIS','GUIDE','OPERATOR']:parent,pp[k]=compact(parent,k)
for k in ['DATA','C1_REGISTRATION','CONTACT','BEAM3D']:child,cc[k]=compact(child,k)
def retitle(s,child=False):
 # Only app-owned script after the data declaration; never rewrite bundled libraries.
 marker='const DATA='if child else'const D=';i=s.index(marker);prefix=s[:i];s=s[i:]
 s=s.replace('INTRADOS','__FACE_IN__').replace('EXTRADOS','INTRADOS').replace('__FACE_IN__','EXTRADOS').replace('intrados','__face_in__').replace('extrados','intrados').replace('__face_in__','extrados')
 s=s.replace('C1','C2').replace('c1','c2').replace('3 485','16 915').replace('3,485','16,915').replace('3485','16915').replace('5 / 5','6 / 6').replace('5/5','6/6').replace('5 EDM','6 EDM').replace('5 reference','6 reference').replace('5 EDM','6 EDM').replace('cinq','six').replace('five','six')
 for a,b in [(41,199),(39,197),(399,1979),(400,1980),(401,1981),(1599,7919),(1600,7920)]:s=re.sub(r'(?<![\w.])'+str(a)+r'(?![\w.])',str(b),s)
 for a,b in [('Math.min(40,','Math.min(198,'),('progress*40','progress*198'),('(m.shot-1)/40','(m.shot-1)/198'),('(40-phase)','(198-phase)'),('(40-glidePhase)','(198-glidePhase)'),('tau>=1?40:','tau>=1?198:'),('glidePhase>=40','glidePhase>=198'),('1/41','1/199'),('41.5','199.5'),('range=[.5,44]','range=[.5,202]')]:s=s.replace(a,b)
 # The 40 samples per station in arc-length inversion is a sampling rate, not the station count.
 s=s.replace('27.6mm reference: centre of first intrados groove.','C2: first intrados groove; mechanically registered source replay.').replace('Réf. 27,6 mm : milieu de la première gorge intrados.','C2 : première gorge intrados ; rejeu source recalé mécaniquement.')
 return ''.join(part if part.startswith('<script') else part.replace('C1','C2').replace('max="41"','max="199"').replace('41 / 41','199 / 199').replace('5 EDM','6 EDM') for part in re.split(r'(<script[\s\S]*?</script>)',prefix))+s
parent=retitle(parent);child=retitle(child,True)
D=json.loads((P/'DONNEES_REJEU_C2_COMPACT.json').read_text());AN=json.loads((P/'ANALYSES_SOURCE.json').read_text());DATA=json.loads(Path('/workspace/C2_mecanique/DATA_C2.json').read_text());REG=json.loads(Path('/workspace/C2_mecanique/REGISTRATION_C2.json').read_text());REG.pop('motion',None);REG['target_path_401']=[f['target']for f in REG['frames']];CONTACT=json.loads(Path('/workspace/C2_mecanique/CONTACT_C2.json').read_text());BEAM=json.loads(Path('/workspace/C2_beam_volume/C2_COHERENT_VOLUME.json').read_text());BEAM['mesh_quantization_mm']=.01
ref=float(D['sensitivity_meta']['reference_amplitude_db']);z=50*np.power(10,(np.array(D['encoded_db'])-ref)/20);vals=D['validation'];sens={r['edm_id']:r for r in D['sensitivity']};OP={**pp['OPERATOR'],'x':D['range_axis'],'y':list(range(1,200)),'z':np.clip(z,0,120).tolist(),'edm_labels':[r['edm_id']for r in vals],'edm_ranges':[r['blind_range_mm']for r in vals],'edm_shots':[r['blind_shot']for r in vals],'customdata':[[sens[r['edm_id']]['fsh_percent'],r['blind_amplitude_db'],r['error_mm']]for r in vals],'source':'Original C2 make_global_cartography calibration; existing path_range_mm alias restored','reference_sha256':hashlib.sha256((P/'DONNEES_REJEU_C2_AFFICHEES.json').read_bytes()).hexdigest()}
guide={'fr':'<h3>C2 — lecture et continuité</h3><p>PA sur extrados, gorge cible intrados. 199 positions ; six références EDM_06 à EDM_11. La cartographie utilise les réponses encodées du code source, avec EDM_10 de 3 mm à 50 % FSH. Les six maxima proviennent des tables d’examen figées chargées par l’application d’origine, puis comparées aux références. Ils ne sont pas les nouvelles sorties du détecteur de pics encodé. Le champ 3D est le maximum du gain cohérent des 85 lois : il ne représente pas le champ rétrodiffusé complet.</p><h3>Contact et mécanique</h3><p>Le contact graphique est projeté sur le maillage d’origine normalisé en millimètres une seule fois. Les coordonnées acoustiques restent dans leur repère source ; des transformations rigides par position construisent la vue mécanique sans changer les distances ni les phases. La face 25 × 25 mm et le slot restent à vérifier pour la fabrication. La mécanique de rupture requiert un matériau et un chargement définis ; aucun résultat de rupture n’est inventé.</p>', 'en':'<h3>C2 — reading and continuity</h3><p>PA on extrados, intrados target groove. 199 positions; six reference notches EDM_06 to EDM_11. Cartography uses the original encoded responses, calibrated with the 3 mm EDM_10 at 50% FSH. Six maxima are loaded from the frozen examination tables used by the original application, then compared with references. They are not new detections from the encoded peak detector. The 3D field is the maximum coherent gain over 85 laws, not the complete backscattered field.</p><h3>Contact and mechanics</h3><p>Graphic contact is projected onto the original mesh, normalized to millimetres once. Acoustic coordinates remain in their source frame; per-position rigid transforms construct the mechanical view without changing distances or phases. The 25 × 25 mm foot and slot still require manufacturing verification. Fracture mechanics requires defined material and loading; no fracture result is invented.</p>'}
# Reconstruct the original cloud snapshots on demand, verified numerically for every shot.
bootstrap='''\nconst cloudCache=new Map();function sourceCloud(i){if(cloudCache.has(i))return cloudCache.get(i);const f=D.frames[i],b=D.cloud_bank,ids=f.cloud_indices_u16?new Uint16Array(Uint8Array.from(atob(f.cloud_indices_u16),c=>c.charCodeAt(0)).buffer):Array.from({length:f.cloud_count},(_,j)=>j),out={cloud_xyz:Array.from(ids,j=>b.xyz[j]),cloud_db:Array.from(ids,j=>b.db[j]),cloud_shot:Array.from(ids,j=>b.shot[j])};cloudCache.clear();cloudCache.set(i,out);return out}D.frames.forEach((f,i)=>{for(const k of ['cloud_xyz','cloud_db','cloud_shot'])Object.defineProperty(f,k,{get:()=>sourceCloud(i)[k]})});\n'''
for k,d in [('D',D),('ANALYSIS',AN),('GUIDE',guide),('OPERATOR',OP)]:parent=parent.replace('__PAYLOAD_'+k+'__',json.dumps(d,separators=(',',':'),ensure_ascii=False,allow_nan=False),1)
# Insert before first code that can access a cloud property.
i=parent.index('const ANALYSIS=');parent=parent[:i]+bootstrap+parent[i:]
for k,d in [('DATA',DATA),('C2_REGISTRATION',REG),('CONTACT',CONTACT),('BEAM3D',BEAM)]:child=child.replace('__PAYLOAD_'+k+'__',json.dumps(d,separators=(',',':'),ensure_ascii=False,allow_nan=False),1)
# The template instructions about C1 peak extraction do not apply to frozen C2 maxima.
extra="""\nT.fr.detectionIntro='Maxima des tables d’examen C2 d’origine, affichés au tir associé. Les réponses encodées et ces maxima sont deux couches de données source conservées.';T.en.detectionIntro='Maxima from the original frozen C2 examination tables, displayed at the associated shot. Encoded responses and these maxima are two preserved source layers.';T.fr.footer='C2 — référence source conservée ; rejeu mécanique, sans nouvelle qualification physique.';T.en.footer='C2 — preserved source reference; mechanical replay, without new physical qualification.';refreshText();\n"""
extra += "\nGUIDE.fr="+json.dumps(guide['fr'],ensure_ascii=False)+";GUIDE.en="+json.dumps(guide['en'],ensure_ascii=False)+";T.fr.retained='Maxima d’examen conservés';T.en.retained='Preserved examination maxima';refreshText();\n"
child += ''
child=child.replace('Référence 27,6 mm : centre de première gorge intrados.','C2 : centre de première gorge intrados.').replace('27.6mm reference: centre of first intrados groove.','C2: centre of first intrados groove.')
child=child.replace('depth_mm:27.6','C1_datum_reference_mm:27.6')
parent=parent.replace('</script></body>',extra+'</script></body>')if '</script></body>'in parent else parent.replace('</script></html>',extra+'</script></html>')
assert '__PAYLOAD_'not in parent and '__PAYLOAD_'not in child
(A/'00_OUVRIR_CYCLE_C2_FR_EN.html').write_text(parent);(A/'SCENE_C2_SYNCHRONISEE.html').write_text(child)
for name in ['C2_RAPPORT_REFERENCE.html','C2_VALIDATION_REFERENCE.csv','C2_DETECTIONS_REFERENCE.csv','C2_CARTOGRAPHIE_REFERENCE.csv','C2_16915_LOIS_FOCALES.csv','C2_REGLAGES_PAR_POSITION.csv']:shutil.copy2(P/name,A/name)
# Display table/export range alias fix only; retain original copies under reference_c2.
import pandas as pd
pd.DataFrame(D['validation']).to_csv(A/'C2_VALIDATION_REFERENCE.csv',index=False);pd.DataFrame(D['frames'][-1]['clusters']).to_csv(A/'C2_DETECTIONS_REFERENCE.csv',index=False)
pd.DataFrame(D['validation']).assign(decision='REFERENCE MATCH / REVUE INGENIERIE').to_csv(A/'C2_ANALYSE_DECISION.csv',index=False)
(A/'C2_CONTEXTE_REFERENCE.json').write_text(json.dumps({'case':'C2','positions':199,'reference_EDMs':6,'source':D['source'],'registration_method':REG['method'],'physical_requalification':False,'backscatter_complete':False},indent=2))
for name in ['CONTROLE_REFERENCE_C2.json','CONTROLE_ALIAS_PARCOURS.json','charger_reference.py','reprendre_source.py','compact_data.py']:shutil.copy2(P/name,R/name)
print('C2 assembled parent',len(parent),'child',len(child),flush=True)
