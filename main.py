import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection

# 1. Configuración
st.set_page_config(page_title="SWARCO SAT", layout="centered", page_icon="🚥")
cargar_estilos()

# 2. Encabezado Corporativo
col_logo, col_lang, col_sem = st.columns([1.5, 1, 0.5])
with col_logo:
    st.image("logo.png", width=140)

with col_lang:
    banderas = {
        "Castellano": "https://flagcdn.com/w40/es.png",
        "English": "https://flagcdn.com/w40/gb.png",
        "Deutsch": "https://flagcdn.com/w40/de.png",
        "Français": "https://flagcdn.com/w40/fr.png",
        "Català": "https://flagcdn.com/w40/es-ct.png",
        "Euskara": "https://flagcdn.com/w40/es-pv.png"
    }
    sel_lang = st.selectbox("", list(banderas.keys()), label_visibility="collapsed")
    st.image(banderas[sel_lang], width=30)
    t = traducir_interfaz(sel_lang)

with col_sem:
    st.markdown("<h2 style='text-align:right;'>🚥</h2>", unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align:center; color:#00549F;'>{t['titulo']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#666;'>{t['sub']}</p>", unsafe_allow_html=True)

# --- SECCIÓN 1: CLIENTE ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
with c2:
    email_usr = st.text_input(t['email'])
    p_nombres = list(PAISES_DATA.keys())
    pais_sel = st.selectbox(t['pais'], p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
    prefijo = PAISES_DATA[pais_sel]
    tel_usr = f"{prefijo} {st.text_input(f'{t['tel']} ({prefijo})')}"

# --- SECCIÓN 2: EQUIPO Y PEGATINA ---
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(f"💡 {t['pegatina']}")
st.image("etiqueta.jpeg", use_container_width=True)

if 'lista_equipos' not in st.session_state: st.session_state.lista_equipos = []

with st.container():
    ce1, ce2, ce3 = st.columns([2, 2, 1])
    ns_in = ce1.text_input(t['ns_titulo'])
    ref_in = ce2.text_input("REF / PN")
    urg_in = ce3.selectbox(t['prioridad'], ["Normal", "Alta", "Crítica"])
    
    # --- SECCIÓN 3: DESCRIPCIÓN DEL PROBLEMA ---
    st.markdown(f"**{t['desc']}**")
    falla_in = st.text_area("", key="falla_area", label_visibility="collapsed")
    st.file_uploader(t['fotos'], accept_multiple_files=True, type=['png', 'jpg', 'mp4'], label_visibility="collapsed")

    if st.button(t['btn_agregar'], use_container_width=True):
        if ns_in and falla_in:
            st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_in, "desc": falla_in})
            st.rerun()

if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# --- ENVÍO FINAL ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button(t['btn'], type="primary"):
    if not empresa or not email_usr or not st.session_state.lista_equipos:
        st.error("Complete los campos obligatorios.")
    else:
        ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        if enviar_email_outlook(empresa, contacto, "", st.session_state.lista_equipos, email_usr, ticket_id, tel_usr):
            st.success(t['exito'])
            st.balloons()
            st.session_state.lista_equipos = []

# Pie de página
st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)