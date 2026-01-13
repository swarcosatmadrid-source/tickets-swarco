import streamlit as st
import os
import sys
import uuid
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# Forzar ruta
directorio_actual = os.path.dirname(os.path.abspath(__file__))
if directorio_actual not in sys.path:
    sys.path.append(directorio_actual)

# Importaciones locales corregidas
try:
    from estilos import cargar_estilos
    from correo import enviar_email_outlook
    from idiomas import traducir_interfaz # Cambiado: importamos la función
    from paises import PAISES_DATA # Importamos la data de países
except ImportError as e:
    st.error(f"Error cargando archivos locales: {e}")
    st.stop()

# 1. Configuración de página
st.set_page_config(page_title="SWARCO SAT Portal", layout="wide")
cargar_estilos()

# Conexión GSheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- NAVEGACIÓN ---
st.sidebar.image("logo.png", use_container_width=True)
idioma_sel = st.sidebar.selectbox("🌐 Idioma", ["Español", "English 🇬🇧", "Deutsch 🇩🇪", "Français 🇫🇷"])

# Generar los textos traducidos usando tu función de idiomas.py
t = traducir_interfaz(idioma_sel)

menu = st.sidebar.radio("🚀 MENÚ", ["📋 Nuevo Ticket", "📊 Mostrador Admin"])

if menu == "📋 Nuevo Ticket":
    st.title(t['titulo'])
    st.subheader(t['sub'])

    if 'lista_equipos' not in st.session_state:
        st.session_state.lista_equipos = []

    # --- FORMULARIO CLIENTE ---
    with st.container():
        st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            empresa = st.text_input(t['cliente'])
            contacto = st.text_input(t['contacto'])
        with col2:
            email_usr = st.text_input(t['email'])
            
            # Lógica de países integrada
            pais_nombres = list(PAISES_DATA.keys())
            pais_sel = st.selectbox(t['pais'], pais_nombres, index=pais_nombres.index("Spain") if "Spain" in pais_nombres else 0)
            prefijo = PAISES_DATA[pais_sel]
            tel_raw = st.text_input(f"{t['tel']} ({prefijo})")
            tel_usr = f"{prefijo} {tel_raw}"

    # --- EQUIPOS ---
    st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
    with st.expander("Añadir Equipo", expanded=True):
        ns = st.text_input(t['ns_titulo'])
        ref = st.text_input("REF")
        urgencia = st.selectbox(t['prioridad'], ["Normal", "Alta", "Crítica"])
        falla = st.text_area(t['desc'])
        
        if st.button("➕ Agregar a la lista"):
            if ns and falla:
                st.session_state.lista_equipos.append({"ns": ns, "ref": ref, "urgencia": urgencia, "desc": falla})
                st.success("Equipo agregado")
            else:
                st.error("S/N y Falla son obligatorios")

    if st.session_state.lista_equipos:
        st.table(pd.DataFrame(st.session_state.lista_equipos))

    # --- ENVÍO ---
    if st.button(t['btn']):
        if not empresa or not email_usr or not st.session_state.lista_equipos:
            st.error("Faltan datos críticos.")
        else:
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            if enviar_email_outlook(empresa, contacto, "", st.session_state.lista_equipos, email_usr, ticket_id, tel_usr):
                
                # Guardar en GSheets
                try:
                    nueva_fila = pd.DataFrame([{"ID_Ticket": ticket_id, "Fecha": datetime.now().strftime("%d/%m/%Y"), "Empresa": empresa, "Estado": "🔴 Recibido"}])
                    df_ex = conn.read(worksheet="Sheet1")
                    df_up = pd.concat([df_ex, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=df_up)
                    st.success(t['exito'])
                    st.balloons()
                except Exception as e:
                    st.warning("Enviado por mail, pero error en Base de Datos.")
            
else:
    # --- MOSTRADOR ---
    st.title("📊 Panel Admin")
    clave = st.text_input("Clave", type="password")
    if clave == st.secrets["admin_password"]:
        df = conn.read(worksheet="Sheet1")
        st.dataframe(df, use_container_width=True)