import streamlit as st
import os
import sys
import uuid
import pandas as pd
from datetime import datetime

# Importaciones de tus archivos (Verifica que se llamen así)
from correo import enviar_email_outlook
from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from streamlit_gsheets import GSheetsConnection

# 1. Configuración de página y estilos originales
st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚥")
cargar_estilos()
# Conexión silenciosa para el histórico
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    pass

# --- ENCABEZADO ORIGINAL (SEMÁFORO Y LOGO) ---
col_logo, col_tit, col_sem = st.columns([1, 4, 1])
with col_logo:
    st.image("logo.png", width=80)
with col_tit:
    idioma_sel = st.selectbox("", ["Español", "English 🇬🇧", "Deutsch 🇩🇪", "Français 🇫🇷", "Català 🚩", "Euskara 🟢"], label_visibility="collapsed")
    t = traducir_interfaz(idioma_sel)
    st.markdown(f"<h1 style='text-align: center; color: #00549F; margin-top: -20px;'>{t['titulo']}</h1>", unsafe_allow_html=True)
with col_sem:
    st.markdown("<div style='font-size: 40px; text-align: center;'>🚥</div>", unsafe_allow_html=True)

st.markdown(f"<p style='text-align: center; font-weight: bold; color: #009FE3;'>{t['sub']}</p>", unsafe_allow_html=True)

# --- CATEGORÍA 1: IDENTIFICACIÓN DEL CLIENTE ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
    proyecto = st.text_input(t['proyecto'])
with c2:
    email_usr = st.text_input(t['email'])
    
    # Selector de País y Prefijo (Tu lógica original)
    pais_nombres = list(PAISES_DATA.keys())
    idx_defecto = pais_nombres.index("Spain") if "Spain" in pais_nombres else 0
    pais_sel = st.selectbox(t['pais'], pais_nombres, index=idx_defecto)
    prefijo = PAISES_DATA[pais_sel]
    
    tel_raw = st.text_input(f"{t['tel']} ({prefijo})")
    tel_usr = f"{prefijo} {tel_raw}"

# --- CATEGORÍA 2: IDENTIFICACIÓN DEL EQUIPO ---
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.write(f"ℹ️ {t['pegatina']}")
st.image("etiqueta.jpeg", use_container_width=True)

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# Bloque para añadir equipos
with st.container():
    ce1, ce2, ce3 = st.columns([2, 2, 1])
    ns_input = ce1.text_input(t['ns_titulo'])
    ref_input = ce2.text_input("REF / PN")
    urgencia_input = ce3.selectbox(t['prioridad'], ["Normal", "Alta", "Crítica"])
    
    st.markdown(f"**{t['desc']}**")
    falla_input = st.text_area("", key="falla_area", label_visibility="collapsed")
    
    if st.button("➕ AGREGAR EQUIPO"):
        if ns_input and falla_input:
            st.session_state.lista_equipos.append({
                "ns": ns_input, 
                "ref": ref_input, 
                "urgencia": urgencia_input, 
                "desc": falla_input
            })
            st.rerun()
        else:
            st.warning("El N.S y la descripción son obligatorios.")

if st.session_state.lista_equipos:
    st.markdown("---")
    st.table(pd.DataFrame(st.session_state.lista_equipos))
    if st.button("🗑️ Limpiar Lista"):
        st.session_state.lista_equipos = []
        st.rerun()

# --- CATEGORÍA 3: ENVÍO ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
if st.button(t['btn'], type="primary", use_container_width=True):
    if not empresa or not email_usr or not st.session_state.lista_equipos:
        st.error("Por favor, rellene los campos obligatorios y agregue al menos un equipo.")
    else:
        ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        
        # 1. Envío de Email (Gmail)
        if enviar_email_outlook(empresa, contacto, proyecto, st.session_state.lista_equipos, email_usr, ticket_id, tel_usr):
            
            # 2. Guardado en Google Sheets (Híbrido)
            try:
                nueva_fila = pd.DataFrame([{
                    "ID": ticket_id,
                    "Fecha": datetime.now().strftime("%d/%m/%Y"),
                    "Empresa": empresa,
                    "Contacto": contacto,
                    "Equipos": len(st.session_state.lista_equipos),
                    "Estado": "Pendiente"
                }])
                df_gs = conn.read(worksheet="Sheet1")
                df_final = pd.concat([df_gs, nueva_fila], ignore_index=True)
                conn.update(worksheet="Sheet1", data=df_final)
            except:
                pass
            
            st.success(f"✔️ {t['exito']}")
            st.info(t['msg_tecnico'])
            st.balloons()
            st.session_state.lista_equipos = []