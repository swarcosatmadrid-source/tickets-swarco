# ==========================================
# ARCHIVO: usuarios.py
# PROYECTO: TicketV1
# VERSIÓN: v1.4 (Mejora de Errores y Teléfono)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Optimización de validación de registro.
#              Añadidos mensajes claros para claves débiles o usuarios duplicados.
# ==========================================

import streamlit as st
import pandas as pd
import hashlib
import re
from datetime import datetime

# Función para encriptar claves
def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    """Interfaz de Login mejorada con feedback claro"""
    st.subheader(t.get('login_title', 'Acceso SAT'))
    
    with st.form("login_form"):
        email = st.text_input(t.get('email_label', 'Correo Electrónico')).lower().strip()
        password = st.text_input(t.get('pass_label', 'Contraseña'), type='password')
        submit = st.form_submit_button(t.get('btn_login', 'Entrar'))

        if submit:
            if not conn:
                st.error("❌ Sistema Offline. Contacte a soporte.")
                return

            try:
                # Buscamos en la pestaña 'Usuarios'
                ws = conn.worksheet("Usuarios")
                df = pd.DataFrame(ws.get_all_records())
                
                if not df.empty and email in df['email'].values:
                    stored_pass = df.loc[df['email'] == email, 'password'].values[0]
                    if encriptar_password(password) == stored_pass:
                        st.session_state.autenticado = True
                        st.session_state.user_email = email
                        st.rerun()
                    else:
                        st.error("❌ " + t.get('err_invalid_pass', 'Contraseña incorrecta'))
                else:
                    st.error("❌ " + t.get('err_user_not_found', 'Usuario no registrado'))
            except Exception as e:
                st.error(f"🔥 Error en Login: {e}")

    # Botón para ir a registro
    if st.button(t.get('btn_go_register', '¿No tienes cuenta? Regístrate')):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    """Interfaz de Registro con validaciones claras (Clave y Teléfono)"""
    st.subheader(t.get('reg_title', 'Registro de Usuario'))

    with st.form("reg_form"):
        nombre = st.text_input(t.get('name_label', 'Nombre Completo'))
        email = st.text_input(t.get('email_label', 'Correo')).lower().strip()
        telefono = st.text_input(t.get('phone_label', 'Teléfono (Ej: +34600000000)'))
        pass1 = st.text_input(t.get('pass_label', 'Contraseña'), type='password')
        pass2 = st.text_input(t.get('confirm_pass', 'Repetir Contraseña'), type='password')
        
        submit = st.form_submit_button(t.get('btn_register', 'Crear Cuenta'))

        if submit:
            # --- 1. VALIDACIONES DE SEGURIDAD ---
            # Verificación de campos vacíos
            if not nombre or not email or not pass1:
                st.warning("⚠️ " + t.get('warn_fields', 'Por favor, rellena los campos obligatorios.'))
                return

            # Verificación de claves coinciden
            if pass1 != pass2:
                st.error("❌ " + t.get('err_pass_match', 'Las contraseñas no coinciden.'))
                return

            # Verificación de longitud de clave (LO QUE PEDISTE)
            if len(pass1) < 6:
                st.error("❌ " + t.get('err_pass_weak', 'La clave es muy débil. Debe tener al menos 6 caracteres.'))
                return

            # Verificación de formato de email
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("❌ " + t.get('err_invalid_email', 'Formato de correo no válido.'))
                return

            try:
                ws = conn.worksheet("Usuarios")
                df = pd.DataFrame(ws.get_all_records())

                # Verificación si el usuario ya existe (DUPLICADOS)
                if not df.empty and email in df['email'].values:
                    st.error("❌ " + t.get('err_user_exists', 'Este correo ya está registrado.'))
                else:
                    # Registro exitoso
                    nueva_fila = [
                        nombre, 
                        email, 
                        encriptar_password(pass1), 
                        telefono, 
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                    ws.append_row(nueva_fila)
                    st.success("✅ " + t.get('success_reg', 'Usuario registrado con éxito.'))
                    st.session_state.mostrar_registro = False
                    # No hacemos rerun directo para que el usuario vea el mensaje de éxito
            except Exception as e:
                st.error(f"🔥 Error al guardar: {e}")

    if st.button(t.get('btn_back_login', 'Volver al Login')):
        st.session_state.mostrar_registro = False
        st.rerun()
