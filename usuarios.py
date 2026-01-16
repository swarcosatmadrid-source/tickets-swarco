# =============================================================================
# ARCHIVO: usuarios.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 2.0.0 (Seguridad & Registro Modular)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Gestiona el acceso de usuarios, cifrado de contraseñas y 
#              el registro de nuevos equipos/clientes.
# =============================================================================

import streamlit as st
import pandas as pd
import hashlib
import estilos
import correo  # El mensajero que guardamos antes

def encriptar_password(password):
    """Cifra la contraseña usando SHA-256."""
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    """Página de Login con redirección al Menú Principal."""
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("login_tit", "Acceso Usuarios")}</p>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input(t.get("user_id", "Usuario / ID")).lower().strip()
        password = st.text_input(t.get("pass", "Contraseña"), type='password')
        
        if st.form_submit_button(t.get("btn_entrar", "INGRESAR")):
            if not conn:
                st.error("Error: No hay conexión con la base de datos.")
                return

            try:
                ws = conn.worksheet("Usuarios")
                df = pd.DataFrame(ws.get_all_records())
                
                if not df.empty and email in df['email'].values:
                    stored_pass = df.loc[df['email'] == email, 'password'].values[0]
                    if encriptar_password(password) == stored_pass:
                        # --- ÉXITO: GUARDAMOS SESIÓN Y CAMBIAMOS PÁGINA ---
                        st.session_state.autenticado = True
                        st.session_state.user_email = email
                        st.session_state.pagina_actual = 'menu' 
                        st.rerun()
                    else:
                        st.error(t.get("no_match", "Contraseña incorrecta"))
                else:
                    st.error(t.get("error_campos", "Usuario no encontrado"))
            except Exception as e:
                st.error(f"Error técnico: {e}")

    if st.button(t.get("btn_ir_registro", "Crear cuenta nueva")):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    """Página de Registro con validación legal y envío de correo."""
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "Registro")}</p>', unsafe_allow_html=True)
    
    # Aquí reusamos la lógica de pasos que me pasaste antes (p1, p2, p3...)
    with st.expander(t.get("guia_titulo", "Ayuda"), expanded=False):
        st.write(t.get("guia_desc", ""))

    with st.form("registro_form"):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input(t.get("nombre", "Nombre"))
            user_mail = st.text_input(t.get("email", "Email")).lower().strip()
        with col2:
            apellido = st.text_input(t.get("apellido", "Apellido"))
            empresa = st.text_input(t.get("cliente", "Empresa"))
            
        pass1 = st.text_input(t.get("pass", "Clave"), type="password")
        
        # Validación legal
        st.info(t.get("msg_legal", "Aviso Legal"))
        acepta = st.checkbox(t.get("acepto", "Acepto los términos"))

        if st.form_submit_button(t.get("btn_generar", "REGISTRAR")):
            if acepta and nombre and user_mail and pass1:
                try:
                    ws = conn.worksheet("Usuarios")
                    # Guardar en Sheets
                    ws.append_row([nombre, apellido, empresa, user_mail, encriptar_password(pass1)])
                    
                    # ENVIAR CORREO (Usando tu correo.py)
                    correo.enviar_correo_bienvenida(user_mail, nombre, user_mail, "********")
                    
                    st.success(t.get("exito_reg", "Usuario creado!"))
                    st.session_state.mostrar_registro = False
                    st.rerun()
                except:
                    st.error("Error al guardar usuario.")
            else:
                st.warning(t.get("error_campos", "Faltan datos o aceptar términos"))

    if st.button(t.get("btn_volver", "VOLVER")):
        st.session_state.mostrar_registro = False
        st.rerun()
