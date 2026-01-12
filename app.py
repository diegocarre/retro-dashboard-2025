import streamlit as st
import google.generativeai as genai
import pandas as pd
import time
import streamlit.components.v1 as components 

# --- 1. CONFIGURACIÓN VISUAL (LOOK & FEEL CARREFOUR) ---
LOGO_URL = "https://images.seeklogo.com/logo-png/27/1/carrefour-logo-png_seeklogo-273111.png"
# 👇 RECUERDA PONER TU LINK DEL FORMULARIO AQUÍ
FORM_URL = "https://forms.gle/TU_FORMULARIO_AQUI" 

st.set_page_config(
    page_title="Dashboard Innovación 2026",
    page_icon=LOGO_URL,
    layout="wide"
)

# Ajustes CSS
st.markdown("""
    <style>
    .block-container {padding-top: 2rem;}
    div[data-testid="stButton"] button {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. TUS DATOS DEL SHEET (Protegidos) ---
try:
    sheet_id = st.secrets["SHEET_ID"]
    gid = st.secrets["GID"]
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
except Exception:
    st.error("⚠️ Faltan configurar los IDs en secrets.toml")
    st.stop()

# --- 3. CONEXIÓN CON IA ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.warning("⚠️ Falta API Key en secrets.toml")
except Exception:
    pass

# --- CACHÉ DE DATOS ---
@st.cache_data(ttl=60)
def load_data(url):
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

# --- 4. ENCABEZADO ---
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
    st.image(LOGO_URL, width=90)
with col_titulo:
    st.title("Retrospectiva Innovación 2026")
    st.caption("Resultados alineados al Ciclo de Vida de Proyectos | Carrefour Argentina")

st.divider()

# --- 5. SECCIÓN DE ACTIVIDAD (TIMER + MÚSICA + QR) ---
st.subheader("⏱️ Actividad: Llenado de Formulario")

col_controls, col_timer, col_qr = st.columns([1, 2, 1])

# --- COLUMNA 1: CONTROLES ---
with col_controls:
    sub_c1, sub_c2 = st.columns([1, 1], vertical_alignment="center")
    with sub_c1:
        st.write("**Tiempo (min):**")
    with sub_c2:
        minutes = st.number_input("Minutos", min_value=1, value=5, step=1, label_visibility="collapsed")
    
    start_button = st.button("▶️ Iniciar Actividad", type="primary", use_container_width=True)
    stop_placeholder = st.empty()
    music_placeholder = st.empty()

# --- COLUMNA 3: QR ---
with col_qr:
    st.info("📱 **Escanea para opinar:**")
    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={FORM_URL}&color=003896"
    st.image(qr_api_url, width=200)

# --- COLUMNA 2: RELOJ ---
with col_timer:
    timer_placeholder = st.empty()
    
    if start_button:
        # Música (Thunderstruck)
        soundcloud_iframe = """
        <iframe width="100%" height="166" scrolling="no" frameborder="no" allow="autoplay" 
        src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/105085838&color=%23003896&auto_play=true&hide_related=false&show_comments=false&show_user=true&show_reposts=false&show_teaser=true"></iframe>
        """
        with col_controls:
            music_placeholder.markdown(soundcloud_iframe, unsafe_allow_html=True)

        # Lógica Reloj
        total_secs = minutes * 60
        stop_clicked = False

        while total_secs >= 0:
            with stop_placeholder:
                if st.button("⛔ Detener / Reset", key=f"stop_{total_secs}", type="secondary"):
                    stop_clicked = True
                    break 

            mins, secs = divmod(total_secs, 60)
            time_format = '{:02d}:{:02d}'.format(mins, secs)
            
            timer_placeholder.markdown(
                f"""
                <div style="text-align: center;">
                    <p style="font-size: 20px; margin-bottom: 0;">Tiempo Restante</p>
                    <h1 style="font-size: 90px; color: #003896; margin-top: 0;">{time_format}</h1>
                </div>
                """, 
                unsafe_allow_html=True
            )
            time.sleep(1)
            total_secs -= 1
        
        if stop_clicked:
            st.rerun()
        else:
            timer_placeholder.markdown(
                "<div style='background-color: #e01e37; padding: 20px; border-radius: 10px; text-align: center; margin-top: 20px;'><h1 style='color: white; margin: 0;'>🛑 ¡TIEMPO FINALIZADO!</h1></div>", 
                unsafe_allow_html=True
            )
            stop_placeholder.empty()

st.divider()

# --- 6. RESULTADOS ---
st.subheader("📊 Resultados en Tiempo Real")

if st.button("🔄 Actualizar Tablero"):
    st.cache_data.clear() 
    st.rerun()

try:
    df = load_data(csv_url)

    if df.empty:
        st.info("📉 Esperando respuestas... (El tablero está limpio)")
    else:
        df.columns = ["Fecha", "Categoria", "Comentario"]
        
        # --- A. MÉTRICAS ---
        c1, c2, c3 = st.columns(3)
        total = len(df)
        keeps = len(df[df['Categoria'].str.contains("KEEP", case=False, na=False)])
        others = total - keeps
        
        c1.metric("Total Tickets", total, border=True)
        c2.metric("🟢 Keep (Mantener)", keeps, border=True)
        c3.metric("🔴 Change/Stop", others, delta_color="inverse", border=True)

        st.write("---")

        # --- B. GRÁFICOS Y FILTROS (NUEVO) ---
        col_grafico, col_filtro = st.columns([2, 1])
        
        with col_grafico:
            st.caption("Distribución por Categoría")
            # Contamos cuántos hay de cada tipo
            conteo_categorias = df["Categoria"].value_counts()
            st.bar_chart(conteo_categorias, color="#003896") # Azul Carrefour
            
        with col_filtro:
            st.caption("🔍 Filtrar Tabla")
            # Obtenemos las categorías únicas
            categorias_unicas = df["Categoria"].unique()
            filtro = st.multiselect("Selecciona Categoría:", options=categorias_unicas, default=categorias_unicas)
            
            # Filtramos el DataFrame según la selección
            df_filtrado = df[df["Categoria"].isin(filtro)]

        # --- C. TABLA DETALLADA ---
        st.subheader("📥 Detalles del Feedback")
        st.dataframe(
            df_filtrado.tail(10), # Mostramos el filtrado, no el original
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Categoria": st.column_config.TextColumn("Tipo", width="small"),
                "Comentario": st.column_config.TextColumn("Observación", width="large"),
                "Fecha": st.column_config.TextColumn("Recibido", width="small"),
            }
        )

        st.divider()
        
        # --- D. CEREBRO IA (PMO) ---
        st.subheader("🧠 Análisis Gerencial (PMO)")
        
        if st.button("✨ Generar Reporte Ejecutivo", type="primary"):
            with st.spinner("Consultando Guía de Ciclo de Vida y analizando..."):
                txt = ""
                # Le enviamos a la IA solo lo que está filtrado (para análisis específicos) o todo si no hay filtro
                data_para_ia = df_filtrado if not df_filtrado.empty else df
                
                for i, row in data_para_ia.iterrows():
                    txt += f"- [{row['Categoria']}] {row['Comentario']}\n"
                
                prompt = """
                Actúa como un Experto en Oficina de Proyectos (PMO). Analiza los comentarios.
                CONTEXTO: Ciclo de Vida de 8 Fases (Génesis a Soporte).
                INSTRUCCIONES:
                1. 🌡️ Termómetro Emocional.
                2. 🏆 Puntos Fuertes (Fases que funcionan).
                3. ⚠️ Cuellos de Botella (Asociados a fases).
                4. 💡 Recomendación Directiva.
                COMENTARIOS:
                """
                model = genai.GenerativeModel('gemini-2.5-pro')
                response = model.generate_content(prompt + txt)
                st.markdown(response.text)

except Exception as e:
    st.error("Error leyendo el Google Sheet.")
    st.text(f"Detalle técnico: {e}")