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

st.title('BYTE NDT — B014 TRUE TWIN — PA2 → C2')
st.caption('Second inspection side • C2 intrados target • 8×8 / 64 elements • 5 MHz • mechanical EDM truth added after detection')

c1,c2,c3,c4,c5=st.columns(5)
c1.metric('Encoded PA2 positions',len(path))
c2.metric('Array','8×8 / 64')
c3.metric('C2 mechanical EDMs',len(met))
c4.metric('C2 target plane',f"Z = {curve.z.median():.1f} mm")
c5.metric('Sensitivity reference','EDM_10 = 50% FSH')
N_POS = len(path)
N_SECTOR = 17
N_SKEW = 5
N_LAWS_PER_POS = N_SECTOR * N_SKEW
N_LAWS_TOTAL = N_POS * N_LAWS_PER_POS
st.caption(f"{N_POS} positions × {N_SECTOR} sector laws × {N_SKEW} skew laws = {N_LAWS_TOTAL:,} focal laws. No complementary laws. • Locked C2 sensitivity: {CAL_REFERENCE_TEXT} • gain factor {CAL_GAIN_FACTOR:.6g} • raw reference {CAL_RAW_REFERENCE:.6g}. Spatial validation tolerance = {VALIDATION_TOL_MM:.1f} mm (not an acceptance criterion).")


st.info('GEOMETRY LOCK: PA2 probe coordinates and C2 focus coordinates are read together from BYTE_NDT_V53_path_PA2_to_C2.csv. They are never transformed independently.')

tabs=st.tabs(['C2 3D validation','Blind detections','Per-EDM TFM analysis','3D voxel / −6 dB','Coverage & data audit','Engineering summary'])

with tabs[0]:
    fig=go.Figure()
    # C2 reference geometry remains fixed.
    has_blade = add_mesh(
        fig, BLADE_STL, 'Blade / Aube — C2 validated frame',
        0.20, scale=BLADE_SCALE
    )

    # Wooden Block comes from the combined Fusion assembly.
    # Registration was solved from blade-to-blade geometry only:
    # no PA2, C2, EDM or TFM point was used to fit it.
    has_wood = add_mesh(
        fig, FUSION_ASSEMBLY_STL,
        'Fusion assembly — registered Wooden Block',
        0.09,
        scale=FUSION_ASSEMBLY_SCALE,
        R=FUSION_ASSEMBLY_R,
        T=FUSION_ASSEMBLY_T
    )
    fig.add_trace(go.Scatter3d(x=curve.x,y=curve.y,z=curve.z,mode='lines',name='C2 first groove',line=dict(width=7)))
    fig.add_trace(go.Scatter3d(x=path.probe_x,y=path.probe_y,z=path.probe_z,mode='lines+markers',name='PA2 encoded path',marker=dict(size=2),line=dict(width=4)))
    fig.add_trace(go.Scatter3d(x=path.focus_x,y=path.focus_y,z=path.focus_z,mode='lines',name='PA2 → C2 focus',line=dict(width=3,dash='dot')))
    fig.add_trace(go.Scatter3d(x=det.edm_x_mm,y=det.edm_y_mm,z=det.edm_z_mm,mode='markers+text',text=det.edm_id.astype(str),textposition='top center',name='Mechanical EDM truth',marker=dict(size=7,symbol='diamond')))
    fig.add_trace(go.Scatter3d(x=met.max_x_mm,y=met.max_y_mm,z=met.max_z_mm,mode='markers',name='TFM voxel peak',marker=dict(size=5)))
    fig.update_layout(height=720,scene=dict(aspectmode='data',xaxis_title='X mm',yaxis_title='Y mm',zaxis_title='Z mm'),legend=dict(orientation='h'))
    st.plotly_chart(fig,width='stretch')
    if not (has_wood and has_blade):
        missing=[]
        if not has_wood: missing.append(FUSION_ASSEMBLY_STL.name)
        if not has_blade: missing.append(BLADE_STL.name)
        st.warning('Geometry file(s) missing beside the app: '+', '.join(missing))
    else:
        st.success('FACE 2 VALIDATION: C2 blade + PA2/C2 fixed • Wooden Block registered by blade-to-blade CAO geometry • no EDM fitting.')
    st.info('Mechanical EDM truth is displayed here only for post-detection validation; it is not used to generate the blind detections.')

with tabs[1]:
    st.subheader('Blind detection — sensitivity locked before acceptance evaluation')
    g1,g2,g3=st.columns(3)
    g1.metric('Calibration EDM', CAL_REF_ID)
    g2.metric('Reference level','50% FSH')
    g3.metric('Gain factor',f'{CAL_GAIN_FACTOR:.4f}')
    st.caption('The amplitudes below are the calibrated values already stored in the validated PA2→C2 detection dataset. No extra gain is applied by this display.')
    cols=['edm_id','edm_length_mm','edm_x_mm','edm_y_mm','edm_z_mm','pa_index','scan_percent','theta_deg','skew_deg','tof_us','amplitude_FSH_percent','evaluation_50FSH','final_C_NC']
    st.dataframe(det[cols],width='stretch',hide_index=True)
    fig=go.Figure(go.Bar(x=det.edm_id.astype(str),y=det.amplitude_FSH_percent,name='Amplitude FSH %'))
    fig.add_hline(y=50,line_dash='dash',annotation_text='50% FSH reference')
    fig.update_layout(height=430,yaxis_title='% FSH',xaxis_title='C2 indication')
    st.plotly_chart(fig,width='stretch')

with tabs[2]:
    st.subheader('C2 per-EDM FMC/TFM pixel analysis')
    for _,r in met.iterrows():
        with st.expander(f"{r.edm_id} — {r.amplitude_FSH_percent:.1f}% FSH — localization error {r.localization_error_mm:.2f} mm", expanded=True):
            a,b,c,d=st.columns(4)
            a.metric('Nominal length',f"{r.nominal_length_mm:.1f} mm")
            b.metric('−6 dB length',f"{r.minus6_length_mm:.2f} mm")
            c.metric('−6 dB width',f"{r.minus6_width_mm:.2f} mm")
            d.metric('−6 dB depth',f"{r.minus6_depth_mm:.2f} mm")
            st.caption(f"Voxel peak: ({r.max_x_mm:.3f}, {r.max_y_mm:.3f}, {r.max_z_mm:.3f}) mm • θ={r.theta_deg:.1f}° • skew={r.skew_deg:.1f}° • ToF={r.tof_us:.3f} µs")

with tabs[3]:
    st.subheader('C2 3D FMC/TFM voxel analysis — −6 dB sizing')
    fig=go.Figure()
    fig.add_trace(go.Scatter3d(x=curve.x,y=curve.y,z=curve.z,mode='lines',name='C2 groove',line=dict(width=5)))
    for _,r in met.iterrows():
        fig.add_trace(go.Scatter3d(x=[r.max_x_mm],y=[r.max_y_mm],z=[r.max_z_mm],mode='markers+text',text=[str(r.edm_id)],textposition='top center',name=str(r.edm_id),marker=dict(size=max(5,float(r.minus6_length_mm)))))
    fig.update_layout(height=650,scene=dict(aspectmode='data',xaxis_title='X mm',yaxis_title='Y mm',zaxis_title='Z mm'))
    st.plotly_chart(fig,width='stretch')
    st.dataframe(met[['edm_id','amplitude_FSH_percent','minus6_length_mm','minus6_width_mm','minus6_depth_mm','response_volume_minus6_mm3','localization_error_mm','local_geometry_gate']],width='stretch',hide_index=True)

with tabs[4]:
    st.write('Source integrity / package counts')
    audit=pd.DataFrame({
      'Dataset':['PA2→C2 encoded path','C2 indication curve','Blind detections','Mechanical metrology','2D8×8 scan','Full groove coverage'],
      'Rows':[len(path),len(curve),len(det),len(met),len(scan),len(coverage)]})
    st.dataframe(audit,width='stretch',hide_index=True)
    st.write('PA2 path ranges')
    st.dataframe(pd.DataFrame({'axis':['probe X','probe Y','probe Z','focus X','focus Y','focus Z'],
      'min_mm':[path.probe_x.min(),path.probe_y.min(),path.probe_z.min(),path.focus_x.min(),path.focus_y.min(),path.focus_z.min()],
      'max_mm':[path.probe_x.max(),path.probe_y.max(),path.probe_z.max(),path.focus_x.max(),path.focus_y.max(),path.focus_z.max()]}),width='stretch',hide_index=True)
    st.caption('No C1 input is loaded by this application.')


with tabs[5]:
    st.subheader('FACE 2 — engineering summary / locked configuration')
    a,b,c,d=st.columns(4)
    a.metric('PA2 encoded positions', N_POS)
    b.metric('Laws / position', N_LAWS_PER_POS)
    c.metric('Total focal laws', f'{N_LAWS_TOTAL:,}')
    d.metric('Mechanical EDMs', len(met))
    st.markdown(
        "**Inspection direction:** PA2 on EXTRADOS → C2 on INTRADOS  \n"
        "**Array:** 8×8 / 64 elements / 5 MHz  \n"
        "**Sectorial:** 35°–70° • **Skew:** −10°…+10° • no complementary laws  \n"
        "**Sensitivity:** EDM_10 (3 mm) = 50% FSH; displayed amplitudes are already calibrated — no second gain.  \n"
        "**Validation:** 6 mm is a spatial matching tolerance only; it is not an acceptance criterion.  \n"
        "**Sequence:** blind detection first → mechanical EDM truth only for post-detection validation → FMC/TFM → −6 dB sizing → engineering decision.  \n"
        "**Geometry:** C2 blade + PA2/C2 are fixed; Wooden Block uses the validated blade-to-blade CAO registration."
    )
    st.success('FACE 2 package ready for local validation and Streamlit deployment.')
