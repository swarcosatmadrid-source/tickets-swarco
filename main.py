import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# 1. SEGURIDAD DE RUTAS Y CONFIGURACIÓN
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection

# Configuración de pestaña del navegador
st.set_page_config(page_title="SWARCO SAT | Portal Técnico", layout="centered", page_icon="🚥")
cargar_estilos()

# Conexión a Google Sheets (Para el respaldo de datos Etapa 1)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- HEADER: LOGO Y TRADUCTOR ---
col_logo, col_lang = st.columns([1.5, 1])
with col_logo:
    st.image("logo.png", width=250)
with col_lang:
    idioma_txt = st.text_input("Idioma / Language", value="Castellano")
    t = traducir_interfaz(idioma_txt)

# --- TÍTULO INSTITUCIONAL ---
st.markdown(f"""
    <div style="text-align: center; margin-top: 10px; margin-bottom: 30px;">
        <h2 style="color: #00549F; font-family: sans-serif; margin-bottom: 0px; font-weight: 800;">
            SWARCO TRAFFIC SPAIN
        </h2>
        <h3 style="color: #666; font-family: sans-serif; margin-top: 5px; border-bottom: 2px solid #F29400; display: inline-block; padding-bottom: 10px;">
            {t.get('titulo_portal', 'Portal de Reporte Técnico SAT')}
        </h3>
    </div>
""", unsafe_allow_html=True)

# --- CATEGORÍA 1: CLIENTE ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'], key="empresa_input")
    contacto = st.text_input(t['contacto'])
    proyecto_ub = st.text_input(t['proyecto'])
with c2:
    email_usr = st.text_input(t['email'])
    p_nombres = list(PAISES_DATA.keys())
    idx_def = p_nombres.index("Spain") if "Spain" in p_nombres else 0
    pais_sel = st.selectbox(t['pais'], p_nombres, index=idx_def)
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})", placeholder="Solo números")
    tel_final = f"{prefijo}{''.join(filter(str.isdigit, tel_raw))}"

# --- CATEGORÍA 2: EQUIPO ---
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(t['pegatina'])
st.image("etiqueta.jpeg", use_container_width=True)

ce1, ce2 = st.columns(2)
with ce1:
    ns_in = st.text_input(t['ns_titulo'], key="ns_input")
with ce2:
    ref_in = st.text_input("REF.", key="ref_input")

# --- CATEGORÍA 3: PROBLEMA Y PRIORIDAD ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
urg_val = st.select_slider(t['urg_instruccion'], options=opciones_urg, value=t['u3'])
falla_in = st.text_area(t['desc_instruccion'], placeholder=t['desc_placeholder'], key="desc_input")

# MULTIMEDIA
st.markdown(f"**{t['fotos']}**")
archivos = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# --- GUÍA Y ACCIONES ---
st.markdown("---")
st.info(f"💡 {t.get('instruccion_final', 'Use + para varios equipos o Generar Ticket para enviar.')}")

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button(f"➕ {t['btn_agregar']}", use_container_width=True):
        if len(ns_in) >= 3 and len(falla_in) >= 10:
            st.session_state.lista_equipos.append({
                "ID": str(uuid.uuid4())[:8],
                "N.S.": ns_in, 
                "REF": ref_in, 
                "Prioridad": urg_val, 
                "Descripción": falla_in
            })
            st.rerun()

with col_btn2:
    if st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True):
        data_final = st.session_state.lista_equipos.copy()
        if not data_final and ns_in and falla_in:
            data_final.append({"ID": str(uuid.uuid4())[:8], "N.S.": ns_in, "REF": ref_in, "Prioridad": urg_val, "Descripción": falla_in})
        
        if empresa and email_usr and data_final:
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            
            # ENVÍO Y REGISTRO
            if enviar_email_outlook(empresa, contacto, proyecto_ub, data_final, email_usr, ticket_id, tel_final):
                try:
                    # Preparar data para Google Sheets (Backup Etapa 1)
                    resumen_equipos = " | ".join([f"NS:{e['N.S.']}" for e in data_final])
                    nueva_fila = pd.DataFrame([{
                        "Ticket": ticket_id,
                        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Cliente": empresa,
                        "Equipos": resumen_equipos,
                        "Estado": "OPEN"
                    }])
                    df_historico = conn.read(worksheet="Sheet1")
                    df_updated = pd.concat([df_historico, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=df_updated)
                    
                    st.success(t['exito'])
                    st.balloons()
                    st.session_state.lista_equipos = []
                except Exception as e:
                    st.warning(f"Ticket enviado. Error en registro DB: {e}")
        else:
            st.error("⚠️ Datos incompletos.")

# TABLA DE RESUMEN
if st.session_state.lista_equipos:
    st.subheader("📋 Equipos en este reporte")
    st.table(pd.DataFrame(st.session_state.lista_equipos).drop(columns=["ID"]))

st.markdown("---")
if st.button(f"🚪 {t['btn_salir']}", use_container_width=True):
    st.warning(t['salir_aviso'])

st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2024 SWARCO TRAFFIC SPAIN</p>", unsafe_allow_html=True)

