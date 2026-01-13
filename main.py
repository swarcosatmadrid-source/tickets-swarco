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
st.set_page_config(page_title="SWARCO SAT GLOBAL", layout="centered", page_icon="🚥")
cargar_estilos()

# --- HEADER: LOGO | BUSCADOR DINÁMICO | SEMÁFORO ---
col_logo, col_lang, col_sem = st.columns([1.2, 1.5, 0.5])

with col_logo:
    st.image("logo.png", width=130)

with col_lang:
    # Selector de idioma: El cliente puede escribir o elegir
    # Agregamos los que tienen banderas "especiales" y el resto se busca solo
    idioma_input = st.selectbox("Idioma / Language", 
        ["Castellano", "Euskara", "Català", "English", "Arabic", "Deutsch", "Français", "Japonés", "Hebreo", "Chino"],
        label_visibility="collapsed")

    # 1. Obtenemos el código ISO a través de un mapeo simple
    mapeo_codigos = {
        "Castellano": "es", "Euskara": "eu", "Català": "ca", "English": "en",
        "Arabic": "ar", "Deutsch": "de", "Français": "fr", "Japonés": "ja",
        "Hebreo": "iw", "Chino": "zh-CN"
    }
    cod = mapeo_codigos.get(idioma_input, "es")

    # 2. LÓGICA DE BANDERA INTELIGENTE (Sin bases pregrabadas gigantes)
    # Si es una región específica, usamos el link directo para que no falle.
    if idioma_input == "Euskara":
        url_bandera = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Flag_of_the_Basque_Country.svg/80px-Flag_of_the_Basque_Country.svg.png"
    elif idioma_input == "Català":
        url_bandera = "https://flagcdn.com/w80/es-ct.png"
    else:
        # Para el resto del mundo, el sistema BUSCA la bandera usando el código ISO
        # Corregimos casos especiales: 'ar' (Árabe) -> 'sa' (Arabia), 'en' -> 'gb'
        cod_f = "sa" if cod == "ar" else ("gb" if cod == "en" else cod)
        url_bandera = f"https://flagcdn.com/w80/{cod_f}.png"

    # Mostramos la bandera encontrada
    st.image(url_bandera, width=40)
    
    # Traducimos todo el portal al idioma detectado
    t = traducir_interfaz(cod)

with col_sem:
    st.markdown("<h2 style='text-align:right; margin:0;'>🚥</h2>", unsafe_allow_html=True)

# --- EL RESTO DEL FORMULARIO SE MANTIENE 100% FIEL A SWARCO ---
st.markdown(f"<h1 style='text-align: center; color: #00549F; margin-top: 0;'>{t['titulo']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #666;'>{t['sub']}</p>", unsafe_allow_html=True)

# SECCIÓN 1: CLIENTE
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
    proyecto = st.text_input(t['proyecto'])
with c2:
    email_usr = st.text_input(t['email'])
    p_nombres = list(PAISES_DATA.keys())
    pais_sel = st.selectbox(t['pais'], p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
    prefijo = PAISES_DATA[pais_sel]
    tel_usr = f"{prefijo} {st.text_input(f'{t['tel']} ({prefijo})')}"

# SECCIÓN 2: EQUIPO
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(f"💡 {t['pegatina']}")
st.image("etiqueta.jpeg", use_container_width=True)

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

with st.container():
    ce1, ce2, ce3 = st.columns([2, 2, 1.2])
    ns_in = ce1.text_input(t['ns_titulo'])
    ref_in = ce2.text_input("REF / PN")
    urg_in = ce3.selectbox(t['prioridad'], ["Normal", "Alta", "Crítica"])
    
    # SECCIÓN 3: PROBLEMA
    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**{t['desc']}**")
    falla_in = st.text_area("", key="falla_area", label_visibility="collapsed")
    st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'mp4'], label_visibility="collapsed")

    if st.button(t['btn_agregar'] if 'btn_agregar' in t else "➕ AGREGAR", use_container_width=True):
        if ns_in and falla_in:
            st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_in, "desc": falla_in})
            st.rerun()

if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# ENVÍO
st.markdown("<br>", unsafe_allow_html=True)
if st.button(t['btn'], type="primary", use_container_width=True):
    if not empresa or not email_usr or not st.session_state.lista_equipos:
        st.error("Datos incompletos.")
    else:
        t_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        if enviar_email_outlook(empresa, contacto, proyecto, st.session_state.lista_equipos, email_usr, t_id, tel_usr):
            st.success(t['exito'])
            st.balloons()
            st.session_state.lista_equipos = []

# FOOTER
st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)
