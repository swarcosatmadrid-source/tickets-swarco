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

# 1. Configuración de página
st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚥")
cargar_estilos()

# --- HEADER: LOGO Y TRADUCCIÓN UNIVERSAL ---
col_logo, col_lang = st.columns([1.5, 1])

with col_logo:
    st.image("logo.png", width=250)

with col_lang:
    idioma_txt = st.text_input("Idioma / Language", value="Castellano")
    t = traducir_interfaz(idioma_txt)

# --- CSS PARA ELIMINAR EL ROJO Y PERSONALIZAR SLIDER ---
st.markdown(f"""
    <style>
    /* 1. Fondo del carril con degradado Swarco */
    .stSlider > div [data-baseweb="slider"] {{
        background: linear-gradient(to right, #ADD8E6 0%, #F29400 100%) !important;
        height: 12px !important;
        border-radius: 6px !important;
    }}
    /* 2. Matar el color rojo de cualquier texto o marca del slider */
    [data-testid="stTickBarMin"], [data-testid="stTickBarMax"], 
    .stSlider div[style*="color: rgb(255, 75, 75)"] {{
        color: #00549F !important;
        font-weight: bold !important;
    }}
    /* 3. Estilo de los botones */
    .stButton>button {{
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }}
    </style>
""", unsafe_allow_html=True)

# --- CATEGORÍA 1: IDENTIFICACIÓN DEL CLIENTE ---
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
    
    # Lógica de Teléfono con Prefijo y Bloqueo de Letras
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})", placeholder="Solo números")
    tel_limpio = "".join(filter(str.isdigit, tel_raw))
    
    if tel_raw and not tel_raw.isdigit():
        st.error(f"⚠️ {t['error_tel']}")
    tel_final = f"{prefijo}{tel_limpio}"

# --- CATEGORÍA 2: IDENTIFICACIÓN DEL EQUIPO (PUNTO 2) ---
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(t['pegatina'])
st.image("etiqueta.jpeg", use_container_width=True)

ce1, ce2 = st.columns(2)
with ce1:
    ns_in = st.text_input(t['ns_titulo'])
with ce2:
    ref_in = st.text_input("REF.")

# --- CATEGORÍA 3: DESCRIPCIÓN DEL PROBLEMA + URGENCIA ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)

# Slider con Pelota Dinámica
opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
urg_val = st.select_slider(t['urg_instruccion'], options=opciones_urg, value=t['u3'])

# Mapa de colores para la pelota (thumb)
colores_pelota = {t['u1']:"#ADD8E6", t['u2']:"#90C3D4", t['u3']:"#7AB1C5", t['u4']:"#C2A350", t['u5']:"#D69B28", t['u6']:"#F29400"}
color_thumb = colores_pelota.get(urg_val, "#7AB1C5")

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

st.markdown(f"**{t['desc_instruccion']}**")
falla_in = st.text_area("", placeholder=t['desc_placeholder'], label_visibility="collapsed")

# Multimedia 200MB
st.markdown(f"**{t['fotos']}**")
archivos = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

if archivos:
    peso_total = sum([f.size for f in archivos]) / (1024 * 1024)
    porcentaje = min(int((peso_total / 200) * 100), 100)
    st.progress(porcentaje / 100)
    st.caption(f"Status: {peso_total:.2f}MB / 200MB ({porcentaje}%)")

# Gestión de equipos en sesión
if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# BOTÓN AGREGAR CON VALIDACIÓN (PUNTO 2)
if st.button(f"➕ {t['btn_agregar']}", use_container_width=True):
    if len(ns_in) < 3 or len(falla_in) < 10:
        st.warning("⚠️ " + (t['error_ns_desc'] if 'error_ns_desc' in t else "N.S. o descripción demasiado corta."))
    else:
        st.session_state.lista_equipos.append({
            "ns": ns_in, "ref": ref_in, "urgencia": urg_val, "desc": falla_in
        })
        st.rerun()

# --- PUNTO 3: PRE-VISUALIZACIÓN ANTES DE ENVIAR ---
if st.session_state.lista_equipos:
    st.markdown("---")
    st.subheader("📋 Resumen del Ticket / Ticket Summary")
    df_resumen = pd.DataFrame(st.session_state.lista_equipos)
    st.table(df_resumen)
    
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
        if st.button("🗑️ Borrar Todo / Clear All", use_container_width=True):
            st.session_state.lista_equipos = []
            st.rerun()

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)


