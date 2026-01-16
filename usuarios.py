# ==========================================
# ARCHIVO: usuarios.py
# PROYECTO: TicketV0
# VERSIÓN: v1.4 (Pacto de Comparación)
# FECHA: 16-Ene-2026
# ==========================================
import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
import estilos

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    # 1. Mundito de idiomas (superior derecha)
    col_v, col_m = st.columns([0.9, 0.1])
    with col_m:
        st.markdown("### 🌐")

    estilos.mostrar_logo()
    estilos.mostrar_cabecera_swarco()
    
    # 2. Formulario de Acceso
    with st.container():
        with st.form("login_form"):
            email = st.text_input(t.get('email_label', 'Correo')).lower().strip()
            password = st.text_input(t.get('pass_label', 'Contraseña'), type='password')
            submit = st.form_submit_button("ENTRAR")

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

    # 3. Botón de Registro fuera del cuadro
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("¿NO TIENES CUENTA? REGÍSTRATE AQUÍ"):
        st.session_state.mostrar_registro = True
        st.rerun()

    # 4. Footer Swarco
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #999; font-size: 12px;">
            SWARCO | First Choice in Traffic Solutions<br>
            <a href="#" style="color:#999; text-decoration:none;">Legal Notice</a> | 
            <a href="#" style="color:#999; text-decoration:none;">Privacy Policy</a>
        </div>
    """, unsafe_allow_html=True)

def interfaz_registro_legal(conn, t):
    st.subheader(t.get('reg_title', 'Registro'))
    with st.form("reg_form"):
        nombre = st.text_input("Nombre")
        email = st.text_input("Email")
        telefono = st.text_input("Teléfono")
        pass1 = st.text_input("Contraseña", type='password')
        pass2 = st.text_input("Confirmar", type='password')
        
        if st.form_submit_button("REGISTRAR"):
            if pass1 == pass2:
                try:
                    ws = conn.worksheet("Usuarios")
                    ws.append_row([nombre, email, encriptar_password(pass1), telefono, datetime.now().strftime("%Y-%m-%d")])
                    st.success("Registrado!")
                    st.session_state.mostrar_registro = False
                    st.rerun()
                except: st.error("Error al guardar")
            else: st.error("Las contraseñas no coinciden")

    if st.button("Volver al Login"):
        st.session_state.mostrar_registro = False
        st.rerun()
