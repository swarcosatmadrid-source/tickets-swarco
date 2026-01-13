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

st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚥")
cargar_estilos()

# HEADER
col_logo, col_lang = st.columns([1.5, 1])
with col_logo:
    st.image("logo.png", width=250)

with col_lang:
    idioma_txt = st.text_input("Idioma / Language", value="Castellano")
    t = traducir_interfaz(idioma_txt)

# SECCIÓN 1: CLIENTE
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
    proyecto_ub = st.text_input(t['proyecto']) # <--- YA SE TRADUCE
with c2:
    email_usr = st.text_input(t['email'])
    p_nombres = list(PAISES_DATA.keys())
    pais_sel = st.selectbox(t['pais'], p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})", placeholder="Solo números")
    tel_final = f"{prefijo}{''.join(filter(str.isdigit, tel_raw))}"

# SECCIÓN 2: EQUIPO
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(t['pegatina'])
st.image("etiqueta.jpeg", use_container_width=True)

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

ce1, ce2 = st.columns(2)
with ce1:
    ns_in = st.text_input(t['ns_titulo'])
with ce2:
    ref_in = st.text_input("REF.")

# SECCIÓN 3: PROBLEMA
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
st.markdown(f"**{t['urg_titulo']}**")

# CSS para matar el rojo del slider y poner el degradado
st.markdown(f"""
    <style>
    .stSlider > div [data-baseweb="slider"] {{
        background: linear-gradient(to right, #ADD8E6 0%, #F29400 100%) !important;
    }}
    </style>
""", unsafe_allow_html=True)

urg_val = st.select_slider(
    t['urg_instruccion'],
    options=[t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']],
    value=t['u3']
)

st.markdown(f"**{t['desc_instruccion']}**")
falla_in = st.text_area("", placeholder=t['desc_placeholder'], label_visibility="collapsed")

st.markdown(f"**{t['fotos']}**")
archivos = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'mp4'], label_visibility="collapsed")

# Botón Agregar con nombre traducido y un solo "+"
if st.button(f"➕ {t['btn_agregar']}", use_container_width=True):
    if ns_in and falla_in:
        st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_val, "desc": falla_in})
        st.rerun()

# ACCIONES FINALES
st.markdown("<br>", unsafe_allow_html=True)
cf1, cf2 = st.columns(2)
with cf1:
    if st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True):
        if empresa and st.session_state.lista_equipos:
            st.success(t['exito'])
            st.balloons()
            st.session_state.lista_equipos = []
with cf2:
    if st.button(f"🚪 {t['btn_salir']}", use_container_width=True):
        st.warning("Cierre la pestaña.")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN</p>", unsafe_allow_html=True)
