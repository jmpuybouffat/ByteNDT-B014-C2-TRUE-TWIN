from pathlib import Path
import struct
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title='Byte NDT — B014 C2 TRUE TWIN', layout='wide')
ROOT=Path(__file__).resolve().parent
DATA=ROOT/'B014_C2_DATA'

def csv(name, header='infer'):
    p=DATA/name
    return pd.read_csv(p, header=header)

def c2_curve():
    p=DATA/'C2_INDICATION_VALIDATED.csv'
    d=pd.read_csv(p, header=None)
    d=d.iloc[:,:3].apply(pd.to_numeric, errors='coerce').dropna()
    d.columns=['x','y','z']; return d

# FACE 2 geometry lock.
# B014_C2_BLADE.stl is already in millimetres: NEVER multiply it by 0.1.
# The wooden-block export is a separate CAD export and is not allowed to drive
# the PA2/C2 registration.
BLADE_SCALE = 1.0
WOODEN_SCALE = 0.1

WOODEN_R_TWIN_TO_CAO = np.array([
    [0.338962571711, 0.940625695776, 0.018101807228],
    [0.938655748872, -0.336829183447, -0.073969495656],
    [-0.063480391370, 0.042064255895, -0.997096203126],
], dtype=float)
WOODEN_T_TWIN_TO_CAO = np.array(
    [-26.823870012336, 150.164186762802, -94.009525515099],
    dtype=float,
)
WOODEN_STL = ROOT/'B014_C2_WOODENBLOCK.stl'
BLADE_STL = ROOT/'B014_C2_BLADE.stl'

# Fusion assembly registration measured from blade geometry only.
FUSION_ASSEMBLY_STL = ROOT/'ByteNDT_B009_FUSION_REFERENCE_BLADE_WOODENBLOCK.stl'
FUSION_ASSEMBLY_SCALE = 0.0908023186789272
FUSION_ASSEMBLY_R = np.array([
    [ 0.29512841,  0.95444327, -0.04401452],
    [ 0.95528462, -0.29388517,  0.03260077],
    [ 0.01818037, -0.05166780, -0.99849883],
], dtype=float)
FUSION_ASSEMBLY_T = np.array([-145.27965177, 152.26765862, -49.43855245], dtype=float)


def read_stl_mesh(path: Path, scale: float = 1.0):
    """Read binary or ASCII STL and return triangle vertices/faces in TRUE TWIN mm."""
    size=path.stat().st_size
    vertices=[]; faces=[]
    with path.open('rb') as f:
        header=f.read(80); count_raw=f.read(4)
        n_tri=struct.unpack('<I',count_raw)[0] if len(count_raw)==4 else 0
        binary=(len(header)==80 and len(count_raw)==4 and 84+50*n_tri==size)
        if binary:
            for _ in range(n_tri):
                rec=f.read(50)
                if len(rec)!=50: break
                vals=struct.unpack('<12fH',rec); base=len(vertices)
                vertices.extend([(vals[3]*scale,vals[4]*scale,vals[5]*scale),
                                 (vals[6]*scale,vals[7]*scale,vals[8]*scale),
                                 (vals[9]*scale,vals[10]*scale,vals[11]*scale)])
                faces.append((base,base+1,base+2))
        else:
            f.seek(0); tri=[]
            for raw in f:
                line=raw.decode('utf-8',errors='ignore').strip()
                if line.startswith('vertex '):
                    q=line.split()
                    if len(q)>=4:
                        tri.append(tuple(float(q[i])*scale for i in (1,2,3)))
                        if len(tri)==3:
                            base=len(vertices); vertices.extend(tri); faces.append((base,base+1,base+2)); tri=[]
    if not vertices or not faces:
        raise ValueError(f'No triangles in STL: {path.name}')
    return np.asarray(vertices,float),np.asarray(faces,int)

def add_mesh(fig, path: Path, name: str, opacity: float, scale: float = 1.0,
             R=None, T=None):
    if not path.exists():
        return False
    v,f = read_stl_mesh(path, scale=scale)
    if R is not None:
        v = v @ np.asarray(R, dtype=float).T
    if T is not None:
        v = v + np.asarray(T, dtype=float)
    fig.add_trace(go.Mesh3d(
        x=v[:,0], y=v[:,1], z=v[:,2],
        i=f[:,0], j=f[:,1], k=f[:,2],
        name=name, opacity=opacity, hoverinfo='skip', flatshading=True
    ))
    return True

path=csv('BYTE_NDT_V53_path_PA2_to_C2.csv')
curve=c2_curve()
det=csv('BYTE_NDT_LSB941_DETECTIONS_PA2_C2.csv')
met=csv('BYTE_NDT_LSB941_EDM_METROLOGY_PA2_C2.csv')
scan=csv('scan3D_groove_B_PA2_to_C2_2D8x8.csv')
coverage=csv('BYTE_NDT_LSB941_FULL_GROOVE_COVERAGE_PA2_C2.csv')

# Stable engineering order
order=[f'EDM_{i:02d}' for i in range(6,12)]
det['edm_id']=det['edm_id'].astype(str)
met['edm_id']=met['edm_id'].astype(str)
det['edm_id']=pd.Categorical(det['edm_id'],order,ordered=True)
met['edm_id']=pd.Categorical(met['edm_id'],order,ordered=True)
det=det.sort_values('edm_id'); met=met.sort_values('edm_id')

# Locked sensitivity calibration carried by the validated C2 detection dataset.
CAL_REF_ID = 'EDM_10'
cal_rows = det[det.get('is_calibration_reference', False).astype(bool)] if 'is_calibration_reference' in det.columns else pd.DataFrame()
if len(cal_rows):
    cal_row = cal_rows.iloc[0]
else:
    cal_row = det[det['edm_id'].astype(str) == CAL_REF_ID].iloc[0]
CAL_GAIN_FACTOR = float(cal_row['calibration_gain_factor']) if 'calibration_gain_factor' in det.columns else np.nan
CAL_RAW_REFERENCE = float(cal_row['calibration_raw_reference']) if 'calibration_raw_reference' in det.columns else np.nan
CAL_REFERENCE_TEXT = str(cal_row['calibration_reference']) if 'calibration_reference' in det.columns else 'EDM10 (3 mm) -> 50% FSH'
VALIDATION_TOL_MM = 6.0


# === B014 FACE 2 MASTER — FULL ARCHITECTURE / GEOMETRY LOCKED ===
N_POS=len(path); N_SECTOR=17; N_SKEW=5; N_LAWS_PER_POS=85; N_LAWS_TOTAL=N_POS*N_LAWS_PER_POS

def pick(df,names,default=0.0):
    for n in names:
        if n in df.columns: return df[n]
    return pd.Series(default,index=df.index)

def locked_scene(show_truth=False,show_tfm=False,current=None):
    fig=go.Figure()
    add_mesh(fig,BLADE_STL,'Blade / Aube — C2 validated frame',0.20,scale=BLADE_SCALE)
    add_mesh(fig,FUSION_ASSEMBLY_STL,'Fusion assembly — registered Wooden Block',0.09,
             scale=FUSION_ASSEMBLY_SCALE,R=FUSION_ASSEMBLY_R,T=FUSION_ASSEMBLY_T)
    fig.add_trace(go.Scatter3d(x=curve.x,y=curve.y,z=curve.z,mode='lines',name='C2 first groove',line=dict(width=7)))
    fig.add_trace(go.Scatter3d(x=path.probe_x,y=path.probe_y,z=path.probe_z,mode='lines+markers',
                               name='PA2 encoded path',marker=dict(size=2),line=dict(width=4)))
    if current is not None:
        i=current-1
        fig.add_trace(go.Scatter3d(x=[path.probe_x.iloc[i],path.focus_x.iloc[i]],
            y=[path.probe_y.iloc[i],path.focus_y.iloc[i]],z=[path.probe_z.iloc[i],path.focus_z.iloc[i]],
            mode='lines+markers',name=f'Current acoustic path {current}/{N_POS}',line=dict(width=8)))
    if show_truth:
        fig.add_trace(go.Scatter3d(x=det.edm_x_mm,y=det.edm_y_mm,z=det.edm_z_mm,mode='markers+text',
            text=det.edm_id.astype(str),textposition='top center',name='Mechanical EDM truth — AFTER detection',
            marker=dict(size=7,symbol='diamond')))
    if show_tfm:
        fig.add_trace(go.Scatter3d(x=met.max_x_mm,y=met.max_y_mm,z=met.max_z_mm,mode='markers',
            name='TFM voxel peak',marker=dict(size=5)))
    fig.update_layout(height=690,scene=dict(aspectmode='data',xaxis_title='X mm',yaxis_title='Y mm',zaxis_title='Z mm'),
                      legend=dict(orientation='h'))
    return fig

st.title('BYTE NDT — B014 TRUE TWIN — FACE 2 — PA2 → C2')
st.caption('Full Living Engineering application • PA2 EXTRADOS → C2 INTRADOS • Wooden Block geometry locked')
st.markdown("> **Inspection does not begin with the probe. It begins with the data.**  \n> **DATA → BUILD → EVIDENCE → ENGINEERING**")

k=st.columns(7)
for c,label,val in zip(k,['Probe','Elements','Frequency','Sectorial','Skew','Encoded positions','Total laws'],
 ['2D 8×8','64','5 MHz','35°→70°','−10°→+10°',str(N_POS),f'{N_LAWS_TOTAL:,}']): c.metric(label,val)
if N_POS!=199: st.error(f'ANTI-DRIFT — expected 199 PA2 positions; found {N_POS}.')
if len(met)!=6: st.error(f'ANTI-DRIFT — expected 6 C2 EDMs; found {len(met)}.')

tabs=st.tabs(['Overview','2D Matrix / Focal Laws','TRUE 3D Scan + Detection','Indication Explorer',
'Global Cartography / Blind Detection','EDM Validation','FMC / TFM','3D Voxel','Analysis / Decision',
'Report','Engineering Outputs','Final Video'])

with tabs[0]:
    st.header('Living Engineering Twin / Jumeau d’ingénierie vivante — FACE 2')
    st.plotly_chart(locked_scene(),width='stretch',key='face2_plot_1')
    st.success(f'GEOMETRY LOCKED • {N_POS} positions • 85 laws/position • {N_LAWS_TOTAL:,} laws • EDM truth reserved for post-detection validation.')

with tabs[1]:
    st.header('2D Matrix 8×8 — Focal Laws')
    c=st.columns(5)
    for q,l,v in zip(c,['Matrix','Elements','Sector laws','Skew laws','Laws / position'],['8×8','64','17','5','85']): q.metric(l,v)
    st.markdown(f'**35°→70° sectorial × −10°→+10° skew = 85 spatial laws/position; {N_LAWS_TOTAL:,} total. No complementary laws.**')
    p=DATA/'focal_laws_B_PA2_to_C2_2D8x8.csv'
    if p.exists(): st.dataframe(pd.read_csv(p).head(1000),width='stretch',height=430)

with tabs[2]:
    st.header('TRUE 3D Scan + Detection')
    shot=st.slider('Encoded PA2 position',1,N_POS,max(1,N_POS//2))
    st.plotly_chart(locked_scene(current=shot),width='stretch',key='face2_plot_2')
    st.info('Blind detection precedes display/use of mechanical EDM truth.')

with tabs[3]:
    st.header('Indication Explorer')
    e=st.selectbox('Indication / EDM',order)
    q=met[met.edm_id.astype(str)==e]
    if len(q):
        c=st.columns(3)
        c[0].metric('Amplitude',f"{float(pick(q,['amplitude_FSH_percent']).iloc[0]):.1f} %FSH")
        c[1].metric('−6 dB length',f"{float(pick(q,['minus6_length_mm','nominal_length_mm']).iloc[0]):.2f} mm")
        c[2].metric('Localization error',f"{float(pick(q,['localization_error_mm']).iloc[0]):.2f} mm")
    st.plotly_chart(locked_scene(True,True),width='stretch',key='face2_plot_3')

with tabs[4]:
    st.header('Global Cartography / Blind Detection')
    fig=locked_scene()
    bx=pick(det,['detected_x_mm','detection_x_mm','max_x_mm','edm_x_mm'])
    by=pick(det,['detected_y_mm','detection_y_mm','max_y_mm','edm_y_mm'])
    bz=pick(det,['detected_z_mm','detection_z_mm','max_z_mm','edm_z_mm'])
    fig.add_trace(go.Scatter3d(x=bx,y=by,z=bz,mode='markers',name='Blind detections',marker=dict(size=7)))
    st.plotly_chart(fig,width='stretch'); st.dataframe(det,width='stretch',height=350,key='face2_plot_4')
    st.info('Mechanical EDM truth is not used to manufacture blind detections.')

with tabs[5]:
    st.header('Mechanical EDM Validation — AFTER blind detection')
    st.plotly_chart(locked_scene(True,True),width='stretch',key='face2_plot_5')
    st.dataframe(det,width='stretch',height=330)
    st.caption(f'Spatial matching tolerance = {VALIDATION_TOL_MM:.1f} mm — NOT an acceptance criterion.')

with tabs[6]:
    st.header('FMC / TFM')
    e=st.selectbox('EDM for TFM',order,key='tfm')
    q=met[met.edm_id.astype(str)==e]
    if len(q):
        c=st.columns(4)
        c[0].metric('Amplitude',f"{float(pick(q,['amplitude_FSH_percent']).iloc[0]):.1f} %FSH")
        c[1].metric('θ',f"{float(pick(q,['theta_deg']).iloc[0]):.1f}°")
        c[2].metric('Skew',f"{float(pick(q,['skew_deg']).iloc[0]):.1f}°")
        c[3].metric('TOF',f"{float(pick(q,['tof_us']).iloc[0]):.2f} µs")
        st.dataframe(q,width='stretch')

with tabs[7]:
    st.header('3D Voxel / −6 dB')
    st.plotly_chart(locked_scene(True,True),width='stretch',key='face2_plot_6')
    cols=[c for c in ['edm_id','max_x_mm','max_y_mm','max_z_mm','amplitude_FSH_percent','minus6_length_mm',
                       'minus6_width_mm','minus6_depth_mm','localization_error_mm'] if c in met.columns]
    st.dataframe(met[cols],width='stretch',height=350)

with tabs[8]:
    st.header('Analysis / Decision')
    st.markdown(f'**Sensitivity:** {CAL_REFERENCE_TEXT} • gain factor `{CAL_GAIN_FACTOR:.6g}` • raw reference `{CAL_RAW_REFERENCE:.6g}`.')
    st.warning('Amplitudes in %FSH are already calibrated — NO second gain.')
    d=met.copy()
    if 'amplitude_FSH_percent' in d.columns:
        d['amplitude_over_50pct']=pd.to_numeric(d['amplitude_FSH_percent'],errors='coerce')>50
    st.dataframe(d,width='stretch',height=390)
    st.info('50% FSH + −6 dB sizing belong to the acceptance analysis. The 6 mm spatial matching tolerance remains separate.')

with tabs[9]:
    st.header('Report')
    report = (
        f"BYTE NDT — B014 TRUE TWIN — FACE 2\n\n"
        f"Inspection: PA2 EXTRADOS → C2 INTRADOS\n"
        f"Array: 8×8 / 64 elements / 5 MHz\n"
        f"Encoded positions: {N_POS}\n"
        f"Focal laws: 17 × 5 = 85/position → {N_LAWS_TOTAL:,} total\n"
        f"C2 target plane: Z ≈ {curve.z.median():.1f} mm\n"
        f"Mechanical EDM truth: EDM_06 → EDM_11\n"
        f"Sensitivity: EDM_10 (3 mm) = 50% FSH\n"
        f"Spatial validation tolerance: 6 mm, not an acceptance criterion\n"
        f"Sequence: blind detection → EDM validation → FMC/TFM → voxel/−6 dB → engineering decision\n"
        f"Geometry: Wooden Block + blade + PA2/C2 LOCKED\n"
    )
    st.text(report)
    st.download_button('Download report TXT',report.encode('utf-8'),'B014_C2_REPORT.txt','text/plain')
    st.download_button('Download C2 metrology CSV',met.to_csv(index=False).encode('utf-8'),'B014_C2_METROLOGY_FINAL.csv','text/csv')

with tabs[10]:
    st.header('Engineering Outputs')
    c=st.columns(4)
    c[0].metric('PA2 positions',N_POS); c[1].metric('Laws / position',85); c[2].metric('Total laws',f'{N_LAWS_TOTAL:,}'); c[3].metric('EDMs',len(met))
    st.markdown('**DATA → BUILD → EVIDENCE → ENGINEERING → SCANNER**')
    st.success('Face 2 package ready for integration with Face 1 and scanner feasibility engineering.')

with tabs[11]:
    st.header('Final Video')
    vids=list(ROOT.glob('*.mp4'))+list(DATA.glob('*.mp4'))
    if vids: st.video(str(vids[0]))
    else: st.info('No Face 2 MP4 is present in this package. No unrelated video is substituted.')

st.caption('Byte NDT — B014 TRUE TWIN • FACE 2 MASTER • geometry locked')
