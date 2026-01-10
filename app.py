import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- 1. CONFIGURACIÓN VISUAL (LOOK & FEEL CARREFOUR) ---
# Usamos el logo oficial desde Wikimedia
# LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Carrefour_logo.svg/1024px-Carrefour_logo.svg"
LOGO_URL = "https://images.seeklogo.com/logo-png/27/1/carrefour-logo-png_seeklogo-273111.png"
st.set_page_config(
    page_title="Dashboard Innovación 2025",
    page_icon=LOGO_URL,
    layout="wide"
)

# Ajustes CSS para mejorar la cabecera
st.markdown("""
    <style>
    .block-container {padding-top: 2rem;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. TUS DATOS DEL SHEET (Protegidos) ---
# En lugar de escribirlo aquí, lo leemos de los secretos
try:
    sheet_id = st.secrets["SHEET_ID"]
    gid = st.secrets["GID"]
except:
    st.error("Faltan configurar los IDs en secrets.toml")
    st.stop()

# --- 3. CONEXIÓN CON IA ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.warning("⚠️ Falta API Key en secrets.toml")
except Exception:
    pass

# --- 4. ENCABEZADO CORPORATIVO ---
col_logo, col_titulo = st.columns([1, 6])

with col_logo:
    st.image(LOGO_URL, width=90) # Logo ajustado

with col_titulo:
    st.title("Retrospectiva Innovación 2026")
    st.caption("Resultados alineados al Ciclo de Vida de Proyectos | Carrefour Argentina")

# Botón de actualización
if st.button("🔄 Actualizar Tablero"):
    st.cache_data.clear()
    st.rerun()

st.divider()

# --- 5. LÓGICA PRINCIPAL ---
try:
    # Leemos directo el CSV (Tu método robusto)
    df = pd.read_csv(csv_url)

    if df.empty:
        st.info("📉 El tablero está limpio. Esperando datos...")
    else:
        # Renombramos columnas
        df.columns = ["Fecha", "Categoria", "Comentario"]
        
        # --- MÉTRICAS CON ESTILO ---
        c1, c2, c3 = st.columns(3)
        total = len(df)
        keeps = len(df[df['Categoria'].str.contains("KEEP", case=False, na=False)])
        others = total - keeps
        
        # Usamos border=True para dar efecto de "tarjeta"
        c1.metric("Total Tickets", total, border=True)
        c2.metric("🟢 Keep (Mantener)", keeps, border=True)
        c3.metric("🔴 Change/Stop", others, delta_color="inverse", border=True)

        # --- TABLA ESTILIZADA ---
        st.subheader("📥 Detalles del Feedback")
        st.dataframe(
            df.tail(10), 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "Categoria": st.column_config.TextColumn("Tipo", width="small"),
                "Comentario": st.column_config.TextColumn("Observación", width="large"),
                "Fecha": st.column_config.TextColumn("Recibido", width="small"),
            }
        )

        # --- 6. CEREBRO IA (PMO Contextualizado) ---
        st.divider()
        st.subheader("🧠 Análisis Gerencial (PMO)")
        
        if st.button("✨ Generar Reporte Ejecutivo", type="primary"):
            with st.spinner("Consultando Guía de Ciclo de Vida y analizando..."):
                txt = ""
                for i, row in df.iterrows():
                    txt += f"- [{row['Categoria']}] {row['Comentario']}\n"
                
                # TU PROMPT EXITOSO
                prompt = """
                Actúa como un Experto en Oficina de Proyectos (PMO) y Calidad.
                Analiza los siguientes comentarios de la retrospectiva anual del equipo de Innovación.
                
                CONTEXTO:
                El equipo NO usa Agile puro. Usamos un Ciclo de Vida de 8 Fases estandarizado. 
                Usa estas definiciones para clasificar los problemas:
                
                1. GÉNESIS: Triage, ideas, urgencia y carga de trabajo inicial.
                2. ANÁLISIS: Definición de alcance, Sponsor/Product Owner y viabilidad técnica.
                3. PROTOTIPADO: Validación de concepto, MVP y Business Case.
                4. APROBACIÓN: Comités (CIP), CAPEX y decisión Go/No-Go.
                5. DESARROLLO: Ejecución, Vendors y gestión de recursos.
                6. PRUEBAS: QA y Aprobación de Seguridad Informática.
                7. DESPLIEGUE: Go Live y puesta en producción.
                8. SOPORTE: Traspaso a Mesa de Ayuda (MDA) y OPEX.
                
                INSTRUCCIONES DE REPORTE (Formato Markdown):
                1. 🌡️ **Termómetro Emocional** (1 frase resumen).
                2. 🏆 **Puntos Fuertes** (Top 2 temas en KEEP). Indica qué fase del ciclo está funcionando bien.
                3. ⚠️ **Cuellos de Botella** (Análisis de CHANGE/STOP). Asocia cada dolor a una de las 8 Fases (Ej: "Problemas en Fase 4 por demoras en Comités" o "Falla en Fase 8 por mal traspaso a Soporte").
                4. 💡 **Recomendación de Gestión**: Una acción directiva basada en la Guía de Ciclo de Vida (Ej: "Reforzar el Business Case en Fase 3").
                
                COMENTARIOS DEL EQUIPO:
                """
                
                # TU MODELO ELEGIDO
                model = genai.GenerativeModel('gemini-2.5-pro')
                response = model.generate_content(prompt + txt)
                st.markdown(response.text)

except Exception as e:
    st.error("Error leyendo el Google Sheet.")
    st.text(f"Detalle: {e}")