import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(page_title="SWARCO SAT", layout="centered", page_icon="🚥")
sys.path.append(os.path.dirname(__file__))

try:
    from estilos import cargar_estilos
    from idiomas import traducir_interfaz
    from paises import PAISES_DATA
    from correo import enviar_email_outlook
    from streamlit_gsheets import GSheetsConnection
    from usuarios import gestionar_acceso
    
    cargar_estilos()
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de sistema: {e}")
    st.stop()

# 2. CONTROL DE ACCESO
if gestionar_acceso(conn):
    d_cli = st.session_state.datos_cliente
    t = traducir_interfaz("Castellano")

    with st.sidebar:
        st.image("logo.png", use_container_width=True)
        st.write(f"👤 {d_cli['Contacto']}")
        st.write(f"🏢 {d_cli['Empresa']}")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.rerun()

    st.markdown("<h2 style='text-align: center; color: #00549F;'>Portal de Reporte Técnico SAT</h2>", unsafe_allow_html=True)

    # FORMULARIO
    st.markdown('### Datos del Reporte')
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Empresa", value=d_cli['Empresa'], disabled=True)
        proyecto = st.text_input("Proyecto / Ubicación")
    with col2:
        st.text_input("Email", value=d_cli['Email'], disabled=True)
        paises = list(PAISES_DATA.keys())
        pais = st.selectbox("País", paises, index=paises.index("Spain") if "Spain" in paises else 0)

    st.markdown('### Detalles del Equipo')
    ce1, ce2 = st.columns(2)
    with ce1:
        ns = st.text_input("N.S. (Número de Serie)")
    with ce2:
        ref = st.text_input("Referencia (REF.)")

    desc = st.text_area("Descripción de la avería")

    if st.button("🚀 ENVIAR TICKET", type="primary", use_container_width=True):
        if ns and desc and proyecto:
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            
            # Intentar enviar email primero
            res_email = enviar_email_outlook(d_cli['Empresa'], d_cli['Contacto'], proyecto, [{"N.S.": ns, "Descripción": desc}], d_cli['Email'], ticket_id, "")
            
            if res_email:
                st.success(f"¡Ticket {ticket_id} generado! Se ha enviado el aviso por correo.")
                st.balloons()
            else:
                st.error("El ticket se generó pero hubo un problema enviando el correo de notificación.")
        else:
            st.warning("Por favor, rellena los campos del equipo y ubicación.")

    st.markdown("<br><p style='text-align:center; color:grey;'>© 2024 SWARCO TRAFFIC SPAIN</p>", unsafe_allow_html=True)

