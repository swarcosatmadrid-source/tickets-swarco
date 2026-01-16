# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 2.1.0 (Restauración Total de Formulario de Registro)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Gestiona el acceso y el registro detallado de 4 pasos.
# =============================================================================

import streamlit as st
import pandas as pd
import hashlib
import estilos
import correo  # Para enviar la bienvenida

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    """Página de Login"""
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("login_tit", "Acceso")}</p>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input(t.get("user_id", "Usuario / ID")).lower().strip()
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
                    else: st.error(t.get("no_match", "Error"))
                else: st.error(t.get("error_campos", "No existe"))
            except: st.error("Error de conexión")

    if st.button(t.get("btn_ir_registro", "Crear cuenta")):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    """Formulario de Registro Completo (4 Pasos en uno para la prueba)"""
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "Registro")}</p>', unsafe_allow_html=True)
    
    with st.expander(t.get("guia_titulo", "Ayuda"), expanded=False):
        st.write(t.get("guia_desc", ""))

    with st.form("registro_maestro"):
        # PASO 1: IDENTIFICACIÓN
        st.subheader(t.get("p1_tit", "1. Identificación"))
        c1, c2 = st.columns(2)
        with c1: nombre = st.text_input(t.get("nombre", "Nombre") + " *")
        with c2: apellido = st.text_input(t.get("apellido", "Apellido") + " *")
        
        # PASO 2: UBICACIÓN
        st.subheader(t.get("p2_tit", "2. Ubicación"))
        c3, c4 = st.columns(2)
        with c3: empresa = st.text_input(t.get("cliente", "Empresa") + " *")
        with c4: pais = st.text_input(t.get("pais", "País") + " *")
        
        email = st.text_input(t.get("email", "Email") + " *").lower().strip()
        tel = st.text_input(t.get("tel", "Teléfono") + " *")

        # PASO 3: SEGURIDAD
        st.subheader(t.get("p3_tit", "3. Seguridad"))
        pass1 = st.text_input(t.get("pass", "Contraseña") + " *", type="password")
        pass2 = st.text_input(t.get("pass_rep", "Repetir Contraseña") + " *", type="password")

        # PASO 4: LEGAL
        st.subheader(t.get("p4_tit", "4. Validación"))
        st.info(t.get("msg_legal", "Aviso Legal"))
        acepta = st.checkbox(t.get("acepto", "Acepto") + t.get("link_texto", " Política"))

        # BOTÓN FINAL CORREGIDO
        if st.form_submit_button(t.get("btn_generar", "REGISTRAR")):
            if not (nombre and apellido and empresa and email and pass1 and acepta):
                st.error(t.get("error_campos", "Faltan campos"))
            elif pass1 != pass2:
                st.error(t.get("no_match", "Claves no coinciden"))
            else:
                try:
                    ws = conn.worksheet("Usuarios")
                    ws.append_row([nombre, apellido, empresa, pais, email, tel, encriptar_password(pass1)])
                    # Enviar correo usando tu correo.py
                    correo.enviar_correo_bienvenida(email, nombre, email, "********")
                    st.success(t.get("exito_reg", "¡Éxito!"))
                    st.session_state.mostrar_registro = False
                    st.rerun()
                except: st.error("Error al guardar")

    if st.button(t.get("btn_volver", "VOLVER")):
        st.session_state.mostrar_registro = False
        st.rerun()
