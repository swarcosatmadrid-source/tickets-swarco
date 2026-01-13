import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# Asegurar que encuentre los otros archivos .py
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook

# 1. Configuración de pantalla
st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚥")
cargar_estilos()

# --- HEADER: LOGO MAXIMIZADO Y BUSCADOR UNIVERSAL ---
col_logo, col_lang = st.columns([1.5, 1])

with col_logo:
    st.image("logo.png", width=250)

with col_lang:
    # Ahora el buscador entiende cualquier idioma escrito en español o inglés
    idioma_txt = st.text_input("Idioma / Language", value="Castellano")
    t = traducir_interfaz(idioma_txt)

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
    # España por defecto
    idx_def = p_nombres.index("Spain") if "Spain" in p_nombres else 0
    pais_sel = st.selectbox(t['pais'], p_nombres, index=idx_def)
    
    # LÓGICA DE TELÉFONO: Prefijo automático y bloqueo de letras
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})", placeholder="Solo números")
    
    # Limpieza de caracteres no numéricos
    tel_limpio = "".join(filter(str.isdigit, tel_raw))
    if tel_raw and not tel_raw.isdigit():
        st.error("⚠️ Error: Solo se permiten números. Las letras serán descartadas.")
    
    # Unión final para el correo
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
    ref_in = st.text_input("REF.") # Solo REF como en la pegatina

# --- CATEGORÍA 3: DESCRIPCIÓN DEL PROBLEMA + URGENCIA ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)

# SLIDER DEGRADADO: Azul Claro (#ADD8E6) a Naranja Swarco (#F29400)
st.markdown("**Nivel de Urgencia / Priority Level**")
st.markdown("""
    <style>
    .stSlider > div [data-baseweb="slider"] {
        background: linear-gradient(to right, #ADD8E6 0%, #F29400 100%);
        height: 12px;
        border-radius: 6px;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

urg_val = st.select_slider(
    "Deslice para indicar la prioridad de la incidencia",
    options=["Mínima", "Baja", "Normal", "Alta", "Muy Alta", "CRÍTICA"],
    value="Normal"
)

st.markdown(f"**Por favor, describa de forma concisa la naturaleza de la incidencia y sus síntomas observados.**")
falla_in = st.text_area("", placeholder="Indique brevemente el fallo...", label_visibility="collapsed")

# Gestión de archivos con barra de progreso (Límite 200MB)
st.markdown("**Multimedia (Límite total: 200MB)**")
archivos = st.file_uploader("Adjunte evidencias", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

if archivos:
    peso_total = sum([f.size for f in archivos]) / (1024 * 1024)
    porcentaje = min(int((peso_total / 200) * 100), 100)
    st.progress(porcentaje / 100)
    st.caption(f"Uso: {peso_total:.2f}MB de 200MB ({porcentaje}%)")

# Botón Agregar con nombre corregido
if st.button("➕ AGREGAR EQUIPO AL TICKET", use_container_width=True):
    if ns_in and falla_in:
        st.session_state.lista_equipos.append({
            "ns": ns_in, "ref": ref_in, "urgencia": urg_val, "desc": falla_in
        })
        st.rerun()

if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# --- ACCIONES FINALES ---
st.markdown("<br>", unsafe_allow_html=True)
col_f1, col_f2 = st.columns(2)

with col_f1:
    if st.button("🚀 GENERAR TICKET", type="primary", use_container_width=True):
        if empresa and st.session_state.lista_equipos:
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            if enviar_email_outlook(empresa, contacto, proyecto_ub, st.session_state.lista_equipos, email_usr, ticket_id, tel_final):
                st.success(t['exito'])
                st.balloons()
                st.session_state.lista_equipos = []

with col_f2:
    if st.button("🚪 SALIR", use_container_width=True):
        st.warning("Ya puede cerrar esta pestaña.")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)
