import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import base64

VERDE_OSCURO = "#1B4332"
VERDE_MEDIO  = "#2D6A4F"
VERDE_CLARO  = "#52B788"
CREMA        = "#F0EAD6"
BLANCO       = "#FFFFFF"

st.set_page_config(page_title="Dashboard Electoral · La Provincia", layout="wide", initial_sidebar_state="expanded")

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'Montserrat', sans-serif; background-color: {CREMA}; color: {VERDE_OSCURO}; }}
    .stApp {{ background-color: {CREMA}; }}
    .block-container {{ padding-top: 1rem; }}
    [data-testid="stSidebar"] {{ background-color: {VERDE_OSCURO}; }}
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p {{ color: {CREMA} !important; }}
    [data-testid="metric-container"] {{ background-color: {VERDE_OSCURO}; border-radius: 8px; padding: 12px; }}
    [data-testid="metric-container"] label {{ color: {VERDE_CLARO} !important; font-size: 0.75rem; font-weight: 600; }}
    [data-testid="metric-container"] [data-testid="stMetricValue"] {{ color: {CREMA} !important; font-size: 1.5rem; font-weight: 700; }}
    .header-box {{ background-color: {VERDE_OSCURO}; padding: 16px 24px; border-radius: 12px; margin-bottom: 18px; display: flex; align-items: center; gap: 20px; }}
    .header-text h1 {{ color: {CREMA}; font-size: 1.4rem; font-weight: 700; margin: 0; }}
    .header-text p {{ color: {VERDE_CLARO}; margin: 4px 0 0 0; font-size: 0.85rem; }}
    .seccion {{ background-color: {BLANCO}; border-left: 4px solid {VERDE_MEDIO}; border-radius: 6px; padding: 6px 14px; margin: 24px 0 10px 0; }}
    .seccion h3 {{ color: {VERDE_OSCURO}; margin: 0; font-size: 1rem; font-weight: 700; }}
    .seccion-grupo {{ background-color: {VERDE_OSCURO}; border-radius: 8px; padding: 8px 16px; margin: 32px 0 16px 0; }}
    .seccion-grupo h2 {{ color: {CREMA}; margin: 0; font-size: 1.1rem; font-weight: 700; }}
    hr {{ border-color: {VERDE_MEDIO}44; }}
</style>
""", unsafe_allow_html=True)

# ── Logo ──────────────────────────────────────────────────────────────────────
def get_b64(path):
    for nombre in [path, path.replace('.png', '.PNG'), path.replace('.PNG', '.png')]:
        p = Path(nombre)
        if p.exists():
            return base64.b64encode(p.read_bytes()).decode()
    return None

logo_b64 = get_b64("logo_provincia.png")
logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="height:70px;border-radius:8px;">' if logo_b64 else "🏔️"

st.markdown(f"""
<div class="header-box">
    {logo_html}
    <div class="header-text">
        <h1>Análisis electoral — Compilado de elecciones políticas del proyecto político Carvalho</h1>
        <p>Producto de: La Provincia &nbsp;·&nbsp; Datos: Registraduría Nacional &nbsp;·&nbsp; Medellín 2022–2026</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Datos ─────────────────────────────────────────────────────────────────────
import os as _os

def _csv_version():
    p = "puestos_medellin_FINAL.csv"
    s = _os.stat(p)
    return f"{s.st_mtime}_{s.st_size}"

@st.cache_data
def cargar(version=""):
    df = pd.read_csv("puestos_medellin_FINAL.csv")
    # Asegurar tipos numéricos
    for col in df.columns:
        if col not in ['id_puesto','municipio','nombre_puesto','nombre_norm','PUESTO','DIRECCIÓN','COMUNA','tipo_match']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
    return df

df = cargar(version=_csv_version())

prom_camilo   = df['votos_camilo'].mean()
prom_carvalho = df['votos_carvalho_2022'].mean()
prom_sanchez  = df['votos_sanchez'].mean()
prom_nanclares= df['votos_nanclares'].mean()
prom_creemos  = df['votos_creemos'].mean()
prom_pacto    = df['votos_pacto'].mean()
prom_cd       = df['votos_cd_total'].mean()

df['consolidado']   = (df['votos_camilo'] >= prom_camilo) & (df['votos_carvalho_2022'] >= prom_carvalho)
df['camilo_supera'] = df['votos_camilo'] > df['votos_carvalho_2022']

CENTER = {"lat": 6.2518, "lon": -75.5636}
ZOOM   = 11

# ── Sidebar ───────────────────────────────────────────────────────────────────
if logo_b64:
    st.sidebar.markdown(f'<div style="text-align:center;padding:10px 0 16px"><img src="data:image/png;base64,{logo_b64}" style="height:55px;border-radius:6px;"></div>', unsafe_allow_html=True)

st.sidebar.markdown(f"<h3 style='color:{CREMA};margin-top:0'>⚙️ Opciones</h3>", unsafe_allow_html=True)

modo = st.sidebar.radio(
    "Modo de análisis",
    ["Votos absolutos", "% del total Medellín", "% de la zona"],
    help="Cambia cómo se muestran los valores en mapas, rankings y correlación"
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"<p style='color:{VERDE_CLARO};font-size:0.72rem;text-align:center'>La Provincia · Análisis Electoral 2026</p>", unsafe_allow_html=True)

# ── Columnas según modo ───────────────────────────────────────────────────────
def col_modo(candidato):
    col_votos = {
        'carvalho': 'votos_carvalho_2022',
        'camilo':   'votos_camilo',
        'sanchez':  'votos_sanchez',
        'nanclares': 'votos_nanclares',
        'creemos':  'votos_creemos',
        'pacto':    'votos_pacto',
        'cd':       'votos_cd_total'
    }
    if modo == "Votos absolutos":
        return col_votos[candidato]
    elif modo == "% del total Medellín":
        return f'pct_medellin_{candidato}'
    else:
        return f'pct_zona_{candidato}'

def label_modo(candidato, nombre):
    """Devuelve la etiqueta correcta para hover y tablas"""
    if modo == "Votos absolutos":
        return f"{nombre}: votos"
    elif modo == "% del total Medellín":
        return f"{nombre}: % Medellín"
    else:
        return f"{nombre}: % zona"

def fmt(val):
    """Formato según modo"""
    if modo == "Votos absolutos":
        return f"{int(val):,}"
    else:
        return f"{val:.2f}%"

# ── Helpers ───────────────────────────────────────────────────────────────────
def mapa_simple(df_m, col, titulo_color, escala=None, height=350):
    df_m = df_m[df_m['lat'].notna() & df_m['lon'].notna()].copy()
    max_val = df_m[col].max() if df_m[col].max() > 0 else 1
    df_m['size'] = df_m[col].apply(lambda x: max(5, min(28, x / max_val * 28)))
    esc = escala or [[0,'#ffffff'],[0.5, VERDE_CLARO],[1, VERDE_OSCURO]]
    fig = go.Figure(go.Scattermapbox(
        lat=df_m['lat'], lon=df_m['lon'], mode='markers',
        marker=dict(size=df_m['size'], color=df_m[col], colorscale=esc,
                    colorbar=dict(title="%" if modo != "Votos absolutos" else "Votos", thickness=10, x=1.0), opacity=0.88),
        text=df_m.apply(lambda r: f"<b>{r['nombre_puesto']}</b><br>Zona: {r['zona']}<br>{titulo_color}: {fmt(r[col])}", axis=1),
        hoverinfo='text'
    ))
    fig.update_layout(mapbox=dict(style="carto-positron", zoom=ZOOM, center=CENTER),
                      margin={"r":0,"t":0,"l":0,"b":0}, height=height,
                      paper_bgcolor=CREMA, showlegend=False)
    return fig

def top40(df_m, col, label, col_abs=None):
    # Siempre incluir votos absolutos si estamos en modo relativo
    if col_abs and col_abs != col:
        top = df_m.nlargest(40, col)[['nombre_puesto','zona', col_abs, col]].reset_index(drop=True)
        top.index += 1
        top[col] = top[col].apply(fmt)
        top.columns = ['Puesto','Zona','Votos', label]
    else:
        top = df_m.nlargest(40, col)[['nombre_puesto','zona', col]].reset_index(drop=True)
        top.index += 1
        top[col] = top[col].apply(fmt)
        top.columns = ['Puesto','Zona', label]
    return top

def seccion(titulo):
    st.markdown(f'<div class="seccion"><h3>{titulo}</h3></div>', unsafe_allow_html=True)

def grupo(titulo):
    st.markdown(f'<div class="seccion-grupo"><h2>{titulo}</h2></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — RESUMEN GENERAL
# ══════════════════════════════════════════════════════════════════════════════
grupo("📊 Sección 1 — Resumen general")

seccion("Totales de votos")
c1,c2,c3,c4,c5,c6,c7 = st.columns(7)
c1.metric("Camilo 2026",          f"{df['votos_camilo'].sum():,}")
c2.metric("Alejandra Sánchez",    f"{df['votos_sanchez'].sum():,}")
c3.metric("Rafael Nanclares",     f"{df['votos_nanclares'].sum():,}")
c4.metric("Carvalho 2022",        f"{df['votos_carvalho_2022'].sum():,}")
c5.metric("Creemos",              f"{df['votos_creemos'].sum():,}")
c6.metric("Pacto Histórico",      f"{df['votos_pacto'].sum():,}")
c7.metric("Centro Democrático",   f"{df['votos_cd_total'].sum():,}")

st.markdown("---")
seccion("Promedio de votos por puesto de votación")
d1,d2,d3,d4,d5,d6,d7 = st.columns(7)
d1.metric("Promedio Camilo",    f"{prom_camilo:.1f}")
d2.metric("Promedio Sánchez",   f"{prom_sanchez:.1f}")
d3.metric("Promedio Nanclares", f"{prom_nanclares:.1f}")
d4.metric("Promedio Carvalho",  f"{prom_carvalho:.1f}")
d5.metric("Promedio Creemos",   f"{prom_creemos:.1f}")
d6.metric("Promedio Pacto",     f"{prom_pacto:.1f}")
d7.metric("Promedio CD",        f"{prom_cd:.1f}")

st.markdown(f"""
> Carvalho promedió **{prom_carvalho:.0f} votos por puesto** en 2022 vs **{prom_camilo:.0f} de Camilo** en 2026 — Carvalho tuvo **{prom_carvalho/prom_camilo:.1f}x más votos por puesto**.
> Pacto Histórico: **{prom_pacto:.0f}** · Creemos: **{prom_creemos:.0f}** · Centro Democrático: **{prom_cd:.0f}** votos promedio por puesto.
""")

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — EL PROYECTO
# ══════════════════════════════════════════════════════════════════════════════
grupo("🟢 Sección 2 — El proyecto: nuestros candidatos")

seccion("🗺️ Votos Carvalho 2022 — Mapa y Top 20 puestos")
col_carvalho = col_modo('carvalho')
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, col_carvalho, label_modo('carvalho','Carvalho 2022')), use_container_width=True)
with col2:
    st.dataframe(top40(df, col_carvalho, label_modo('carvalho','Carvalho 2022'), col_abs='votos_carvalho_2022'), use_container_width=True, height=580)

st.markdown("---")
seccion("🗺️ Votos Camilo 2026 — Mapa y Top 20 puestos")
col_camilo = col_modo('camilo')
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, col_camilo, label_modo('camilo','Camilo 2026')), use_container_width=True)
with col2:
    st.dataframe(top40(df, col_camilo, label_modo('camilo','Camilo 2026'), col_abs='votos_camilo'), use_container_width=True, height=580)

st.markdown("---")
seccion("🗺️ Votos Alejandra Sánchez 2026 — Mapa y Top 20 puestos")
col_sanchez = col_modo('sanchez')
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, col_sanchez, label_modo('sanchez','Alejandra Sánchez'),
                                escala=[[0,'#ffffff'],[0.5,'#A8D5A2'],[1,VERDE_OSCURO]]),
                    use_container_width=True)
with col2:
    st.dataframe(top40(df, col_sanchez, label_modo('sanchez','Alejandra Sánchez'), col_abs='votos_sanchez'), use_container_width=True, height=580)

st.markdown("---")
seccion("🗺️ Votos Rafael Nanclares 2026 — Mapa y Top 20 puestos")
col_nanclares = col_modo('nanclares')
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, col_nanclares, label_modo('nanclares','Rafael Nanclares'),
                                escala=[[0,'#ffffff'],[0.5,'#A8C8A0'],[1,VERDE_OSCURO]]),
                    use_container_width=True)
with col2:
    st.dataframe(top40(df, col_nanclares, label_modo('nanclares','Rafael Nanclares'), col_abs='votos_nanclares'), use_container_width=True, height=580)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — COMPARACIÓN CAMILO VS CARVALHO
# ══════════════════════════════════════════════════════════════════════════════
grupo("🔄 Sección 3 — Comparación Camilo 2026 vs Carvalho 2022")

seccion("🗺️ Mapa A — Camilo 2026 vs Carvalho 2022 superpuestos")
st.markdown(f"Camilo en **verde** (derecha) · Carvalho en **azul** (izquierda) · Modo: **{modo}**")
df_a = df[df['lat'].notna() & df['lon'].notna()].copy()
df_a['lat'] = df_a['lat'].astype(float)
df_a['lon'] = df_a['lon'].astype(float)
OFFSET = 0.0003
col_a_carvalho = col_modo('carvalho')
col_a_camilo   = col_modo('camilo')
escala_a = 8 if modo == "Votos absolutos" else 0.3

fig_a = go.Figure()
fig_a.add_trace(go.Scattermapbox(
    lat=df_a['lat'], lon=df_a['lon'] - OFFSET, mode='markers',
    marker=dict(size=df_a[col_a_carvalho].apply(lambda x: max(6, min(30, x/escala_a))),
                color='#4A90D9', opacity=0.85),
    text=df_a.apply(lambda r: f"<b>{r['nombre_puesto']}</b><br>Carvalho: {fmt(r[col_a_carvalho])}<br>Camilo: {fmt(r[col_a_camilo])}", axis=1),
    hoverinfo='text', name='Carvalho 2022'
))
fig_a.add_trace(go.Scattermapbox(
    lat=df_a['lat'], lon=df_a['lon'] + OFFSET, mode='markers',
    marker=dict(size=df_a[col_a_camilo].apply(lambda x: max(6, min(30, x/escala_a))),
                color=VERDE_OSCURO, opacity=0.85),
    text=df_a.apply(lambda r: f"<b>{r['nombre_puesto']}</b><br>Camilo: {fmt(r[col_a_camilo])}<br>Carvalho: {fmt(r[col_a_carvalho])}", axis=1),
    hoverinfo='text', name='Camilo 2026'
))
fig_a.update_layout(mapbox=dict(style="carto-positron", zoom=ZOOM, center=CENTER),
                    margin={"r":0,"t":0,"l":0,"b":0}, height=480, paper_bgcolor=CREMA,
                    showlegend=True, legend=dict(bgcolor=CREMA, bordercolor=VERDE_MEDIO,
                    borderwidth=1, font=dict(color=VERDE_OSCURO), x=0.01, y=0.99))
st.plotly_chart(fig_a, use_container_width=True)

st.markdown("---")
seccion(f"📈 Correlación Carvalho 2022 vs Camilo 2026 — {modo}")
df_sc = df[df[col_a_carvalho] > 0].copy()
fig_sc = px.scatter(df_sc, x=col_a_carvalho, y=col_a_camilo,
                    hover_name='nombre_puesto', color='zona', size=col_a_camilo,
                    height=420,
                    labels={col_a_carvalho: f'Carvalho 2022 ({modo})',
                            col_a_camilo: f'Camilo 2026 ({modo})', 'zona':'Zona'},
                    color_continuous_scale=[[0,VERDE_CLARO],[1,VERDE_OSCURO]])
max_val = max(df_sc[col_a_carvalho].max(), df_sc[col_a_camilo].max())
fig_sc.add_shape(type='line', x0=0, y0=0, x1=max_val, y1=max_val,
                 line=dict(color=VERDE_CLARO, dash='dash', width=1.5))
fig_sc.update_layout(paper_bgcolor=CREMA, plot_bgcolor=CREMA, font=dict(color=VERDE_OSCURO),
                     xaxis=dict(gridcolor="#E0D8C8"), yaxis=dict(gridcolor="#E0D8C8"))
st.plotly_chart(fig_sc, use_container_width=True)
corr = df_sc[[col_a_carvalho, col_a_camilo]].corr().iloc[0,1]
st.markdown(f"**Correlación de Pearson: {corr:.3f}** {'— correlación positiva fuerte ✅' if corr > 0.5 else '— correlación moderada ⚠️' if corr > 0.3 else '— correlación débil ❌'}")

st.markdown("---")
seccion("🔍 Puestos donde Camilo superó a Carvalho 2022")
df_sup = df[df['camilo_supera']].copy()
df_sup_real = df_sup[df_sup['votos_carvalho_2022'] > 0]
df_sup_cero = df_sup[df_sup['votos_carvalho_2022'] == 0]
st.markdown(f"""
**{len(df_sup)} puestos** en total — con una lectura importante:
- **{len(df_sup_cero)} puestos** donde Carvalho tuvo **0 votos** en 2022 — puestos nuevos o donde el proyecto no llegó.
- **{len(df_sup_real)} puestos** donde Carvalho sí tuvo votos y Camilo lo superó — diferencia de 1 a 2 votos (prácticamente empate).

**Conclusión:** Camilo no superó a Carvalho en ningún territorio consolidado. La base de Carvalho ({prom_carvalho:.0f} votos promedio) es {prom_carvalho/prom_camilo:.1f}x más amplia que la de Camilo ({prom_camilo:.0f}).
""")
col1, col2 = st.columns([1.6, 1])
with col1:
    df_sup_m = df_sup[df_sup['lat'].notna()].copy()
    fig_sup = go.Figure()
    fig_sup.add_trace(go.Scattermapbox(
        lat=df_sup_m[df_sup_m['votos_carvalho_2022']==0]['lat'],
        lon=df_sup_m[df_sup_m['votos_carvalho_2022']==0]['lon'], mode='markers',
        marker=dict(size=10, color='#888888', opacity=0.8),
        text=df_sup_m[df_sup_m['votos_carvalho_2022']==0].apply(
            lambda r: f"<b>{r['nombre_puesto']}</b><br>Camilo: {int(r['votos_camilo'])} | Carvalho: 0", axis=1),
        hoverinfo='text', name='Carvalho sin votos en 2022'
    ))
    fig_sup.add_trace(go.Scattermapbox(
        lat=df_sup_m[df_sup_m['votos_carvalho_2022']>0]['lat'],
        lon=df_sup_m[df_sup_m['votos_carvalho_2022']>0]['lon'], mode='markers',
        marker=dict(size=14, color=VERDE_OSCURO, opacity=0.9),
        text=df_sup_m[df_sup_m['votos_carvalho_2022']>0].apply(
            lambda r: f"<b>{r['nombre_puesto']}</b><br>Camilo: {int(r['votos_camilo'])} | Carvalho: {int(r['votos_carvalho_2022'])}", axis=1),
        hoverinfo='text', name='Camilo supera (real)'
    ))
    fig_sup.update_layout(mapbox=dict(style="carto-positron", zoom=ZOOM, center=CENTER),
                          margin={"r":0,"t":0,"l":0,"b":0}, height=350,
                          paper_bgcolor=CREMA, showlegend=True,
                          legend=dict(bgcolor=CREMA, font=dict(color=VERDE_OSCURO), x=0.01, y=0.99))
    st.plotly_chart(fig_sup, use_container_width=True)
with col2:
    tabla_sup = df_sup[['nombre_puesto','zona','votos_camilo','votos_carvalho_2022']].sort_values('votos_camilo', ascending=False).reset_index(drop=True)
    tabla_sup.index += 1
    tabla_sup.columns = ['Puesto','Zona','Camilo','Carvalho 2022']
    st.dataframe(tabla_sup, use_container_width=True, height=580)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — LA COMPETENCIA
# ══════════════════════════════════════════════════════════════════════════════
grupo("⚔️ Sección 4 — La competencia: comparación de partidos")

seccion("🗺️ Mapa Pacto Histórico + Top 20")
col_pacto = col_modo('pacto')
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, col_pacto, label_modo('pacto','Pacto Histórico'),
                                escala=[[0,'#ffffff'],[0.5,'#E87070'],[1,'#C0392B']]),
                    use_container_width=True)
with col2:
    st.dataframe(top40(df, col_pacto, label_modo('pacto','Pacto Histórico'), col_abs='votos_pacto'), use_container_width=True, height=580)

st.markdown("---")
seccion("🗺️ Mapa Creemos + Top 20")
col_creemos = col_modo('creemos')
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, col_creemos, label_modo('creemos','Creemos'),
                                escala=[[0,'#ffffff'],[0.5,'#F0C060'],[1,'#E8A838']]),
                    use_container_width=True)
with col2:
    st.dataframe(top40(df, col_creemos, label_modo('creemos','Creemos'), col_abs='votos_creemos'), use_container_width=True, height=580)

st.markdown("---")
seccion("🗺️ Mapa Centro Democrático — Total partido + Top 20")
col_cd = col_modo('cd')
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, col_cd, label_modo('cd','Centro Democrático'),
                                escala=[[0,'#ffffff'],[0.5,'#6090D9'],[1,'#1A3A6B']]),
                    use_container_width=True)
with col2:
    st.dataframe(top40(df, col_cd, label_modo('cd','Centro Democrático'), col_abs='votos_cd_total'), use_container_width=True, height=580)

st.markdown("---")
seccion("🗺️ Mapa B — Dominancia por puesto (Creemos vs Pacto vs Centro Democrático)")
df_b = df[df['lat'].notna() & df['lon'].notna()].copy()
def quien_domina(r):
    v = {'Creemos': r['votos_creemos'], 'Pacto': r['votos_pacto'], 'Centro Democrático': r['votos_cd_total']}
    return max(v, key=v.get)
df_b['dominante'] = df_b.apply(quien_domina, axis=1)
colores_dom = {'Creemos': '#E8A838', 'Pacto': '#C0392B', 'Centro Democrático': '#1A3A6B'}
fig_b = go.Figure()
for partido, color in colores_dom.items():
    sub = df_b[df_b['dominante'] == partido]
    fig_b.add_trace(go.Scattermapbox(
        lat=sub['lat'], lon=sub['lon'], mode='markers',
        marker=dict(size=10, color=color, opacity=0.85),
        text=sub.apply(lambda r: f"<b>{r['nombre_puesto']}</b><br>Zona: {r['zona']}<br>Domina: {r['dominante']}<br>Creemos: {int(r['votos_creemos'])} | Pacto: {int(r['votos_pacto'])} | CD: {int(r['votos_cd_total'])}", axis=1),
        hoverinfo='text', name=partido
    ))
fig_b.update_layout(mapbox=dict(style="carto-positron", zoom=ZOOM, center=CENTER),
                    margin={"r":0,"t":0,"l":0,"b":0}, height=480, paper_bgcolor=CREMA,
                    showlegend=True, legend=dict(bgcolor=CREMA, bordercolor=VERDE_MEDIO,
                    borderwidth=1, font=dict(color=VERDE_OSCURO), x=0.01, y=0.99))
st.plotly_chart(fig_b, use_container_width=True)
dom_count = df_b['dominante'].value_counts()
c1,c2,c3 = st.columns(3)
c1.metric("Puestos Creemos domina",           f"{dom_count.get('Creemos',0)}")
c2.metric("Puestos Pacto domina",             f"{dom_count.get('Pacto',0)}")
c3.metric("Puestos Centro Democrático domina",f"{dom_count.get('Centro Democrático',0)}")

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5 — ESTRATÉGICO ALCALDÍA
# ══════════════════════════════════════════════════════════════════════════════
grupo("🏛️ Sección 5 — Análisis estratégico de cara a la alcaldía")

seccion(f"✅ Puestos consolidados — Carvalho alto Y Camilo alto")
df_con = df[df['consolidado']].copy()
st.markdown(f"**{len(df_con)} puestos consolidados** — núcleo duro del proyecto. Prioridad máxima de retención.")
col1, col2 = st.columns([1.6, 1])
with col1:
    df_con_m = df_con[df_con['lat'].notna()].copy()
    col_con_cam = col_modo('camilo')
    col_con_car = col_modo('carvalho')
    max_c = df_con_m[col_con_cam].max() if df_con_m[col_con_cam].max() > 0 else 1
    fig_con = go.Figure(go.Scattermapbox(
        lat=df_con_m['lat'], lon=df_con_m['lon'], mode='markers',
        marker=dict(
            size=df_con_m[col_con_cam].apply(lambda x: max(8, min(28, x/max_c*28))),
            color=df_con_m[col_con_cam],
            colorscale=[[0,VERDE_CLARO],[1,VERDE_OSCURO]],
            colorbar=dict(title=modo, thickness=10, x=1.0),
            opacity=0.9),
        text=df_con_m.apply(lambda r: f"<b>{r['nombre_puesto']}</b><br>Camilo ({modo}): {fmt(r[col_con_cam])} | Carvalho ({modo}): {fmt(r[col_con_car])}<br>Camilo votos: {int(r['votos_camilo'])} | Carvalho votos: {int(r['votos_carvalho_2022'])}", axis=1),
        hoverinfo='text'
    ))
    fig_con.update_layout(mapbox=dict(style="carto-positron", zoom=ZOOM, center=CENTER),
                          margin={"r":0,"t":0,"l":0,"b":0}, height=350, paper_bgcolor=CREMA, showlegend=False)
    st.plotly_chart(fig_con, use_container_width=True)
with col2:
    t = df_con[['nombre_puesto','zona','votos_camilo','votos_carvalho_2022',
                col_modo('camilo'), col_modo('carvalho')]].sort_values('votos_carvalho_2022', ascending=False).reset_index(drop=True)
    t.index += 1
    t.columns = ['Puesto','Zona','Camilo (votos)','Carvalho (votos)', f'Camilo ({modo})', f'Carvalho ({modo})']
    st.dataframe(t, use_container_width=True, height=580)

st.markdown("---")
seccion("📋 Tabla completa por puesto")
_cols_base = ['zona','nombre_puesto','votos_camilo','votos_carvalho_2022',
              'votos_sanchez','votos_nanclares','votos_creemos','votos_pacto','votos_cd_total']
_nombres_base = ['Zona','Puesto','Camilo','Carvalho 2022','Sánchez','Nanclares',
                 'Creemos','Pacto','Centro Democrático']

if modo == "Votos absolutos":
    # Solo columnas absolutas — sin duplicados
    tabla = df[_cols_base].sort_values('votos_camilo', ascending=False).reset_index(drop=True)
    tabla.index += 1
    tabla.columns = _nombres_base
else:
    # Absolutas + columnas relativas formateadas como "X.XX%"
    _pct_suffix = 'medellin' if modo == "% del total Medellín" else 'zona'
    _candidatos = ['camilo','carvalho','sanchez','nanclares','creemos','pacto','cd']
    _cols_pct = [f'pct_{_pct_suffix}_{c}' for c in _candidatos]
    _nombres_pct = [f'Camilo %', f'Carvalho %', f'Sánchez %',
                    f'Nanclares %', f'Creemos %', f'Pacto %', f'CD %']
    tabla = df[_cols_base + _cols_pct].sort_values('votos_camilo', ascending=False).reset_index(drop=True)
    tabla.index += 1
    tabla.columns = _nombres_base + _nombres_pct
    for col in _nombres_pct:
        tabla[col] = tabla[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "0.00%")
st.dataframe(tabla, use_container_width=True, height=420)

st.markdown("---")
st.markdown(f"<p style='text-align:center;color:{VERDE_MEDIO};font-size:0.78rem'>La Provincia · Dashboard Electoral Medellín 2026 · Datos: Registraduría Nacional</p>", unsafe_allow_html=True)
