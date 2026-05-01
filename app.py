import streamlit as st
import pandas as pd
import google.generativeai as genai

# ==========================================
# 1. DEFINICIÓN DE LA CLASE (POO)
# ==========================================
class AsistenteDiagnostico:
    def __init__(self, ruta_archivo):
        self.ruta_archivo = ruta_archivo
        self.df = self.cargar_datos()

    @st.cache_data(show_spinner=False)
    def cargar_datos(_self):
        try:
            return pd.read_csv(_self.ruta_archivo)
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            return pd.DataFrame()

    def obtener_dispositivos(self):
        if not self.df.empty:
            return self.df["Dispositivo"].unique()
        return []

    def obtener_componentes(self, dispositivo):
        if not self.df.empty:
            filtrado = self.df[self.df["Dispositivo"] == dispositivo]
            return ["No lo sé / Otros"] + list(filtrado["Componente"].unique())
        return ["No lo sé / Otros"]

    def buscar_diagnostico_exacto(self, dispositivo, componente):
        return self.df[(self.df["Dispositivo"] == dispositivo) & (self.df["Componente"] == componente)]

    # --- NUEVO MÉTODO: EL CEREBRO DE LA IA ---
    def analizar_con_ia(self, busqueda, dispositivo):
        try:
            # 1. Configurar la IA con la llave secreta
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # 2. Elegir el modelo de IA
            # CÓDIGO CORREGIDO
            # CÓDIGO CORREGIDO
            modelo = genai.GenerativeModel('gemini-2.5-flash')
            
            # 3. Preparar el "Contexto" (Solo la tabla de ese dispositivo)
            df_filtrado = self.df[self.df["Dispositivo"] == dispositivo]
            # Convertimos la tabla a texto para que la IA la pueda leer
            contexto_datos = df_filtrado.to_string(index=False)
            
            # 4. Diseñar el Prompt Maestro
            prompt = f"""
            Eres un técnico de soporte experto, empático y claro.
            Tu objetivo es diagnosticar el problema del usuario basándote ÚNICAMENTE en la siguiente base de datos:
            
            {contexto_datos}
            
            El usuario tiene un {dispositivo} y reporta los siguientes síntomas: "{busqueda}"
            
            Instrucciones:
            1. Analiza los síntomas y busca la fila que mejor coincida en la base de datos.
            2. Si encuentras la falla, respóndele al usuario de manera conversacional y amable.
            3. Menciona el Problema, la Causa técnica, y explícale la Solución paso a paso según la base de datos.
            4. Si la Acción sugerida dice que necesita un técnico, adviérteselo amablemente.
            5. Si los síntomas del usuario NO tienen relación con nada de la base de datos, dile que por ahora no tienes información sobre ese problema específico y recomiéndale ir a soporte técnico.
            """
            
            # 5. Generar la respuesta
            respuesta = modelo.generate_content(prompt)
            return respuesta.text
            
        except Exception as e:
            return f"Hubo un error de conexión con la Inteligencia Artificial: {e}"


# ==========================================
# 2. INTERFAZ DE USUARIO (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Asistente de Diagnóstico Tech", layout="wide")
st.title("🤖 Sistema de Diagnóstico Inteligente")

asistente = AsistenteDiagnostico("data/base_mantenimiento.csv")

if not asistente.df.empty:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Navegación Guiada")
        dispositivo_sel = st.selectbox("Selecciona tu dispositivo:", asistente.obtener_dispositivos())
        componente_sel = st.selectbox("¿Qué componente falla?", asistente.obtener_componentes(dispositivo_sel))

    with col2:
        if componente_sel == "No lo sé / Otros":
            st.subheader(f"Dime qué le pasa a tu {dispositivo_sel}")
            busqueda = st.text_area("Describe los síntomas con tus propias palabras (ej. 'La pantalla se pone azul y se reinicia sola'):")
            
            # --- NUEVA INTEGRACIÓN VISUAL DE LA IA ---
            if st.button("Analizar con Inteligencia Artificial ✨"):
                if busqueda:
                    with st.spinner("La IA está leyendo tu queja y analizando la base de datos..."):
                        # Llamamos a nuestro nuevo método
                        respuesta_ia = asistente.analizar_con_ia(busqueda, dispositivo_sel)
                        
                        st.success("Análisis completado:")
                        st.markdown(respuesta_ia)
                else:
                    st.warning("Por favor, escribe un síntoma antes de analizar.")
        
        else:
            # Búsqueda exacta (Sigue igual, no necesita IA porque el usuario ya sabe qué es)
            resultado = asistente.buscar_diagnostico_exacto(dispositivo_sel, componente_sel)
            for i, row in resultado.iterrows():
                st.subheader(f"Diagnóstico para: {row['Problema']}")
                st.warning(f"**Causa:** {row['Causa_tecnica']}")
                st.info(f"**Solución:** {row['Solucion']}")
                if 'Link_tutorial' in row and pd.notnull(row['Link_tutorial']):
                    st.link_button("Ver Tutorial", row['Link_tutorial'])
else:
    st.error("No se pudo iniciar el asistente porque no se encontró la base de datos.")
