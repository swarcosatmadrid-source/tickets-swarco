import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# Asegurar ruta de archivos locales para evitar errores de carga
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection

# 1. Configuración inicial del portal
st.set_page_config(page_title="SWARCO SAT", layout="centered", page_icon="🚥")
cargar_estilos()

# Conexión a la base de datos de tickets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    pass

# --- HEADER: LOGO | BANDERAS REALES | SEMÁFORO ---
col_logo, col_lang, col_sem = st.columns([1.5, 1.2, 0.5])

with col_logo:
    # Logo Swarco sin cortes
    st.image("logo.png", width=140)

with col_lang:
    # Diccionario con links a imágenes reales de banderas (FlagCDN)
    banderas_reales = {
        "Castellano": "https://flagcdn.com/w80/es.png",
        "English": "https://flagcdn.com/w80/gb.png",
        "Deutsch": "https://flagcdn.com/w80/de.png",
        "Français": "https://flagcdn.com/w80/fr.png",
        "Català": "https://flagcdn.com/w80/es-ct.png", # Senyera oficial
        "Euskara": "https://flagcdn.com/w80/es-pv.png", # Ikurriña oficial
        "Galego": "https://flagcdn.com/w80/es-ga.png",  # Bandera Galicia
        "Hebreo": "https://flagcdn.com/w80/il.png",
        "Japonés": "https://flagcdn.com/w80/jp.png"
    }
    
    # Selector de texto limpio
    lang_sel = st.selectbox("Idioma / Language", list(banderas_reales.keys()), label_visibility="collapsed")
    
    # Mostramos la bandera en imagen (esto NO falla)
    st.image(banderas_reales[lang_sel], width=45)
    
    # Llamamos al segmento de traducción
    t = traducir_interfaz(lang_sel)

with col_sem:
    st.markdown("<h2 style='margin:0; text-align:right;'>🚥</h2>", unsafe_allow_html=True)

# Título Principal centrado y en Azul Swarco
st.markdown(f"<h1 style='text-align: center; color: #00549F; margin-top: 0;'>{t['titulo']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #666;'>{t['sub']}</p>", unsafe_allow_html=True)

# --- SECCIÓN 1: IDENTIFICACIÓN DEL CLIENTE ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
    proyecto = st.text_input(t['proyecto'])
with c2:
    email_usr = st.text_input(t['email'])
    p_nombres = list(PAISES_DATA.keys())
    idx_sp = p_nombres.index("Spain") if "Spain" in p_nombres else 0
    pais_sel = st.selectbox(t['pais'], p_nombres, index=idx_sp)
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} ({prefijo})")
    tel_usr = f"{prefijo} {tel_raw}"

# --- SECCIÓN 2: IDENTIFICACIÓN DEL EQUIPO (PEGATINA) ---
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
    
    # --- SECCIÓN 3: DETALLE DEL PROBLEMA (Antes del botón) ---
    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**{t['desc']}**")
    falla_in = st.text_area("", key="falla_area", label_visibility="collapsed")
    
    st.markdown(f"**{t['fotos']}**")
    st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

    if st.button(t['btn_agregar'], use_container_width=True):
        if ns_in and falla_in:
            st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_in, "desc": falla_in})
            st.rerun()

# Listado de equipos añadidos
if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# --- BOTÓN DE ENVÍO FINAL (Naranja Corporativo) ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button(t['btn'], type="primary", use_container_width=True):
    if not empresa or not email_usr or not st.session_state.lista_equipos:
        st.error("Rellene los campos obligatorios (*) y agregue al menos un equipo.")
    else:
        t_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        if enviar_email_outlook(empresa, contacto, proyecto, st.session_state.lista_equipos, email_usr, t_id, tel_usr):
            try:
                fila = pd.DataFrame([{"ID": t_id, "Fecha": datetime.now().strftime("%d/%m/%Y"), "Empresa": empresa, "Estado": "Pendiente"}])
                df_ex = conn.read(worksheet="Sheet1")
                conn.update(worksheet="Sheet1", data=pd.concat([df_ex, fila], ignore_index=True))
            except: pass
            st.success(t['exito'])
            st.info(t['msg_tecnico'])
            st.balloons()
            st.session_state.lista_equipos = []

# --- PIE DE PÁGINA (FOOTER) ---
st.markdown("---")
st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)