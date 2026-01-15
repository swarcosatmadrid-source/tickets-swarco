import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys
import requests 

# 1. CONFIGURACIÓN Y RUTAS
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection
from usuarios import gestionar_acceso

# URL DE TU GOOGLE APPS SCRIPT
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyDpHS4nU16O7YyvABvmbFYHTLv2e2J8vrpSD-iCmamjmS4Az6p9iZNUmVEwzMVyzx9/exec"

st.set_page_config(page_title="SWARCO SAT | Portal Técnico", layout="centered", page_icon="🚥")
cargar_estilos()
conn = st.connection("gsheets", type=GSheetsConnection)

# --- ESTADOS DE SESIÓN ---
if 'ticket_exitoso' not in st.session_state:
    st.session_state.ticket_exitoso = False
if 'ultimo_ticket' not in st.session_state:
    st.session_state.ultimo_ticket = ""
if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# --- SEGURIDAD ---
if gestionar_acceso(conn):
    
    # --- PANTALLA DE ÉXITO (Lo que ve el cliente al terminar) ---
    if st.session_state.ticket_exitoso:
        st.markdown(f"""
            <div style="background-color: #f0fff0; padding: 40px; border-radius: 20px; border: 2px solid #2ecc71; text-align: center; margin-top: 50px;">
                <h1 style="color: #27ae60;">✅ ¡Ticket Registrado con Éxito!</h1>
                <p style="font-size: 18px; color: #333;">Su reporte técnico ha sido enviado correctamente.</p>
                <div style="background-color: white; padding: 25px; border-radius: 15px; margin: 30px 0; border: 1px solid #ddd; box-shadow: 0px 4px 10px rgba(0,0,0,0.05);">
                    <p style="color: #666; margin-bottom: 5px; text-transform: uppercase; font-weight: bold; font-size: 12px;">Referencia de Seguimiento:</p>
                    <h2 style="color: #00549F; margin: 0; font-family: monospace; font-size: 32px;">{st.session_state.ultimo_ticket}</h2>
                </div>
                <p style="font-size: 15px; color: #555;">Un técnico de SWARCO procesará su solicitud a la brevedad.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            if st.button("➕ Registrar otro reporte", use_container_width=True):
                st.session_state.ticket_exitoso = False
                st.session_state.lista_equipos = []
                st.rerun()
        with col_ex2:
            if st.button("🚪 Cerrar Sesión", type="primary", use_container_width=True):
                st.session_state.autenticado = False
                st.session_state.ticket_exitoso = False
                st.rerun()
        st.stop()

    # --- FORMULARIO PRINCIPAL ---
    d_cli = st.session_state.get('datos_cliente', {})
    
    col_logo, col_lang = st.columns([1.5, 1])
    with col_logo: st.image("logo.png", width=250)
    with col_lang:
        idioma_txt = st.selectbox("Idioma / Language", ["Castellano", "English"])
        t = traducir_interfaz(idioma_txt)

    # 1. IDENTIFICACIÓN CLIENTE
    st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        empresa = st.text_input(t['cliente'], value=d_cli.get('Empresa', ''), disabled=True)
        contacto = st.text_input(t['contacto'], value=d_cli.get('Contacto', ''))
        proyecto_ub = st.text_input(t['proyecto'], placeholder="Ej: Túnel de la Castellana")
    with c2:
        email_usr = st.text_input(t['email'], value=d_cli.get('Email', ''), disabled=True)
        p_nombres = list(PAISES_DATA.keys())
        pais_sel = st.selectbox(t['pais'], p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
        prefijo = PAISES_DATA[pais_sel]
        tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})")
        tel_limpio = ''.join(filter(str.isdigit, tel_raw))
        tel_final = f"{prefijo}{tel_limpio}"

    # 2. IDENTIFICACIÓN EQUIPO
    st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
    st.info(t['pegatina'])
    st.image("etiqueta.jpeg", use_container_width=True)
    ce1, ce2 = st.columns(2)
    with ce1: ns_in = st.text_input(t['ns_titulo'], key="ns_input")
    with ce2: ref_in = st.text_input("REF.", key="ref_input")

    # 3. PROBLEMA Y FOTOS
    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    urg_val = st.select_slider(t['urg_instruccion'], options=[t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']], value=t['u3'])
    falla_in = st.text_area(t['desc_instruccion'], placeholder=t['desc_placeholder'], key="desc_input")
    
    # --- AQUÍ ESTÁ EL CARGADOR DE ARCHIVOS ---
    archivos = st.file_uploader(t['fotos'], accept_multiple_files=True, type=['png', 'jpg', 'jpeg
