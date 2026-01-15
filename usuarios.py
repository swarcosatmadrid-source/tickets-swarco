import streamlit as st
import pandas as pd
import json
import requests

# URL que me pasaste
URL_BRIDGE = "https://script.google.com/macros/s/AKfycbyDpHS4nU16O7YyvABvmbFYHTLv2e2J8vrpSD-iCmamjmS4Az6p9iZNUmVEwzMVyzx9/exec"

def gestionar_acceso(conn):
    if st.session_state.get('autenticado', False):
        return True

    st.markdown("<h2 style='text-align: center; color: #00549F;'>🔐 Acceso al Portal SAT</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        user_in = st.text_input("Usuario (Nombre Apellido)").strip().lower()
        pass_in = st.text_input("Contraseña", type="password")
        
        if st.form_submit_button("ENTRAR AL SISTEMA", use_container_width=True):
            try:
                df = conn.read(worksheet="Usuarios", ttl=0)
                validado = df[(df['Usuario'].str.lower() == user_in) & (df['Password'].astype(str) == pass_in)]
                
                if not validado.empty:
                    st.session_state.autenticado = True
                    st.session_state.datos_cliente = {
                        'Empresa': validado.iloc[0]['Empresa'],
                        'Contacto': validado.iloc[0]['Usuario'],
                        'Email': validado.iloc[0]['Email']
                    }
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas.")
            except Exception as e:
                st.error(f"Error de base de datos: {e}")
    return False

def interfaz_registro_legal(conn):
    st.markdown("<h3 style='color: #F29400;'>📝 Registro de Nuevo Usuario</h3>", unsafe_allow_html=True)
    
    with st.form("form_registro_v0"):
        # Honeypot oculto (sin validación para evitar errores de auto-completado)
        st.text_input("Extra", key="hp_field", label_visibility="collapsed")
        
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre *").strip()
            apellido = st.text_input("Primer Apellido *").strip()
            empresa = st.text_input("Empresa *").strip()
        with c2:
            email = st.text_input("Email Corporativo *").strip()
            telefono = st.text_input("Teléfono")
            pregunta_seguridad = st.number_input("Seguridad: ¿Cuánto es 10 + 5?", step=1)
            
        st.markdown("---")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            pass1 = st.text_input("Defina Clave *", type="password")
        with col_p2:
            pass2 = st.text_input("Repita Clave *", type="password")
            
        st.markdown("---")
        acepta_rgpd = st.checkbox("He leído y acepto la Política de Protección de Datos.")
        
        btn_registrar = st.form_submit_button("CREAR MI CUENTA", use_container_width=True)

    if btn_registrar:
        if pregunta_seguridad != 15:
            st.error("❌ Respuesta de seguridad incorrecta.")
        elif not (nombre and apellido and empresa and email and pass1):
            st.warning("⚠️ Rellene los campos obligatorios.")
        elif pass1 != pass2:
            st.error("❌ Las claves no coinciden.")
        elif not acepta_rgpd:
            st.error("❌ Debe aceptar los términos legales.")
        else:
            try:
                nombre_completo = f"{nombre} {apellido}"
                payload = {
                    "Accion": "Registro",
                    "Usuario": nombre_completo,
                    "Nombre": nombre,
                    "Apellido": apellido,
                    "Email": email,
                    "Password": pass1,
                    "Empresa": empresa,
                    "Telefono": telefono,
                    "RGPD": "SÍ"
                }
                
                # CORRECCIÓN PARA EVITAR EL ERROR 400:
                # Enviamos los datos como texto plano (JSON string) para que Apps Script lo reciba bien
                response = requests.post(
                    URL_BRIDGE, 
                    data=json.dumps(payload),
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200 and "Éxito" in response.text:
                    st.success("✅ ¡Registro completado! Ya puede iniciar sesión.")
                else:
                    st.error(f"❌ Error en el servidor: {response.text}")
                    
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")
