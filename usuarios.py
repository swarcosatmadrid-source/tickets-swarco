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
                    # Intento de lectura robusta
                    try:
                        df = conn.read(worksheet="Clientes", ttl=0)
                    except:
                        df = conn.read(ttl=0)
                    
                    val = df[(df['Usuario'].astype(str).str.strip() == u.strip()) & 
                             (df['Clave'].astype(str) == p)]
                    
                    if not val.empty:
                        st.session_state.autenticado = True
                        st.session_state.datos_cliente = val.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ Usuario o clave incorrectos")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

        with t2:
            st.info("Cree su cuenta corporativa para el portal SAT.")
            r_u = st.text_input("Nuevo Usuario").strip()
            r_p = st.text_input("Nueva Clave", type="password")
            r_e = st.text_input("Empresa")
            r_c = st.text_input("Nombre de Contacto")
            r_m = st.text_input("Email")
            
            if st.button("Registrar Ahora", use_container_width=True):
                # Validación de campos vacíos antes de enviar
                if not r_u or not r_p or not r_e:
                    st.error("⚠️ Usuario, Clave y Empresa son campos obligatorios.")
                else:
                    # TU URL DE APPS SCRIPT
                    URL_BRIDGE = "https://script.google.com/macros/s/AKfycbyDpHS4nU16O7YyvABvmbFYHTLv2e2J8vrpSD-iCmamjmS4Az6p9iZNUmVEwzMVyzx9/exec"
                    
                    payload = {
                        "Usuario": r_u, 
                        "Clave": r_p, 
                        "Empresa": r_e, 
                        "Contacto": r_c, 
                        "Email": r_m
                    }
                    
                    try:
                        res = requests.post(URL_BRIDGE, data=json.dumps(payload))
                        
                        # --- LÓGICA DE RESPUESTA DEL SCRIPT ---
                        if "Éxito" in res.text:
                            st.success("✅ ¡Registrado con éxito! Ya puedes iniciar sesión.")
                        elif "Duplicado" in res.text:
                            st.warning(f"⚠️ El usuario '{r_u}' ya existe. Por favor, elige otro nombre.")
                        else:
                            st.error(f"Respuesta inesperada: {res.text}")
                            
                    except Exception as e:
                        st.error(f"Error de red al registrar: {e}")
        return False
    return True
