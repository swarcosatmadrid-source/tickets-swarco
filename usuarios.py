# ==========================================
# ARCHIVO: usuarios.py | PROYECTO: TicketV1
# DESCRIPCIÓN: Login y Registro con estética original.
# ==========================================
import streamlit as st
import pandas as pd
import hashlib
import estilos

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    estilos.mostrar_logo()
    st.markdown('<p class="swarco-title">Swarco Traffic Spain</p>', unsafe_allow_html=True)
    st.markdown('<p class="swarco-subtitle">🔐 Acceso Usuarios Registrados</p>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("Usuario / ID").lower().strip()
        password = st.text_input("Contraseña", type='password')
        if st.form_submit_button("INGRESAR AL SISTEMA"):
            try:
                ws = conn.worksheet("Usuarios")
                df = pd.DataFrame(ws.get_all_records())
                if not df.empty and email in df['email'].values:
                    stored_pass = df.loc[df['email'] == email, 'password'].values[0]
                    if encriptar_password(password) == stored_pass:
                        st.session_state.autenticado = True
                        st.session_state.user_email = email
                        st.rerun()
                    else: st.error("Contraseña incorrecta")
                else: st.error("Usuario no registrado")
            except: st.error("Error de conexión")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("No tengo cuenta, quiero registrarme"):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    st.markdown('<p class="swarco-title">Registro de Usuario</p>', unsafe_allow_html=True)
    with st.form("reg_form"):
        nombre = st.text_input("Nombre Completo")
        email = st.text_input("Email Corporativo")
        pass1 = st.text_input("Contraseña", type='password')
        pass2 = st.text_input("Repetir Contraseña", type='password')
        if st.form_submit_button("CREAR MI CUENTA"):
            # Lógica de guardado...
            pass
    if st.button("Volver atrás"):
        st.session_state.mostrar_registro = False
        st.rerun()
