import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚥")

# 2. SEGURIDAD DE RUTAS Y CONEXIÓN
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection
from usuarios import gestionar_acceso

cargar_estilos()
conn = st.connection("gsheets", type=GSheetsConnection)

# --- CONTROL DE ACCESO (LOGIN) ---
if gestionar_acceso(conn):
    d_cli = st.session_state.datos_cliente
    
    # --- HEADER ---
    col_logo, col_lang = st.columns([1.5, 1])
    with col_logo:
        st.image("logo.png", width=250)
    with col_lang:
        idioma_txt = st.text_input("Idioma / Language", value="Castellano")
        t = traducir_interfaz(idioma_txt)

    # --- SECCIÓN 1: CLIENTE ---
    st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.text_input(t['cliente'], value=d_cli.get('Empresa', ''), disabled=True)
        contacto = st.text_input(t['contacto'], value=d_cli.get('Contacto', ''))
        proyecto_ub = st.text_input(t['proyecto'], placeholder="Ej: Túnel de la Castellana")
    with c2:
        st.text_input(t['email'], value=d_cli.get('Email', ''), disabled=True)
        p_nombres = list(PAISES_DATA.keys())
        idx_def = p_nombres.index("Spain") if "Spain" in p_nombres else 0
        pais_sel = st.selectbox(t['pais'], p_nombres, index=idx_def)
        prefijo = PAISES_DATA[pais_sel]
        tel_raw = st.text_input(f"{t['tel']} (Prefijo: {prefijo})")
        tel_final = f"{prefijo}{''.join(filter(str.isdigit, tel_raw))}"

    # --- SECCIÓN 2: EQUIPO ---
    st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
    st.info(t['pegatina'])
    st.image("etiqueta.jpeg", use_container_width=True)

    if 'lista_equipos' not in st.session_state:
        st.session_state.lista_equipos = []

    ce1, ce2 = st.columns(2)
    with ce1:
        ns_in = st.text_input(t['ns_titulo'], key="ns_act")
    with ce2:
        ref_in = st.text_input("REF.", key="ref_act")

    # --- SECCIÓN 3: FALLO ---
    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
    urg_val = st.select_slider(t['urg_instruccion'], options=opciones_urg, value=t['u3'])
    falla_in = st.text_area(t['desc_instruccion'], placeholder=t['desc_placeholder'], key="desc_act")
    archivos = st.file_uploader(t['fotos'], accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'])

    st.divider()

    # --- LÓGICA DE BOTONES Y CUADRO DE EXPLICACIÓN ---
    col_add, col_gen = st.columns(2)
    
    with col_add:
        btn_add = st.button(f"➕ {t['btn_agregar']}", use_container_width=True)
        if btn_add:
            if ns_in and falla_in:
                st.session_state.lista_equipos.append({
                    "N.S.": ns_in, "REF": ref_in, "Prioridad": urg_val, "Descripción": falla_in
                })
                st.rerun()
            else:
                st.error("⚠️ Rellene N.S. y Descripción.")

    with col_gen:
        btn_generar = st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True)

    # --- AQUÍ ESTÁ EL CUADRO DE DIALOGO/EXPLICACIÓN QUE FALTABA ---
    if not st.session_state.lista_equipos:
        st.warning("📢 **Nota:** Primero debes rellenar los datos del equipo arriba y pulsar en '**Añadir otro equipo**' para que se guarde en la lista. Una vez que veas el equipo en la tabla inferior, podrás generar el ticket final.")
        
        if btn_generar:
            st.error("❌ La lista está vacía. Añade al menos un equipo antes de generar el ticket.")
    
    else:
        # Si ya hay equipos, mostramos la tabla de ayer
        st.markdown("### 📋 Equipos en este reporte:")
        st.table(pd.DataFrame(st.session_state.lista_equipos))
        
        if btn_generar:
            if proyecto_ub:
                ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
                try:
                    # Lógica de guardado en GSheets
                    resumen_ns = " | ".join([e['N.S.'] for e in st.session_state.lista_equipos])
                    nueva_fila = pd.DataFrame([{
                        "Ticket_ID": ticket_id, "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Cliente": d_cli['Empresa'], "Ubicacion": proyecto_ub, "Equipos": resumen_ns, "Estado": "OPEN"
                    }])
                    df_h = conn.read(worksheet="Sheet1", ttl=0)
                    conn.update(worksheet="Sheet1", data=pd.concat([df_h, nueva_fila], ignore_index=True))
                    
                    if enviar_email_outlook(d_cli['Empresa'], contacto, proyecto_ub, st.session_state.lista_equipos, d_cli['Email'], ticket_id, tel_final):
                        st.success(t['exito'])
                        st.balloons()
                        st.session_state.lista_equipos = []
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("⚠️ Por favor, indica la Ubicación/Proyecto.")

    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

