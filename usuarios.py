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
        t1, t2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registro de Cliente"])
        
        with t1:
            u = st.text_input("Usuario", key="l_u")
            p = st.text_input("Clave", type="password", key="l_p")
            if st.button("Entrar", use_container_width=True):
                try:
                    # LEER es gratis y funciona con la URL pública
                    df = conn.read(worksheet="Clientes", ttl=0)
                    val = df[(df['Usuario'].astype(str) == u) & (df['Clave'].astype(str) == p)]
                    if not val.empty:
                        st.session_state.autenticado = True
                        st.session_state.datos_cliente = val.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("Usuario o clave incorrectos")
                except Exception as e:
                    st.error(f"Error al conectar con la base de datos: {e}")

        with t2:
            st.info("Complete los datos para crear su cuenta SAT.")
            r_u = st.text_input("Nombre de Usuario")
            r_p = st.text_input("Contraseña", type="password")
            r_e = st.text_input("Nombre de la Empresa")
            r_c = st.text_input("Persona de Contacto")
            r_m = st.text_input("Email Corporativo")
            
            if st.button("Crear Cuenta Ahora", use_container_width=True):
                if r_u and r_p and r_e and r_m:
                    # --- AQUÍ PEGA TU URL DE APPS SCRIPT ---
                    URL_BRIDGE = "https://script.google.com/macros/s/TU_ID_AQUÍ/exec"
                    
                    payload = {
                        "Usuario": r_u,
                        "Clave": r_p,
                        "Empresa": r_e,
                        "Contacto": r_c,
                        "Email": r_m
                    }
                    
                    try:
                        # ESCRIBIR mediante el puente de Google Apps Script
                        response = requests.post(URL_BRIDGE, data=json.dumps(payload))
                        if "Exito" in response.text:
                            st.success("✅ Registro exitoso. ¡Ya puedes iniciar sesión!")
                        else:
                            st.error(f"Error del servidor: {response.text}")
                    except Exception as e:
                        st.error(f"Fallo de conexión: {e}")
                else:
                    st.warning("Por favor, rellene todos los campos.")
        return False
    return True
