import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SWARCO TRAFFIC SPAIN | Portal SAT", layout="centered", page_icon="🚥")

# 2. IMPORTACIONES
sys.path.append(os.path.dirname(__file__))

try:
    from estilos import cargar_estilos
    from idiomas import traducir_interfaz
    from paises import PAISES_DATA
    from correo import enviar_email_outlook
    from streamlit_gsheets import GSheetsConnection
    from usuarios import gestionar_acceso # El único cambio: importar el acceso
    
    cargar_estilos()
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error: {e}")
    st.stop()

# --- 3. CAPA DE SEGURIDAD (Login/Registro) ---
# Aquí es donde se valida el usuario antes de mostrar lo de ayer
if gestionar_acceso(conn):
    
    # Datos del usuario que acaba de entrar
    d_cli = st.session_state.datos_cliente
    t = traducir_interfaz("Castellano")

    # BARRA LATERAL (Como la tenías)
    with st.sidebar:
        st.image("logo.png", use_container_width=True)
        st.markdown(f"### 👤 {d_cli.get('Contacto', 'Usuario')}")
        st.caption(f"🏢 {d_cli.get('Empresa', 'Cliente')}")
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # TÍTULOS ORIGINALES
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #00549F; font-weight: 800;">SWARCO TRAFFIC SPAIN</h2>
            <h3 style="color: #666; border-bottom: 2px solid #F29400; display: inline-block;">Portal de Reporte Técnico SAT</h3>
        </div>
    """, unsafe_allow_html=True)

    # --- SECCIÓN 1: DATOS DEL REPORTE (Auto-rellenados) ---
    st.markdown('<div class="section-header">DATOS DEL REPORTE</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        # Aquí usamos los datos del login para rellenar
        st.text_input("Empresa", value=d_cli.get('Empresa', ''), disabled=True)
        proyecto_ub = st.text_input("Proyecto / Ubicación exacta", placeholder="Ej: Túnel de la Castellana")
    with c2:
        st.text_input("Email de contacto", value=d_cli.get('Email', ''), disabled=True)
        p_nombres = list(PAISES_DATA.keys())
        pais_sel = st.selectbox("País", p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
        tel_raw = st.text_input("Móvil de contacto")
        tel_final = f"{PAISES_DATA[pais_sel]}{''.join(filter(str.isdigit, tel_raw))}"

    # --- SECCIÓN 2: DETALLES DEL EQUIPO ---
    st.markdown('<div class="section-header">DETALLES DEL EQUIPO</div>', unsafe_allow_html=True)
    
    # TU NOTA DE LA PEGATINA DE AYER
    st.info("Localice la pegatina plateada en el chasis del equipo para obtener el N.S. y la Referencia.")
    
    [Image of an industrial equipment identification plate with serial number and reference]

    ce1, ce2 = st.columns(2)
    with ce1:
        ns_in = st.text_input("N.S. (Número de Serie)", key="ns_input")
    with ce2:
        ref_in = st.text_input("Referencia (REF.)", key="ref_input")

    # --- SECCIÓN 3: DESCRIPCIÓN DE LA AVERÍA ---
    st.markdown('<div class="section-header">DESCRIPCIÓN DE LA AVERÍA</div>', unsafe_allow_html=True)
    
    # TU SELECTOR DE PRIORIDAD DE AYER
    opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
    urg_val = st.select_slider("Prioridad del reporte", options=opciones_urg, value=t['u3'])
    
    falla_in = st.text_area("¿Qué problema presenta el equipo?", placeholder="Describa el fallo detalladamente...", key="desc_input")

    # SUBIDA DE ARCHIVOS
    archivos = st.file_uploader("Subir evidencias (Fotos/Vídeos)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'])

    if 'lista_equipos' not in st.session_state:
        st.session_state.lista_equipos = []

    # ACCIONES
    st.divider()
    col_add, col_gen = st.columns(2)
    
    with col_add:
        if st.button("➕ Añadir otro equipo a este ticket", use_container_width=True):
            if len(ns_in) >= 3 and len(falla_in) >= 10:
                st.session_state.lista_equipos.append({
                    "ID": str(uuid.uuid4())[:8], 
                    "N.S.": ns_in, 
                    "REF": ref_in, 
                    "Prioridad": urg_val, 
                    "Descripción": falla_in
                })
                st.success("Equipo añadido a la lista temporal.")
                st.rerun()
            else:
                st.error("⚠️ Complete el N.S. y la descripción.")

    with col_gen:
        if st.button("🚀 GENERAR TICKET FINAL", type="primary", use_container_width=True):
            data_final = st.session_state.lista_equipos.copy()
            if ns_in and falla_in:
                data_final.append({
                    "ID": str(uuid.uuid4())[:8], "N.S.": ns_in, "REF": ref_in, 
                    "Prioridad": urg_val, "Descripción": falla_in
                })
            
            if data_final and proyecto_ub:
                ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
                
                # ENVÍO EMAIL
                if enviar_email_outlook(d_cli['Empresa'], d_cli['Contacto'], proyecto_ub, data_final, d_cli['Email'], ticket_id, tel_final):
                    
                    # REGISTRO EN GOOGLE
                    try:
                        resumen_ns = " | ".join([e['N.S.'] for e in data_final])
                        nueva_fila = pd.DataFrame([{
                            "Ticket_ID": ticket_id, 
                            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Cliente": d_cli['Empresa'], "Usuario": d_cli['Usuario'],
                            "Ubicacion": proyecto_ub, "Equipos": resumen_ns, "Estado": "OPEN"
                        }])
                        
                        df_h = conn.read(worksheet="Sheet1", ttl=0)
                        df_updated = pd.concat([df_h, nueva_fila], ignore_index=True)
                        conn.update(worksheet="Sheet1", data=df_updated)
                        
                        st.success(f"Ticket {ticket_id} enviado correctamente.")
                        st.balloons()
                        st.session_state.lista_equipos = []
                    except Exception as e:
                        st.warning(f"Ticket enviado, pero error al registrar en Excel: {e}")
            else:
                st.error("⚠️ Falta ubicación o datos del equipo.")

    # TABLA DE RESUMEN (Como la tenías)
    if st.session_state.lista_equipos:
        st.subheader("📋 Equipos en el reporte actual")
        st.table(pd.DataFrame(st.session_state.lista_equipos).drop(columns=["ID"]))

    st.markdown("<p style='text-align:center; color:#999; margin-top:50px;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)



