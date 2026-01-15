import streamlit as st
import pandas as pd
import json
import requests
import random
import re
import time

URL_BRIDGE = "https://script.google.com/macros/s/AKfycbyDpHS4nU16O7YyvABvmbFYHTLv2e2J8vrpSD-iCmamjmS4Az6p9iZNUmVEwzMVyzx9/exec"

def validar_password(password):
    """Seguridad de clave: 8+ carac, 1 Mayus, 1 Núm"""
    if len(password) < 8:
        return False, "Mínimo 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "Falta una mayúscula."
    if not re.search(r"[0-9]", password):
        return False, "Falta un número."
    return True, ""

def gestionar_acceso(conn):
    """Pestaña de Login para usuarios o equipos"""
    st.markdown("<h2 style='text-align: center; color: #00549F;'>🔐 Acceso Usuarios</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user_in = st.text_input("Usuario (ID de Equipo o Personal)", placeholder="Ej: UTE_Sevilla").strip()
        pass_in = st.text_input("Contraseña", type="password")
        
        if st.form_submit_button("INGRESAR AL PORTAL", use_container_width=True):
            try:
                df = conn.read(worksheet="Usuarios", ttl=0)
                # Validamos contra el nuevo ID de usuario personalizado
                validado = df[(df['Usuario'].astype(str) == user_in) & (df['Password'].astype(str) == pass_in)]
                
                if not validado.empty:
                    st.session_state.autenticado = True
                    st.session_state.datos_cliente = {
                        'Empresa': validado.iloc[0]['Empresa'],
                        'Contacto': validado.iloc[0]['Usuario'],
                        'Email': validado.iloc[0]['Email']
                    }
                    st.success("✅ Acceso concedido")
                    return True
                else:
                    st.error("❌ Credenciales incorrectas.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
    return False

def interfaz_registro_legal(conn):
    """Pestaña de Registro con seguridad White Hat y validación pro"""
    st.markdown("<h3 style='color: #F29400;'>📝 Registro de Nuevo Usuario / UTE</h3>", unsafe_allow_html=True)
    st.caption("🔒 Datos protegidos bajo protocolo RGPD. Todos los campos con (*) son obligatorios.")

    if 'n1' not in st.session_state:
        st.session_state.n1 = random.randint(1, 10)
        st.session_state.n2 = random.randint(1, 10)

    with st.form("form_registro_v0", clear_on_submit=True):
        st.markdown("##### **1. Identificación del Usuario o Grupo**")
        usuario_id = st.text_input("Nombre de Usuario Deseado * (Ej: Equipo_Sur_01)").strip()
        
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Responsable / Equipo *").strip()
            apellido = st.text_input("Apellidos *").strip()
        with c2:
            empresa = st.text_input("Empresa / UTE *").strip()
            email = st.text_input("Email Corporativo *").strip()

        st.markdown("---")
        st.markdown("##### **2. Seguridad de Acceso**")
        cp1, cp2 = st.columns(2)
        with cp1:
            pass1 = st.text_input("Defina Clave (8+ carac, Mayús, Núm) *", type="password")
            pass2 = st.text_input("Confirme su Clave *", type="password")
        with cp2:
            telefono = st.text_input("Teléfono móvil (Obligatorio) *").strip()
            captcha_user = st.number_input(f"Validación Humana: {st.session_state.n1} + {st.session_state.n2}?", step=1)

        # Validación visual de claves en el formulario
        if pass1 and pass2 and pass1 != pass2:
            st.warning("⚠️ Las claves no coinciden todavía.")

        st.markdown("---")
        acepta_rgpd = st.checkbox("Acepto el tratamiento de mis datos personales para fines técnicos.")
        
        btn_registrar = st.form_submit_button("CREAR CUENTA SEGURA", use_container_width=True)

    if btn_registrar:
        es_valida, msg_p = validar_password(pass1)
        
        if not (usuario_id and nombre and apellido and empresa and email and pass1 and telefono):
            st.error("❌ Todos los campos son obligatorios.")
        elif pass1 != pass2:
            st.error("❌ Las contraseñas no coinciden.")
        elif not es_valida:
            st.error(f"❌ Clave débil: {msg_p}")
        elif captcha_user != (st.session_state.n1 + st.session_state.n2):
            st.error("❌ Error de validación humana.")
        elif not acepta_rgpd:
            st.error("❌ Debe aceptar la política de datos.")
        else:
            try:
                # Payload para Google Sheets
                payload = {
                    "Accion": "Registro",
                    "Usuario": usuario_id,
                    "Nombre": nombre,
                    "Apellido": apellido,
                    "Email": email,
                    "Password": pass1,
                    "Empresa": empresa,
                    "Telefono": telefono,
                    "RGPD": "SÍ"
                }
                
                response = requests.post(
                    URL_BRIDGE, 
                    data=json.dumps(payload), 
                    headers={'Content-Type': 'application/json'}
                )
                
                if "Éxito" in response.text:
                    st.success("🎊 ¡USUARIO CREADO CORRECTAMENTE!")
                    st.info("Redirigiendo al inicio...")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ Error en base de datos: {response.text}")
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")
