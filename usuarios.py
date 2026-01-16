# =============================================================================
# ARCHIVO: usuarios.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 2.2.0 (Restauración de Validación por Labels)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Registro detallado con validación visual nativa estable.
# =============================================================================

import streamlit as st
import pandas as pd
import hashlib
import estilos
import correo 

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("login_tit", "Acceso")}</p>', unsafe_allow_html=True)
    with st.form("login_form"):
        email = st.text_input(t.get("user_id", "Usuario")).lower().strip()
        password = st.text_input(t.get("pass", "Contraseña"), type='password')
        if st.form_submit_button(t.get("btn_entrar", "INGRESAR")):
            try:
                ws = conn.worksheet("Usuarios")
                df = pd.DataFrame(ws.get_all_records())
                if not df.empty and email in df['email'].values:
                    stored_pass = df.loc[df['email'] == email, 'password'].values[0]
                    if encriptar_password(password) == stored_pass:
                        st.session_state.autenticado = True
                        st.session_state.user_email = email
                        st.session_state.pagina_actual = 'menu' 
                        st.rerun()
                st.error(t.get("no_match", "Error de acceso"))
            except: st.error("Error de conexión")
    if st.button(t.get("btn_ir_registro", "Registrarse")):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "Registro")}</p>', unsafe_allow_html=True)
    
    if 'errores_registro' not in st.session_state:
        st.session_state.errores_registro = []

    def label_error(texto, clave):
        if clave in st.session_state.errores_registro:
            return f":red[{texto} *]"
        return f"{texto} *"

    with st.form("registro_maestro"):
        st.subheader(t.get("p1_tit", "1. Identificación"))
        c1, c2 = st.columns(2)
        with c1: nombre = st.text_input(label_error(t.get("nombre", "Nombre"), "nombre"))
        with c2: apellido = st.text_input(label_error(t.get("apellido", "Apellido"), "apellido"))
        
        st.subheader(t.get("p2_tit", "2. Ubicación"))
        c3, c4 = st.columns(2)
        with c3: empresa = st.text_input(label_error(t.get("cliente", "Empresa"), "empresa"))
        with c4: pais = st.text_input(label_error(t.get("pais", "País"), "pais"))
        
        email = st.text_input(label_error(t.get("email", "Email"), "email")).lower().strip()
        tel = st.text_input(label_error(t.get("tel", "Teléfono"), "tel"))

        st.subheader(t.get("p3_tit", "3. Seguridad"))
        pass1 = st.text_input(label_error(t.get("pass", "Contraseña"), "pass1"), type="password")
        pass2 = st.text_input(label_error(t.get("pass_rep", "Repetir Contraseña"), "pass2"), type="password")

        acepta = st.checkbox(t.get("acepto", "Acepto") + t.get("link_texto", " Política"))

        if st.form_submit_button(t.get("btn_registro_final", "REGISTRAR")):
            st.session_state.errores_registro = []
            # Lógica de validación
            if not nombre: st.session_state.errores_registro.append("nombre")
            if not apellido: st.session_state.errores_registro.append("apellido")
            if not empresa: st.session_state.errores_registro.append("empresa")
            if not pais: st.session_state.errores_registro.append("pais")
            if not email: st.session_state.errores_registro.append("email")
            if not tel: st.session_state.errores_registro.append("tel")
            if not pass1: st.session_state.errores_registro.append("pass1")
            if not acepta: st.session_state.errores_registro.append("acepta")

            if st.session_state.errores_registro:
                st.error("⚠️ Rellene los campos que se encuentran en rojo")
                st.rerun()
            elif pass1 != pass2:
                st.error(t.get("no_match", "Las claves no coinciden"))
            else:
                try:
                    ws = conn.worksheet("Usuarios")
                    ws.append_row([nombre, apellido, empresa, pais, email, tel, encriptar_password(pass1)])
                    correo.enviar_correo_bienvenida(email, nombre, email, "********")
                    st.success(t.get("exito_reg", "¡Éxito!"))
                    st.session_state.mostrar_registro = False
                    st.rerun()
                except: st.error("Error al guardar")

    if st.button(t.get("btn_volver", "VOLVER")):
        st.session_state.mostrar_registro = False
        st.session_state.errores_registro = []
        st.rerun()
