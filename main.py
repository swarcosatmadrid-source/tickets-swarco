import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys
from streamlit_javascript import st_javascript 

# Asegurar ruta de archivos locales
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook

# 1. Configuración de pantalla
st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚥")
cargar_estilos()

# --- DETECCIÓN Y BUSCADOR UNIVERSAL DE IDIOMA ---
# Detectamos el idioma del navegador automáticamente
lang_nav = st_javascript('window.navigator.language || window.navigator.userLanguage')

if 'idioma_detectado' not in st.session_state:
    st.session_state.idioma_detectado = lang_nav if lang_nav else "es"

# --- HEADER: LOGO SWARCO (GRANDE) E IDIOMA ---
col_logo, col_lang = st.columns([1.5, 1])

with col_logo:
    st.image("logo.png", width=250)

with col_lang:
    # El usuario puede ver el detectado o ESCRIBIR el que quiera (en cualquier lengua)
    idioma_usr = st.text_input(
        "Idioma / Language", 
        value=st.session_state.idioma_detectado,
        help="Detectado automáticamente. Puede escribir otro (ej: 'Ruso', 'Russian', 'Pусский')"
    )
    # El motor de idiomas.py procesa la entrada
    t = traducir_interfaz(idioma_usr)

# --- CATEGORÍA 1: IDENTIFICACIÓN DEL CLIENTE ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
    proyecto_ub = st.text_input("Proyecto / Ubicación (Opcional)")

with c2:
    email_usr = st.text_input(t['email'])
    p_nombres = list(PAISES_DATA.keys())
    pais_sel = st.selectbox(t['pais'], p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
    
    # LÓGICA DE TELÉFONO: El prefijo se pasa junto al número
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})", placeholder="Solo números")
    
    # Prohibición de letras: filtramos el input
    tel_limpio = "".join(filter(str.isdigit, tel_raw))
    if tel_raw and not tel_raw.isdigit():
        st.error("⚠️ Error: Solo se permiten caracteres numéricos.")
    
    # Variable final para el envío
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
    ref_in = st.text_input("REF.") # Solo REF. como en la pegatina

# --- CATEGORÍA 3: DESCRIPCIÓN DEL PROBLEMA ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)

# SLIDER DEGRADADO: Azul Claro a Naranja Swarco
st.markdown("**Nivel de Urgencia**")
st.markdown("""
    <style>
    .stSlider > div [data-baseweb="slider"] {
        background: linear-gradient(to right, #ADD8E6 0%, #F29400 100%);
        height: 12px;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

urg_val = st.select_slider(
    "Seleccione la prioridad de la incidencia",
    options=["Mínima", "Baja", "Normal", "Alta", "Muy Alta", "CRÍTICA"],
    value="Normal"
)

st.markdown(f"**Por favor, describa de forma concisa la naturaleza de la incidencia y sus síntomas observados.**")
falla_in = st.text_area("", placeholder="Indique brevemente en qué consiste la falla...", label_visibility="collapsed")

# Multimedia con monitor de espacio (200MB)
st.markdown("**Multimedia (Límite total: 200MB)**")
archivos = st.file_uploader("Adjunte evidencias", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

if archivos:
    peso_total = sum([f.size for f in archivos]) / (1024 * 1024)
    porcentaje = min(int((peso_total / 200) * 100), 100)
    st.progress(porcentaje / 100)
    st.caption(f"Espacio utilizado: {peso_total:.2f}MB de 200MB ({porcentaje}%)")

if st.button("➕ AGREGAR EQUIPO AL TICKET", use_container_width=True):
    if ns_in and falla_in:
        st.session_state.lista_equipos.append({
            "ns": ns_in, "ref": ref_in, "urgencia": urg_in, "desc": falla_in
        })
        st.rerun()

# --- ACCIONES FINALES ---
st.markdown("<br>", unsafe_allow_html=True)
col_fin1, col_fin2 = st.columns(2)

with col_fin1:
    if st.button("🚀 GENERAR TICKET", type="primary", use_container_width=True):
        if empresa and st.session_state.lista_equipos:
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            if enviar_email_outlook(empresa, contacto, proyecto_ub, st.session_state.lista_equipos, email_usr, ticket_id, tel_final):
                st.success(t['exito'])
                st.balloons()
                st.session_state.lista_equipos = []

with col_fin2:
    if st.button("🚪 SALIR DE LA PÁGINA", use_container_width=True):
        st.markdown('<script>window.close();</script>', unsafe_allow_html=True)
        st.warning("Cierre la pestaña manualmente.")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)