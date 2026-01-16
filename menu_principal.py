# =============================================================================
# ARCHIVO: menu_principal.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 1.0.0 (Tablero de Control)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Interfaz intermedia que permite al usuario navegar hacia 
#              SAT, Repuestos o Equipos Nuevos.
# =============================================================================

import streamlit as st
import estilos

def mostrar_menu(conn, t):
    """Muestra los botones de acceso a las diferentes áreas del sistema."""
    
    # 1. Encabezado de Bienvenida
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("titulo_portal", "Panel de Control")}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="swarco-subtitle">Sesión: {st.session_state.user_email}</p>', unsafe_allow_html=True)
    st.markdown("---")

    # 2. Grid de Botones (Diseño de 2 columnas para que sean grandes)
    col1, col2 = st.columns(2)

    with col1:
        # Botón para ir al SAT
        if st.button(f"🎫 {t.get('cat1', 'Gestión de Tickets SAT')}"):
            st.session_state.pagina_actual = 'sat'
            st.rerun()

    with col2:
        # Botón para Repuestos (Página a crear)
        if st.button(f"📦 {t.get('btn_repuestos', 'Solicitud de Repuestos')}"):
            st.warning("Próximamente: Módulo de Repuestos")
            # st.session_state.pagina_actual = 'repuestos'
            # st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        # Botón para Equipos Nuevos (Página a crear)
        if st.button(f"🚜 {t.get('btn_equipos_nuevos', 'Equipos Nuevos')}"):
            st.warning("Próximamente: Módulo de Equipos Nuevos")
            # st.session_state.pagina_actual = 'equipos_nuevos'
            # st.rerun()

    with col4:
        # Botón de Salida
        if st.button(f"🚪 {t.get('btn_salir', 'SALIR')}"):
            st.session_state.autenticado = False
            st.session_state.pagina_actual = 'login'
            st.rerun()
