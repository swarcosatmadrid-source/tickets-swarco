import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# 1. SEGURIDAD DE RUTAS Y CONFIGURACIÓN
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook

# Configuración de página
st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚥")
cargar_estilos()

# --- HEADER: LOGO Y TRADUCTOR ---
col_logo, col_lang = st.columns([1.5, 1])
with col_logo:
    st.image("logo.png", width=250)
with col_lang:
    idioma_txt = st.text_input("Idioma / Language", value="Castellano")
    t = traducir_interfaz(idioma_txt)

# --- BLOQUE CSS (DISEÑO SLIDER SIN ROJO) ---
st.markdown("""
    <style>
    .stSlider > div [data-baseweb="slider"] {
        background: linear-gradient(to right, #ADD8E6 0%, #F29400 100%) !important;
        height: 12px !important;
    }
    .stSlider > div [data-baseweb="slider"] > div:nth-child(2) {
        background-color: transparent !important;
    }
    [data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {
        color: #00549F !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CATEGORÍA 1: CLIENTE ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'], key="empresa_input")
    contacto = st.text_input(t['contacto'])
    proyecto_ub = st.text_input(t['proyecto'])
with c2:
    email_usr = st.text_input(t['email'])
    p_nombres = list(PAISES_DATA.keys())
    idx_def = p_nombres.index("Spain") if "Spain" in p_nombres else 0
    pais_sel = st.selectbox(t['pais'], p_nombres, index=idx_def)
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
    ns_in = st.text_input(t['ns_titulo'], key="ns_input")
with ce2:
    ref_in = st.text_input("REF.", key="ref_input")

# --- CATEGORÍA 3: PROBLEMA Y URGENCIA ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
st.markdown(f"**{t['urg_titulo']}**")

opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
urg_val = st.select_slider(t['urg_instruccion'], options=opciones_urg, value=t['u3'])

colores_p = {t['u1']:"#ADD8E6", t['u2']:"#90C3D4", t['u3']:"#7AB1C5", t['u4']:"#C2A350", t['u5']:"#D69B28", t['u6']:"#F29400"}
st.markdown(f"<style>div[role='slider'] {{ background-color: {colores_p.get(urg_val, '#7AB1C5')} !important; border: 2px solid white !important; }}</style>", unsafe_allow_html=True)

falla_in = st.text_area(t['desc_instruccion'], placeholder=t['desc_placeholder'], key="desc_input")

# MULTIMEDIA
st.markdown(f"**{t['fotos']}**")
archivos = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# --- NOTA EXPLICATIVA PARA EL CLIENTE ---
st.markdown("---")
st.markdown(f"""
    <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 5px solid #00549F; margin-bottom: 20px;">
        <p style="color: #00549F; font-weight: bold; margin-bottom: 5px;">💡 {t.get('instruccion_final', '¿Cómo proceder?')}</p>
        <p style="font-size: 14px; color: #333;">
            • Use <b>"{t['btn_agregar']}"</b> si desea reportar más de un equipo en este mismo ticket.<br>
            • Use <b>"{t['btn_generar']}"</b> directamente si solo va a reportar este equipo o si ya terminó su lista.
        </p>
    </div>
""", unsafe_allow_html=True)

# BOTONES DE ACCIÓN
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button(f"➕ {t['btn_agregar']}", use_container_width=True):
        if len(ns_in) >= 3 and len(falla_in) >= 10:
            st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_val, "desc": falla_in})
            st.rerun()
        else:
            st.warning("⚠️ Complete N.S. y descripción antes de agregar.")

with col_btn2:
    if st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True):
        data_final = st.session_state.lista_equipos.copy()
        if not data_final and ns_in and falla_in:
            data_final.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_val, "desc": falla_in})
        
        if empresa and email_usr and data_final:
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            if enviar_email_outlook(empresa, contacto, proyecto_ub, data_final, email_usr, ticket_id, tel_final):
                st.success(t['exito'])
                st.balloons()
                st.session_state.lista_equipos = []
        else:
            st.error("⚠️ Falta información crítica para enviar el ticket.")

# TABLA DE RESUMEN
if st.session_state.lista_equipos:
    st.subheader("📋 Resumen actual")
    st.table(pd.DataFrame(st.session_state.lista_equipos))
    if st.button("🗑️ Limpiar Lista"):
        st.session_state.lista_equipos = []
        st.rerun()

# BOTÓN SALIR
st.markdown("---")
if st.button(f"🚪 {t['btn_salir']}", use_container_width=True):
    st.warning(t['salir_aviso'])

st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN</p>", unsafe_allow_html=True)
