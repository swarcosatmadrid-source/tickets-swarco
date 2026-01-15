import streamlit as st
import pandas as pd
import json
import requests
import random
import re
import time

URL_BRIDGE = "https://script.google.com/macros/s/AKfycbyDpHS4nU16O7YyvABvmbFYHTLv2e2J8vrpSD-iCmamjmS4Az6p9iZNUmVEwzMVyzx9/exec"

def chequear_calidad_clave(p):
    if not p: return "", ""
    puntos = 0
    if len(p) >= 8: puntos += 1
    if re.search(r"[A-Z]", p): puntos += 1
    if re.search(r"[0-9]", p): puntos += 1
    if puntos <= 1: return "🔴 Débil", "error"
    if puntos <= 2: return "🟠 Media", "warning"
    return "🟢 Fuerte", "success"

def gestionar_acceso(conn):
    st.markdown("<h2 style='text-align: center; color: #00549F;'>🔐 Acceso Usuarios</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user_in = st.text_input("Usuario (ID)", placeholder="Ej: UTE_Sevilla").strip()
        pass_in = st.text_input("Contraseña", type="password")
        if st.form_submit_button("INGRESAR", use_container_width=True):
            try:
                df = conn.read(worksheet="Usuarios", ttl=0)
                validado = df[(df['Usuario'].astype(str) == user_in) & (df['Password'].astype(str) == pass_in)]
                if not validado.empty:
                    st.session_state.autenticado = True
                    st.session_state.datos_cliente = {'Empresa': validado.iloc[0]['Empresa'], 'Contacto': validado.iloc[0]['Usuario'], 'Email': validado.iloc[0]['Email']}
                    st.rerun()
                else: st.error("❌ Credenciales incorrectas.")
            except Exception as e: st.error(f"Error: {e}")
    return False

def interfaz_registro_legal(conn):
    st.markdown("<h3 style='color: #F29400;'>📝 Registro de Nuevo Usuario o Equipo</h3>", unsafe_allow_html=True)
    st.info("👋 **Bienvenido.** Siga los pasos a continuación para crear su cuenta de acceso al SAT de Swarco.")

    # --- INICIO DEL FORMULARIO PASO A PASO ---
    with st.form("form_registro_v0"):
        
        # PASO 1
        st.markdown("#### **Paso 1: Identificación**")
        st.caption("Defina cómo se identificará en el sistema (ideal para grupos de trabajo o UTEs).")
        usuario_id = st.text_input("Nombre de Usuario / ID de Equipo *", placeholder="Ej: Equipo_Norte_01")
        
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre Responsable *")
            apellido = st.text_input("Apellidos *")
        with c2:
            empresa = st.text_input("Empresa / UTE *")
            email = st.text_input("Email Corporativo *")
        
        st.markdown("---")

        # PASO 2 (Validación dentro del form para que sea intuitivo visualmente)
        st.markdown("#### **Paso 2: Seguridad de la Cuenta**")
        st.caption("Cree una contraseña segura para proteger su acceso.")
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            pass1 = st.text_input("Defina su Clave *", type="password")
            calidad, _ = chequear_calidad_clave(pass1)
            if pass1: st.write(f"Calidad: **{calidad}**")
        with col_p2:
            pass2 = st.text_input("Confirme su Clave *", type="password")
            if pass1 and pass2:
                if pass1 == pass2: st.success("✅ Las claves coinciden")
                else: st.warning("⚠️ Las claves no coinciden")

        st.markdown("---")

        # PASO 3
        st.markdown("#### **Paso 3: Verificación y Legal**")
        st.caption("Cumplimiento del protocolo de seguridad y protección de datos.")
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            telefono = st.text_input("Teléfono móvil de contacto *")
        with col_v2:
            if 'n1' not in st.session_state:
                st.session_state.n1, st.session_state.n2 = random.randint(1, 10), random.randint(1, 10)
            captcha_user = st.number_input(f"¿Cuánto es {st.session_state.n1} + {st.session_state.n2}? *", step=1)

        st.warning("🔒 Sus datos serán tratados siguiendo el reglamento RGPD.")
        acepta_rgpd = st.checkbox("Acepto los términos y condiciones de Swarco SAT *")
        
        # BOTÓN FINAL
        btn_registrar = st.form_submit_button("FINALIZAR REGISTRO", use_container_width=True)

    # Lógica de procesamiento (Fuera del form para persistencia en caso de error)
    if btn_registrar:
        if not (usuario_id and nombre and apellido and empresa and email and pass1 and telefono):
            st.error("❌ Por favor, rellene todos los campos marcados con (*).")
        elif pass1 != pass2:
            st.error("❌ Las claves deben ser idénticas.")
        elif captcha_user != (st.session_state.n1 + st.session_state.n2):
            st.error("❌ La suma de verificación es incorrecta.")
        elif not acepta_rgpd:
            st.error("❌ Debe aceptar el tratamiento de datos para continuar.")
        else:
            try:
                payload = {
                    "Accion": "Registro", "Usuario": usuario_id, "Nombre": nombre, "Apellido": apellido,
                    "Email": email, "Password": pass1, "Empresa": empresa, "Telefono": telefono, "RGPD": "SÍ"
                }
                response = requests.post(URL_BRIDGE, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
                
                if "Éxito" in response.text:
                    st.success("🎊 ¡USUARIO CREADO CORRECTAMENTE!")
                    st.balloons()
                    time.sleep(3)
                    st.rerun()
                else:
                    st.error(f"❌ Error en el servidor: {response.text}")
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")
