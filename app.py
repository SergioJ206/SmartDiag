import streamlit as st
import pandas as pd

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
            # Filtramos para que solo aparezcan componentes de ESE dispositivo
            filtrado = self.df[self.df["Dispositivo"] == dispositivo]
            return ["No lo sé / Otros"] + list(filtrado["Componente"].unique())
        return ["No lo sé / Otros"]

    # --- CORRECCIÓN AQUÍ: Ahora recibe 'dispositivo' para filtrar ---
    def buscar_por_sintomas(self, busqueda, dispositivo):
        # 1. Filtramos la base de datos solo por el dispositivo seleccionado
        df_dispositivo = self.df[self.df["Dispositivo"] == dispositivo]
        
        # 2. Buscamos el síntoma solo dentro de ese grupo
        return df_dispositivo[df_dispositivo['Sintomas'].str.contains(busqueda, case=False, na=False)]

    def buscar_diagnostico_exacto(self, dispositivo, componente):
        return self.df[(self.df["Dispositivo"] == dispositivo) & (self.df["Componente"] == componente)]

# --- INTERFAZ ---
st.set_page_config(page_title="Asistente de Diagnóstico Tech", layout="wide")
st.title("🛠️ Sistema de Diagnóstico Técnico")

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
            busqueda = st.text_input("Describe los síntomas:")
            
            if busqueda:
                # LLAMADA CORREGIDA: Pasamos el dispositivo seleccionado
                resultado = asistente.buscar_por_sintomas(busqueda, dispositivo_sel)
                
                if not resultado.empty:
                    st.success(f"Coincidencias encontradas para {dispositivo_sel}:")
                    for i, row in resultado.iterrows():
                        with st.expander(f"🚩 Problema: {row['Problema']}"):
                            st.warning(f"**Causa:** {row['Causa_tecnica']}")
                            st.info(f"**Solución:** {row['Solucion']}")
                            if 'Link_tutorial' in row and pd.notnull(row['Link_tutorial']):
                                st.link_button("Ver Tutorial", row['Link_tutorial'])
                else:
                    st.error(f"No encontré fallas de '{dispositivo_sel}' con esos síntomas.")
        
        else:
            # Búsqueda directa por componente
            resultado = asistente.buscar_diagnostico_exacto(dispositivo_sel, componente_sel)
            for i, row in resultado.iterrows():
                st.subheader(f"Diagnóstico: {row['Problema']}")
                st.warning(f"**Causa:** {row['Causa_tecnica']}")
                st.info(f"**Solución:** {row['Solucion']}")
                if 'Link_tutorial' in row and pd.notnull(row['Link_tutorial']):
                    st.link_button("Ver Tutorial", row['Link_tutorial'])
