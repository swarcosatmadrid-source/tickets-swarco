import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# 1. SEGURIDAD DE RUTAS Y CONFIGURACIÓN RAÍZ
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook

# Configuración de página y blindaje de color primario
st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚥")

# MUERTE AL ROJO: Inyectamos el azul corporativo en la raíz de Streamlit
st.markdown("""
    <style>
    :root { --primary-color: #00549F !important; }
    /* Matamos el rastro rojo del carril del slider */
    div[data-baseweb="slider"] > div { background-color: transparent !important; }
    /* Estilo de la pelota y marcas de graduación */
    div[role="slider"] { border: 2px solid white !important; box-shadow: 0px 0px 5px rgba(0,0,0,0.2); }
    .stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"] { 
        color: #00549F !important; 
        font-weight: bold !important; 
    }
    .stButton>button { border-radius: 12px !important; }
    </style>
""", unsafe_allow_html=True)

cargar_estilos()

# --- HEADER: LOGO MAXIMIZADO Y TRADUCTOR UNIVERSAL ---
col_logo, col_lang = st.columns([1.5, 1])
with col_logo:
    st.image("logo.png", width=250)
with col_lang:
    # Buscador que entiende cualquier idioma escrito
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
    
    # TELÉFONO BLINDADO: Solo números + Prefijo automático
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})", placeholder="Solo números")
    tel_limpio = "".join(filter(str.isdigit, tel_raw))
    if tel_raw and not tel_raw.isdigit():
        st.error(f"⚠️ {t['error_tel']}")
    tel_final = f"{prefijo}{tel_limpio}"

# --- CATEGORÍA 2: IDENTIFICACIÓN DEL EQUIPO ---
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(t['pegatina'])
st.image("etiqueta.jpeg", use_container_width=True)

ce1, ce2 = st.columns(2)
with ce1:
    ns_in = st.text_input(t['ns_titulo'])
with ce2:
    ref_in = st.text_input("REF.")

# --- CATEGORÍA 3: DESCRIPCIÓN DEL PROBLEMA + URGENCIA DINÁMICA ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
st.markdown(f"**{t['urg_titulo']}**")

# Slider con Degradado Azul Claro -> Naranja Swarco
st.markdown("""<style>.stSlider > div [data-baseweb="slider"] { background: linear-gradient(to right, #ADD8E6 0%, #F29400 100%) !important; height: 12px !important; }</style>""", unsafe_allow_html=True)

opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
urg_val = st.select_slider(t['urg_instruccion'], options=opciones_urg, value=t['u3'])

# La pelota cambia de color según la selección
colores_map = {t['u1']:"#ADD8E6", t['u2']:"#90C3D4", t['u3']:"#7AB1C5", t['u4']:"#C2A350", t['u5']:"#D69B28", t['u6']:"#F29400"}
color_thumb = colores_map.get(urg_val, "#7AB1C5")
st.markdown(f"<style>div[role='slider'] {{ background-color: {color_thumb} !important; }}</style>", unsafe_allow_html=True)

falla_in = st.text_area(t['desc_instruccion'], placeholder=t['desc_placeholder'])

# MULTIMEDIA RECUPERADO (200MB)
st.markdown(f"**{t['fotos']}**")
archivos = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

if archivos:
    peso_total = sum([f.size for f in archivos]) / (1024 * 1024)
    st.progress(min(peso_total / 200, 1.0))
    st.caption(f"{peso_total:.2f}MB / 200MB")

# GESTIÓN DE LA LISTA DE EQUIPOS
if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# BOTÓN AGREGAR CON VALIDACIÓN (Mínimo 3 caracteres en NS y 10 en descripción)
if st.button(f"➕ {t['btn_agregar']}", use_container_width=True):
    if len(ns_in) >= 3 and len(falla_in) >= 10:
        st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_val, "desc": falla_in})
        st.rerun()
    else:
        st.warning(t['error_tel']) # Reutilizamos el aviso de error para datos incompletos

# --- RESUMEN VISUAL Y ENVÍO FINAL ---
if st.session_state.lista_equipos:
    st.markdown("---")
    st.subheader("📋 RESUMEN / SUMMARY")
    df = pd.DataFrame(st.session_state.lista_equipos)
    
    # Función para pintar las filas de la tabla según la urgencia
    def style_urgencia(val):
        return f'background-color: {colores_map.get(val, "white")}; color: black'
    
    st.dataframe(df.style.applymap(style_urgencia, subset=['urgencia']), use_container_width=True)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        if st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True):
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            if enviar_email_outlook(empresa, contacto, proyecto_ub, st.session_state.lista_equipos, email_usr, ticket_id, tel_final):
                st.success(t['exito'])
                st.session_state.lista_equipos = []
                st.rerun()
    with col_f2:
        if st.button("🗑️ BORRAR TODO / CLEAR ALL", use_container_width=True):
            st.session_state.lista_equipos = []
            st.rerun()

st.markdown("---")
# BOTÓN SALIR FINAL
if st.button(f"🚪 {t['btn_salir']}", key="exit_final_btn"):
    st.warning(t['salir_aviso'])

st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)




