import streamlit as st
import pandas as pd
import json
import requests
import random
import re

URL_BRIDGE = "https://script.google.com/macros/s/AKfycbyDpHS4nU16O7YyvABvmbFYHTLv2e2J8vrpSD-iCmamjmS4Az6p9iZNUmVEwzMVyzx9/exec"

def validar_password(password):
    """Verifica que la clave tenga min 8 caracteres, una mayúscula y un número"""
    if len(password) < 8:
        return False, "La clave debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "La clave debe contener al menos una letra mayúscula."
    if not re.search(r"[0-9]", password):
        return False, "La clave debe contener al menos un número."
    return True, ""

def gestionar_acceso(conn):
    st.markdown("<h2 style='text-align: center; color: #00549F;'>🔐 Acceso Usuarios Registrados</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user_in = st.text_input("Introduzca su Usuario (Nombre Apellido)", placeholder="ej: Juan Perez").strip().lower()
        pass_in = st.text_input("Introduzca su Contraseña", type="password")
        
        if st.form_submit_button("INGRESAR AL PORTAL", use_container_width=True):
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
                    st.error("❌ Error: Usuario o clave incorrectos.")
            except Exception as e:
                st.error(f"Error de conexión: {e}")
    return False

def interfaz_registro_legal(conn):
    st.markdown("<h3 style='color: #F29400;'>📝 Registro de Nuevo Técnico</h3>", unsafe_allow_html=True)
    st.info("💡 **Instrucciones:** Complete todos los campos marcados con (*). Su usuario será creado automáticamente con su Nombre y Apellido.")

    # Generar números aleatorios para el Captcha cada vez que carga
    if 'n1' not in st.session_state:
        st.session_state.n1 = random.randint(1, 10)
        st.session_state.n2 = random.randint(1, 10)

    with st.form("form_registro_v0"):
        st.markdown("#### **Paso 1: Datos Personales**")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre *", placeholder="Su nombre").strip()
            apellido = st.text_input("Primer Apellido *", placeholder="Su apellido").strip()
        with c2:
            empresa = st.text_input("Empresa *", placeholder="Nombre de su empresa").strip()
            email = st.text_input("Email Corporativo *", placeholder="usuario@swarco.com").strip()

        st.markdown("#### **Paso 2: Seguridad**")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            pass1 = st.text_input("Defina Clave (Min. 8 caracteres, 1 Mayus, 1 Núm) *", type="password")
            pass2 = st.text_input("Repita su Clave *", type="password")
        with col_p2:
            telefono = st.text_input("Teléfono de Contacto", placeholder="+34...")
            captcha_user = st.number_input(f"Verificación Humana: ¿Cuánto es {st.session_state.n1} + {st.session_state.n2}?", step=1)

        st.markdown("#### **Paso 3: Términos Legales**")
        acepta_rgpd = st.checkbox("Confirmo que he leído y acepto la Política de Privacidad de SWARCO.")
        
        btn_registrar = st.form_submit_button("FINALIZAR REGISTRO Y CREAR CUENTA", use_container_width=True)

    if btn_registrar:
        # VALIDACIONES ESTRICTAS
        es_valida, mensaje_pass = validar_password(pass1)
        
        if captcha_user != (st.session_state.n1 + st.session_state.n2):
            st.error("❌ Error de verificación humana. Inténtelo de nuevo.")
            # Cambiamos los números para la próxima vez
            st.session_state.n1 = random.randint(1, 10)
            st.session_state.n2 = random.randint(1, 10)
        elif not (nombre and apellido and empresa and email and pass1):
            st.warning("⚠️ Todos los campos con asterisco (*) son obligatorios.")
        elif pass1 != pass2:
            st.error("❌ Las contraseñas no coinciden.")
        elif not es_valida:
            st.error(f"❌ {mensaje_pass}")
        elif not acepta_rgpd:
            st.error("❌ Debe aceptar los términos legales para continuar.")
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
                
                response = requests.post(URL_BRIDGE, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
                
                if response.status_code == 200 and "Éxito" in response.text:
                    st.success(f"✅ ¡Excelente! Usuario '{nombre_completo}' creado. Vaya a la pestaña de Login.")
                    # Limpiamos los números para el siguiente
                    del st.session_state.n1
                    del st.session_state.n2
                else:
                    st.error(f"❌ Error en el servidor de base de datos.")
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")
