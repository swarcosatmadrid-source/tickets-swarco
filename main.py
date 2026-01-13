import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# Aseguramos que el sistema encuentre tus archivos locales
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de página con el estilo de la web oficial
st.set_page_config(page_title="SWARCO | The Better Way. Every Day.", layout="centered", page_icon="🚥")
cargar_estilos()

# Conexión silenciosa a la base de datos
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    pass

# --- ENCABEZADO: IDENTIDAD CORPORATIVA ---
# Logo a la izquierda, Selector e Info al centro, Semáforo a la derecha
col_logo, col_tit, col_sem = st.columns([1.5, 4, 1])

with col_logo:
    st.image("logo.png", width=140) # Logo Swarco original

with col_tit:
    # Selector de idioma discreto y elegante
    idioma_sel = st.selectbox("", ["Español", "English 🇬🇧", "Deutsch 🇩🇪", "Français 🇫🇷"], label_visibility="collapsed")
    t = traducir_interfaz(idioma_sel)
    st.markdown(f"<h1 style='text-align: center; color: #00549F; font-family: Arial; margin-bottom: 0;'>{t['titulo']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #009FE3; font-size: 1.1em; font-weight: 500;'>{t['sub']}</p>", unsafe_allow_html=True)

with col_sem:
    st.markdown("<div style='font-size: 45px; text-align: center; padding-top: 10px;'>🚥</div>", unsafe_allow_html=True)

# --- SECCIÓN 1: DATOS DEL CLIENTE ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)

with col_a:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
    proyecto = st.text_input(t['proyecto'])

with col_b:
    email_usr = st.text_input(t['email'])
    # Lógica de países y prefijos
    paises_list = list(PAISES_DATA.keys())
    idx_esp = paises_list.index("Spain") if "Spain" in paises_list else 0
    pais_sel = st.selectbox(t['pais'], paises_list, index=idx_esp)
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} ({prefijo})")
    tel_usr = f"{prefijo} {tel_raw}"

# --- SECCIÓN 2: DATOS DEL EQUIPO (La Pegatina) ---
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(f"💡 {t['pegatina']}")
st.image("etiqueta.jpeg", use_container_width=True, caption="Referencia de etiqueta Swarco")

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

with st.container():
    c_ns, c_ref, c_urg = st.columns([2, 2, 1.2])
    ns_val = c_ns.text_input(t['ns_titulo'])
    ref_val = c_ref.text_input("Referencia / PN")
    urg_val = c_urg.selectbox(t['prioridad'], ["Normal", "Alta", "Crítica"])
    
    st.markdown(f"**{t['desc']}**")
    falla_val = st.text_area("", key="falla_txt", label_visibility="collapsed", placeholder="Describa el problema técnico...")
    
    # CARGA DE ARCHIVOS (Fotos/Video)
    st.markdown(f"**{t['fotos']}**")
    st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4', 'mov'], label_visibility="collapsed")

    if st.button("➕ REGISTRAR EQUIPO", use_container_width=True):
        if ns_val and falla_val:
            st.session_state.lista_equipos.append({
                "ns": ns_val, "ref": ref_val, "urgencia": urg_val, "desc": falla_val
            })
            st.rerun()

# Tabla de resumen de equipos añadidos
if st.session_state.lista_equipos:
    st.markdown("---")
    st.table(pd.DataFrame(st.session_state.lista_equipos))
    if st.button("🗑️ Borrar Lista"):
        st.session_state.lista_equipos = []
        st.rerun()

# --- SECCIÓN 3: FINALIZAR ENVÍO ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
if st.button(t['btn'], type="primary", use_container_width=True):
    if not empresa or not email_usr or not st.session_state.lista_equipos:
        st.error("❌ Por favor, complete la información obligatoria y añada al menos un equipo.")
    else:
        t_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        
        if enviar_email_outlook(empresa, contacto, proyecto, st.session_state.lista_equipos, email_usr, t_id, tel_usr):
            # Guardado en Google Sheets
            try:
                fila = pd.DataFrame([{"ID": t_id, "Fecha": datetime.now().strftime("%d/%m/%Y"), "Empresa": empresa, "Estado": "Recibido"}])
                df_gs = conn.read(worksheet="Sheet1")
                conn.update(worksheet="Sheet1", data=pd.concat([df_gs, fila]))
            except: pass
            
            st.success(f"✔️ {t['exito']}")
            st.info(t['msg_tecnico'])
            st.balloons()
            st.session_state.lista_equipos = []