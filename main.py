import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys
import requests 

# --- 1. CONFIGURACIÓN DE RUTAS (Solución al error de línea 17) ---
# Forzamos a Python a mirar en la carpeta del proyecto y subcarpetas
base_path = os.path.dirname(__file__)
sys.path.append(base_path)

# Intentamos cargar los módulos con manejo de errores limpio
try:
    from usuarios import gestionar_acceso, interfaz_registro_legal
    from estilos import cargar_estilos
    from idiomas import traducir_interfaz
    from paises import PAISES_DATA
    # from correo import enviar_email_outlook # Descomentar cuando correo.py esté listo
    from streamlit_gsheets import GSheetsConnection
except Exception as e:
    st.error(f"❌ Error de importación: {e}")
    st.info("Revisa que usuarios.py y estilos.py estén en la carpeta raíz.")
    st.stop()

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SWARCO SAT | Portal Técnico", layout="centered", page_icon="🚥")
cargar_estilos()
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. LIMPIEZA AUTOMÁTICA Y PERSISTENCIA ---
if 'autenticado' not in st.session_state:
    # Si no está logueado, barremos cualquier basura de sesiones previas
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.autenticado = False

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []
if 'ticket_exitoso' not in st.session_state:
    st.session_state.ticket_exitoso = False

# --- 4. LÓGICA DE ACCESO (Login y Registro) ---
if not st.session_state.autenticado:
    tab_login, tab_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registro Nuevo Usuario"])
    
    with tab_login:
        if gestionar_acceso(conn):
            st.rerun()
            
    with tab_reg:
        # Aquí es donde entra tu "Broche de Oro" White Hat
        interfaz_registro_legal(conn)
    st.stop() # Si no está autenticado, no ve el resto de la app

# --- 5. PANTALLA DE ÉXITO ---
if st.session_state.get('ticket_exitoso'):
    st.markdown(f"""
        <div style="background-color: #f0fff0; padding: 40px; border-radius: 20px; border: 2px solid #2ecc71; text-align: center;">
            <h1 style="color: #27ae60;">✅ ¡Ticket Registrado!</h1>
            <h2 style="color: #00549F;">Referencia: {st.session_state.get('ultimo_ticket')}</h2>
        </div>
    """, unsafe_allow_html=True)
    if st.button("➕ Crear otro reporte"):
        st.session_state.ticket_exitoso = False
        st.session_state.lista_equipos = []
        st.rerun()
    st.stop()

# --- 6. FORMULARIO TÉCNICO (Solo visible si está logueado) ---
d_cli = st.session_state.get('datos_cliente', {})
idioma_txt = st.sidebar.selectbox("Idioma", ["Castellano", "English"])
t = traducir_interfaz(idioma_txt)

st.image("logo.png", width=250)
st.markdown(f"### Bienvenido, {d_cli.get('Contacto', 'Técnico')}")

# --- SECCIÓN CLIENTE (Datos auto-rellenados y bloqueados) ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.text_input(t['cliente'], value=d_cli.get('Empresa', ''), disabled=True)
    proyecto_ub = st.text_input(t['proyecto'], placeholder="Ubicación exacta")
with c2:
    st.text_input(t['email'], value=d_cli.get('Email', ''), disabled=True)
    tel_raw = st.text_input(t['tel'])
    tel_limpio = ''.join(filter(str.isdigit, tel_raw))

# --- SECCIÓN EQUIPO Y DESCRIPCIÓN ---
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
ce1, ce2 = st.columns(2)
with ce1: ns_in = st.text_input(t['ns_titulo'])
with ce2: ref_in = st.text_input("REF.")

falla_in = st.text_area(t['desc_instruccion'])
archivos = st.file_uploader(t['fotos'], accept_multiple_files=True)

# INSTRUCCIONES VISUALES
st.info("💡 1. Registra equipo -> 2. Verifica tabla -> 3. Genera Ticket.")

# --- BOTONES DE ACCIÓN ---
col_b1, col_b2 = st.columns(2)
with col_b1:
    if st.button("➕ Registrar Dispositivo", use_container_width=True):
        if ns_in and len(falla_in) > 10:
            st.session_state.lista_equipos.append({"N.S.": ns_in, "REF": ref_in, "Descripción": falla_in})
            st.rerun()
        else:
            st.warning("⚠️ Datos incompletos.")

if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))
    with col_b2:
        if st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True):
            if not proyecto_ub or not tel_limpio:
                st.error("⚠️ Falta Proyecto o Teléfono")
            else:
                # Lógica de envío final (aquí conectamos con Apps Script y correo.py)
                st.success("Enviando...") 
                # (Simulación de éxito para pruebas)
                st.session_state.ultimo_ticket = f"SAT-{datetime.now().strftime('%Y%m%d')}"
                st.session_state.ticket_exitoso = True
                st.rerun()
