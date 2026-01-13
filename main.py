import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys
import pycountry # Librería estándar para países e idiomas

sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook

# 1. Configuración
st.set_page_config(page_title="SWARCO SAT GLOBAL", layout="centered", page_icon="🚥")
cargar_estilos()

# --- HEADER DINÁMICO ---
col_logo, col_lang, col_sem = st.columns([1.2, 1.5, 0.5])

with col_logo:
    st.image("logo.png", width=130)

with col_lang:
    # Selector de Idiomas: Ahora es una lista simple
    opciones = ["Castellano", "Euskara", "Català", "English", "Chinese", "Arabic", "Japanese", "German", "French"]
    idioma_nom = st.selectbox("Language", opciones, label_visibility="collapsed")

    # --- LÓGICA DE MATCH AUTOMÁTICO ---
    # Mapeamos el nombre al código ISO 639-1 (el de idiomas)
    mapeo_iso = {
        "Castellano": "es", "Euskara": "eu", "Català": "ca", "English": "en",
        "Chinese": "zh", "Arabic": "ar", "Japanese": "ja", "German": "de", "French": "fr"
    }
    cod_iso = mapeo_iso.get(idioma_nom, "es")

    # MATCH DE BANDERA AUTOMÁTICO
    # 1. Casos especiales que no son países ISO estándar
    if idioma_nom == "Euskara":
        url_bandera = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Flag_of_the_Basque_Country.svg/80px-Flag_of_the_Basque_Country.svg.png"
    elif idioma_nom == "Català":
        url_bandera = "https://flagcdn.com/w80/es-ct.png"
    else:
        # 2. Match automático para el resto del mundo
        # Convertimos código de idioma a código de país (ej: ar -> sa, en -> gb, zh -> cn)
        match_pais = {"ar": "sa", "en": "gb", "zh": "cn", "ja": "jp"}
        cod_pais = match_pais.get(cod_iso, cod_iso)
        url_bandera = f"https://flagcdn.com/w80/{cod_pais}.png"

    # Mostrar bandera automáticamente
    st.image(url_bandera, width=40)
    
    # Traducir portal
    t = traducir_interfaz(cod_iso)

with col_sem:
    st.markdown("<h2 style='text-align:right; margin:0;'>🚥</h2>", unsafe_allow_html=True)

# --- CUERPO DEL PORTAL (Usando el diccionario t) ---
st.markdown(f"<h1 style='text-align: center; color: #00549F;'>{t['titulo']}</h1>", unsafe_allow_html=True)

# SECCIÓN 1: CLIENTE
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
with c2:
    email_usr = st.text_input(t['email'])
    # Aquí los países ya vienen de tu servicio paises.py
    p_nombres = list(PAISES_DATA.keys())
    pais_sel = st.selectbox(t['pais'], p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
    prefijo = PAISES_DATA[pais_sel]
    tel_usr = f"{prefijo} {st.text_input(f'{t['tel']} ({prefijo})')}"

# SECCIÓN 2: EQUIPO
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(t['pegatina'])
st.image("etiqueta.jpeg", use_container_width=True)

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

with st.container():
    ce1, ce2, ce3 = st.columns([2, 2, 1.2])
    ns_in = ce1.text_input(t['ns_titulo'] if 'ns_titulo' in t else "N.S")
    ref_in = ce2.text_input("REF / PN")
    urg_in = ce3.selectbox(t['prioridad'], ["Normal", "Alta", "Crítica"])
    
    # SECCIÓN 3: PROBLEMA
    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**{t['desc']}**")
    falla_in = st.text_area("", key="falla_area", label_visibility="collapsed")
    
    if st.button(t['btn_agregar'] if 'btn_agregar' in t else "➕ ADD", use_container_width=True):
        if ns_in and falla_in:
            st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_in, "desc": falla_in})
            st.rerun()

if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# ENVÍO
if st.button(t['btn'], type="primary", use_container_width=True):
    if empresa and st.session_state.lista_equipos:
        st.success(t['exito'])
        st.balloons()

st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN</p>", unsafe_allow_html=True)