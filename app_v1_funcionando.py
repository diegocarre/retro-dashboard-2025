import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Tablero Retro 2025", page_icon="📊", layout="wide")

# --- TUS DATOS DEL SHEET (Pégalos aquí abajo) ---
# El código largo que ya tenías:
sheet_id = "1mi4jrEZ-mYxmFL-pshxKrMSWLTDkOdFyt9Y7ni41NTE" 
# EL NUMERO GID QUE COPIASTE RECIEN (Si es la primera hoja suele ser 0, pero verifica):
gid = "868100695"  

# Construimos la URL mágica de exportación
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

# --- CONEXIÓN CON GEMINI ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    else:
        st.warning("⚠️ Falta la clave GEMINI_API_KEY en secrets.toml")
except Exception as e:
    st.error(f"Error IA: {e}")

# --- INTERFAZ ---
st.title("📊 Dashboard de Retrospectiva")

if st.button("🔄 Actualizar Datos"):
    st.cache_data.clear()
    st.rerun()

# --- LECTURA DIRECTA (A prueba de fallos) ---
try:
    # Leemos directo el CSV de Google
    df = pd.read_csv(csv_url)

    if df.empty:
        st.info("📉 La hoja está vacía.")
    else:
        # Renombramos columnas (Ajusta esto al orden de tu Formulario)
        # Asumiendo: Marca temporal, Categoría, Comentario
        # Si tienes más columnas, agrega nombres a la lista
        df.columns = ["Fecha", "Categoria", "Comentario"]
        
        # Métricas
        c1, c2, c3 = st.columns(3)
        total = len(df)
        keeps = len(df[df['Categoria'].str.contains("KEEP", case=False, na=False)])
        others = total - keeps
        
        c1.metric("Total", total)
        c2.metric("🟢 Keeps", keeps)
        c3.metric("🔴 Change/Stop", others)

        # Tabla
        st.dataframe(df.tail(10), use_container_width=True, hide_index=True)

        # IA
        st.divider()
        if st.button("✨ Generar Insights con IA", type="primary"):
            with st.spinner("Analizando..."):
                txt = ""
                for i, row in df.iterrows():
                    txt += f"- [{row['Categoria']}] {row['Comentario']}\n"
                
# --- NUEVO PROMPT CONTEXTUALIZADO (Ciclo de Vida Carrefour) ---
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
                
                model = genai.GenerativeModel('gemini-2.5-pro')
                response = model.generate_content(prompt + txt)
                st.markdown(response.text)

except Exception as e:
    st.error("Error leyendo el Google Sheet.")
    st.text(f"Detalle: {e}")
    st.info(f"Verifica que el GID sea correcto. URL intentada: {csv_url}")