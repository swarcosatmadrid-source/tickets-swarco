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
    if not re.search(r"[A-Z]", p) or not re.search(r"[0-9]", p): return "🟠 Media", False
    return "🟢 Fuerte", True

@st.cache_data
def obtener_paises_mundo(lang_code):
    paises_dict = {}
    # Diccionario manual para asegurar que los nombres clave cambien con el idioma
    trads_paises = {
        "es": {"Spain": "España", "France": "Francia", "Germany": "Alemania", "Slovakia": "Eslovaquia"},
        "en": {"Spain": "Spain", "France": "France", "Germany": "Germany", "Slovakia": "Slovakia"}
    }
    trads = trads_paises.get(lang_code, trads_paises["en"])

    for country in pycountry.countries:
        nombre_base = country.name
        nombre_final = trads.get(nombre_base, nombre_base)
        codigo_iso = country.alpha_2
        prefijo = phonenumbers.country_code_for_region(codigo_iso)
        if prefijo != 0:
            paises_dict[nombre_final] = f"+{prefijo}"
    return dict(sorted(paises_dict.items()))

# --- INTERFAZ DE LOGIN ---
def gestionar_acceso(conn, t):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("logo.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        with st.form("login_form", border=False):
            user_in = st.text_input(t.get('user_id', 'Usuario')).strip()
            pass_in = st.text_input(t.get('pass', 'Contraseña'), type="password")
            if st.form_submit_button(t.get('btn_entrar', 'INGRESAR'), use_container_width=True):
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
                        st.rerun()
                    else: st.error(t.get('error_login', 'Credenciales incorrectas'))
                except: st.error("Database Error")
    
    if st.button(t.get('btn_ir_registro', 'CREAR NUEVA CUENTA'), use_container_width=True):
        st.session_state.mostrar_registro = True
        st.rerun()

# --- INTERFAZ DE REGISTRO TOTALMENTE TRADUCIBLE ---
def interfaz_registro_legal(conn, t):
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2: st.image("logo.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)

    # 1. IDENTIFICACIÓN (Usa t.get para traducir)
    with st.expander(f"👤 {t.get('p1_tit', '1. Identificación')}", expanded=True):
        col_n, col_a = st.columns(2)
        with col_n: nombre = st.text_input(f"{t.get('nombre', 'Nombre')} *")
        with col_a: apellido = st.text_input(f"{t.get('apellido', 'Apellido')} *")
        empresa = st.text_input(f"{t.get('cliente', 'Empresa')} *")
        email_new = st.text_input(f"{t.get('email', 'Email')} *")

    # 2. PAÍS Y TELÉFONO
    with st.expander(f"🌍 {t.get('p2_tit', '2. País y Contacto')}", expanded=True):
        idioma = st.session_state.get('codigo_lang', 'es')
        paises_data = obtener_paises_mundo(idioma)
        nombres_paises = list(paises_data.keys())
        
        nombre_buscar = "España" if idioma == "es" else "Spain"
        idx_def = nombres_paises.index(nombre_buscar) if nombre_buscar in nombres_paises else 0
            
        pais_sel = st.selectbox(f"{t.get('pais', 'País')} *", nombres_paises, index=idx_def)
        prefijo_sel = paises_data[pais_sel]
        
        c_pre, c_tel = st.columns([1, 3])
        with c_pre: st.info(f"{prefijo_sel}")
        with c_tel: tel_local = st.text_input(f"{t.get('tel', 'Teléfono')} *")

    # 3. SEGURIDAD
    with st.expander(f"🔐 {t.get('p2_tit', '3. Seguridad')}", expanded=True):
        user_id = st.text_input(f"{t.get('user_id', 'Usuario')} *")
        p1 = st.text_input(f"{t.get('pass', 'Contraseña')} *", type="password")
        p2 = st.text_input(f"{t.get('pass_rep', 'Repetir Contraseña')} *", type="password")
        
        es_fuerte = False
        if p1:
            msg, es_fuerte = chequear_fuerza_clave(p1)
            st.write(f"Fuerza: {msg}")
            if p2 and p1 != p2: st.error("❌ Mismatch")

    # 4. LEGAL
    with st.expander(f"⚖️ {t.get('p3_tit', '4. Verificación Legal')}", expanded=True):
        acepta = st.checkbox(t.get('acepto', 'Acepto política de privacidad'))
        captcha = st.number_input("Security: 12 + 3 =", min_value=0)

    # BOTONES ALINEADOS
    st.markdown("<style>div.stButton > button:first-child {background-color: #003366; color: white;}</style>", unsafe_allow_html=True)
    c_env, c_vol = st.columns(2)
    with c_env:
        if st.button(t.get('btn_generar', 'REGISTRAR'), use_container_width=True):
            fallos = []
            if not (nombre and apellido and empresa and email_new and tel_local and p1==p2 and acepta and captcha==15):
                st.error(t.get('error_campos', 'Faltan datos obligatorios'))
            else:
                st.success("✅ Success!")
                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()

    with c_vol:
        if st.button(t.get('btn_volver', 'VOLVER'), use_container_width=True):
            st.session_state.mostrar_registro = False
            st.rerun()
