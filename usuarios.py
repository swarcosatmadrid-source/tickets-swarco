import streamlit as st
import pandas as pd
import json
import requests
import random
import re
import time

URL_BRIDGE = "https://script.google.com/macros/s/AKfycbyDpHS4nU16O7YyvABvmbFYHTLv2e2J8vrpSD-iCmamjmS4Az6p9iZNUmVEwzMVyzx9/exec"

def validar_password(password):
    if len(password) < 8:
        return False, "Mínimo 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "Falta una mayúscula."
    if not re.search(r"[0-9]", password):
        return False, "Falta un número."
    return True, ""

def interfaz_registro_legal(conn):
    st.markdown("<h3 style='color: #F29400;'>📝 Registro de Nuevo Usuario / Equipo Técnico</h3>", unsafe_allow_html=True)
    
    # Mensaje de confianza técnica
    st.caption("🔒 Sus datos se cifran y almacenan siguiendo el protocolo RGPD de SWARCO.")

    if 'n1' not in st.session_state:
        st.session_state.n1 = random.randint(1, 10)
        st.session_state.n2 = random.randint(1, 10)

    with st.form("form_registro_v0", clear_on_submit=True):
        st.markdown("##### **1. Identificación del Usuario o Equipo**")
        st.info("💡 Si son una UTE o grupo, pueden crear un usuario compartido (ej: 'UTE_Sevilla_Norte').")
        
        # Campo de Usuario creado por ellos
        usuario_id = st.text_input("Nombre de Usuario Deseado *", placeholder="Ej: Equipo_Tecnico_Swarco").strip()
        
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre del Responsable / Equipo *").strip()
            apellido = st.text_input("Apellidos *").strip()
        with c2:
            empresa = st.text_input("Empresa / UTE *").strip()
            email = st.text_input("Email Corporativo *").strip()

        st.markdown("---")
        st.markdown("##### **2. Credenciales y Seguridad**")
        
        cp1, cp2 = st.columns(2)
        with cp1:
            pass1 = st.text_input("Defina su Clave (8+ carac, Mayús, Núm) *", type="password")
            pass2 = st.text_input("Confirme su Clave *", type="password")
            
            # Validación inmediata visual
            if pass1 and pass2 and pass1 != pass2:
                st.error("⚠️ Las claves no coinciden actualmente.")
            elif pass1 and pass2 and pass1 == pass2:
                st.success("✅ Las claves coinciden.")

        with cp2:
            telefono = st.text_input("Teléfono de contacto móvil *")
            captcha_user = st.number_input(f"Validación de Seguridad: {st.session_state.n1} + {st.session_state.n2}?", step=1)

        st.markdown("---")
        st.markdown("##### **3. Consentimiento Legal**")
        st.warning("⚠️ Todos los campos son de carácter obligatorio para el acceso al SAT.")
        acepta_rgpd = st.checkbox("Acepto que SWARCO trate mis datos para la gestión técnica de incidencias.")
        
        btn_registrar = st.form_submit_button("VALIDAR Y CREAR CUENTA", use_container_width=True)

    if btn_registrar:
        es_valida, msg_p = validar_password(pass1)
        
        # VALIDACIONES
        if not (usuario_id and nombre and apellido and empresa and email and pass1 and telefono):
            st.error("❌ Error: Todos los campos marcados con (*) son obligatorios.")
        elif pass1 != pass2:
            st.error("❌ Error: Las contraseñas deben ser idénticas.")
        elif not es_valida:
            st.error(f"❌ Seguridad de Clave: {msg_p}")
        elif captcha_user != (st.session_state.n1 + st.session_state.n2):
            st.error("❌ Verificación humana incorrecta.")
        elif not acepta_rgpd:
            st.error("❌ Debe aceptar el tratamiento de datos (RGPD).")
        else:
            try:
                # Comprobar duplicado en el Sheet
                df_actual = conn.read(worksheet="Usuarios", ttl=0)
                if usuario_id.lower() in df_actual['Usuario'].str.lower().values:
                    st.error(f"⚠️ El nombre de usuario '{usuario_id}' ya está en uso. Elija otro.")
                else:
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
                    
                    response = requests.post(URL_BRIDGE, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
                    
                    if response.status_code == 200 and "Éxito" in response.text:
                        st.success("🎊 ¡USUARIO CREADO CORRECTAMENTE!")
                        st.info("Redirigiendo a la página de inicio...")
                        time.sleep(3) # Pausa para que lean el mensaje de éxito
                        
                        # Limpiar y volver al inicio
                        st.session_state.autenticado = False
                        st.rerun()
                    else:
                        st.error("❌ Error en el enlace con la base de datos.")
            except Exception as e:
                st.error(f"❌ Error de conexión: {e}")
