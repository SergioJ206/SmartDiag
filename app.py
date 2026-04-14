import streamlit as st
import pandas as pd

# ==========================================
# 1. DEFINICIÓN DE LA CLASE (AQUÍ ESTÁ LA POO)
# ==========================================
class AsistenteDiagnostico:
    """Clase que maneja la lógica de la base de datos y los diagnósticos."""
    
    # Constructor: Se ejecuta al crear el objeto
    def __init__(self, ruta_archivo):
        self.ruta_archivo = ruta_archivo
        self.df = self.cargar_datos()

    # Método para cargar la base de datos
    @st.cache_data(show_spinner=False)
    def cargar_datos(_self):
        try:
            return pd.read_csv(_self.ruta_archivo)
        except Exception as e:
            st.error(f"Error al cargar el archivo: {e}")
            return pd.DataFrame() # Retorna tabla vacía si falla

    # Método para obtener lista de dispositivos
    def obtener_dispositivos(self):
        if not self.df.empty:
            return self.df["Dispositivo"].unique()
        return []

    # Método para obtener componentes de un dispositivo específico
    def obtener_componentes(self, dispositivo):
        if not self.df.empty:
            filtrado = self.df[self.df["Dispositivo"] == dispositivo]
            return ["No lo sé / Otros"] + list(filtrado["Componente"].unique())
        return ["No lo sé / Otros"]

    # Método para buscar por palabras clave (síntomas)
    def buscar_por_sintomas(self, busqueda):
        return self.df[self.df['Sintomas'].str.contains(busqueda, case=False, na=False)]

    # Método para buscar el diagnóstico exacto
    def buscar_diagnostico_exacto(self, dispositivo, componente):
        return self.df[(self.df["Dispositivo"] == dispositivo) & (self.df["Componente"] == componente)]


# ==========================================
# 2. INTERFAZ DE USUARIO (STREAMLIT)
# ==========================================
st.set_page_config(page_title="Asistente de Diagnóstico Tech", layout="wide")
st.title("🛠️ Sistema de Diagnóstico Técnico")
st.write("Bienvenido. Selecciona tu problema o descríbelo para obtener una solución.")

# INSTANCIACIÓN: Creamos el objeto basado en nuestra clase
asistente = AsistenteDiagnostico("data/base_mantenimiento.csv")

# Verificamos que la base de datos cargó bien antes de mostrar la interfaz
if not asistente.df.empty:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Navegación Guiada")
        # Usamos los MÉTODOS del objeto 'asistente'
        dispositivo = st.selectbox("Selecciona tu dispositivo:", asistente.obtener_dispositivos())
        componente = st.selectbox("¿Qué componente falla?", asistente.obtener_componentes(dispositivo))

    with col2:
        if componente == "No lo sé / Otros":
            st.subheader("Cuéntame qué sucede")
            busqueda = st.text_input("Describe los síntomas (ej. 'pantalla parpadea' o 'huele a quemado'):")
            
            if busqueda:
                # Usamos el método de búsqueda
                resultado = asistente.buscar_por_sintomas(busqueda)
                
                if not resultado.empty:
                    st.success("He encontrado una posible coincidencia:")
                    for i, row in resultado.iterrows():
                        st.markdown(f"### 🚩 Problema: {row['Problema']}")
                        st.warning(f"**Causa probable:** {row['Causa_tecnica']}")
                        st.info(f"**Solución sugerida:** {row['Solucion']}")
                        st.write(f"**Recomendación:** {row['Accion_sugerida']}")
                        
                        if 'Link_tutorial' in row and pd.notnull(row['Link_tutorial']):
                            st.link_button("Ver Video Tutorial / Guía", row['Link_tutorial'])
                else:
                    st.error("No encontré esa falla en mi base de datos. Intenta con otras palabras.")
        
        else:
            # Usamos el método de búsqueda exacta
            resultado = asistente.buscar_diagnostico_exacto(dispositivo, componente)
            
            for i, row in resultado.iterrows():
                st.subheader(f"Diagnóstico para: {row['Componente']}")
                st.warning(f"**Causa:** {row['Causa_tecnica']}")
                st.info(f"**Pasos a seguir:** {row['Solucion']}")
                st.write(f"**Nota del técnico:** {row['Accion_sugerida']}")
                
                if 'Link_tutorial' in row and pd.notnull(row['Link_tutorial']):
                    st.link_button("Ver Video Tutorial / Guía", row['Link_tutorial'])
else:
    st.error("No se pudo iniciar el asistente porque no se encontró la base de datos.")
