import streamlit as st
import pandas as pd
import uuid

def gestionar_equipos(t, urg_val_default):
    # Inicializar lista si no existe
    if 'lista_equipos' not in st.session_state:
        st.session_state.lista_equipos = []

    st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
    st.info(t['pegatina'])
    st.image("etiqueta.jpeg", use_container_width=True)

    ce1, ce2 = st.columns(2)
    with ce1:
        ns_in = st.text_input(t['ns_titulo'], key="ns_input")
    with ce2:
        ref_in = st.text_input("REF.", key="ref_input")

    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    
    opciones_urg = [t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']]
    urg_val = st.select_slider(t['urg_instruccion'], options=opciones_urg, value=urg_val_default)

    falla_in = st.text_area(t['desc_instruccion'], placeholder=t['desc_placeholder'], key="desc_input")

    # Retornamos los valores actuales para que main.py pueda usarlos al "Generar Ticket"
    return ns_in, ref_in, urg_val, falla_in
