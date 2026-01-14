import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SWARCO SAT", layout="centered", page_icon="🚥")
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
    st.error(f"Error cargando módulos: {e}")
    st.stop()

# --- 2. CONTROL DE ACCESO (LOGIN) ---
if gestionar_acceso(conn):
    d_cli = st.session_state.datos_cliente
    # Usamos castellano por defecto
    t = traducir_interfaz("Castellano")

    # BARRA LATERAL
    with st.sidebar:
        st.image("logo.png", use_container_width=True)
        st.markdown(f"### 👤 {d_cli.get('Contacto', 'Usuario')}")
        st.caption(f"🏢 {d_cli.get('Empresa', 'Cliente Swarco')}")
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.rerun()

    # TÍTULO
    st.markdown("<h2 style='text-align: center; color: #00549F;'>Portal de Reporte Técnico SAT</h2>", unsafe_allow_html=True)

    # --- SECCIÓN 1: DATOS DEL REPORTE ---
    st.markdown('### 📍 UBICACIÓN Y CONTACTO')
    c1, c2 = st.columns(2)
    with c1:
        st.text_input("Empresa", value=d_cli.get('Empresa', ''), disabled=True)
        proyecto_ub = st.text_input("Proyecto / Ubicación exacta", placeholder="Ej: Túnel de la Castellana")
    with c2:
        p_nombres = list(PAISES_DATA.keys())
        pais_sel = st.selectbox("País", p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
        tel_raw = st.text_input("Móvil de contacto (sin prefijo)")
        # Armamos el teléfono final con el prefijo del país seleccionado
        tel_final = f"{PAISES_DATA[pais_sel]} {''.join(filter(str.isdigit, tel_raw))}"

    # --- SECCIÓN 2: DETALLES DEL EQUIPO ---
    st.markdown('### ⚙️ DETALLES DEL EQUIPO')
    st.info("Localice la pegatina plateada en el chasis del equipo.")
    ce1, ce2 = st.columns(2)
    with ce1:
        ns_in = st.text_input("N.S. (Número de Serie)", placeholder="Ej: 2023-1234")
    with ce2:
        ref_in = st.text_input("Referencia (REF.)", placeholder="Ej: VMS-123-A")

    # --- SECCIÓN 3: PRIORIDAD Y FALLO ---
    st.markdown('### 🚨 DESCRIPCIÓN DE LA AVERÍA')
    
    # Recuperamos el selector de urgencia (Prioridad)
    opciones_urg = ["Baja", "Media", "Alta", "Crítica (Sistema fuera de servicio)"]
    urg_val = st.select_slider("Seleccione la urgencia del reporte", options=opciones_urg, value="Media")
    
    falla_in = st.text_area("¿Qué problema presenta el equipo?", placeholder="Describa el fallo detalladamente...", height=150)

    # RECUPERAMOS: Subida de archivos (Fotos/Videos)
    st.markdown('### 📸 EVIDENCIAS')
    archivos = st.file_uploader("Subir fotos o vídeos del equipo/avería", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'])

    if 'lista_equipos' not in st.session_state:
        st.session_state.lista_equipos = []

    st.divider()
    
    # BOTONES DE ACCIÓN
    col_add, col_gen = st.columns(2)
    
    with col_add:
        if st.button("➕ Añadir otro equipo al mismo ticket", use_container_width=True):
            if ns_in and falla_in:
                st.session_state.lista_equipos.append({
                    "N.S.": ns_in, 
                    "REF": ref_in, 
                    "Prioridad": urg_val, 
                    "Descripción": falla_in
                })
                st.success("✅ Equipo añadido a la lista. Puedes registrar otro arriba.")
                st.rerun()
            else:
                st.warning("⚠️ Escribe al menos el N.S. y el problema.")

    with col_gen:
        if st.button("🚀 GENERAR TICKET FINAL", type="primary", use_container_width=True):
            # Consolidamos los datos
            equipos_finales = st.session_state.lista_equipos.copy()
            if ns_in and falla_in: # Añade el que está en pantalla si no se le dio al botón de añadir
                equipos_finales.append({
                    "N.S.": ns_in, "REF": ref_in, "Prioridad": urg_val, "Descripción": falla_in
                })
            
            if equipos_finales and proyecto_ub:
                ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
                
                # ENVIAR EMAIL (Función que ya tienes configurada)
                exito_email = enviar_email_outlook(
                    d_cli['Empresa'], d_cli['Contacto'], proyecto_ub, 
                    equipos_finales, d_cli['Email'], ticket_id, tel_final
                )
                
                if exito_email:
                    # GUARDAR EN GOOGLE SHEETS (Pestaña Sheet1)
                    try:
                        resumen_ns = ", ".join([e['N.S.'] for e in equipos_finales])
                        nueva_fila = pd.DataFrame([{
                            "Ticket_ID": ticket_id, 
                            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Cliente": d_cli['Empresa'], 
                            "Usuario": d_cli['Usuario'],
                            "Ubicacion": proyecto_ub, 
                            "Telefono": tel_final,
                            "Equipos": resumen_ns, 
                            "Estado": "OPEN"
                        }])
                        
                        df_h = conn.read(worksheet="Sheet1", ttl=0)
                        df_updated = pd.concat([df_h, nueva_fila], ignore_index=True)
                        conn.update(worksheet="Sheet1", data=df_updated)
                        
                        st.success(f"🎊 ¡Ticket {ticket_id} enviado con éxito!")
                        st.balloons()
                        st.session_state.lista_equipos = [] # Limpiamos lista
                    except Exception as e:
                        st.error(f"Se envió el email pero falló el registro en Excel: {e}")
            else:
                st.error("⚠️ Falta información crítica (Ubicación o datos del equipo).")

    # Visualización de equipos añadidos
    if st.session_state.lista_equipos:
        st.subheader("📋 Equipos en este reporte:")
        st.dataframe(pd.DataFrame(st.session_state.lista_equipos), use_container_width=True)

    st.markdown("<p style='text-align:center; color:#999; margin-top:50px;'>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>", unsafe_allow_html=True)


