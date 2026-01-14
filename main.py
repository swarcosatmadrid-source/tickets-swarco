import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys
import requests # Necesario para la conexión con el Script

# 1. CONFIGURACIÓN Y RUTAS
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection
from usuarios import gestionar_acceso

# URL DE TU GOOGLE APPS SCRIPT (Ya integrada)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbyDpHS4nU16O7YyvABvmbFYHTLv2e2J8vrpSD-iCmamjmS4Az6p9iZNUmVEwzMVyzx9/exec"

st.set_page_config(page_title="SWARCO SAT | Portal Técnico", layout="centered", page_icon="🚥")
cargar_estilos()
conn = st.connection("gsheets", type=GSheetsConnection)

if gestionar_acceso(conn):
    d_cli = st.session_state.get('datos_cliente', {})
    
    # --- HEADER ---
    col_logo, col_lang = st.columns([1.5, 1])
    with col_logo:
        st.image("logo.png", width=250)
    with col_lang:
        idioma_txt = st.text_input("Idioma / Language", value="Castellano")
        t = traducir_interfaz(idioma_txt)

    # --- TÍTULO PRINCIPAL ---
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

    # --- BLOQUE CSS SLIDER ---
    st.markdown("""
        <style>
        .stSlider > div [data-baseweb="slider"] {
            background: linear-gradient(to right, #ADD8E6 0%, #F29400 100%) !important;
            height: 12px !important;
        }
        .stSlider > div [data-baseweb="slider"] > div:nth-child(2) {
            background-color: transparent !important;
        }
        [data-testid="stTickBarMin"], [data-testid="stTickBarMax"] {
            color: #00549F !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- CATEGORÍA 1: CLIENTE ---
    st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        empresa = st.text_input(t['cliente'], value=d_cli.get('Empresa', ''), disabled=True)
        contacto = st.text_input(t['contacto'], value=d_cli.get('Contacto', ''))
        proyecto_ub = st.text_input(t['proyecto'], placeholder="Ej: Túnel de la Castellana")
    with c2:
        email_usr = st.text_input(t['email'], value=d_cli.get('Email', ''), disabled=True)
        p_nombres = list(PAISES_DATA.keys())
        idx_def = p_nombres.index("Spain") if "Spain" in p_nombres else 0
        pais_sel = st.selectbox(t['pais'], p_nombres, index=idx_def)
        prefijo = PAISES_DATA[pais_sel]
        tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})")
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

    # --- CATEGORÍA 3: PROBLEMA ---
    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
    urg_val = st.select_slider(t['urg_instruccion'], options=opciones_urg, value=t['u3'])
    
    colores_p = {t['u1']:"#ADD8E6", t['u2']:"#90C3D4", t['u3']:"#7AB1C5", t['u4']:"#C2A350", t['u5']:"#D69B28", t['u6']:"#F29400"}
    st.markdown(f"<style>div[role='slider'] {{ background-color: {colores_p.get(urg_val, '#7AB1C5')} !important; border: 2px solid white !important; }}</style>", unsafe_allow_html=True)

    falla_in = st.text_area(t['desc_instruccion'], placeholder=t['desc_placeholder'], key="desc_input")
    archivos = st.file_uploader(t['fotos'], accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'])

    if 'lista_equipos' not in st.session_state:
        st.session_state.lista_equipos = []

    # --- LÓGICA DINÁMICA DE BOTONES ---
    texto_btn_add = "➕ Registrar Dispositivo" if not st.session_state.lista_equipos else f"➕ {t['btn_agregar']}"

    # --- NOTA EXPLICATIVA ---
    st.markdown("---")
    st.markdown(f"""
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 5px solid #00549F;">
            <p style="color: #00549F; font-weight: bold; margin-bottom: 5px;">💡 ¿Cómo procesar su solicitud?</p>
            <p style="font-size: 14px; color: #333;">
                1. Complete los datos técnicos y pulse <b>"{texto_btn_add}"</b> para incluirlo en el reporte.<br>
                2. Verifique en la <b>tabla inferior</b> que la información registrada es correcta.<br>
                3. Una vez validado, pulse <b>"Generar Ticket Final"</b> para dar curso a su reporte.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button(texto_btn_add, use_container_width=True):
            if len(ns_in) >= 3 and len(falla_in) >= 10:
                st.session_state.lista_equipos.append({"N.S.": ns_in, "REF": ref_in, "Prioridad": urg_val, "Descripción": falla_in})
                st.rerun()
            else:
                st.warning("⚠️ Complete N.S. y Descripción antes de registrar.")

    # --- TABLA Y ENVÍO FINAL ---
    if st.session_state.lista_equipos:
        st.markdown("### 📋 Equipos registrados en esta solicitud")
        st.table(pd.DataFrame(st.session_state.lista_equipos))
        
        with col_btn2:
            if st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True):
                if proyecto_ub:
                    ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
                    try:
                        # Resumen técnico
                        resumen_ns = " | ".join([f"SN:{e['N.S.']} (Ref:{e['REF']})" for e in st.session_state.lista_equipos])
                        
                        # Datos para el Script de Google
                        payload = {
                            "Ticket_ID": str(ticket_id),
                            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Cliente": str(empresa),
                            "Ubicacion": str(proyecto_ub),
                            "Equipos": str(resumen_ns),
                            "Urgencia_Max": str(st.session_state.lista_equipos[-1]['Prioridad']),
                            "Estado": "OPEN"
                        }
                        
                        # Envío al Script
                        resp = requests.post(URL_SCRIPT, json=payload)
                        
                        if "Éxito_Ticket" in resp.text:
                            if enviar_email_outlook(empresa, contacto, proyecto_ub, st.session_state.lista_equipos, email_usr, ticket_id, tel_final):
                                st.success("✅ ¡Reporte enviado y registrado exitosamente!")
                                st.balloons()
                                st.session_state.lista_equipos = []
                                st.rerun()
                        else:
                            st.error(f"Error en base de datos: {resp.text}")
                    except Exception as e:
                        st.error(f"Error de conexión: {e}")
                else:
                    st.error("⚠️ Indique la ubicación del proyecto.")
        
        if st.button("🗑️ Vaciar Lista"):
            st.session_state.lista_equipos = []
            st.rerun()
    else:
        with col_btn2:
            st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True, disabled=True)

    st.markdown("---")
    if st.button(f"🚪 {t['btn_salir']}", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

    st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2026 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)

