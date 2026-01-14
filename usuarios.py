import streamlit as st
import pandas as pd
import requests
import json

def gestionar_acceso(conn):
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.datos_cliente = {}

    if not st.session_state.autenticado:
        st.image("logo.png", width=300)
        t1, t2 = st.tabs(["🔑 Login", "📝 Registro"])
        
        with t1:
            u = st.text_input("Usuario", key="l_u")
            p = st.text_input("Clave", type="password", key="l_p")
            if st.button("Entrar"):
                df = conn.read(worksheet="Clientes", ttl=0)
                val = df[(df['Usuario'].astype(str) == u) & (df['Clave'].astype(str) == p)]
                if not val.empty:
                    st.session_state.autenticado = True
                    st.session_state.datos_cliente = val.iloc[0].to_dict()
                    st.rerun()
                else: st.error("Fallo")

        with t2:
            r_u = st.text_input("Nuevo Usuario")
            r_p = st.text_input("Nueva Clave", type="password")
            r_e = st.text_input("Empresa")
            r_c = st.text_input("Tu Nombre")
            r_m = st.text_input("Tu Email")
            if st.button("Registrar"):
                # PEGA AQUÍ TU URL DEL PASO 2
                URL_TUNEZ = "TU_URL_DE_APPS_SCRIPT_AQUI"
                datos = {"Usuario": r_u, "Clave": r_p, "Empresa": r_e, "Contacto": r_c, "Email": r_m}
                res = requests.post(URL_TUNEZ, data=json.dumps(datos))
                if "Exito" in res.text:
                    st.success("¡Listo! Ya puedes loguearte.")
                else: st.error("Error de conexión")
        return False
    return True
