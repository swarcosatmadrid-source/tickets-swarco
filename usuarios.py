# ==========================================
# ARCHIVO: usuarios.py
# PROYECTO: TicketV0
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Gestión de login y registro original.
# ==========================================
import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import estilos

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    estilos.mostrar_logo()
    st.subheader(t.get('login_title', 'Acceso SAT'))
    with st.form("login_form"):
        email = st.text_input(t.get('email_label', 'Correo')).lower().strip()
        password = st.text_input(t.get('pass_label', 'Contraseña'), type='password')
        submit = st.form_submit_button(t.get('btn_login', 'Entrar'))
        if submit:
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
            except: st.error("Error de conexión")

    if st.button(t.get('btn_go_register', 'Registrarse')):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    st.subheader(t.get('reg_title', 'Registro'))
    with st.form("reg_form"):
        nombre = st.text_input(t.get('name_label', 'Nombre'))
        email = st.text_input(t.get('email_label', 'Email'))
        telefono = st.text_input(t.get('phone_label', 'Teléfono'))
        pass1 = st.text_input(t.get('pass_label', 'Contraseña'), type='password')
        pass2 = st.text_input(t.get('confirm_pass', 'Confirmar'), type='password')
        submit = st.form_submit_button(t.get('btn_register', 'Registrar'))
        if submit:
            if pass1 == pass2:
                try:
                    ws = conn.worksheet("Usuarios")
                    ws.append_row([nombre, email, encriptar_password(pass1), telefono, datetime.now().strftime("%Y-%m-%d")])
                    st.success(t.get('success_reg', 'OK'))
                    st.session_state.mostrar_registro = False
                    st.rerun()
                except: st.error("Error al guardar")
            else: st.error("Las contraseñas no coinciden")
