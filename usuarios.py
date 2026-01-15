import streamlit as st
import pandas as pd
import time
import re
import pycountry
import phonenumbers

# --- FUNCIONES DE APOYO ---
def validar_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def chequear_fuerza_clave(p):
    if len(p) < 8: return "🔴 Débil", False
    if not re.search(r"[A-Z]", p) or not re.search(r"[0-9]", p):
        return "🟠 Media", False
    return "🟢 Fuerte", True

@st.cache_data
def obtener_paises_registro():
    paises_dict = {}
    for country in pycountry.countries:
        nombre = country.name
        codigo_iso = country.alpha_2
        prefijo = phonenumbers.country_code_for_region(codigo_iso)
        if prefijo != 0:
            paises_dict[nombre] = f"+{prefijo}"
    return dict(sorted(paises_dict.items()))

PAISES_REG = obtener_paises_registro()

# --- INTERFAZ DE REGISTRO ---
def interfaz_registro_legal(conn, t):
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2: st.image("logo.png", use_container_width=True)
    
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{t.get('reg_tit', 'Registro de Nuevo Usuario')}</h4>", unsafe_allow_html=True)

    # 1. DATOS PERSONALES Y EMPRESA
    with st.expander("👤 1. Identificación del Usuario", expanded=True):
        col_n, col_a = st.columns(2)
        with col_n:
            nombre = st.text_input("Nombre / First Name *")
        with col_a:
            apellido = st.text_input("Apellido / Last Name *")
        
        empresa = st.text_input(t.get('cliente', 'Empresa / Cliente') + " *")
        email_new = st.text_input(t.get('email', 'Email Oficial') + " *")

    # 2. LOCALIZACIÓN Y TELÉFONO (Tu lógica de países)
    with st.expander("🌍 2. Ubicación y Contacto", expanded=True):
        nombres_paises = list(PAISES_REG.keys())
        try: idx_esp = nombres_paises.index("Spain")
        except: idx_esp = 0
        
        pais_sel = st.selectbox("País de Residencia *", nombres_paises, index=idx_esp)
        prefijo_sel = PAISES_REG[pais_sel]
        
        col_p, col_t = st.columns([1, 3])
        with col_p:
            st.info(f"Cód: {prefijo_sel}")
        with col_t:
            tel_local = st.text_input("Número de Teléfono (sin prefijo) *")
        
        telefono_completo = f"{prefijo_sel} {tel_local}"

    # 3. SEGURIDAD
    with st.expander("🔐 3. Credenciales de Acceso", expanded=True):
        user_id = st.text_input(t.get('user_id', 'Nombre de Usuario (ID)') + " *")
        p1 = st.text_input(t.get('pass', 'Contraseña') + " *", type="password")
        p2 = st.text_input("Repetir Contraseña *", type="password")
        if p1:
            msg, fuerte = chequear_fuerza_clave(p1)
            st.write(f"Seguridad: {msg}")

    # 4. LEGAL
    with st.expander("⚖️ 4. Verificación y GDPR", expanded=True):
        st.caption("Sus datos serán almacenados de forma segura en los servidores de Swarco Traffic Spain.")
        acepta = st.checkbox("Acepto la política de privacidad y protección de datos *")
        captcha = st.number_input("Seguridad: ¿Cuánto es 10 + 5?", min_value=0)

    # BOTONES
    c_env, c_vol = st.columns(2)
    with c_env:
        if st.button("REGISTRAR USUARIO", type="primary", use_container_width=True):
            if not (nombre and apellido and empresa and email_new and tel_local and p1 == p2 and acepta and captcha == 15):
                st.error("⚠️ Por favor, rellene todos los campos correctamente.")
            else:
                # AQUÍ SE GUARDA EN TU BASE DE DATOS
                # El orden de las columnas debe coincidir con tu Excel:
                # [Empresa, Usuario, Password, Email, Telefono, Nombre, Apellido, Pais]
                st.success(f"✅ ¡Bienvenido {nombre}! Registro completado.")
                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()

    with col_vol:
        if st.button("CANCELAR", use_container_width=True):
            st.session_state.mostrar_registro = False
            st.rerun()
