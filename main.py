import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# Aseguramos que Python encuentre tus archivos locales (estilos, idiomas, etc.)
sys.path.append(os.path.dirname(__file__))

# Importaciones locales (Verifica que tus archivos se llamen así)
from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA (Centrado y profesional)
st.set_page_config(page_title="SWARCO SAT PORTAL", layout="centered", page_icon="🚥")
cargar_estilos() # Esta función debe estar en estilos.py

# Conexión a la base de datos (GSheets)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    pass

# --- ENCABEZADO (HEADER) ---
# Diseñado para que el logo no se corte y las banderas sean discretas
col_logo, col_lang, col_sem = st.columns([1.5, 1, 0.5])

with col_logo:
    st.image("logo.png", width=140)

with col_lang:
    # Selector de idioma pequeño con banderas
    idioma_map = {"🇪🇸 ES": "Español", "🇬🇧 EN": "English 🇬🇧", "🇩🇪 DE": "Deutsch 🇩🇪", "🇫🇷 FR": "Français 🇫🇷"}
    idioma_key = st.selectbox("", list(idioma_map.keys()), label_visibility="collapsed")
    t = traducir_interfaz(idioma_map[idioma_key])

with col_sem:
    st.markdown("<h2 style='margin:0; text-align:right;'>🚥</h2>", unsafe_allow_html=True)

# Título y Subtítulo (Estilo Limpio Swarco)
st.markdown(f"<h1 style='text-align: center; color: #00549F; margin-top: 0;'>{t['titulo']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #666; font-weight: 500;'>{t['sub']}</p>", unsafe_allow_html=True)

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
st.info(f"ℹ️ {t['pegatina']}")
st.image("etiqueta.jpeg", use_container_width=True)

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# Bloque para añadir equipos
with st.container():
    ce1, ce2, ce3 = st.columns([2, 2, 1])
    ns_in = ce1.text_input(t['ns_titulo'])
    ref_in = ce2.text_input("REF / PN")
    urg_in = ce3.selectbox(t['prioridad'], ["Normal", "Alta", "Crítica"])
    
    # --- SECCIÓN 3: DESCRIPCIÓN DEL PROBLEMA (Antes del botón) ---
    st.markdown(f"**{t['desc']}**")
    falla_in = st.text_area("", key="falla_area", label_visibility="collapsed", placeholder="Explique la falla técnica...")
    
    st.markdown(f"**{t['fotos']}**")
    st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

    if st.button("➕ AGREGAR ESTE EQUIPO"):
        if ns_in and falla_in:
            st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_in, "desc": falla_in})
            st.rerun()

# Tabla de resumen
if st.session_state.lista_equipos:
    st.markdown("---")
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# --- SECCIÓN FINAL: ENVÍO (BOTÓN NARANJA) ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button(t['btn'], type="primary", use_container_width=True):
    if not empresa or not email_usr or not st.session_state.lista_equipos:
        st.error("Rellene los campos obligatorios (*) y agregue al menos un equipo.")
    else:
        ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        
        # 1. Enviar Email
        if enviar_email_outlook(empresa, contacto, proyecto, st.session_state.lista_equipos, email_usr, ticket_id, tel_usr):
            
            # 2. Guardar en GSheets (Opcional)
            try:
                nueva_fila = pd.DataFrame([{"ID": ticket_id, "Fecha": datetime.now().strftime("%d/%m/%Y"), "Empresa": empresa, "Estado": "Pendiente"}])
                df_ex = conn.read(worksheet="Sheet1")
                conn.update(worksheet="Sheet1", data=pd.concat([df_ex, nueva_fila], ignore_index=True))
            except:
                pass
            
            st.success(f"✔️ {t['exito']}")
            st.info(t['msg_tecnico'])
            st.balloons()
            st.session_state.lista_equipos = []

# --- FOOTER (PIE DE PÁGINA) ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #999; font-size: 12px; padding-bottom: 30px;'>
        <p>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>
        <p><a href='https://www.swarco.com/es/aviso-legal' target='_blank' style='color: #F29400;'>Aviso Legal</a> | <a href='https://www.swarco.com/es/privacidad' target='_blank' style='color: #F29400;'>Privacidad</a></p>
    </div>
""", unsafe_allow_html=True)