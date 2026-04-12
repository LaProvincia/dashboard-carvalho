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

st.set_page_config(page_title="Dashboard Electoral · La Provincia", layout="wide", initial_sidebar_state="collapsed")

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
    p = Path(path)
    return base64.b64encode(p.read_bytes()).decode() if p.exists() else None

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
@st.cache_data
def cargar():
    df = pd.read_csv("puestos_medellin_FINAL.csv")
    df = df.rename(columns={'votos_quintero': 'votos_camilo', 'votos_cd': 'votos_cd_total'})
    return df

df = cargar()

prom_camilo   = df['votos_camilo'].mean()
prom_carvalho = df['votos_carvalho_2022'].mean()
prom_sanchez  = df['votos_sanchez'].mean()
prom_nanclares= df['votos_nanclares'].mean()
prom_creemos  = df['votos_creemos'].mean()
prom_pacto    = df['votos_pacto'].mean()
prom_cd       = df['votos_cd_total'].mean()
prom_hoyos    = df['votos_hoyos'].mean()

df['consolidado']   = (df['votos_camilo'] >= prom_camilo) & (df['votos_carvalho_2022'] >= prom_carvalho)
df['camilo_supera'] = df['votos_camilo'] > df['votos_carvalho_2022']
df['q_nucleo']      = (df['votos_carvalho_2022'] >= prom_carvalho) & (df['votos_hoyos'] < prom_hoyos)
df['q_disputa']     = (df['votos_carvalho_2022'] >= prom_carvalho) & (df['votos_hoyos'] >= prom_hoyos)
df['q_oport']       = (df['votos_carvalho_2022'] < prom_carvalho)  & (df['votos_hoyos'] >= prom_hoyos)
df['q_hostil']      = (df['votos_carvalho_2022'] < prom_carvalho)  & (df['votos_hoyos'] < prom_hoyos)

CENTER = {"lat": 6.2518, "lon": -75.5636}
ZOOM   = 11

def mapa_simple(df_m, col, titulo_color, escala=None, height=350):
    df_m = df_m[df_m['lat'].notna() & df_m['lon'].notna()].copy()
    df_m['size'] = df_m[col].apply(lambda x: max(5, min(28, x / 8)))
    esc = escala or [[0,'#ffffff'],[0.5, VERDE_CLARO],[1, VERDE_OSCURO]]
    fig = go.Figure(go.Scattermapbox(
        lat=df_m['lat'], lon=df_m['lon'], mode='markers',
        marker=dict(size=df_m['size'], color=df_m[col], colorscale=esc,
                    colorbar=dict(title="Votos", thickness=10, x=1.0), opacity=0.88),
        text=df_m.apply(lambda r: f"<b>{r['nombre_puesto']}</b><br>Zona: {r['zona']}<br>{titulo_color}: {int(r[col])}", axis=1),
        hoverinfo='text'
    ))
    fig.update_layout(mapbox=dict(style="carto-positron", zoom=ZOOM, center=CENTER),
                      margin={"r":0,"t":0,"l":0,"b":0}, height=height,
                      paper_bgcolor=CREMA, showlegend=False)
    return fig

def top20(df_m, col, label):
    top = df_m.nlargest(20, col)[['nombre_puesto','zona', col]].reset_index(drop=True)
    top.index += 1
    top.columns = ['Puesto','Zona', label]
    return top

def seccion(titulo):
    st.markdown(f'<div class="seccion"><h3>{titulo}</h3></div>', unsafe_allow_html=True)

def grupo(titulo):
    st.markdown(f'<div class="seccion-grupo"><h2>{titulo}</h2></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — MÉTRICAS Y DATOS CLAVE
# ══════════════════════════════════════════════════════════════════════════════
grupo("📊 Sección 1 — Resumen general")

seccion("Totales de votos")
c1,c2,c3,c4,c5,c6 = st.columns(6)
c1.metric("Camilo 2026",       f"{df['votos_camilo'].sum():,}")
c2.metric("Alejandra Sánchez", f"{df['votos_sanchez'].sum():,}")
c3.metric("Rafael Nanclares",  f"{df['votos_nanclares'].sum():,}")
c4.metric("Carvalho 2022",     f"{df['votos_carvalho_2022'].sum():,}")
c5.metric("Creemos",           f"{df['votos_creemos'].sum():,}")
c6.metric("Pacto Histórico",   f"{df['votos_pacto'].sum():,}")

st.markdown("---")
seccion("Promedio de votos por puesto de votación")
st.markdown("Estos promedios definen el umbral de 'alto' en el análisis estratégico.")
d1,d2,d3,d4,d5,d6 = st.columns(6)
d1.metric("Promedio Camilo",    f"{prom_camilo:.1f}")
d2.metric("Promedio Sánchez",   f"{prom_sanchez:.1f}")
d3.metric("Promedio Nanclares", f"{prom_nanclares:.1f}")
d4.metric("Promedio Carvalho",  f"{prom_carvalho:.1f}")
d5.metric("Promedio Creemos",   f"{prom_creemos:.1f}")
d6.metric("Promedio Pacto",     f"{prom_pacto:.1f}")

st.markdown(f"""
> Carvalho promedió **{prom_carvalho:.0f} votos por puesto** en 2022 vs **{prom_camilo:.0f} de Camilo** en 2026 — Carvalho tuvo **{prom_carvalho/prom_camilo:.1f}x más votos por puesto**. El reto de cara a la alcaldía es reactivar esa base.
""")

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — EL PROYECTO
# ══════════════════════════════════════════════════════════════════════════════
grupo("🟢 Sección 2 — El proyecto: nuestros candidatos")

seccion("🗺️ Votos Carvalho 2022 — Mapa y Top 20 puestos")
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, 'votos_carvalho_2022', 'Carvalho 2022'), use_container_width=True)
with col2:
    st.dataframe(top20(df, 'votos_carvalho_2022', 'Carvalho 2022'), use_container_width=True, height=370)

st.markdown("---")
seccion("🗺️ Votos Camilo 2026 — Mapa y Top 20 puestos")
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, 'votos_camilo', 'Camilo 2026'), use_container_width=True)
with col2:
    st.dataframe(top20(df, 'votos_camilo', 'Camilo 2026'), use_container_width=True, height=370)

st.markdown("---")
seccion("🗺️ Votos Alejandra Sánchez 2026 — Mapa y Top 20 puestos")
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, 'votos_sanchez', 'Alejandra Sánchez',
                                escala=[[0,'#ffffff'],[0.5,'#A8D5A2'],[1,VERDE_OSCURO]]),
                    use_container_width=True)
with col2:
    st.dataframe(top20(df, 'votos_sanchez', 'Alejandra Sánchez'), use_container_width=True, height=370)

st.markdown("---")
seccion("🗺️ Votos Rafael Nanclares 2026 — Mapa y Top 20 puestos")
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, 'votos_nanclares', 'Rafael Nanclares',
                                escala=[[0,'#ffffff'],[0.5,'#A8C8A0'],[1,VERDE_OSCURO]]),
                    use_container_width=True)
with col2:
    st.dataframe(top20(df, 'votos_nanclares', 'Rafael Nanclares'), use_container_width=True, height=370)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — COMPARACIÓN CAMILO VS CARVALHO
# ══════════════════════════════════════════════════════════════════════════════
grupo("🔄 Sección 3 — Comparación Camilo 2026 vs Carvalho 2022")

seccion("🗺️ Mapa A — Camilo 2026 vs Carvalho 2022 superpuestos")
st.markdown("Camilo en **verde** (círculo derecho) · Carvalho en **azul** (círculo izquierdo) · Tamaño proporcional a votos")
df_a = df[df['lat'].notna() & df['lon'].notna()].copy()
OFFSET = 0.0003
fig_a = go.Figure()
fig_a.add_trace(go.Scattermapbox(
    lat=df_a['lat'], lon=df_a['lon'] - OFFSET, mode='markers',
    marker=dict(size=df_a['votos_carvalho_2022'].apply(lambda x: max(6, min(30, x/12))),
                color='#4A90D9', opacity=0.85),
    text=df_a.apply(lambda r: f"<b>{r['nombre_puesto']}</b><br>Carvalho 2022: {int(r['votos_carvalho_2022'])}<br>Camilo 2026: {int(r['votos_camilo'])}", axis=1),
    hoverinfo='text', name='Carvalho 2022'
))
fig_a.add_trace(go.Scattermapbox(
    lat=df_a['lat'], lon=df_a['lon'] + OFFSET, mode='markers',
    marker=dict(size=df_a['votos_camilo'].apply(lambda x: max(6, min(30, x/5))),
                color=VERDE_OSCURO, opacity=0.85),
    text=df_a.apply(lambda r: f"<b>{r['nombre_puesto']}</b><br>Camilo 2026: {int(r['votos_camilo'])}<br>Carvalho 2022: {int(r['votos_carvalho_2022'])}", axis=1),
    hoverinfo='text', name='Camilo 2026'
))
fig_a.update_layout(mapbox=dict(style="carto-positron", zoom=ZOOM, center=CENTER),
                    margin={"r":0,"t":0,"l":0,"b":0}, height=480, paper_bgcolor=CREMA,
                    showlegend=True, legend=dict(bgcolor=CREMA, bordercolor=VERDE_MEDIO,
                    borderwidth=1, font=dict(color=VERDE_OSCURO), x=0.01, y=0.99))
st.plotly_chart(fig_a, use_container_width=True)

st.markdown("---")
seccion("📈 Correlación Carvalho 2022 vs Camilo 2026")
df_sc = df[df['votos_carvalho_2022'] > 0].copy()
fig_sc = px.scatter(df_sc, x='votos_carvalho_2022', y='votos_camilo',
                    hover_name='nombre_puesto', color='zona', size='votos_camilo',
                    height=420, labels={'votos_carvalho_2022':'Carvalho 2022','votos_camilo':'Camilo 2026','zona':'Zona'},
                    color_continuous_scale=[[0,VERDE_CLARO],[1,VERDE_OSCURO]])
max_val = max(df_sc['votos_carvalho_2022'].max(), df_sc['votos_camilo'].max())
fig_sc.add_shape(type='line', x0=0, y0=0, x1=max_val, y1=max_val,
                 line=dict(color=VERDE_CLARO, dash='dash', width=1.5))
fig_sc.update_layout(paper_bgcolor=CREMA, plot_bgcolor=CREMA, font=dict(color=VERDE_OSCURO),
                     xaxis=dict(gridcolor="#E0D8C8"), yaxis=dict(gridcolor="#E0D8C8"))
st.plotly_chart(fig_sc, use_container_width=True)
corr = df_sc[['votos_carvalho_2022','votos_camilo']].corr().iloc[0,1]
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
    st.dataframe(tabla_sup, use_container_width=True, height=370)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — COMPARACIÓN DE PARTIDOS
# ══════════════════════════════════════════════════════════════════════════════
grupo("⚔️ Sección 4 — La competencia: comparación de partidos")

seccion("🗺️ Mapa Pacto Histórico + Top 20")
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, 'votos_pacto', 'Pacto Histórico',
                                escala=[[0,'#ffffff'],[0.5,'#E87070'],[1,'#C0392B']]),
                    use_container_width=True)
with col2:
    st.dataframe(top20(df, 'votos_pacto', 'Pacto Histórico'), use_container_width=True, height=370)

st.markdown("---")
seccion("🗺️ Mapa Creemos + Top 20")
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, 'votos_creemos', 'Creemos',
                                escala=[[0,'#ffffff'],[0.5,'#F0C060'],[1,'#E8A838']]),
                    use_container_width=True)
with col2:
    st.dataframe(top20(df, 'votos_creemos', 'Creemos'), use_container_width=True, height=370)

st.markdown("---")
seccion("🗺️ Mapa Centro Democrático — Total partido + Top 20")
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, 'votos_cd_total', 'Centro Democrático',
                                escala=[[0,'#ffffff'],[0.5,'#6090D9'],[1,'#1A3A6B']]),
                    use_container_width=True)
with col2:
    st.dataframe(top20(df, 'votos_cd_total', 'Centro Democrático'), use_container_width=True, height=370)

st.markdown("---")
seccion("🗺️ Mapa Federico Hoyos — Individual + Top 20")
col1, col2 = st.columns([1.6, 1])
with col1:
    st.plotly_chart(mapa_simple(df, 'votos_hoyos', 'Federico Hoyos',
                                escala=[[0,'#ffffff'],[0.5,'#8AAAE0'],[1,'#4A90D9']]),
                    use_container_width=True)
with col2:
    st.dataframe(top20(df, 'votos_hoyos', 'Federico Hoyos'), use_container_width=True, height=370)

st.markdown("---")
seccion("🗺️ Mapa B — Dominancia por puesto (Creemos vs Pacto vs Centro Democrático)")
df_b = df[df['lat'].notna() & df['lon'].notna()].copy()
def quien_domina(r):
    votos = {'Creemos': r['votos_creemos'], 'Pacto': r['votos_pacto'], 'Centro Democrático': r['votos_cd_total']}
    return max(votos, key=votos.get)
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
c1.metric("Puestos Creemos domina", f"{dom_count.get('Creemos',0)}")
c2.metric("Puestos Pacto domina", f"{dom_count.get('Pacto',0)}")
c3.metric("Puestos Centro Democrático domina", f"{dom_count.get('Centro Democrático',0)}")

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5 — ANÁLISIS ESTRATÉGICO ALCALDÍA
# ══════════════════════════════════════════════════════════════════════════════
grupo("🏛️ Sección 5 — Análisis estratégico de cara a la alcaldía")

seccion(f"✅ Puestos consolidados — Carvalho alto Y Camilo alto")
df_con = df[df['consolidado']].copy()
st.markdown(f"**{len(df_con)} puestos consolidados** — núcleo duro del proyecto. Prioridad máxima de retención.")
col1, col2 = st.columns([1.6, 1])
with col1:
    df_con_m = df_con[df_con['lat'].notna()].copy()
    fig_con = go.Figure(go.Scattermapbox(
        lat=df_con_m['lat'], lon=df_con_m['lon'], mode='markers',
        marker=dict(size=12, color=VERDE_OSCURO, opacity=0.9),
        text=df_con_m.apply(lambda r: f"<b>{r['nombre_puesto']}</b><br>Camilo: {int(r['votos_camilo'])} | Carvalho: {int(r['votos_carvalho_2022'])}", axis=1),
        hoverinfo='text'
    ))
    fig_con.update_layout(mapbox=dict(style="carto-positron", zoom=ZOOM, center=CENTER),
                          margin={"r":0,"t":0,"l":0,"b":0}, height=350, paper_bgcolor=CREMA, showlegend=False)
    st.plotly_chart(fig_con, use_container_width=True)
with col2:
    t = df_con[['nombre_puesto','zona','votos_camilo','votos_carvalho_2022']].sort_values('votos_carvalho_2022', ascending=False).reset_index(drop=True)
    t.index += 1
    t.columns = ['Puesto','Zona','Camilo','Carvalho 2022']
    st.dataframe(t, use_container_width=True, height=370)

st.markdown("---")
seccion(f"🧭 Análisis de cuadrantes — Carvalho vs Federico Hoyos")
n1,n2,n3,n4 = df['q_nucleo'].sum(), df['q_disputa'].sum(), df['q_oport'].sum(), df['q_hostil'].sum()
st.markdown(f"Promedio Carvalho: **{prom_carvalho:.0f} votos/puesto** · Promedio Hoyos: **{prom_hoyos:.0f} votos/puesto**")
m1,m2,m3,m4 = st.columns(4)
m1.metric("🟢 Núcleo puro",          f"{n1} puestos", "Carvalho alto + Hoyos bajo")
m2.metric("🔵 Territorio disputado", f"{n2} puestos", "Carvalho alto + Hoyos alto")
m3.metric("🟡 Oportunidad CD",       f"{n3} puestos", "Carvalho bajo + Hoyos alto")
m4.metric("⚫ Terreno hostil",       f"{n4} puestos", "Carvalho bajo + Hoyos bajo")

df_q = df[df['lat'].notna() & df['lon'].notna()].copy()
cuadrantes = [
    ('q_nucleo',  '🟢 Núcleo puro',          VERDE_OSCURO),
    ('q_disputa', '🔵 Territorio disputado',  '#4A90D9'),
    ('q_oport',   '🟡 Oportunidad CD',        '#E8A838'),
    ('q_hostil',  '⚫ Terreno hostil',        '#888888'),
]
fig_q = go.Figure()
for col_q, nombre_q, color_q in cuadrantes:
    sub = df_q[df_q[col_q]]
    fig_q.add_trace(go.Scattermapbox(
        lat=sub['lat'], lon=sub['lon'], mode='markers',
        marker=dict(size=10, color=color_q, opacity=0.88),
        text=sub.apply(lambda r: f"<b>{r['nombre_puesto']}</b><br>Zona: {r['zona']}<br>Carvalho: {int(r['votos_carvalho_2022'])} | Hoyos: {int(r['votos_hoyos'])}<br>Camilo: {int(r['votos_camilo'])}", axis=1),
        hoverinfo='text', name=nombre_q
    ))
fig_q.update_layout(mapbox=dict(style="carto-positron", zoom=ZOOM, center=CENTER),
                    margin={"r":0,"t":0,"l":0,"b":0}, height=500, paper_bgcolor=CREMA,
                    showlegend=True, legend=dict(bgcolor=CREMA, bordercolor=VERDE_MEDIO,
                    borderwidth=1, font=dict(color=VERDE_OSCURO), x=0.01, y=0.99))
st.plotly_chart(fig_q, use_container_width=True)

st.markdown("""
**Lectura estratégica:**
- 🟢 **Núcleo puro** — votantes exclusivos del proyecto, sin competencia de CD. Retener a toda costa.
- 🔵 **Territorio disputado** — el mismo electorado se divide entre Carvalho y CD. Hay que ganarle ese votante a Hoyos.
- 🟡 **Oportunidad CD** — electorado de CD donde el proyecto no ha penetrado. Potencial de crecimiento con propuesta de centro.
- ⚫ **Terreno hostil** — ni el proyecto ni CD tienen fuerza. Territorio de Creemos o Pacto. No invertir.
""")

st.markdown("---")
seccion("📋 Tabla completa por puesto")
cols = ['zona','nombre_puesto','votos_camilo','votos_carvalho_2022','votos_hoyos','votos_sanchez','votos_nanclares','votos_creemos','votos_pacto','votos_cd_total']
tabla = df[cols].sort_values('votos_camilo', ascending=False).reset_index(drop=True)
tabla.index += 1
tabla.columns = ['Zona','Puesto','Camilo','Carvalho 2022','Hoyos','Sánchez','Nanclares','Creemos','Pacto','Centro Democrático']
st.dataframe(tabla, use_container_width=True, height=420)

st.markdown("---")
st.markdown(f"<p style='text-align:center;color:{VERDE_MEDIO};font-size:0.78rem'>La Provincia · Dashboard Electoral Medellín 2026 · Datos: Registraduría Nacional</p>", unsafe_allow_html=True)
