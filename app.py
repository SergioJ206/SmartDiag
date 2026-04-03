import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Asistente de Diagnóstico Tech", layout="wide")

st.title("🛠️ Sistema de Diagnóstico Técnico")
st.write("Bienvenido. Selecciona tu problema o descríbelo para obtener una solución.")

# 1. Cargar la base de datos
@st.cache_data # Para que la app sea rápida
def cargar_datos():
    # Se actualizó el nombre del archivo a base_mantenimiento.csv
    df = pd.read_csv("data/base_mantenimiento.csv")
    return df

try:
    df = cargar_datos()

    # 2. Interfaz de Usuario
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Navegación Guiada")
        dispositivo = st.selectbox("Selecciona tu dispositivo:", df["Dispositivo"].unique())
        
        # Filtrar componentes por dispositivo
        df_filtrado = df[df["Dispositivo"] == dispositivo]
        componente = st.selectbox("¿Qué componente falla?", ["No lo sé / Otros"] + list(df_filtrado["Componente"].unique()))

    with col2:
        if componente == "No lo sé / Otros":
            st.subheader("Cuéntame qué sucede")
            busqueda = st.text_input("Describe los síntomas (ej. 'pantalla parpadea' o 'huele a quemado'):")
            
            if busqueda:
                # Lógica de búsqueda simple por palabras clave en la columna Sintomas
                resultado = df[df['Sintomas'].str.contains(busqueda, case=False, na=False)]
                if not resultado.empty:
                    st.success("He encontrado una posible coincidencia:")
                    for i, row in resultado.iterrows():
                        st.markdown(f"### 🚩 Problema: {row['Problema']}")
                        st.warning(f"**Causa probable:** {row['Causa_tecnica']}")
                        st.info(f"**Solución sugerida:** {row['Solucion']}")
                        st.write(f"**Recomendación:** {row['Accion_sugerida']}")
                        
                        # Se actualizó a la nueva columna Link_tutorial
                        if 'Link_tutorial' in row and pd.notnull(row['Link_tutorial']):
                            st.link_button("Ver Video Tutorial / Guía", row['Link_tutorial'])
                else:
                    st.error("No encontré esa falla en mi base de datos. Intenta con otras palabras.")
        
        else:
            # Mostrar resultado directo si seleccionó componente
            resultado = df[(df["Dispositivo"] == dispositivo) & (df["Componente"] == componente)]
            for i, row in resultado.iterrows():
                st.subheader(f"Diagnóstico para: {row['Componente']}")
                st.warning(f"**Causa:** {row['Causa_tecnica']}")
                st.info(f"**Pasos a seguir:** {row['Solucion']}")
                st.write(f"**Nota del técnico:** {row['Accion_sugerida']}")
                
                # Se actualizó a la nueva columna Link_tutorial
                if 'Link_tutorial' in row and pd.notnull(row['Link_tutorial']):
                    st.link_button("Ver Video Tutorial / Guía", row['Link_tutorial'])

except Exception as e:
    st.error(f"Error al cargar la base de datos: {e}")
    st.info("Asegúrate de que el archivo 'base_mantenimiento.csv' esté guardado correctamente en la carpeta 'data'.")
