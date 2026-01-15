import streamlit as st
import pandas as pd

def interfaz_tickets(t):
    d_cli = st.session_state.get('datos_cliente', {})
    
    # Sidebar de usuario
    st.sidebar.image("logo.png", width=150)
    st.sidebar.success(f"👤 {d_cli.get('Contacto')}")
    if st.sidebar.button(t.get('btn_salir', 'SALIR')):
        st.session_state.autenticado = False
        st.rerun()

    st.title(f"🎫 {t.get('titulo_portal')}")

    if st.session_state.get('ticket_enviado', False):
        st.success(t.get("exito"))
        if st.button("Nuevo ticket"):
            st.session_state.ticket_enviado = False
            st.session_state.lista_equipos = []
            st.rerun()
        return

    # Formulario
    with st.expander(t.get("cat1"), expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input(t.get("cliente"), value=d_cli.get('Empresa'), disabled=True)
            proyecto = st.text_input(t.get("proyecto") + " *")
        with col2:
            st.text_input(t.get("email"), value=d_cli.get('Email'), disabled=True)
            telefono = st.text_input(t.get("tel") + " *")

    # Detalle de equipos
    st.subheader(t.get("cat2"))
    ns = st.text_input(t.get("ns_titulo") + " *")
    falla = st.text_area(t.get("desc_instruccion") + " *")
    
    if st.button(t.get("btn_agregar")):
        if ns and falla:
            st.session_state.lista_equipos.append({"N.S.": ns, "Avería": falla})
            st.toast("Equipo añadido")

    if st.session_state.get('lista_equipos'):
        st.table(pd.DataFrame(st.session_state.lista_equipos))
        if st.button(t.get("btn_generar"), type="primary", use_container_width=True):
            st.session_state.ticket_enviado = True
            st.rerun()
