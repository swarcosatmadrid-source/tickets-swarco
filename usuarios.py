import streamlit as st
import pandas as pd
import json
import requests
import random
import re
import time
from idiomas import traducir_interfaz # Importamos tu función

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
    # Detectamos el idioma desde el inicio
    idioma_actual = st.session_state.get('idioma', 'Castellano')
    t = traducir_interfaz(idioma_actual)

    st.markdown(f"<h2 style='text-align: center; color: #00549F;'>{t.get('login_tit', '🔐 Acceso Usuarios')}</h2>", unsafe_allow_html=True)
    with st.form("login_form"):
        user_in = st.text_input(t.get('user_id', 'Usuario (ID)'), placeholder="Ej: Equipo_Levante").strip()
        pass_in = st.text_input(t.get('pass', 'Contraseña'), type="password")
        if st.form_submit_button(t.get('btn_entrar', 'INGRESAR'), use_container_width=True):
            try:
                df = conn.read(worksheet="Usuarios", ttl=0)
                validado = df[(df['Usuario'].astype(str) == user_in) & (df['Password'].astype(str) == pass_in)]
                if not validado.empty:
                    st.session_state.autenticado = True
                    st.session_state.datos_cliente = {'Empresa': validado.iloc[0]['Empresa'], 'Contacto': validado.iloc[0]['Usuario'], 'Email': validado.iloc[0]['Email']}
                    st.rerun()
                else: st.error(t.get('error_cred', "❌ Credenciales incorrectas."))
            except Exception as e: st.error(f"Error: {e}")
    return False

def interfaz_registro_legal(conn):
    # Detectamos idioma
    idioma_actual = st.session_state.get('idioma', 'Castellano')
    t = traducir_interfaz(idioma_actual)

    # 1. CONTROL DE BORRADO: Éxito
    if st.session_state.get('registro_exitoso', False):
        st.success(t.get('exito_reg', "✨ **¡Usuario creado con éxito! Bienvenidos a Swarco Spain SAT.**"))
        st.info(t.get('redir_login', "🔄 Redirigiendo automáticamente a la página de inicio de sesión..."))
        time.sleep(3)
        st.session_state.registro_exitoso = False
        # IMPORTANTE: Cambiamos el estado para que vuelva al login
        st.session_state.mostrar_registro = False 
        st.rerun()
        return

    st.markdown(f"<h3 style='color: #F29400;'>{t.get('reg_tit', '📝 Registro de Nuevo Usuario / Equipo')}</h3>", unsafe_allow_html=True)
    
    # --- EL CONSEJO ---
    st.info(t.get('consejo', "💡 Los campos se validan automáticamente al cambiar de casilla."))

    # --- PASO 1 Y 2 FUERA DEL FORM ---
    st.markdown(f"#### **{t.get('p1_tit', 'Paso 1: Identificación')}**")
    st.caption(t.get('p1_sub', "Defina su identidad en el sistema."))
    usuario_id = st.text_input(t.get('user_id', 'Nombre de Usuario / ID de Equipo *'), placeholder="Ej: UTE_Madrid_Sur")
    
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("Nombre / Name *")
        apellido = st.text_input("Apellidos / Last Name *")
    with c2:
        empresa = st.text_input(t.get('cliente', 'Empresa / UTE') + " *")
        email = st.text_input(t.get('email', 'Email Corporativo') + " *")

    st.markdown("---")
    st.markdown(f"#### **{t.get('p2_tit', 'Paso 2: Seguridad de la Cuenta')}**")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        pass1 = st.text_input(t.get('pass', 'Defina su Clave') + " *", type="password")
        calidad, _ = chequear_calidad_clave(pass1)
        if pass1: st.write(f"Calidad: **{calidad}**")
    with col_p2:
        pass2 = st.text_input(t.get('pass_conf', 'Confirme su Clave') + " *", type="password")
        if pass1 and pass2:
            if pass1 == pass2: st.success(t.get('match', "✅ Las claves coinciden"))
            else: st.error(t.get('no_match', "⚠️ Las claves NO coinciden"))

    st.markdown("---")

    # --- PASO 3 DENTRO DEL FORM ---
    with st.form("form_registro_final"):
        st.markdown(f"#### **{t.get('p3_tit', 'Paso 3: Verificación y Legal')}**")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            telefono = st.text_input(t.get('tel', 'Teléfono móvil de contacto') + " *")
        with col_v2:
            if 'n1' not in st.session_state:
                st.session_state.n1, st.session_state.n2 = random.randint(1, 10), random.randint(1, 10)
            captcha_user = st.number_input(f"Seguridad: {st.session_state.n1} + {st.session_state.n2}?", step=1)

        st.warning("🔒 RGPD / Privacy Policy")
        acepta_rgpd = st.checkbox(t.get('rgpd', 'Acepto los términos y condiciones *'))
        
        btn_registrar = st.form_submit_button(t.get('btn_generar', 'FINALIZAR REGISTRO'), use_container_width=True)

    if btn_registrar:
        if not (usuario_id and nombre and apellido and empresa and email and pass1 and telefono):
            st.error(t.get('error_campos', "❌ Por favor, rellene todos los campos obligatorios."))
        elif pass1 != pass2:
            st.error("❌ Passwords match error")
        elif captcha_user != (st.session_state.n1 + st.session_state.n2):
            st.error("❌ Captcha error")
        elif not acepta_rgpd:
            st.error("❌ RGPD error")
        else:
            try:
                payload = {
                    "Accion": "Registro", "Usuario": usuario_id, "Nombre": nombre, "Apellido": apellido,
                    "Email": email, "Password": pass1, "Empresa": empresa, "Telefono": telefono, "RGPD": "SÍ"
                }
                response = requests.post(URL_BRIDGE, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
                
                if "Éxito" in response.text:
                    st.session_state.registro_exitoso = True
                    st.rerun()
                else:
                    st.error(f"❌ Error: {response.text}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
