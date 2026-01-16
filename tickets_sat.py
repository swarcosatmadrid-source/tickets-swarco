# =============================================================================
# ARCHIVO: tickets_sat.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 2.0.0 (Fusión SAT + Equipos)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Formulario de reporte de averías. Gestiona la entrada de datos
#              del proyecto y los detalles del equipo (N.S. y Falla).
# =============================================================================

import streamlit as st
import estilos
import pandas as pd
from datetime import datetime

def interfaz_tickets(conn, t):
    """Interfaz unificada para reportar averías al SAT."""
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("titulo_portal", "Reporte Técnico SAT")}</p>', unsafe_allow_html=True)
    
    # 1. BOTÓN VOLVER (Para regresar al Menú Principal)
    if st.button(f"⬅️ {t.get('btn_volver', 'VOLVER')}"):
        st.session_state.pagina_actual = 'menu'
        st.rerun()

    # 2. FORMULARIO PRINCIPAL
    with st.form("form_sat"):
        # --- SECCIÓN 1: DATOS DEL SERVICIO ---
        st.subheader(t.get("cat1", "Datos del Servicio"))
        col1, col2 = st.columns(2)
        with col1:
            proyecto = st.text_input(t.get("proyecto", "Proyecto / Ubicación"))
            empresa = st.text_input(t.get("cliente", "Empresa"))
        with col2:
            contacto = st.text_input(t.get("nombre", "Persona de Contacto"))
            telefono = st.text_input(t.get("tel", "Teléfono"))

        st.markdown("---")

        # --- SECCIÓN 2: DETALLE DEL EQUIPO (Lógica de equipos.py) ---
        st.subheader(t.get("cat2", "Detalle de Equipos"))
        
        # Ayuda visual de la pegatina
        with st.expander(t.get("guia_titulo", "Ver ayuda de etiqueta"), expanded=False):
            st.image("etiqueta.jpeg", caption="Localización del Número de Serie (N.S.)")
        
        ce1, ce2 = st.columns(2)
        with ce1:
            ns = st.text_input(t.get("ns_titulo", "N.S. (Número de Serie)"))
        with ce2:
            ref = st.text_input("REF. / Modelo")

        # Urgencia (Slider)
        opciones_urg = ["Baja", "Media", "Alta", "Crítica"] # O usar t.get('u1')...
        urgencia = st.select_slider("Nivel de Urgencia", options=opciones_urg, value="Baja")
        
        falla = st.text_area(t.get("desc_instruccion", "Descripción del fallo"))

        # 3. ENVÍO DE DATOS
        enviar = st.form_submit_button(t.get("btn_generar", "GENERAR TICKET"))
        
        if enviar:
            if proyecto and ns and falla:
                try:
                    ws = conn.worksheet("Tickets")
                    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
                    # Guardamos en la fila de Google Sheets
                    ws.append_row([fecha_hoy, st.session_state.user_email, proyecto, empresa, contacto, telefono, ns, ref, urgencia, falla])
                    
                    st.success(t.get("exito", "✅ Ticket enviado correctamente."))
                    # Opcional: Limpiar campos o volver al menú
                except Exception as e:
                    st.error(f"Error al guardar en Sheets: {e}")
            else:
                st.warning(t.get("error_campos", "Por favor, rellene los campos obligatorios (*)"))
