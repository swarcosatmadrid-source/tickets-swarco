import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# Asegurar rutas de archivos locales
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook

# 1. Configuración de pantalla
st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚥")
cargar_estilos()

# --- HEADER: LOGO Y TRADUCCIÓN ---
col_logo, col_lang = st.columns([1.5, 1])
with col_logo:
    st.image("logo.png", width=250)
with col_lang:
    idioma_txt = st.text_input("Idioma / Language", value="Castellano")
    t = traducir_interfaz(idioma_txt)

# --- CSS ULTRA-BLINDADO (MATAMOS EL ROJO AQUÍ) ---
st.markdown(f"""
    <style>
    /* Forzamos el color de acento de toda la app para que no use rojo */
    :root {{
        --primary-color: #00549F;
    }}
    
    /* 1. Carril del slider: Degradado Swarco */
    .stSlider > div [data-baseweb="slider"] {{
        background: linear-gradient(to right, #ADD8E6 0%, #F29400 100%) !important;
        height: 12px !important;
        border-radius: 6px !important;
    }}

    /* 2. Matamos la línea roja que sale al deslizar (el 'track' activo) */
    .stSlider > div [data-baseweb="slider"] > div {{
        background-color: transparent !important;
    }}

    /* 3. Matar el rojo en los números y etiquetas debajo del slider */
    [data-testid="stTickBarMin"], [data-testid="stTickBarMax"], 
    .stSlider span, .stSlider div {{
        color: #00549F !important;
        font-family: sans-serif !important;
    }}

    /* 4. Botones con estilo Swarco */
    .stButton>button {{
        border-radius: 12px !important;
        border: 1px solid #00549F !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- CATEGORÍA 1: CLIENTE ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
    proyecto_ub = st.text_input(t['proyecto'])
with c2:
    email_usr = st.text_input(t['email'])
    p_nombres = list(PAISES_DATA.keys())
    idx_def = p_nombres.index("Spain") if "Spain" in p_nombres else 0
    pais_sel = st.selectbox(t['pais'], p_nombres, index=idx_def)
    
    # Teléfono blindado
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})", placeholder="Solo números")
    tel_limpio = "".join(filter(str.isdigit, tel_raw))
    if tel_raw and not tel_raw.isdigit():
        st.error(f"⚠️ {t['error_tel']}")
    tel_final = f"{prefijo}{tel_limpio}"

# --- CATEGORÍA 2: EQUIPO ---
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(t['pegatina'])
st.image("etiqueta.jpeg", use_container_width=True)

ce1, ce2 = st.columns(2)
with ce1:
    ns_in = st.text_input(t['ns_titulo'])
with ce2:
    ref_in = st.text_input("REF.")

# --- CATEGORÍA 3: PROBLEMA Y URGENCIA ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)

# Slider con Pelota Dinámica
opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
urg_val = st.select_slider(t['urg_instruccion'], options=opciones_urg, value=t['u3'])

# Mapa de colores para la pelota (thumb)
colores_pelota = {t['u1']:"#ADD8E6", t['u2']:"#90C3D4", t['u3']:"#7AB1C5", t['u4']:"#C2A350", t['u5']:"#D69B28", t['u6']:"#F29400"}
color_thumb = colores_pelota.get(urg_val, "#7AB1C5")

# Aplicamos el color a la pelota mediante CSS inyectado
st.markdown(f"""
    <style>
    .stSlider > div [role="slider"] {{
        background-color: {color_thumb} !important;
        border: 2px solid white !important;
        width: 24px !important;
        height: 24px !important;
    }}
    </style>
""", unsafe_allow_html=True)

falla_in = st.text_area(t['desc_instruccion'], placeholder=t['desc_placeholder'])

# Multimedia
st.markdown(f"**{t['fotos']}**")
archivos = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# AGREGAR EQUIPO (PUNTO 2: VALIDACIÓN)
if st.button(f"➕ {t['btn_agregar']}", use_container_width=True):
    if len(ns_in) < 3 or len(falla_in) < 10:
        st.warning("⚠️ " + (t['error_tel'] if 'error_tel' in t else "N.S. o descripción inválida."))
    else:
        st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_val, "desc": falla_in})
        st.rerun()

# --- PUNTO 3: PRE-VISUALIZACIÓN ---
if st.session_state.lista_equipos:
    st.markdown("---")
    st.subheader("📋 Resumen / Summary")
    st.table(pd.DataFrame(st.session_state.lista_equipos))
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        if st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True):
            if empresa and email_usr:
                ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
                if enviar_email_outlook(empresa, contacto, proyecto_ub, st.session_state.lista_equipos, email_usr, ticket_id, tel_final):
                    st.success(t['exito'])
                    st.balloons()
                    st.session_state.lista_equipos = []
                    st.rerun()
    with col_f2:
        if st.button("🗑️ Borrar / Clear", use_container_width=True):
            st.session_state.lista_equipos = []
            st.rerun()

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN</p>", unsafe_allow_html=True)



