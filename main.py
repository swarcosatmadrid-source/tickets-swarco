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
from usuarios import gestionar_acceso

# Configuración de pestaña del navegador
st.set_page_config(page_title="SWARCO SAT | Portal Técnico", layout="centered", page_icon="🚥")
cargar_estilos()

# Conexión para el Login y Registro en Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CAPA DE SEGURIDAD (LOGIN) ---
if gestionar_acceso(conn):
    
    d_cli = st.session_state.get('datos_cliente', {})
    
    # --- HEADER: LOGO Y TRADUCTOR ---
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

    # --- BLOQUE CSS (DISEÑO DEL SLIDER) ---
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
        tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})", placeholder="Solo números")
        tel_limpio = "".join(filter(str.isdigit, tel_raw))
        tel_final = f"{prefijo}{tel_limpio}"

    # --- CATEGORÍA 2: EQUIPO ---
    st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
    st.info(t['pegatina'])
    st.image("etiqueta.jpeg", use_container_width=True)

    ce1, ce2 = st.columns(2)
    with ce1:
        ns_in = st.text_input(t['ns_titulo'], key="ns_input")
    with ce2:
        ref_in = st.text_input("REF.", key="ref_input")

    # --- CATEGORÍA 3: PROBLEMA Y URGENCIA ---
    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**{t['urg_titulo']}**")

    opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
    urg_val = st.select_slider(t['urg_instruccion'], options=opciones_urg, value=t['u3'])

    colores_p = {t['u1']:"#ADD8E6", t['u2']:"#90C3D4", t['u3']:"#7AB1C5", t['u4']:"#C2A350", t['u5']:"#D69B28", t['u6']:"#F29400"}
    st.markdown(f"<style>div[role='slider'] {{ background-color: {colores_p.get(urg_val, '#7AB1C5')} !important; border: 2px solid white !important; }}</style>", unsafe_allow_html=True)

    falla_in = st.text_area(t['desc_instruccion'], placeholder=t['desc_placeholder'], key="desc_input")

    # MULTIMEDIA
    st.markdown(f"**{t['fotos']}**")
    archivos = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

    if 'lista_equipos' not in st.session_state:
        st.session_state.lista_equipos = []

    # --- LÓGICA DINÁMICA DE BOTONES ---
    if not st.session_state.lista_equipos:
        texto_boton_agregar = "➕ Registrar Dispositivo"
    else:
        texto_boton_agregar = f"➕ {t['btn_agregar']}"

    # --- NOTA EXPLICATIVA ---
    st.markdown("---")
    st.markdown(f"""
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 10px; border-left: 5px solid #00549F;">
            <p style="color: #00549F; font-weight: bold; margin-bottom: 5px;">💡 {t.get('instruccion_final', '¿Cómo procesar su solicitud?')}</p>
            <p style="font-size: 14px; color: #333;">
                1. Complete los datos técnicos y pulse <b>"{texto_boton_agregar}"</b> para incluirlo en el reporte.<br>
                2. Verifique en la <b>tabla inferior</b> que la información registrada es correcta.<br>
                3. Una vez validado, pulse <b>"Generar Ticket Final"</b> para dar curso a su reporte.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # BOTONES DE ACCIÓN
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button(texto_boton_agregar, use_container_width=True):
            if len(ns_in) >= 3 and len(falla_in) >= 10:
                st.session_state.lista_equipos.append({
                    "N.S.": ns_in, 
                    "REF": ref_in, 
                    "Prioridad": urg_val, 
                    "Descripción": falla_in
                })
                st.rerun()
            else:
                st.warning("⚠️ Por favor, complete los datos del equipo antes de registrarlo.")

    # TABLA DE RESUMEN Y ENVÍO (Solo si hay equipos)
    if st.session_state.lista_equipos:
        st.markdown("### 📋 Equipos registrados en esta solicitud")
        st.table(pd.DataFrame(st.session_state.lista_equipos))
        
        with col_btn2:
            if st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True):
                if proyecto_ub:
                    ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
                    try:
                        # Registro en GSheets
                        resumen_ns = " | ".join([e['N.S.'] for e in st.session_state.lista_equipos])
                        nueva_fila = pd.DataFrame([{
                            "Ticket_ID": ticket_id, 
                            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Cliente": empresa, "Ubicacion": proyecto_ub, 
                            "Equipos": resumen_ns, "Estado": "OPEN"
                        }])
                        df_h = conn.read(worksheet="Sheet1", ttl=0)
                        conn.update(worksheet="Sheet1", data=pd.concat([df_h, nueva_fila], ignore_index=True))
                        
                        if enviar_email_outlook(empresa, contacto, proyecto_ub, st.session_state.lista_equipos, email_usr, ticket_id, tel_final):
                            st.success("✅ ¡Reporte enviado correctamente! Se ha generado su ticket.")
                            st.balloons()
                            st.session_state.lista_equipos = []
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error al registrar: {e}")
                else:
                    st.error("⚠️ Por favor, indique la Ubicación/Proyecto.")
        
        if st.button("🗑️ Vaciar Lista / Reiniciar"):
            st.session_state.lista_equipos = []
            st.rerun()
    else:
        with col_btn2:
            st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True, disabled=True, help="Añada un equipo primero")

    # BOTÓN SALIR
    st.markdown("---")
    if st.button(f"🚪 {t['btn_salir']}", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

    st.markdown("<p style='text-align:center; font-size:12px; color:#999;'>© 2026 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)
