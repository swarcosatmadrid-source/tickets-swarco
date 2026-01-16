# ==========================================
# ARCHIVO: usuarios.py
# PROYECTO: TicketV0 -> MEJORA: SEGURIDAD
# VERSIÓN: v1.1 (Validaciones Activas)
# FECHA: 16-Ene-2026
# COMPARACIÓN: Basado en v1.0 (Original Hoy). 
#              Mantiene 100% el diseño original.
# ==========================================

import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import estilos

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    """Interfaz de login (IDÉNTICA A V1.0)"""
    estilos.mostrar_logo()
    st.markdown("---")
    
    with st.container():
        st.subheader(t.get('login_title', 'Acceso SAT'))
        with st.form("login_form"):
            email = st.text_input(t.get('email_label', 'Correo')).lower().strip()
            password = st.text_input(t.get('pass_label', 'Contraseña'), type='password')
            submit = st.form_submit_button(t.get('btn_login', 'ENTRAR'))

            if submit:
                if not conn:
                    st.error("Error: Sin conexión.")
                    return
                try:
                    ws = conn.worksheet("Usuarios")
                    df = pd.DataFrame(ws.get_all_records())
                    if not df.empty and email in df['email'].values:
                        stored_pass = df.loc[df['email'] == email, 'password'].values[0]
                        if encriptar_password(password) == stored_pass:
                            st.session_state.autenticado = True
                            st.session_state.user_email = email
                            st.rerun()
                        else: st.error(t.get('err_invalid_pass', 'Contraseña incorrecta'))
                    else: st.error(t.get('err_user_not_found', 'Usuario no registrado'))
                except Exception as e:
                    st.error(f"Error técnico: {e}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(t.get('btn_go_register', '¿No tienes cuenta? Regístrate aquí')):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    """Registro con validación de clave y duplicados."""
    st.subheader(t.get('reg_title', 'Registro de Usuario'))
    
    with st.form("reg_form"):
        nombre = st.text_input(t.get('name_label', 'Nombre'))
        email = st.text_input(t.get('email_label', 'Email')).lower().strip()
        telefono = st.text_input(t.get('phone_label', 'Teléfono'))
        pass1 = st.text_input(t.get('pass_label', 'Contraseña'), type='password')
        pass2 = st.text_input(t.get('confirm_pass', 'Confirmar Contraseña'), type='password')
        
        submit = st.form_submit_button(t.get('btn_register', 'REGISTRAR'))

        if submit:
            # --- NUEVAS VALIDACIONES (PACTO DE COMPARACIÓN) ---
            if pass1 != pass2:
                st.error(t.get('err_pass_match', 'Las contraseñas no coinciden'))
                return

            if len(pass1) < 6:
                st.error("❌ La contraseña debe tener al menos 6 caracteres.")
                return

            try:
                ws = conn.worksheet("Usuarios")
                df = pd.DataFrame(ws.get_all_records())
                
                # Validación de Usuario Duplicado
                if not df.empty and email in df['email'].values:
                    st.error("❌ Este correo electrónico ya está registrado.")
                    return

                # Si pasa las pruebas, se guarda
                ws.append_row([nombre, email, encriptar_password(pass1), telefono, datetime.now().strftime("%Y-%m-%d")])
                st.success(t.get('success_reg', '¡Registrado con éxito!'))
                st.session_state.mostrar_registro = False
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")

    if st.button(t.get('btn_back_login', 'Volver al Login')):
        st.session_state.mostrar_registro = False
        st.rerun()
