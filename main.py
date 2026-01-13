import streamlit as st
import os
import sys

# Esto obliga al sistema a buscar en la carpeta donde está main.py
directorio_actual = os.path.dirname(os.path.abspath(__file__))
if directorio_actual not in sys.path:
    sys.path.append(directorio_actual)

# Ahora sí, el resto de imports
import uuid
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Importaciones locales (tus archivos)
try:
    from estilos import cargar_estilos_swarco
    from correo import enviar_email_outlook
    from idiomas import textos
except ImportError as e:
    st.error(f"Error cargando archivos locales: {e}")
    st.stop()

# 1. Configuración de página
st.set_page_config(page_title="SWARCO SAT Portal", layout="wide")
cargar_estilos()

# Conexión a la base de datos (Google Sheets)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVEGACIÓN ---
st.sidebar.image("logo.png", use_container_width=True)
st.session_state.lang = st.sidebar.selectbox("🌐 Idioma", ["Español", "English", "Deutsch", "Français"])
t = textos[st.session_state.lang]
menu = st.sidebar.radio("🚀 MENÚ", ["📋 Nuevo Ticket", "📊 Mostrador Admin"])

if menu == "📋 Nuevo Ticket":
    st.title(t['titulo'])
    # ... (Aquí va todo tu código de inputs: empresa, contacto, equipos, etc.) ...
    
    # --- AL MOMENTO DE ENVIAR ---
    if st.button("🚀 " + t['btn_enviar'], type="primary"):
        ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        
        # 1. ENVIAR CORREO
        if enviar_email_outlook(empresa, contacto, proyecto, st.session_state.lista_equipos, email_usr, ticket_id, tel_usr):
            
            # 2. GUARDAR EN GOOGLE SHEETS (EL HÍBRIDO)
            try:
                # Preparamos la fila nueva
                nueva_fila = pd.DataFrame([{
                    "ID_Ticket": ticket_id,
                    "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Empresa": empresa,
                    "Contacto": contacto,
                    "Telefono": tel_usr,
                    "Equipos": len(st.session_state.lista_equipos),
                    "Estado": "🔴 Recibido"
                }])
                
                # Leemos lo que hay y pegamos lo nuevo
                df_existente = conn.read(worksheet="Sheet1") # O el nombre de tu pestaña
                df_actualizado = pd.concat([df_existente, nueva_fila], ignore_index=True)
                conn.update(worksheet="Sheet1", data=df_actualizado)
                
                st.success("✅ Ticket registrado en base de datos.")
            except Exception as e:
                st.warning(f"Aviso: El correo se envió, pero no se pudo anotar en el Excel: {e}")

            # Mostrar pantalla de éxito...
            st.balloons()

# ---------------------------------------------------------
# VISTA DEL MOSTRADOR (LA QUE VERÁS EN EL ORDENADOR)
# ---------------------------------------------------------
else:
    st.title("📊 Monitor de Gestión SAT")
    clave = st.text_input("Clave Admin", type="password")
    
    if clave == st.secrets["admin_password"]:
        try:
            # LEER DATOS REALES DE GOOGLE SHEETS
            df_historico = conn.read(worksheet="Sheet1")
            
            st.subheader("Tickets en tiempo real")
            # Mostramos la tabla interactiva
            st.dataframe(df_historico.sort_index(ascending=False), use_container_width=True)
            
            # Botón de descarga para el reporte de IT
            csv = df_historico.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar histórico (.csv)", csv, "reporte_sat.csv")
            
        except:
            st.info("Todavía no hay tickets en la base de datos.")
    else:
        st.info("Ingrese la clave.")