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

# --- INICIALIZACIÓN DE ESTADOS (Persistencia) ---
if 'ticket_exitoso' not in st.session_state:
    st.session_state.ticket_exitoso = False
if 'ultimo_ticket' not in st.session_state:
    st.session_state.ultimo_ticket = ""
if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# --- SEGURIDAD ---
if gestionar_acceso(conn):
    
    # --- 1. PANTALLA DE ÉXITO (Solo si el ticket se creó) ---
    if st.session_state.ticket_exitoso:
        st.markdown(f"""
            <div style="background-color: #f0fff0; padding: 40px; border-radius: 20px; border: 2px solid #2ecc71; text-align: center; margin-top: 50px;">
                <h1 style="color: #27ae60; font-family: sans-serif; font-weight: 800;">✅ ¡Ticket Registrado!</h1>
                <p style="font-size: 18px; color: #333;">Su reporte técnico ha sido enviado correctamente a nuestro centro de control.</p>
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

    # --- 2. ENCABEZADO Y SELECTOR DE IDIOMA ---
    d_cli = st.session_state.get('datos_cliente', {})
    
    col_logo, col_lang = st.columns([1.5, 1])
    with col_logo:
        st.image("logo.png", width=250)
    with col_lang:
        idioma_txt = st.selectbox("Seleccione Idioma / Select Language", ["Castellano", "English"], index=0)
        t = traducir_interfaz(idioma_txt)

    # Título Principal
    st.markdown(f"""
        <div style="text-align: center; margin-top: 10px; margin-bottom: 30px;">
            <h2 style="color: #00549F; font-family: sans-serif; margin-bottom: 0px; font-weight: 800;">SWARCO TRAFFIC SPAIN</h2>
            <h3 style="color: #666; font-family: sans-serif; margin-top: 5px; border-bottom: 2px solid #F29400; display: inline-block; padding-bottom: 10px;">
                {t.get('titulo_portal', 'Portal de Reporte Técnico SAT')}
            </h3>
        </div>
    """, unsafe_allow_html=True)

    # Estilos CSS del Slider
    st.markdown("""
        <style>
        .stSlider > div [data-baseweb="slider"] {
            background: linear-gradient(to right, #ADD8E6 0%, #F29400 100%) !important;
            height: 12px !important;
        }
        .stSlider > div [data-baseweb="slider"] > div:nth-child(2) { background-color: transparent !important; }
        [data-testid="stTickBarMin"], [data-testid="stTickBarMax"] { color: #00549F !important; font-weight: bold !important; }
        .section-header { background-color: #00549F; color: white; padding: 10px; border-radius: 5px; margin-top: 20px; font-weight: bold; }
        </style>
    """, unsafe_allow_html=True)

    # --- 3. SECCIÓN 1: CLIENTE ---
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

    # --- 4. SECCIÓN 2: EQUIPO ---
    st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
    st.info(t['pegatina'])
    st.image("etiqueta.jpeg", use_container_width=True)
    ce1, ce2 = st.columns(2)
    with ce1: ns_in = st.text_input(t['ns_titulo'], key="ns_input")
    with ce2: ref_in = st.text_input("REF.", key="ref_input")

    # --- 5. SECCIÓN 3: DESCRIPCIÓN Y FOTOS ---
    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
    urg_val = st.select_slider(t['urg_instruccion'], options=opciones_urg, value=t['u3'])
    falla_in = st.text_area(t['desc_instruccion'], placeholder=t['desc_placeholder'], key="desc_input")
    
    # CARGADOR DE ARCHIVOS (IMÁGENES/VÍDEOS)
    archivos = st.file_uploader(t['fotos'], accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'])

    # --- 6. REGISTRO Y TABLA ---
    st.markdown("---")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("➕ Registrar Dispositivo", use_container_width=True):
            if len(ns_in) >= 3 and len(falla_in) >= 10:
                st.session_state.lista_equipos.append({
                    "N.S.": str(ns_in), "REF": str(ref_in), 
                    "Prioridad": str(urg_val), "Descripción": str(falla_in)
                })
                st.rerun()
            else:
                st.warning("⚠️ Complete N.S. y Descripción antes de registrar el equipo.")

    if st.session_state.lista_equipos:
        st.markdown("### 📋 Equipos registrados en esta solicitud")
        st.table(pd.DataFrame(st.session_state.lista_equipos))
        
        with col_b2:
            if st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True):
                # --- VALIDACIONES FINALES ---
                if not proyecto_ub:
                    st.error("⚠️ Error: Indique la Ubicación o Proyecto del reporte.")
                elif not tel_limpio or len(tel_limpio) < 7:
                    st.error("⚠️ Error: Ingrese un número de teléfono de contacto válido.")
                else:
                    ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
                    ahora = datetime.now()
                    try:
                        res_ns = ", ".join([str(e.get('N.S.', '')) for e in st.session_state.lista_equipos])
                        res_ref = ", ".join([str(e.get('REF', '')) for e in st.session_state.lista_equipos])
                        
                        payload = {
                            "Ticket_ID": str(ticket_id),
                            "Fecha": ahora.strftime("%d/%m/%Y"),
                            "Hora": ahora.strftime("%H:%M"),
                            "Cliente": str(empresa),
                            "Ubicacion": str(proyecto_ub),
                            "NS": res_ns, "REF": res_ref,
                            "Urgencia_Max": str(st.session_state.lista_equipos[-1].get('Prioridad', '')),
                            "Estado": "OPEN"
                        }
                        
                        resp = requests.post(URL_SCRIPT, json=payload)
                        
                        if "Éxito_Ticket" in resp.text:
                            # ENVÍO DE CORREO
                            enviar_email_outlook(empresa, contacto, proyecto_ub, st.session_state.lista_equipos, email_usr, ticket_id, tel_final)
                            st.session_state.ultimo_ticket = ticket_id
                            st.session_state.ticket_exitoso = True
                            st.rerun()
                        else:
                            st.error(f"❌ Error en base de datos: {resp.text}")
                    except Exception as e:
                        st.error(f"❌ Error crítico: {e}")

    # --- SALIR ---
    st.markdown("---")
    if st.button(f"🚪 {t['btn_salir']}", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

    st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2026 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)

