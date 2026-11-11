"""C2 bilingual source replay, separate from the accepted C1 app."""
from pathlib import Path
import hashlib,json
import streamlit as st
from publication_view import build_publication_document
st.set_page_config(page_title='BYTE NDT — LSB941 C2 — FR / EN',layout='wide',initial_sidebar_state='collapsed')
RELEASE_ID='C2-VUES-R04'
root=Path(__file__).resolve().parent
st.info('C2 · VUES R04 · Première gorge intrados G1 · 199 positions')
st.caption('PA EXTRADOS → gorge INTRADOS · six EDM 06–11 · 16 915 lois · FR / EN')
st.caption('Rejeu des résultats sources dans des poses mécaniques recalées ; sans nouvelle qualification physique. / Source results replayed in registered mechanical poses; no new physical qualification.')
assets=root/'assets'
manifest=json.loads((root/'reference_c2/MANIFESTE_ASSETS_PUBLIES.json').read_text())
bad=[name for name,digest in manifest.items()if not(assets/name).is_file()or hashlib.sha256((assets/name).read_bytes()).hexdigest()!=digest]
if bad:
 st.error('Version incomplète. / Incomplete release files.');st.stop()
with st.spinner('Chargement C2 / Loading C2…'):
 st.iframe(build_publication_document(assets),height='content',alt='C2 — 199 positions — FR / EN')
with st.expander('Notice et identification / Guide and identification'):
 st.download_button('Notice FR / EN', (assets/'NOTICE_C2_FR_EN.pdf').read_bytes(),file_name='NOTICE_C2_FR_EN.pdf',mime='application/pdf')
 st.caption('La version affichée dans cette application est le point de référence actuel. / The version displayed here is the current reference.')
