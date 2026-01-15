import streamlit as st
import pandas as pd
import time
import re

# --- FUNCIONES DE VALIDACIÓN (ADN DE SEGURIDAD) ---
def validar_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def chequear_fuerza_clave(p):
    if len(p) < 8: return "🔴 Débil (mín. 8 caracteres)", False
    if not re.search(r"[A-Z]", p) or not re.search(r"[0-9]", p):
        return "🟠 Media (añade Mayúscula y Número)", False
    return "🟢 Fuerte", True

# --- 1. INTERFAZ DE LOGIN (ACCESO) ---
def gestionar_acceso(conn, t):
    """Maneja el login con estética Swarco Spain"""
    # Logo centrado
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("logo.png", use_container_width=True)
    
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h5 style='text-align: center; color: gray;'>{t.get('login_tit', 'Acceso Usuarios Registrados')}</h5>", unsafe_allow_html=True)

    with st.form("login_form"):
        user_in = st.text_input(t.get('user_id', 'Usuario / Email')).strip()
        pass_in = st.text_input(t.get('pass', 'Contraseña'), type="password")
        btn_login = st.form_submit_button(t.get('btn_entrar', 'INGRESAR'), use_container_width=True)
        
        if btn_login:
            if not user_in or not pass_in:
                st.warning("⚠️ Por favor, rellene todos los campos.")
            else:
                try:
                    df = conn.read(worksheet="Usuarios", ttl=0)
                    validar = df[(df['Usuario'].astype(str) == user_in) & (df['Password'].astype(str) == pass_in)]
                    
                    if not validar.empty:
                        st.session_state.autenticado = True
                        st.session_state.datos_cliente = {
                            'Empresa': validar.iloc[0]['Empresa'],
                            'Contacto': validar.iloc[0]['Usuario'],
                            'Email': validar.iloc[0]['Email'],
                            'Telefono': validar.iloc[0].get('Telefono', '')
                        }
                        st.success("✅ Acceso concedido")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    st.markdown("---")
    st.write(t.get('no_tienes_cuenta', '¿No tienes una cuenta de equipo?'))
    if st.button(t.get('btn_ir_registro', 'CREAR NUEVA CUENTA'), use_container_width=True):
        st.session_state.mostrar_registro = True
        st.rerun()

# --- 2. INTERFAZ DE REGISTRO (NUEVO USUARIO) ---
def interfaz_registro_legal(conn, t):
    """Formulario de registro intuitivo, seguro y legal"""
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2:
        st.image("logo.png", use_container_width=True)
    
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{t.get('reg_tit', 'Registro de Nuevo Usuario')}</h4>", unsafe_allow_html=True)

    # EXPLICACIÓN PARA EL CLIENTE
    st.info("""
    **Instrucciones para el registro:**
    - Complete los datos de su empresa para la facturación y soporte.
    - Cree una contraseña segura (mínimo 8 caracteres, una mayúscula y un número).
    - Acepte los términos de protección de datos (GDPR) para poder operar en el portal.
    """)

    # BLOQUE 1: DATOS DE EMPRESA
    with st.expander("📍 1. Datos de Empresa", expanded=True):
        empresa = st.text_input(t.get('cliente', 'Nombre de Empresa / Cliente') + " *")
        email_new = st.text_input(t.get('email', 'Email Oficial de Contacto') + " *")
        tel_new = st.text_input(t.get('tel', 'Teléfono') + " *")

    # BLOQUE 2: SEGURIDAD
    with st.expander("🔐 2. Seguridad de la Cuenta", expanded=True):
        user_new = st.text_input(t.get('user_id', 'Nombre de Usuario') + " *")
        p1 = st.text_input(t.get('pass', 'Contraseña') + " *", type="password")
        p2 = st.text_input(t.get('pass_rep', 'Repetir Contraseña') + " *", type="password")
        
        if p1:
            msg, es_fuerte = chequear_fuerza_clave(p1)
            st.write(f"Estado de clave: {msg}")
            if p1 != p2 and p2:
                st.error("❌ Las contraseñas no coinciden")

    # BLOQUE 3: LEGAL Y CAPTCHA
    with st.expander("⚖️ 3. Verificación Legal", expanded=True):
        st.warning("De conformidad con el RGPD, Swarco Traffic Spain tratará sus datos únicamente para la gestión de incidencias técnicas.")
        acepta = st.checkbox("Acepto la política de privacidad y protección de datos *")
        
        # Captcha matemático para evitar bots
        st.write("**Verificación Anti-Bot:**")
        captcha_val = st.number_input("¿Cuánto es 7 + 3?", min_value=0, max_value=20)

    # BOTONES DE ACCIÓN
    col_env, col_vol = st.columns(2)
    with col_env:
        if st.button(t.get('btn_generar', 'REGISTRAR USUARIO'), type="primary", use_container_width=True):
            if not empresa or not email_new or not user_new or not p1:
                st.error("⚠️ Faltan campos obligatorios.")
            elif not validar_email(email_new):
                st.error("❌ El formato del email es incorrecto.")
            elif p1 != p2:
                st.error("❌ Las contraseñas no coinciden.")
            elif not es_fuerte:
                st.error("❌ La contraseña no cumple los requisitos de seguridad.")
            elif not acepta:
                st.error("⚠️ Debe aceptar la protección de datos.")
            elif captcha_val != 10:
                st.error("❌ Captcha incorrecto.")
            else:
                with st.spinner('Guardando nuevo usuario...'):
                    # Lógica para guardar en Google Sheets (conn.create...)
                    st.success("✅ Registro completado con éxito. Ya puede iniciar sesión.")
                    time.sleep(2)
                    st.session_state.mostrar_registro = False
                    st.rerun()

    with col_vol:
        if st.button(t.get('btn_volver', 'VOLVER AL LOGIN'), use_container_width=True):
            st.session_state.mostrar_registro = False
            st.rerun()
