import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# Asegurar integridad de rutas locales
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook

# 1. Configuración de pantalla y límites
st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚥")
cargar_estilos()

# --- HEADER: IDENTIDAD CORPORATIVA Y BUSCADOR ---
col_logo, col_lang = st.columns([1.5, 1])

with col_logo:
    st.image("logo.png", width=250)

with col_lang:
    # El buscador universal ahora procesa cualquier entrada
    idioma_txt = st.text_input("Idioma / Language", value="Castellano")
    t = traducir_interfaz(idioma_txt)

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
    
    # LÓGICA DE TELÉFONO BLINDADA
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})", placeholder="Solo números")
    
    # Filtrado estricto de caracteres no numéricos
    tel_limpio = "".join(filter(str.isdigit, tel_raw))
    
    # Validación visual para el usuario
    if tel_raw and not tel_raw.isdigit():
        st.error(f"⚠️ {t['u6'] if 'u6' in t else 'Error'}: Solo números permitidos.")
    
    # Resultado final: Prefijo + Números limpios
    tel_final = f"{prefijo}{tel_limpio}"

# --- CATEGORÍA 2: IDENTIFICACIÓN DEL EQUIPO ---
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

# --- CATEGORÍA 3: DESCRIPCIÓN DEL PROBLEMA + URGENCIA ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
st.markdown(f"**{t['urg_titulo']}**")

# CSS REFORZADO: Forzamos el degradado y eliminamos el rojo nativo
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

# MONITOR DE ESPAÑO MULTIMEDIA (200MB)
st.markdown(f"**{t['fotos']}**")
archivos = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

if archivos:
    peso_total = sum([f.size for f in archivos]) / (1024 * 1024)
    porcentaje = min(int((peso_total / 200) * 100), 100)
    st.progress(porcentaje / 100)
    st.caption(f"Status: {peso_total:.2f}MB / 200MB ({porcentaje}%)")

# BOTÓN DE ACCIÓN (Un solo signo +)
if st.button(f"➕ {t['btn_agregar']}", use_container_width=True):
    if ns_in and falla_in:
        st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_val, "desc": falla_in})
        st.rerun()

if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# --- ACCIONES FINALES ---
st.markdown("<br>", unsafe_allow_html=True)
cf1, cf2 = st.columns(2)

with cf1:
    if st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True):
        if empresa and st.session_state.lista_equipos:
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            if enviar_email_outlook(empresa, contacto, proyecto_ub, st.session_state.lista_equipos, email_usr, ticket_id, tel_final):
                st.success(t['exito'])
                st.balloons()
                st.session_state.lista_equipos = []

with cf2:
    if st.button(f"🚪 {t['btn_salir']}", use_container_width=True):
        st.warning("Sesión finalizada. Puede cerrar la pestaña.")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)
