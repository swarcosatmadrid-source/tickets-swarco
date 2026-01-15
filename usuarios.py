import streamlit as st
import pandas as pd
import time
import re

# --- ESTÉTICA Y FUNCIONES BÁSICAS ---
def validar_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def chequear_fuerza_clave(p):
    if len(p) < 8: return "🔴 Débil", False
    if not re.search(r"[A-Z]", p) or not re.search(r"[0-9]", p): return "🟠 Media", False
    return "🟢 Fuerte", True

# --- 1. LOGIN (EL QUE SE VEÍA BIEN) ---
def gestionar_acceso(conn, t):
    # Centrado con columnas invisibles para que el logo quede perfecto
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("logo.png", use_container_width=True)
    
    st.markdown("<h3 style='text-align: center; color: #333;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: gray;'>{t.get('login_tit', 'Acceso Usuarios')}</p>", unsafe_allow_html=True)

    # Tarjeta limpia con borde
    with st.container(border=True):
        user_in = st.text_input(t.get('user_id', 'Usuario'), key="log_u")
        pass_in = st.text_input(t.get('pass', 'Contraseña'), type="password", key="log_p")
        
        # Botón Azul Swarco
        st.markdown("""<style>div.stButton > button {background-color: #003366; color: white; width: 100%;}</style>""", unsafe_allow_html=True)
        
        if st.button(t.get('btn_entrar', 'INGRESAR'), key="btn_log"):
            try:
                df = conn.read(worksheet="Usuarios", ttl=0)
                # Validación simple y robusta
                validar = df[(df['Usuario'].astype(str) == user_in) & (df['Password'].astype(str) == pass_in)]
                if not validar.empty:
                    st.session_state.autenticado = True
                    st.session_state.datos_cliente = {
                        'Empresa': validar.iloc[0]['Empresa'],
                        'Contacto': validar.iloc[0]['Usuario'],
                        'Email': validar.iloc[0]['Email'],
                        'Telefono': validar.iloc[0].get('Telefono', '')
                    }
                    st.rerun()
                else:
                    st.error("❌ Datos incorrectos")
            except:
                st.error("⚠️ Error de conexión")

    # Botón discreto para registro
    st.markdown("---")
    col_reg1, col_reg2, col_reg3 = st.columns([1, 2, 1])
    with col_reg2:
        if st.button("Crear Cuenta Nueva", key="goto_reg"):
            st.session_state.mostrar_registro = True
            st.rerun()

# --- 2. REGISTRO (EL QUE NECESITAMOS QUE FUNCIONE) ---
def interfaz_registro_legal(conn, t):
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2:
        st.image("logo.png", use_container_width=True)
    
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown("<h5 style='text-align: center;'>Registro de Técnico</h5>", unsafe_allow_html=True)

    # Formulario estético y ordenado
    with st.container(border=True):
        st.info("ℹ️ Complete los datos para dar de alta su equipo.")
        
        # Grupo 1: Quién eres
        col_nom, col_ape = st.columns(2)
        with col_nom: nombre = st.text_input("Nombre *", key="r_nom")
        with col_ape: apellido = st.text_input("Apellido *", key="r_ape")
        
        # Grupo 2: Empresa y Contacto
        empresa = st.text_input("Empresa / Cliente *", key="r_emp")
        email = st.text_input("Email Oficial *", key="r_mail")
        
        # Grupo 3: País (Simplificado manual para que no falle)
        paises = ["España (+34)", "Portugal (+351)", "France (+33)", "Other"]
        pais_sel = st.selectbox("País / Country *", paises, key="r_pais")
        tel = st.text_input("Teléfono Móvil *", key="r_tel")

        st.markdown("---")
        
        # Grupo 4: Tu cuenta
        uid = st.text_input("Usuario Deseado *", key="r_uid")
        col_p1, col_p2 = st.columns(2)
        with col_p1: p1 = st.text_input("Contraseña *", type="password", key="r_p1")
        with col_p2: p2 = st.text_input("Repetir Contraseña *", type="password", key="r_p2")
        
        # Seguridad visual
        if p1 and p2 and p1==p2: st.caption("✅ Coinciden")
        
        acepta = st.checkbox("Acepto política de privacidad (GDPR)", key="r_check")

    # Botones de Acción
    c_ok, c_back = st.columns(2)
    with c_ok:
        # Estilo forzado para el botón azul
        st.markdown("""<style>div.stButton > button {background-color: #003366; color: white;}</style>""", unsafe_allow_html=True)
        if st.button("REGISTRARME AHORA", key="btn_save_reg", use_container_width=True):
            if nombre and apellido and empresa and email and tel and uid and p1==p2 and acepta:
                st.success("✅ ¡Bienvenido a Swarco! Cuenta creada.")
                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()
            else:
                st.error("⚠️ Faltan datos obligatorios")
                
    with c_back:
        if st.button("Cancelar / Volver", key="btn_cancel_reg", use_container_width=True):
            st.session_state.mostrar_registro = False
            st.rerun()
            
