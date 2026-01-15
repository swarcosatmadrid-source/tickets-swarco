import streamlit as st
import pandas as pd
import time
import re
import pycountry
import phonenumbers

# --- 1. FUNCIONES DE APOYO ---
def validar_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def chequear_fuerza_clave(p):
    if len(p) < 8: return "🔴 Débil", False
    if not re.search(r"[A-Z]", p) or not re.search(r"[0-9]", p): return "🟠 Media", False
    return "🟢 Fuerte", True

@st.cache_data
def obtener_paises_mundo(lang_code):
    """Maneja la lista de países y traduce 'Spain' manualmente para evitar errores"""
    paises_dict = {}
    
    # Traducción manual para los países donde Swarco opera más
    traducciones_paises = {
        "es": {"Spain": "España", "France": "Francia", "Germany": "Alemania", "Slovakia": "Eslovaquia", "Italy": "Italia"},
        "en": {"Spain": "Spain", "France": "France", "Germany": "Germany", "Slovakia": "Slovakia", "Italy": "Italy"},
        # Puedes añadir más idiomas aquí
    }
    
    trads = traducciones_paises.get(lang_code, traducciones_paises["en"])

    for country in pycountry.countries:
        # Si tenemos traducción manual, la usamos; si no, el nombre oficial
        nombre_final = trads.get(country.name, country.name)
        codigo_iso = country.alpha_2
        prefijo = phonenumbers.country_code_for_region(codigo_iso)
        if prefijo != 0:
            paises_dict[nombre_final] = f"+{prefijo}"
            
    return dict(sorted(paises_dict.items()))

# --- 2. INTERFAZ DE LOGIN ---
def gestionar_acceso(conn, t):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("logo.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    
    with st.form("login_form"):
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
                else: st.error("❌ Credenciales incorrectas")
            except: st.error("Error de conexión con la base de datos")
    
    st.markdown("---")
    if st.button(t.get('btn_ir_registro', 'CREAR NUEVA CUENTA'), use_container_width=True):
        st.session_state.mostrar_registro = True
        st.rerun()

# --- 3. INTERFAZ DE REGISTRO ---
def interfaz_registro_legal(conn, t):
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2: st.image("logo.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)

    # 1. IDENTIFICACIÓN
    with st.expander("👤 1. Identificación", expanded=True):
        col_n, col_a = st.columns(2)
        with col_n: nombre = st.text_input("Nombre *")
        with col_a: apellido = st.text_input("Apellido *")
        empresa = st.text_input("Empresa / Cliente *")
        email_new = st.text_input("Email Oficial *")

    # 2. PAÍS Y TELÉFONO (CORREGIDO)
    with st.expander("🌍 2. País y Contacto", expanded=True):
        idioma = st.session_state.get('codigo_lang', 'es')
        paises_data = obtener_paises_mundo(idioma)
        nombres_paises = list(paises_data.keys())
        
        # Buscamos el índice de España según el idioma seleccionado
        nombre_buscar = "España" if idioma == "es" else "Spain"
        try:
            idx_def = nombres_paises.index(nombre_buscar)
        except:
            idx_def = 0
            
        pais_sel = st.selectbox("País *", nombres_paises, index=idx_def)
        prefijo_sel = paises_data[pais_sel]
        
        c_pre, c_tel = st.columns([1, 3])
        with c_pre: st.info(f"Cód: {prefijo_sel}")
        with c_tel: tel_local = st.text_input("Número de Teléfono *")

    # 3. SEGURIDAD
    with st.expander("🔐 3. Seguridad", expanded=True):
        user_id = st.text_input("ID de Usuario *")
        p1 = st.text_input("Contraseña *", type="password")
        p2 = st.text_input("Repetir Contraseña *", type="password")
        
        es_fuerte = False
        if p1:
            msg, es_fuerte = chequear_fuerza_clave(p1)
            st.write(f"Fuerza: {msg}")
            if p2 and p1 != p2: st.error("❌ Las claves no coinciden")
            elif p2 and p1 == p2: st.success("✅ Las claves coinciden")

    # 4. LEGAL
    with st.expander("⚖️ 4. Verificación Legal", expanded=True):
        st.download_button(label="📄 Descargar Política GDPR (PDF)", data="Documento Swarco", file_name="GDPR_Swarco.pdf")
        acepta = st.checkbox("Acepto la política de privacidad *")
        captcha = st.number_input("Seguridad: ¿Cuánto es 12 + 3?", min_value=0)

    # BOTONES
    col_env, col_vol = st.columns(2)
    with col_env:
        st.markdown("<style>div.stButton > button:first-child {background-color: #003366; color: white;}</style>", unsafe_allow_html=True)
        if st.button("CREAR USUARIO", use_container_width=True):
            errores = []
            if not nombre: errores.append("Nombre")
            if not apellido: errores.append("Apellido")
            if not empresa: errores.append("Empresa")
            if not email_new or not validar_email(email_new): errores.append("Email")
            if not tel_local: errores.append("Teléfono")
            if p1 != p2: errores.append("Las claves deben coincidir")
            if not es_fuerte: errores.append("Clave más segura")
            if not acepta: errores.append("Aceptar política")
            if captcha != 15: errores.append("Captcha")

            if errores:
                st.error(f"⚠️ Faltan datos: {', '.join(errores)}")
            else:
                st.success("✅ ¡Registro enviado!")
                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()

    with col_vol:
        if st.button("VOLVER", use_container_width=True):
            st.session_state.mostrar_registro = False
            st.rerun()
