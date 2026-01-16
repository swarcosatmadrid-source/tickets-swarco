# ==========================================
# ARCHIVO: usuarios.py
# PROYECTO: TicketV1
# VERSIÓN: v1.4 (Sincronizado & Corregido)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Mantiene TODA la estructura original de v1.0.
#              Se añaden alertas específicas para:
#              - Clave menor a 6 caracteres.
#              - Usuario ya existente en la base de datos.
#              - Se optimiza el input de teléfono para evitar lentitud.
# ==========================================

import streamlit as st
import pandas as pd
import hashlib
import re
from datetime import datetime

# Función para encriptar (Se mantiene igual)
def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    """Mantiene la lógica original de login"""
    st.subheader(t.get('login_title', 'Acceso SAT'))
    
    with st.form("login_form"):
        email = st.text_input(t.get('email_label', 'Correo')).lower().strip()
        password = st.text_input(t.get('pass_label', 'Contraseña'), type='password')
        submit = st.form_submit_button(t.get('btn_login', 'Entrar'))

        if submit:
            if not conn:
                st.error("Error de conexión con la base de datos")
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
                    else:
                        st.error(t.get('err_invalid_pass', 'Contraseña incorrecta'))
                else:
                    st.error(t.get('err_user_not_found', 'Usuario no encontrado'))
            except Exception as e:
                st.error(f"Error: {e}")

    if st.button(t.get('btn_go_register', 'Registrarse')):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    """Mantiene la estructura original pero con las alertas que pediste"""
    st.subheader(t.get('reg_title', 'Registro'))

    with st.form("reg_form"):
        nombre = st.text_input(t.get('name_label', 'Nombre'))
        email = st.text_input(t.get('email_label', 'Email')).lower().strip()
        # CAMBIO: Usamos text_input simple para que no tarde en cargar
        telefono = st.text_input(t.get('phone_label', 'Teléfono'))
        pass1 = st.text_input(t.get('pass_label', 'Contraseña'), type='password')
        pass2 = st.text_input(t.get('confirm_pass', 'Repetir Contraseña'), type='password')
        
        submit = st.form_submit_button(t.get('btn_register', 'Registrar'))

        if submit:
            # --- COMPARACIÓN Y VALIDACIÓN ---
            if pass1 != pass2:
                st.error(t.get('err_pass_match', 'Las contraseñas no coinciden'))
                return
            
            # Alerta de clave débil (Lo que pediste)
            if len(pass1) < 6:
                st.error("❌ La clave debe tener al menos 6 caracteres")
                return

            try:
                ws = conn.worksheet("Usuarios")
                df = pd.DataFrame(ws.get_all_records())

                # Alerta de usuario duplicado (Lo que pediste)
                if not df.empty and email in df['email'].values:
                    st.error("❌ Este correo ya está registrado")
                else:
                    # Si todo está bien, registramos
                    nueva_fila = [nombre, email, encriptar_password(pass1), telefono, datetime.now().strftime("%Y-%m-%d")]
                    ws.append_row(nueva_fila)
                    st.success(t.get('success_reg', 'Registrado correctamente'))
                    st.session_state.mostrar_registro = False
            except Exception as e:
                st.error(f"Error al guardar: {e}")

    if st.button(t.get('btn_back_login', 'Volver')):
        st.session_state.mostrar_registro = False
        st.rerun()
