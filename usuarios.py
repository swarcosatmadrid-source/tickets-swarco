# ==========================================
# ARCHIVO: usuarios.py
# PROYECTO: TicketV0
# VERSIÓN: v1.5 (LOOK RECUPERADO DE FOTO)
# ==========================================
import streamlit as st
import pandas as pd
import hashlib
import estilos

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    estilos.mostrar_logo()
    
    # Encabezado de la foto
    st.markdown('<p class="swarco-title">Swarco Traffic Spain</p>', unsafe_allow_html=True)
    st.markdown('<p class="swarco-subtitle">🔐 Acceso Usuarios Registrados</p>', unsafe_allow_html=True)
    
    with st.container():
        with st.form("login_form"):
            email = st.text_input("Usuario / ID").lower().strip()
            password = st.text_input("Contraseña", type='password')
            submit = st.form_submit_button("INGRESAR AL SISTEMA")

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
                        else: st.error("Contraseña incorrecta")
                    else: st.error("Usuario no registrado")
                except: st.error("Error de conexión")

    st.markdown("<br>", unsafe_allow_html=True)
    # Botón naranja de abajo
    if st.button("No tengo cuenta, quiero registrarme"):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    st.markdown('<p class="swarco-title">Registro SAT</p>', unsafe_allow_html=True)
    with st.form("reg_form"):
        nombre = st.text_input("Nombre")
        email = st.text_input("Email")
        pass1 = st.text_input("Contraseña", type='password')
        pass2 = st.text_input("Confirmar Contraseña", type='password')
        if st.form_submit_button("CREAR CUENTA"):
            if pass1 == pass2:
                try:
                    ws = conn.worksheet("Usuarios")
                    ws.append_row([nombre, email, encriptar_password(pass1)])
                    st.success("¡Registrado!")
                    st.session_state.mostrar_registro = False
                    st.rerun()
                except: st.error("Error")
            else: st.error("Las contraseñas no coinciden")

    if st.button("Volver al Inicio"):
        st.session_state.mostrar_registro = False
        st.rerun()
