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

# 1. Configuración de página
st.set_page_config(page_title="SWARCO SAT PORTAL", layout="centered", page_icon="🚥")
cargar_estilos()

# --- HEADER BÁSICO (Fijamos Castellano por ahora para avanzar) ---
col_logo, col_lang, col_sem = st.columns([1.2, 1.5, 0.5])
with col_logo:
    st.image("logo.png", width=130)
with col_lang:
    # Mantenemos el selector simple para no romper el flujo
    t = traducir_interfaz("Castellano")
with col_sem:
    st.markdown("<h3 style='text-align:right; margin:0;'>🚥</h3>", unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align: center; color: #00549F;'>{t['titulo']}</h1>", unsafe_allow_html=True)

# --- CATEGORÍA 1: IDENTIFICACIÓN DEL CLIENTE ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
    # RECUPERADO: Proyecto / Ubicación (Opcional)
    proyecto_ub = st.text_input("Proyecto / Ubicación (Opcional)")
with c2:
    email_usr = st.text_input(t['email'])
    p_nombres = list(PAISES_DATA.keys())
    pais_sel = st.selectbox(t['pais'], p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
    tel_usr = f"{PAISES_DATA[pais_sel]} {st.text_input(t['tel'])}"

# --- CATEGORÍA 2: IDENTIFICACIÓN DEL EQUIPO ---
# Se elimina la urgencia de aquí por tu petición
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(t['pegatina'])
st.image("etiqueta.jpeg", use_container_width=True)

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

with st.container():
    ce1, ce2 = st.columns(2)
    ns_in = ce1.text_input(t['ns_titulo'])
    ref_in = ce2.text_input("REF / PN")
    
    # --- CATEGORÍA 3: DESCRIPCIÓN DEL PROBLEMA + URGENCIA ---
    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    
    # BARRA DE URGENCIA DEGRADADA (Azul a Naranja)
    st.markdown("**Nivel de Urgencia / Priority Level**")
    # CSS para la barra degradada en el slider
    st.markdown("""
        <style>
        .stSlider > div [data-baseweb="slider"] {
            background: linear-gradient(to right, #00549F 0%, #F29400 100%);
            height: 10px;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # 6 Estados de urgencia
    prioridad_val = st.select_slider(
        "Deslice para indicar la urgencia",
        options=["Muy Baja", "Baja", "Normal", "Alta", "Muy Alta", "CRÍTICA"],
        value="Normal"
    )
    
    st.markdown(f"**{t['desc']}**")
    falla_in = st.text_area("", key="falla_area", label_visibility="collapsed")
    
    st.file_uploader(t['fotos'], accept_multiple_files=True, type=['png', 'jpg', 'mp4'], label_visibility="collapsed")

    if st.button("➕ " + (t['btn_agregar'] if 'btn_agregar' in t else "AGREGAR EQUIPO"), use_container_width=True):
        if ns_in and falla_in:
            st.session_state.lista_equipos.append({
                "ns": ns_in, 
                "ref": ref_in, 
                "urgencia": prioridad_val, 
                "desc": falla_in
            })
            st.rerun()

# Tabla de resumen
if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# --- BOTÓN DE ENVÍO FINAL ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button(t['btn'], type="primary", use_container_width=True):
    if empresa and st.session_state.lista_equipos:
        t_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        if enviar_email_outlook(empresa, contacto, proyecto_ub, st.session_state.lista_equipos, email_usr, t_id, tel_usr):
            st.success(t['exito'])
            st.balloons()
            st.session_state.lista_equipos = []