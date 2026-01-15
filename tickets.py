import streamlit as st
import pandas as pd

def interfaz_tickets(conn, t):
    """
    Módulo principal para la creación de reportes técnicos.
    Recibe 'conn' para la DB y 't' para el idioma.
    """
    # 1. Recuperamos datos del cliente logueado
    d_cli = st.session_state.get('datos_cliente', {})
    
    # 2. Sidebar de control
    st.sidebar.image("logo.png", width=150)
    st.sidebar.markdown(f"### 👤 {d_cli.get('Contacto', 'Usuario')}")
    st.sidebar.info(f"🏢 {d_cli.get('Empresa', 'Swarco Partner')}")
    
    if st.sidebar.button(t.get('btn_salir', 'SALIR'), use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.lista_equipos = [] # Limpiamos al salir
        st.rerun()

    # 3. Título y Estado del Ticket
    st.title(f"🎫 {t.get('titulo_portal', 'Portal de Reportes')}")

    # Pantalla de éxito tras enviar
    if st.session_state.get('ticket_enviado', False):
        st.success(t.get("exito", "✅ Ticket enviado correctamente."))
        if st.button("Crear otro reporte"):
            st.session_state.ticket_enviado = False
            st.session_state.lista_equipos = []
            st.rerun()
        return

    # --- FORMULARIO DE REPORTE ---

    # SECCIÓN A: Datos del lugar (Expander para ahorrar espacio)
    with st.expander(f"📍 {t.get('cat1', 'Datos del Servicio')}", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            # Estos vienen de la base de datos, no se tocan
            st.text_input(t.get("cliente", "Empresa"), value=d_cli.get('Empresa'), disabled=True)
            proyecto = st.text_input(t.get("proyecto", "Ubicación/Proyecto") + " *")
        with c2:
            st.text_input(t.get("email", "Email"), value=d_cli.get('Email'), disabled=True)
            telefono = st.text_input(t.get("tel", "Teléfono de contacto") + " *")

    # SECCIÓN B: Añadir Equipos
    st.subheader(f"🛠️ {t.get('cat2', 'Detalle de Equipos')}")
    
    with st.container(border=True):
        ce1, ce2 = st.columns([3, 2])
        with ce1:
            ns_equipo = st.text_input(t.get("ns_titulo", "N.S. (Número de Serie)") + " *")
        with ce2:
            referencia = st.text_input("Referencia / Modelo")

        falla_desc = st.text_area(t.get("desc_instruccion", "Descripción de la avería") + " *")
        
        # ADN: Manejo de fotos (guardamos nombres de archivos por ahora)
        archivos = st.file_uploader(t.get("fotos", "Adjuntar evidencias"), accept_multiple_files=True)

        if st.button(t.get("btn_agregar", "➕ Añadir Equipo a la lista"), use_container_width=True):
            if ns_equipo and falla_desc:
                # Inicializamos la lista en la sesión si no existe
                if 'lista_equipos' not in st.session_state:
                    st.session_state.lista_equipos = []
                
                # Guardamos el equipo en el ADN de la sesión
                st.session_state.lista_equipos.append({
                    "N.S.": ns_equipo,
                    "Referencia": referencia,
                    "Avería": falla_desc,
                    "Fotos": len(archivos) if archivos else 0
                })
                st.toast(f"Equipo {ns_equipo} añadido")
            else:
                st.error("⚠️ El N.S. y la descripción son obligatorios.")

    # SECCIÓN C: Resumen y Envío
    if st.session_state.get('lista_equipos'):
        st.markdown("---")
        st.write(f"### 📋 {t.get('resumen', 'Equipos para reportar')}")
        
        # Mostramos la tabla machete
        df_resumen = pd.DataFrame(st.session_state.lista_equipos)
        st.dataframe(df_resumen, use_container_width=True)

        if st.button(t.get("btn_generar", "🚀 ENVIAR REPORTE FINAL"), type="primary", use_container_width=True):
            if not proyecto or not telefono:
                st.warning("⚠️ Completa la ubicación y el teléfono antes de enviar.")
            else:
                # Aquí es donde el ADN de 'correo.py' entrará en juego
                # Por ahora, simulamos el éxito
                st.session_state.ticket_enviado = True
                st.rerun()
