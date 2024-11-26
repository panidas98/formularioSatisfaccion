import streamlit as st
import pandas as pd
import base64
from github import Github

# Configuración de GitHub
GITHUB_TOKEN = "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"  # Reemplaza con tu token
REPO_NAME = "panidas98/formularioSatisfaccion"  # Reemplaza con el nombre de tu repositorio
FILE_PATH = "blob/main/respuestas_formulario.xlsx"  # Ruta en el repositorio

# Función para validar el nombre de usuario
def validar_usuario(usuario):
    return usuario.endswith("@inmel.co")

# Función para leer el archivo desde el repositorio
def leer_excel_desde_github(repo, path):
    try:
        archivo = repo.get_contents(path)
        contenido = base64.b64decode(archivo.content)
        return pd.read_excel(contenido)
    except Exception:
        return pd.DataFrame()  # Si no existe, devuelve un DataFrame vacío

# Función para actualizar el archivo en el repositorio
def actualizar_excel_en_github(repo, path, dataframe):
    contenido = dataframe.to_excel(index=False)
    try:
        archivo = repo.get_contents(path)
        repo.update_file(
            path,
            "Actualización de respuestas",
            contenido,
            archivo.sha,
        )
    except Exception:
        repo.create_file(path, "Creación de archivo de respuestas", contenido)

# Crear formulario en Streamlit
def main():
    st.title("Formulario de Satisfacción sobre los Tableros")
    
    # Pregunta 1: Nombre de usuario
    usuario = st.text_input("Nombre de usuario (debe contener @inmel.co):")
    
    if usuario and not validar_usuario(usuario):
        st.error("El nombre de usuario debe contener @inmel.co")
    else:
        # Continuar si el usuario es válido
        with st.form(key="formulario"):
            # Pregunta 2
            satisfaccion_general = st.slider(
                "1. Del 1 al 5, siendo 1 Muy insatisfecho y 5 Muy Satisfecho, ¿qué tan satisfecho(a) estás con los tableros en general?",
                min_value=1,
                max_value=5,
                value=3,
            )
            
            # Pregunta 3
            claridad_informacion = st.radio(
                "2. ¿La información presentada es clara y fácil de entender?",
                ("Sí, totalmente", "Algo clara", "No, Confusa"),
            )
            
            # Pregunta 4
            informacion_completa = st.radio(
                "3. ¿Consideras que los tableros contienen toda la información que necesitas?",
                ("Sí, es completa", "Algo completa", "No, es insuficiente"),
            )
            
            # Pregunta 5
            utilidad_tableros = st.slider(
                "4. ¿Qué tan útiles son los tableros para la toma de decisiones? Siendo 5 Muy útiles y 1 Nada útiles.",
                min_value=1,
                max_value=5,
                value=3,
            )
            
            # Pregunta 6
            mejoras_tableros = st.text_area(
                "5. ¿Qué mejorarías en los tableros?"
            )
            
            # Pregunta 7
            capacitacion = st.radio(
                "6. ¿Te gustaría recibir capacitación para usar mejor los tableros?",
                ("Sí", "No"),
            )
            
            # Botón de enviar
            submit = st.form_submit_button("Enviar")
            
            if submit:
                if not usuario:
                    st.error("Por favor ingresa un nombre de usuario válido con @inmel.co.")
                else:
                    # Guardar las respuestas en un archivo Excel
                    datos = {
                        "Usuario": [usuario],
                        "Satisfacción General": [satisfaccion_general],
                        "Claridad Información": [claridad_informacion],
                        "Información Completa": [informacion_completa],
                        "Utilidad Tableros": [utilidad_tableros],
                        "Mejoras Sugeridas": [mejoras_tableros],
                        "Capacitación Deseada": [capacitacion],
                    }
                    df_nuevo = pd.DataFrame(datos)
                    
                    # Conectar con el repositorio de GitHub
                    g = Github(GITHUB_TOKEN)
                    repo = g.get_repo(REPO_NAME)
                    
                    # Leer archivo existente
                    df_existente = leer_excel_desde_github(repo, FILE_PATH)
                    
                    # Actualizar archivo con las nuevas respuestas
                    df_actualizado = pd.concat([df_existente, df_nuevo], ignore_index=True)
                    actualizar_excel_en_github(repo, FILE_PATH, df_actualizado)
                    
                    st.success("Tus respuestas han sido registradas correctamente.")
                    st.balloons()

if __name__ == "__main__":
    main()