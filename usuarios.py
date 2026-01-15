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

# --- INTERFAZ DE LOGIN ---
def gestionar_acceso(conn, t):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("logo.png", use_container_width=True)
    
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h5 style='text-align: center; color: gray;'>{t.get('login_tit', 'Acceso Usuarios Registrados')}</h5>", unsafe_allow_html=True)

    with st.form("login_form"):
        user_in = st.text_input(t.get('user_id', 'Usuario')).strip()
        pass_in = st.text_input(t.get('pass', 'Contraseña'), type="password")
        btn_login = st.form_submit_button(t.get('btn_entrar', 'INGRESAR'), use_container_width=True)
        
        if btn_login:
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
                st.error(f"Error: {e}")
    
    st.markdown("---")
    if st.button(t.get('btn_ir_registro', 'CREAR NUEVA CUENTA'), use_container_width=True):
        st.session_state.mostrar_registro = True
        st.rerun()

# --- INTERFAZ DE REGISTRO ---
def interfaz_registro_legal(conn, t):
    # Centramos logo
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2: st.image("logo.png", use_container_width=True)
    
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{t.get('reg_tit', 'Registro de Nuevo Usuario')}</h4>", unsafe_allow_html=True)

    # 1. IDENTIFICACIÓN
    with st.expander("👤 1. Identificación del Usuario", expanded=True):
        col_n, col_a = st.columns(2)
        with col_n: nombre = st.text_input("Nombre *")
        with col_a: apellido = st.text_input("Apellido *")
        empresa = st.text_input("Empresa / Cliente *")
        email_new = st.text_input("Email Oficial *")

    # 2. PAÍS Y TELÉFONO
    with st.expander("🌍 2. Ubicación y Contacto", expanded=True):
        nombres_paises = list(PAISES_REG.keys())
        try: idx_esp = nombres_paises.index("Spain")
        except: idx_esp = 0
        
        pais_sel = st.selectbox("País de Residencia *", nombres_paises, index=idx_esp)
        prefijo_sel = PAISES_REG[pais_sel]
        
        c_pre, c_tel = st.columns([1, 3])
        with c_pre: st.info(f"Cód: {prefijo_sel}")
        with c_tel: tel_local = st.text_input("Número de Teléfono *")
        
        telefono_completo = f"{prefijo_sel} {tel_local}"

    # 3. SEGURIDAD
    with st.expander("🔐 3. Credenciales de Acceso", expanded=True):
        user_id = st.text_input("ID de Usuario *")
        p1 = st.text_input("Contraseña *", type="password")
        p2 = st.text_input("Repetir Contraseña *", type="password")
        es_fuerte = False
        if p1:
            msg, es_fuerte = chequear_fuerza_clave(p1)
            st.write(f"Seguridad: {msg}")

    # 4. LEGAL
    with st.expander("⚖️ 4. Verificación y GDPR", expanded=True):
        st.caption("Aviso: Swarco Traffic Spain cumple con la normativa de protección de datos.")
        acepta = st.checkbox("Acepto la política de privacidad *")
        captcha_res = st.number_input("Seguridad: ¿Cuánto es 10 + 5?", min_value=0)

    # BOTONES DE ACCIÓN (Corregido el error de nombre de columnas)
    col_env, col_vol = st.columns(2) # <-- Aquí definimos col_env y col_vol
    
    with col_env:
        if st.button("REGISTRAR USUARIO", type="primary", use_container_width=True):
            if not (nombre and apellido and empresa and email_new and tel_local and p1 == p2 and acepta and captcha_res == 15):
                st.error("⚠️ Faltan datos o el captcha es incorrecto.")
            elif not es_fuerte:
                st.error("❌ La contraseña es muy débil.")
            else:
                st.success(f"✅ ¡Bienvenido {nombre}! Usuario creado.")
                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()

    with col_vol:
        if st.button("VOLVER", use_container_width=True):
            st.session_state.mostrar_registro = False
            st.rerun()
