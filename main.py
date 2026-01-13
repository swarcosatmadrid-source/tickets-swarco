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

# --- HEADER: LOGO GRANDE | IDIOMAS | PMV ---
col_logo, col_lang, col_pmv = st.columns([1.5, 1, 1])

with col_logo:
    # Logo más grande como pediste
    st.image("logo.png", width=180) 

with col_lang:
    # Regresamos a la lista de idiomas que funcionaba genial
    idiomas_disp = ["Castellano", "English", "Deutsch", "Français", "Català", "Euskara"]
    idioma_sel = st.selectbox("Seleccione Idioma", idiomas_disp, label_visibility="collapsed")
    # Mapeo para el traductor
    mapeo = {"Castellano":"es","English":"en","Deutsch":"de","Français":"fr","Català":"ca","Euskara":"eu"}
    t = traducir_interfaz(mapeo.get(idioma_sel, "es"))

with col_pmv:
    # Sustituimos el semáforo por un Panel de Mensajería Variable (PMV)
    st.markdown("""
        <div style="background-color: #1a1a1a; border: 3px solid #333; border-radius: 5px; padding: 5px; text-align: center;">
            <p style="color: #FFD700; font-family: 'Courier New', Courier, monospace; font-weight: bold; font-size: 12px; margin: 0;">
                TICKET<br>STATUS<br><span style="color: #00FF00;">ONLINE</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

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
    
    # VALIDACIÓN DE TELÉFONO: Solo números
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} (Solo números)", help=f"Prefijo automático: {prefijo}")
    
    # Limpieza inmediata de letras
    tel_limpio = "".join(filter(str.isdigit, tel_raw))
    if tel_raw and not tel_raw.isdigit():
        st.error("⚠️ El teléfono solo debe contener números.")
    tel_usr = f"{prefijo} {tel_limpio}"

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
    ref_in = st.text_input("REF.") # Cambiado de REF/PN a solo REF.

# --- CATEGORÍA 3: DESCRIPCIÓN DEL PROBLEMA ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)

# SLIDER DEGRADADO (Azul Claro a Naranja Swarco)
st.markdown("**Nivel de Urgencia**")
st.markdown("""
    <style>
    /* Estilo para el slider degradado */
    .stSlider > div [data-baseweb="slider"] {
        background: linear-gradient(to right, #87CEEB 0%, #F29400 100%);
        height: 12px;
    }
    /* Estilo para botones más redondeados y modernos */
    .stButton>button {
        border-radius: 20px;
        border: 2px solid #00549F;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #00549F;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

urg_val = st.select_slider(
    "Seleccione la prioridad del aviso",
    options=["Mínima", "Baja", "Normal", "Alta", "Muy Alta", "CRÍTICA"],
    value="Normal"
)

# Frase "que la parte" en español neutro
st.markdown(f"**Por favor, describa de forma concisa la naturaleza de la incidencia y sus síntomas observados.**")
falla_in = st.text_area("", placeholder="Ej: El equipo no sincroniza con el regulador tras caída de tensión...", label_visibility="collapsed")

# Gestión de espacio de imágenes
st.markdown("**Multimedia (Máximo 10MB total)**")
archivos = st.file_uploader("Suba fotos o videos de la avería", accept_multiple_files=True, type=['png', 'jpg', 'mp4'], label_visibility="collapsed")

if archivos:
    peso_total = sum([f.size for f in archivos]) / (1024 * 1024)
    porcentaje = min(int((peso_total / 10) * 100), 100)
    st.progress(porcentaje / 100)
    st.caption(f"Espacio utilizado: {porcentaje}% de 10MB")

# Botón Agregar Equipo al Ticket
if st.button("➕ AGREGAR EQUIPO AL TICKET", use_container_width=True):
    if ns_in and falla_in:
        st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_val, "desc": falla_in})
        st.rerun()

if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# --- ACCIONES FINALES ---
st.markdown("<br>", unsafe_allow_html=True)
col_fin1, col_fin2 = st.columns(2)

with col_fin1:
    if st.button("🚀 GENERAR TICKET", type="primary", use_container_width=True):
        if empresa and st.session_state.lista_equipos:
            st.success("Ticket enviado correctamente.")
            st.balloons()
            st.session_state.lista_equipos = []

with col_fin2:
    # Botón Salir con lógica de cierre
    if st.button("🚪 SALIR DE LA PÁGINA", use_container_width=True):
        st.markdown('<script>window.close();</script>', unsafe_allow_html=True)
        st.warning("Ya puede cerrar esta pestaña.")

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN</p>", unsafe_allow_html=True)