import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# 1. CONFIGURACIÓN DE RUTA Y PÁGINA (De primero para evitar errores)
sys.path.append(os.path.dirname(__file__))
st.set_page_config(page_title="SWARCO TRAFFIC SPAIN | Portal SAT", layout="centered", page_icon="🚥")

# 2. INTENTO DE CARGA DE MÓDULOS PROPIOS
try:
    from estilos import cargar_estilos
    from idiomas import traducir_interfaz
    from paises import PAISES_DATA
    from correo import enviar_email_outlook
    from streamlit_gsheets import GSheetsConnection
    from usuarios import gestionar_acceso  # <--- SE ASEGURA QUE SEA 'usuarios.py'
    
    cargar_estilos()
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"❌ Error al cargar archivos del sistema: {e}")
    st.stop()

# --- 3. CAPA DE SEGURIDAD (Login/Registro) ---
if gestionar_acceso(conn):
    
    # Si entra aquí, el usuario ya está validado
    d_cli = st.session_state.datos_cliente
    t = traducir_interfaz("Castellano")

    # BARRA LATERAL (SIDEBAR)
    with st.sidebar:
        st.image("logo.png", use_container_width=True)
        st.markdown(f"### 👤 {d_cli.get('Contacto', 'Usuario')}")
        st.caption(f"🏢 {d_cli.get('Empresa', 'Swarco Client')}")
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # TÍTULO PRINCIPAL INSTITUCIONAL
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #00549F; font-weight: 800;">SWARCO TRAFFIC SPAIN</h2>
            <h3 style="color: #666; border-bottom: 2px solid #F29400; display: inline-block;">Portal de Reporte Técnico SAT</h3>
        </div>
    """, unsafe_allow_html=True)

    # --- SECCIÓN 1: DATOS DEL REPORTE ---
    st.markdown('<div class="section-header">DATOS DEL REPORTE</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Empresa", value=d_cli.get('Empresa', ''), disabled=True)
        proyecto_ub = st.text_input("Proyecto / Ubicación exacta")
    with c2:
        st.text_input("Email", value=d_cli.get('Email', ''), disabled=True)
        p_nombres = list(PAISES_DATA.keys())
        pais_sel = st.selectbox("País del proyecto", p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
        tel_raw = st.text_input("Móvil de contacto local")
        tel_final = f"{PAISES_DATA[pais_sel]}{''.join(filter(str.isdigit, tel_raw))}"

    # --- SECCIÓN 2: DATOS DEL EQUIPO ---
    st.markdown('<div class="section-header">DETALLES DEL EQUIPO</div>', unsafe_allow_html=True)
    st.info("Utilice los datos de la pegatina plateada del equipo.")
    ce1, ce2 = st.columns(2)
    with ce1:
        ns_in = st.text_input("N.S. (Número de Serie)", key="ns_input")
    with ce2:
        ref_in = st.text_input("Referencia (REF.)", key="ref_input")

    # --- SECCIÓN 3: PROBLEMA ---
    st.markdown('<div class="section-header">DESCRIPCIÓN DE LA AVERÍA</div>', unsafe_allow_html=True)
    opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
    urg_val = st.select_slider("Prioridad / Urgencia", options=opciones_urg, value=t['u3'])
    falla_in = st.text_area("Describa el problema:", placeholder="¿Qué falla exactamente?", key="desc_input")

    # ARCHIVOS
    st.file_uploader("Adjuntar fotos o vídeos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'])

    if 'lista_equipos' not in st.session_state:
        st.session_state.lista_equipos = []

    # ACCIONES FINALES
    st.divider()
    col_add, col_gen = st.columns(2)
    
    with col_add:
        if st.button("➕ Añadir otro equipo", use_container_width=True):
            if len(ns_in) >= 3 and len(falla_in) >= 10:
                st.session_state.lista_equipos.append({
                    "ID": str(uuid.uuid4())[:8], "N.S.": ns_in, "REF": ref_in, "Prioridad": urg_val, "Descripción": falla_in
                })
                st.rerun()
            else:
                st.error("⚠️ Ingrese N.S. y descripción para añadir.")

    with col_gen:
        if st.button("🚀 ENVIAR REPORTE", type="primary", use_container_width=True):
            data_final = st.session_state.lista_equipos.copy()
            if not data_final and ns_in and falla_in:
                data_final.append({"ID": str(uuid.uuid4())[:8], "N.S.": ns_in, "REF": ref_in, "Prioridad": urg_val, "Descripción": falla_in})
            
            if data_final and proyecto_ub:
                ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
                
                # ENVÍO EMAIL
                if enviar_email_outlook(d_cli['Empresa'], d_cli['Contacto'], proyecto_ub, data_final, d_cli['Email'], ticket_id, tel_final):
                    # REGISTRO EN GOOGLE SHEETS
                    try:
                        res_ns = " | ".join([e['N.S.'] for e in data_final])
                        nueva_fila = pd.DataFrame([{
                            "Ticket_ID": ticket_id, "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Cliente": d_cli['Empresa'], "Usuario": d_cli['Usuario'],
                            "Ubicacion": proyecto_ub, "Equipos": res_ns, "Estado": "OPEN"
                        }])
                        df_h = conn.read(worksheet="Sheet1", ttl=0)
                        conn.update(worksheet="Sheet1", data=pd.concat([df_h, nueva_fila], ignore_index=True))
                        
                        st.success(f"Ticket {ticket_id} registrado exitosamente.")
                        st.balloons()
                        st.session_state.lista_equipos = []
                        st.rerun()
                    except Exception as e:
                        st.warning(f"Email enviado, pero error al anotar en Excel: {e}")
            else:
                st.error("⚠️ Faltan datos (Ubicación o Equipo).")

    # TABLA RESUMEN
    if st.session_state.lista_equipos:
        st.subheader("📋 Resumen del reporte actual")
        st.table(pd.DataFrame(st.session_state.lista_equipos).drop(columns=["ID"]))

    st.markdown("<p style='text-align:center; color:#999; margin-top:50px;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)

