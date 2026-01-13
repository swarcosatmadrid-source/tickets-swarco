import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# Asegurar que encuentre los archivos locales
sys.path.append(os.path.dirname(__file__))

# Importaciones de tus archivos originales
from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de pantalla completa y estilos Swarco
st.set_page_config(page_title="SAT SWARCO TRAFFIC SPAIN", layout="wide", page_icon="🚥")
cargar_estilos()

# Conexión silenciosa a GSheets para tu histórico
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    pass

# --- ENCABEZADO: LOGO | TÍTULO | SEMÁFORO ---
col_logo, col_tit, col_sem = st.columns([1, 5, 1])
with col_logo:
    st.image("logo.png", width=100)
with col_tit:
    # Selector de idioma discreto arriba como lo tenías
    idioma_sel = st.selectbox("Language", ["Español", "English 🇬🇧", "Deutsch 🇩🇪", "Français 🇫🇷", "Català 🚩", "Euskara 🟢"], label_visibility="collapsed")
    t = traducir_interfaz(idioma_sel)
    st.markdown(f"<h1 style='text-align: center; color: #00549F;'>{t['titulo']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #009FE3; font-weight: bold;'>{t['sub']}</p>", unsafe_allow_html=True)
with col_sem:
    st.markdown("<div style='font-size: 40px; text-align: right;'>🚥</div>", unsafe_allow_html=True)

# --- CATEGORÍA 1: IDENTIFICACIÓN DEL CLIENTE ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    persona_contacto = st.text_input(t['contacto'])
    proyecto = st.text_input(t['proyecto'])
with c2:
    email_usr = st.text_input(t['email'])
    
    # Selector de País y Prefijo (Lógica Original)
    pais_nombres = list(PAISES_DATA.keys())
    idx_spain = pais_nombres.index("Spain") if "Spain" in pais_nombres else 0
    pais_sel = st.selectbox(t['pais'], pais_nombres, index=idx_spain)
    prefijo = PAISES_DATA[pais_sel]
    
    tel_raw = st.text_input(f"{t['tel']} ({prefijo})")
    tel_usr = f"{prefijo} {tel_raw}"

# --- CATEGORÍA 2: IDENTIFICACIÓN DEL EQUIPO ---
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(f"ℹ️ {t['pegatina']}")
st.image("etiqueta.jpeg", use_container_width=True)

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# Formulario para añadir equipos a la tabla
with st.container():
    ce1, ce2, ce3 = st.columns([2, 2, 1])
    ns_in = ce1.text_input(t['ns_titulo'])
    ref_in = ce2.text_input("REF / PN")
    urg_in = ce3.selectbox(t['prioridad'], ["Normal", "Alta", "Crítica"])
    
    st.markdown(f"**{t['desc']}**")
    falla_in = st.text_area("", key="falla_area", label_visibility="collapsed")
    
    # --- CARGA DE MULTIMEDIA (RECUPERADA) ---
    st.markdown(f"**{t['fotos']}**")
    archivos = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4', 'mov'], label_visibility="collapsed")

    if st.button(t['btn_agregar'] if 'btn_agregar' in t else "AGREGAR EQUIPO"):
        if ns_in and falla_in:
            st.session_state.lista_equipos.append({
                "ns": ns_in, "ref": ref_in, "urgencia": urg_in, "desc": falla_in
            })
            st.rerun()

if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))
    if st.button("🗑️ Limpiar lista"):
        st.session_state.lista_equipos = []
        st.rerun()

# --- CATEGORÍA 3: ENVÍO ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
if st.button(t['btn'], type="primary", use_container_width=True):
    if not empresa or not email_usr or not st.session_state.lista_equipos:
        st.error("Faltan campos obligatorios.")
    else:
        ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        
        # Envío de Correo
        if enviar_email_outlook(empresa, persona_contacto, proyecto, st.session_state.lista_equipos, email_usr, ticket_id, tel_usr):
            
            # Registro en GSheets (El Híbrido que no molesta al cliente)
            try:
                nueva_fila = pd.DataFrame([{"ID": ticket_id, "Fecha": datetime.now().strftime("%d/%m/%Y"), "Empresa": empresa, "Estado": "Pendiente"}])
                df_ex = conn.read(worksheet="Sheet1")
                conn.update(worksheet="Sheet1", data=pd.concat([df_ex, nueva_fila]))
            except: pass
            
            st.success(f"✔️ {t['exito']}")
            st.info(t['msg_tecnico'])
            st.balloons()
            st.session_state.lista_equipos = []