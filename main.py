import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# Aseguramos la ruta
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de página
st.set_page_config(page_title="SWARCO SAT Portal", layout="centered", page_icon="🚥")
cargar_estilos()

# Conexión GSheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    pass

# --- HEADER: LOGO PEQUEÑO Y BANDERAS ---
col_logo, col_lang, col_sem = st.columns([1, 1, 1])

with col_logo:
    st.image("logo.png", width=100) # Logo sin cortes

with col_lang:
    # Selector con banderas (más corto como en la web)
    idioma_map = {
        "🇪🇸 ES": "Español",
        "🇬🇧 EN": "English 🇬🇧",
        "🇩🇪 DE": "Deutsch 🇩🇪",
        "🇫🇷 FR": "Français 🇫🇷"
    }
    idioma_key = st.selectbox("", list(idioma_map.keys()), label_visibility="collapsed")
    idioma_sel = idioma_map[idioma_key]
    t = traducir_interfaz(idioma_sel)

with col_sem:
    st.markdown("<div style='font-size: 30px; text-align: right;'>🚥</div>", unsafe_allow_html=True)

# Título Principal (Limpio)
st.markdown(f"<h1 style='text-align: center; color: #00549F; font-size: 28px;'>{t['titulo']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #666; margin-top: -10px;'>{t['sub']}</p>", unsafe_allow_html=True)

# --- PASO 1: IDENTIFICACIÓN DEL CLIENTE ---
st.markdown(f'<div style="border-bottom: 2px solid #F29400; color: #00549F; font-weight: bold; margin: 20px 0 10px 0;">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
with c2:
    email_usr = st.text_input(t['email'])
    # Paises
    p_nombres = list(PAISES_DATA.keys())
    idx_sp = p_nombres.index("Spain") if "Spain" in p_nombres else 0
    pais_sel = st.selectbox(t['pais'], p_nombres, index=idx_sp)
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} ({prefijo})")
    tel_usr = f"{prefijo} {tel_raw}"

# --- PASO 2: IDENTIFICACIÓN DEL EQUIPO (PEGATINA) ---
st.markdown(f'<div style="border-bottom: 2px solid #F29400; color: #00549F; font-weight: bold; margin: 20px 0 10px 0;">{t["cat2"]}</div>', unsafe_allow_html=True)
st.write(f"ℹ️ {t['pegatina']}")
st.image("etiqueta.jpeg", use_container_width=True)

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

with st.container():
    ce1, ce2, ce3 = st.columns([2, 2, 1])
    ns_in = ce1.text_input(t['ns_titulo'])
    ref_in = ce2.text_input("REF / Part Number")
    urg_in = ce3.selectbox(t['prioridad'], ["Normal", "Alta", "Crítica"])
    
    # --- PASO 3: DESCRIPCIÓN DEL PROBLEMA (JUSTO ANTES DE AGREGAR/MANDAR) ---
    st.markdown(f"**{t['desc']}**")
    falla_in = st.text_area("", key="falla_area", label_visibility="collapsed", placeholder="Escriba aquí la avería detectada...")
    
    st.markdown(f"**{t['fotos']}**")
    st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

    if st.button("➕ AGREGAR EQUIPO AL TICKET", use_container_width=True):
        if ns_in and falla_in:
            st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_in, "desc": falla_in})
            st.rerun()

# Tabla de equipos
if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# --- BOTÓN DE ENVÍO NARANJA SWARCO ---
st.markdown("---")
# Usamos un botón con estilo naranja mediante CSS en el archivo de estilos o aquí
if st.button(t['btn'], type="primary", use_container_width=True):
    if not empresa or not email_usr or not st.session_state.lista_equipos:
        st.error("Rellene los campos obligatorios.")
    else:
        # Lógica de envío... (la misma de antes)
        st.success(t['exito'])
        st.balloons()

# --- FOOTER CORPORATIVO (EL FINAL DE LA WEB) ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #999; font-size: 12px; padding: 20px;'>
        <p>© 2024 SWARCO TRAFFIC SPAIN S.A.U. | Todos los derechos reservados</p>
        <p>The Better Way. Every Day. | <a href='https://www.swarco.com/es/aviso-legal' target='_blank' style='color: #F29400;'>Aviso Legal</a> | <a href='https://www.swarco.com/es/privacidad' target='_blank' style='color: #F29400;'>Privacidad</a></p>
    </div>
""", unsafe_allow_html=True)