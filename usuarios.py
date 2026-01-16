# ==========================================
# ARCHIVO: usuarios.py
# PROYECTO: TicketV1
# VERSIÓN: v1.4 (Sincronización Estricta con Original)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Basado 100% en el código del usuario. 
#              Se añaden validaciones de seguridad para clave y 
#              detección de usuarios existentes sin alterar la estructura.
# ==========================================

import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime

# --- FUNCIONES DE SEGURIDAD (Originales) ---
def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    """Estructura original del usuario."""
    st.subheader(t.get('login_title', 'Acceso SAT'))
    
    with st.form("login_form"):
        email = st.text_input(t.get('email_label', 'Correo')).lower().strip()
        password = st.text_input(t.get('pass_label', 'Contraseña'), type='password')
        submit = st.form_submit_button(t.get('btn_login', 'Entrar'))

        if submit:
            if not conn:
                st.error("Error: Sin conexión")
                return

            try:
                # Mantiene tu lógica de gspread
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
                    st.error(t.get('err_user_not_found', 'Usuario no registrado'))
            except Exception as e:
                st.error(f"Error técnico: {e}")

    if st.button(t.get('btn_go_register', 'Registrarse')):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    """Estructura original del usuario con parches de validación."""
    st.subheader(t.get('reg_title', 'Registro'))

    with st.form("reg_form"):
        nombre = st.text_input(t.get('name_label', 'Nombre'))
        email = st.text_input(t.get('email_label', 'Email')).lower().strip()
        # MEJORA: Input simple para evitar la lentitud que reportaste
        telefono = st.text_input(t.get('phone_label', 'Teléfono'))
        pass1 = st.text_input(t.get('pass_label', 'Contraseña'), type='password')
        pass2 = st.text_input(t.get('confirm_pass', 'Repetir Contraseña'), type='password')
        
        submit = st.form_submit_button(t.get('btn_register', 'Registrar'))

        if submit:
            # VALIDACIONES SOLICITADAS
            if pass1 != pass2:
                st.error(t.get('err_pass_match', 'Las contraseñas no coinciden'))
                return
            
            # Chequeo de longitud de clave
            if len(pass1) < 6:
                st.error("❌ La clave es muy corta (mínimo 6 caracteres)")
                return

            try:
                ws = conn.worksheet("Usuarios")
                df = pd.DataFrame(ws.get_all_records())

                # Chequeo de duplicados
                if not df.empty and email in df['email'].values:
                    st.error("❌ Este usuario ya existe en la base de datos")
                else:
                    # Registro (Tu lógica de append_row)
                    nueva_fila = [
                        nombre, 
                        email, 
                        encriptar_password(pass1), 
                        telefono, 
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ]
                    ws.append_row(nueva_fila)
                    st.success(t.get('success_reg', 'Usuario creado correctamente'))
                    st.session_state.mostrar_registro = False
            except Exception as e:
                st.error(f"Error al guardar: {e}")

    if st.button(t.get('btn_back_login', 'Volver')):
        st.session_state.mostrar_registro = False
        st.rerun()
