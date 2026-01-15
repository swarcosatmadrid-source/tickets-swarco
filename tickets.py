import streamlit as st
import pandas as pd
import correo  # <--- Importante para conectar con el mensajero

def interfaz_tickets(conn, t):
    """
    Módulo principal para la creación de reportes técnicos.
    Recibe 'conn' para la DB y 't' para el idioma.
    """
    # 1. Recuperamos datos del cliente logueado
    d_cli = st.session_state.get('datos_cliente', {})
    
    # 2. Sidebar de control y salida
    st.sidebar.image("logo.png", width=150)
    st.sidebar.success(f"👤 {d_cli.get('Contacto', 'User')}")
    
    if st.sidebar.button(t.get('btn_salir', 'SALIR'), use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.lista_equipos = [] # Limpiamos memoria
        st.rerun()

    st.title(f"🎫 {t.get('titulo_portal', 'Portal SAT')}")

    # --- PANTALLA DE ÉXITO ---
    if st.session_state.get('ticket_enviado', False):
        st.balloons() # Un toque de celebración
        st.success(t.get("exito", "✅ Ticket enviado correctamente."))
        if st.button("Crear un nuevo reporte"):
            st.session_state.ticket_enviado = False
            st.session_state.lista_equipos = []
            st.rerun()
        return

    # --- FORMULARIO DE REPORTE ---

    # SECCIÓN A: Datos del lugar
    with st.expander(f"📍 {t.get('cat1', 'Datos del Servicio')}", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(t.get("cliente", "Empresa"), value=d_cli.get('Empresa'), disabled=True)
            proyecto = st.text_input(t.get("proyecto", "Ubicación") + " *")
        with col2:
            st.text_input(t.get("email", "Email"), value=d_cli.get('Email'), disabled=True)
            telefono = st.text_input(t.get("tel", "Teléfono") + " *")

    # SECCIÓN B: Añadir Equipos
    st.subheader(f"🛠️ {t.get('cat2', 'Detalle de Equipos')}")
    
    with st.container(border=True):
        ce1, ce2 = st.columns([3, 2])
        with ce1:
            ns_equipo = st.text_input(t.get("ns_titulo", "N.S.") + " *")
        with ce2:
            referencia = st.text_input("Referencia / Ref")

        falla_desc = st.text_area(t.get("desc_instruccion", "Fallo") + " *")
        archivos = st.file_uploader(t.get("fotos", "Fotos"), accept_multiple_files=True)

        if st.button(t.get("btn_agregar", "Añadir Equipo"), use_container_width=True):
            if ns_equipo and falla_desc:
                if 'lista_equipos' not in st.session_state:
                    st.session_state.lista_equipos = []
                
                st.session_state.lista_equipos.append({
                    "N.S.": ns_equipo,
                    "Referencia": referencia,
                    "Avería": falla_desc,
                    "Fotos": len(archivos) if archivos else 0
                })
                st.toast(f"Equipo {ns_equipo} OK")
            else:
                st.error("⚠️ Falta N.S. o Descripción")

    # SECCIÓN C: Resumen y Envío Final por Correo
    if st.session_state.get('lista_equipos'):
        st.markdown("---")
        st.write(f"### 📋 {t.get('resumen', 'Resumen del Reporte')}")
        
        df_resumen = pd.DataFrame(st.session_state.lista_equipos)
        st.table(df_resumen)

        # EL BOTÓN DE ENVÍO FINAL
        if st.button(t.get("btn_generar", "🚀 ENVIAR TICKET"), type="primary", use_container_width=True):
            if not proyecto or not telefono:
                st.warning("⚠️ Rellene ubicación y teléfono.")
            else:
                # 📧 LLAMADA AL MÓDULO DE CORREO
                with st.spinner('Enviando reporte a Swarco...'):
                    exito_mail = correo.enviar_ticket_soporte(
                        datos_cliente=d_cli,
                        proyecto=proyecto,
                        telefono=telefono,
                        lista_equipos=st.session_state.lista_equipos,
                        idioma_t=t
                    )
                
                if exito_mail:
                    st.session_state.ticket_enviado = True
                    st.rerun()
                else:
                    st.error("❌ Error al enviar el email. Revise la configuración SMTP en Secrets.")
