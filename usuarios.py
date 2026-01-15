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
    if re.search(r"[!@#$%^&*]", p): puntos += 1
    
    if puntos <= 1: return "🔴 Débil", "error"
    if puntos <= 3: return "🟠 Media", "warning"
    return "🟢 Fuerte", "success"

def gestionar_acceso(conn):
    st.markdown("<h2 style='text-align: center; color: #00549F;'>🔐 Acceso Usuarios</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user_in = st.text_input("Usuario (ID)").strip()
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
    st.markdown("<h3 style='color: #F29400;'>📝 Registro de Usuario o Equipo</h3>", unsafe_allow_html=True)
    
    # --- VALIDACIÓN EN TIEMPO REAL (Fuera del Form) ---
    st.markdown("##### **Configuración de Seguridad**")
    c_p1, c_p2 = st.columns(2)
    with c_p1:
        pass1 = st.text_input("Defina su Clave *", type="password", help="Mínimo 8 caracteres, Mayúscula y Número recomendados.")
        calidad, tipo = chequear_calidad_clave(pass1)
        if calidad: st.write(f"Calidad de clave: **{calidad}**")
    with c_p2:
        pass2 = st.text_input("Confirme su Clave *", type="password")
        if pass1 and pass2:
            if pass1 == pass2: st.success("✅ Las claves coinciden")
            else: st.error("⚠️ Las claves NO coinciden")

    # --- RESTO DEL FORMULARIO ---
    if 'n1' not in st.session_state:
        st.session_state.n1, st.session_state.n2 = random.randint(1, 10), random.randint(1, 10)

    # Nota: No usamos clear_on_submit=True para que no se borre si hay error
    with st.form("form_registro_v0"):
        st.markdown("##### **Datos de Identificación**")
        usuario_id = st.text_input("Nombre de Usuario / ID de Equipo *")
        
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre Responsable *")
            apellido = st.text_input("Apellidos *")
        with col2:
            empresa = st.text_input("Empresa / UTE *")
            email = st.text_input("Email Corporativo *")
            
        telefono = st.text_input("Teléfono móvil *")
        captcha_user = st.number_input(f"Seguridad: {st.session_state.n1} + {st.session_state.n2}?", step=1)
        acepta_rgpd = st.checkbox("Acepto el tratamiento de mis datos (RGPD) *")
        
        btn_registrar = st.form_submit_button("CREAR CUENTA SEGURA", use_container_width=True)

    if btn_registrar:
        if not (usuario_id and nombre and apellido and empresa and email and pass1 and telefono):
            st.error("❌ Todos los campos son obligatorios.")
        elif pass1 != pass2:
            st.error("❌ Las contraseñas no coinciden.")
        elif captcha_user != (st.session_state.n1 + st.session_state.n2):
            st.error("❌ Validación humana incorrecta.")
        elif not acepta_rgpd:
            st.error("❌ Debe aceptar la política de datos.")
        else:
            try:
                payload = {
                    "Accion": "Registro", "Usuario": usuario_id, "Nombre": nombre, "Apellido": apellido,
                    "Email": email, "Password": pass1, "Empresa": empresa, "Telefono": telefono, "RGPD": "SÍ"
                }
                response = requests.post(URL_BRIDGE, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
                
                if "Éxito" in response.text:
                    st.success("🎊 ¡USUARIO CREADO CORRECTAMENTE!")
                    time.sleep(2)
                    # Aquí es donde realmente limpiamos y redirigimos
                    st.rerun()
                else:
                    st.error(f"❌ Error en base de datos: {response.text}")
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")
