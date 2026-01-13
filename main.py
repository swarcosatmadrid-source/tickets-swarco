import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# Asegurar ruta de archivos locales
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook

# 1. Configuración de pantalla
st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚥")
cargar_estilos()

# --- HEADER: LOGO GRANDE Y BUSCADOR UNIVERSAL DE IDIOMAS ---
col_logo, col_lang = st.columns([1.5, 1])

with col_logo:
    st.image("logo.png", width=220)

with col_lang:
    # RECUPERADO: El buscador donde puedes escribir el idioma que quieras
    idioma_libre = st.text_input("Idioma / Language", value="Castellano", help="Escriba el idioma deseado (ej: Ruso, Japonés, Euskara...)")
    
    # El sistema procesa lo que escribas y busca la traducción
    t = traducir_interfaz(idioma_libre)

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
    
    # LÓGICA DE TELÉFONO: El prefijo se muestra y se une al final
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})", placeholder="Solo números")
    
    # Filtro de seguridad: eliminamos cualquier cosa que no sea número
    tel_limpio = "".join(filter(str.isdigit, tel_raw))
    if tel_raw and not tel_raw.isdigit():
        st.error("⚠️ El sistema solo admite caracteres numéricos en este campo.")
    
    # UNIÓN: Aquí se junta el prefijo con el número para el envío final
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

# --- CATEGORÍA 3: DESCRIPCIÓN DEL PROBLEMA ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)

# SLIDER DEGRADADO (Azul Claro a Naranja Swarco)
st.markdown("**Nivel de Urgencia**")
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
    "Deslice para indicar la prioridad",
    options=["Mínima", "Baja", "Normal", "Alta", "Muy Alta", "CRÍTICA"],
    value="Normal"
)

st.markdown(f"**Por favor, describa de forma concisa la naturaleza de la incidencia y sus síntomas observados.**")
falla_in = st.text_area("", placeholder="Describa aquí el fallo...", label_visibility="collapsed")

# Gestión de Multimedia (Límite 200MB)
st.markdown("**Multimedia (Límite total: 200MB)**")
archivos = st.file_uploader("Adjunte evidencias", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

if archivos:
    peso_total = sum([f.size for f in archivos]) / (1024 * 1024)
    porcentaje = min(int((peso_total / 200) * 100), 100)
    st.progress(porcentaje / 100)
    st.caption(f"Espacio utilizado: {peso_total:.2f}MB de 200MB ({porcentaje}%)")

if st.button("➕ AGREGAR EQUIPO AL TICKET", use_container_width=True):
    if ns_in and falla_in:
        # Se guarda el equipo con el nivel de urgencia del slider
        st.session_state.lista_equipos.append({
            "ns": ns_in, "ref": ref_in, "urgencia": urg_val, "desc": falla_in
        })
        st.rerun()

if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# --- ACCIONES FINALES ---
st.markdown("<br>", unsafe_allow_html=True)
col_fin1, col_fin2 = st.columns(2)

with col_fin1:
    # Al generar el ticket, se envía tel_final (Prefijo + Número)
    if st.button("🚀 GENERAR TICKET", type="primary", use_container_width=True):
        if empresa and st.session_state.lista_equipos:
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            if enviar_email_outlook(empresa, contacto, proyecto_ub, st.session_state.lista_equipos, email_usr, ticket_id, tel_final):
                st.success(t['exito'])
                st.balloons()
                st.session_state.lista_equipos = []

with col_fin2:
    if st.button("🚪 SALIR", use_container_width=True):
        st.warning("Ya puede cerrar la pestaña de su navegador.")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)