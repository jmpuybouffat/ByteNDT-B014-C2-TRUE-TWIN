from pathlib import Path
import json,csv
p=Path(__file__).parent;data=json.loads((p/'DONNEES_REJEU_C2.json').read_text());rows={r['edm_id']:r for r in csv.DictReader(open('/workspace/ByteNDT-B014-C2-TRUE-TWIN/BYTE_NDT_LSB941_DETECTIONS_PA2_C2.csv'))};aliases={k:float(r['path_range_mm'])for k,r in rows.items()};assert len(aliases)==6
for f in data['frames']:
 for c in f['clusters']:
  assert c['range_mm'] is None
  c['range_mm']=aliases[c['edm_label']]
for v in data['validation']:
 assert v['blind_range_mm'] is None
 v['blind_range_mm']=aliases[v['edm_id']]
for v in data['sensitivity']:v['blind_range_mm']=aliases[v['edm_id']]
data['range_alias_correction']={'input_column':'path_range_mm','output_column':'range_mm','reason':'Original loader omitted existing frozen source field; no acoustic value recomputed','values':aliases}
(p/'DONNEES_REJEU_C2_AFFICHEES.json').write_text(json.dumps(data,separators=(',',':'),allow_nan=False));(p/'CONTROLE_ALIAS_PARCOURS.json').write_text(json.dumps(data['range_alias_correction'],indent=2));print(aliases)
