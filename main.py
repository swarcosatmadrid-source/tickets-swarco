import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# 1. CONFIGURACIÓN DE PÁGINA (Debe ser lo primero)
st.set_page_config(page_title="SWARCO SAT", layout="centered", page_icon="🚥")

# 2. IMPORTACIONES
sys.path.append(os.path.dirname(__file__))

try:
    from estilos import cargar_estilos
    from idiomas import traducir_interfaz
    from paises import PAISES_DATA
    from correo import enviar_email_outlook
    from streamlit_gsheets import GSheetsConnection
    from usuarios import gestionar_acceso
    
    cargar_estilos()
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de sistema: {e}")
    st.stop()

# --- 3. CONTROL DE ACCESO ---
if gestionar_acceso(conn):
    d_cli = st.session_state.datos_cliente
    t = traducir_interfaz("Castellano")

    # SIDEBAR
    with st.sidebar:
        st.image("logo.png", use_container_width=True)
        st.markdown(f"### 👤 {d_cli.get('Contacto', 'Usuario')}")
        st.caption(f"🏢 {d_cli.get('Empresa', 'Cliente Swarco')}")
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # HEADER CON ESTILO SWARCO
    st.markdown("""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #00549F; font-weight: 800; margin-bottom: 0;">SWARCO TRAFFIC SPAIN</h1>
            <h3 style="color: #F29400; font-weight: 400; margin-top: 0;">Portal de Reporte Técnico SAT</h3>
        </div>
    """, unsafe_allow_html=True)

    # --- SECCIÓN 1: DATOS DEL REPORTE ---
    st.markdown('<div class="section-header">📍 UBICACIÓN Y CONTACTO</div>', unsafe_allow_html=True)
    
    col_u1, col_u2 = st.columns(2)
    with col_u1:
        st.text_input("Empresa / Cliente", value=d_cli.get('Empresa', ''), disabled=True)
        proyecto_ub = st.text_input("Proyecto / Ubicación exacta", placeholder="Ej: Túnel de la Castellana, Madrid")
    
    with col_u2:
        p_nombres = list(PAISES_DATA.keys())
        pais_sel = st.selectbox("País", p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
        tel_raw = st.text_input("Móvil de contacto (Sin prefijo)")
        tel_final = f"{PAISES_DATA[pais_sel]} {tel_raw.strip()}"

    # --- SECCIÓN 2: DETALLES DEL EQUIPO ---
    st.markdown('<div class="section-header">⚙️ DETALLES DEL EQUIPO</div>', unsafe_allow_html=True)
    
    # El mensaje de la pegatina que me pediste
    st.warning("👉 **IMPORTANTE:** Localice la **pegatina plateada** en el chasis del equipo para obtener los datos correctos.")
    
    

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        ns_in = st.text_input("N.S. (Número de Serie)", placeholder="Ej: 2024-XXXX-XXXX")
    with col_e2:
        ref_in = st.text_input("Referencia (REF.)", placeholder="Ej: 102.405.001")

    # --- SECCIÓN 3: DESCRIPCIÓN DE LA AVERÍA ---
    st.markdown('<div class="section-header">🚨 DESCRIPCIÓN DE LA AVERÍA</div>', unsafe_allow_html=True)
    
    # Selector de Urgencia (Slider)
    st.write("**Prioridad del reporte:**")
    opciones_urg = ["Baja (Mantenimiento)", "Media (Fallo parcial)", "Alta (Afecta tráfico)", "Crítica (Sistema fuera de servicio)"]
    urg_val = st.select_slider("Deslice para indicar la urgencia", options=opciones_urg, value="Media (Fallo parcial)")
    
    st.write("**Descripción detallada del fallo:**")
    falla_in = st.text_area("¿Qué problema presenta el equipo?", 
                           placeholder="Por favor, sea lo más descriptivo posible. Indique si el equipo tiene alimentación, si hay luces encendidas, etc.",
                           height=150)

    # SUBIDA DE ARCHIVOS
    st.markdown('<div class="section-header">📸 EVIDENCIAS Y ADJUNTOS</div>', unsafe_allow_html=True)
    st.caption("Suba fotos de la pegatina, del equipo o vídeos del fallo (Máximo 200MB por archivo)")
    archivos = st.file_uploader("Arrastre aquí sus archivos", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4', 'pdf'])

    # LÓGICA DE MULTI-EQUIPO
    if 'lista_equipos' not in st.session_state:
        st.session_state.lista_equipos = []

    st.divider()

    # BOTONES DE ACCIÓN
    c_btn1, c_btn2 = st.columns(2)
    
    with c_btn1:
        if st.button("➕ AÑADIR OTRO EQUIPO A ESTE TICKET", use_container_width=True):
            if ns_in and falla_in:
                st.session_state.lista_equipos.append({
                    "N.S.": ns_in, 
                    "REF": ref_in, 
                    "Urgencia": urg_val, 
                    "Fallo": falla_in
                })
                st.success("✅ Equipo añadido a la lista. Los campos se han limpiado para el siguiente.")
                st.rerun()
            else:
                st.error("⚠️ Debe rellenar el N.S. y la Descripción antes de añadir.")

    with c_btn2:
        if st.button("🚀 GENERAR TICKET FINAL", type="primary", use_container_width=True):
            # Consolidar datos
            data_envio = st.session_state.lista_equipos.copy()
            if ns_in and falla_in:
                data_envio.append({"N.S.": ns_in, "REF": ref_in, "Urgencia": urg_val, "Fallo": falla_in})
            
            if data_envio and proyecto_ub:
                ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
                
                # ENVÍO DE EMAIL
                with st.spinner("Enviando reporte al servicio técnico..."):
                    exito = enviar_email_outlook(
                        d_cli['Empresa'], d_cli['Contacto'], proyecto_ub, 
                        data_envio, d_cli['Email'], ticket_id, tel_final
                    )
                
                if exito:
                    # GUARDADO EN EXCEL (Sheet1)
                    try:
                        resumen_ns = ", ".join([e['N.S.'] for e in data_envio])
                        nueva_fila = pd.DataFrame([{
                            "Ticket_ID": ticket_id, 
                            "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "Cliente": d_cli['Empresa'], 
                            "Contacto": d_cli['Contacto'],
                            "Ubicacion": proyecto_ub, 
                            "Equipos": resumen_ns, 
                            "Estado": "ABIERTO"
                        }])
                        
                        df_h = conn.read(worksheet="Sheet1", ttl=0)
                        df_final = pd.concat([df_h, nueva_fila], ignore_index=True)
                        conn.update(worksheet="Sheet1", data=df_final)
                        
                        st.success(f"🎊 Ticket **{ticket_id}** creado correctamente. Se ha enviado una copia a su email.")
                        st.balloons()
                        st.session_state.lista_equipos = []
                    except Exception as e:
                        st.error(f"Error al registrar en base de datos: {e}")
            else:
                st.error("⚠️ Falta información necesaria para generar el ticket.")

    # TABLA DE RESUMEN
    if st.session_state.lista_equipos:
        st.subheader("📋 Equipos incluidos en este reporte:")
        st.table(pd.DataFrame(st.session_state.lista_equipos))

    st.markdown("<p style='text-align:center; color:#999; margin-top:50px;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)


