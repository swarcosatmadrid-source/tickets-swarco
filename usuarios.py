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
        t1, t2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registro"])
        
        with t1:
            u = st.text_input("Usuario", key="l_u")
            p = st.text_input("Clave", type="password", key="l_p")
            if st.button("Entrar", use_container_width=True):
                try:
                    # Intentamos leer la pestaña 'Clientes', si falla, leemos la primera
                    try:
                        df = conn.read(worksheet="Clientes", ttl=0)
                    except:
                        df = conn.read(ttl=0)
                    
                    val = df[(df['Usuario'].astype(str) == u) & (df['Clave'].astype(str) == p)]
                    if not val.empty:
                        st.session_state.autenticado = True
                        st.session_state.datos_cliente = val.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("Usuario o clave incorrectos")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

        with t2:
            r_u = st.text_input("Nuevo Usuario")
            r_p = st.text_input("Nueva Clave", type="password")
            r_e = st.text_input("Empresa")
            r_c = st.text_input("Nombre")
            r_m = st.text_input("Email")
            
            if st.button("Registrar Ahora", use_container_width=True):
                URL_BRIDGE = "TU_URL_DE_APPS_SCRIPT_AQUI" # <--- PON LA NUEVA URL AQUÍ
                payload = {"Usuario": r_u, "Clave": r_p, "Empresa": r_e, "Contacto": r_c, "Email": r_m}
                
                try:
                    res = requests.post(URL_BRIDGE, data=json.dumps(payload))
                    if "Éxito" in res.text:
                        st.success("✅ ¡Registrado! Ve a la pestaña de Login.")
                    else:
                        st.error(f"Google dice: {res.text}")
                except Exception as e:
                    st.error(f"Error de red: {e}")
        return False
    return True
