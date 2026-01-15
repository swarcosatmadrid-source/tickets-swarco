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
    """Maneja la lista de países y traduce 'Spain' manualmente"""
    paises_dict = {}
    trads_paises = {
        "es": {"Spain": "España", "France": "Francia", "Germany": "Alemania", "Slovakia": "Eslovaquia", "Italy": "Italia"},
        "en": {"Spain": "Spain", "France": "France", "Germany": "Germany", "Slovakia": "Slovakia", "Italy": "Italy"}
    }
    trads = trads_paises.get(lang_code, trads_paises["en"])
    for country in pycountry.countries:
        nombre_f = trads.get(country.name, country.name)
        prefijo = phonenumbers.country_code_for_region(country.alpha_2)
        if prefijo != 0:
            paises_dict[nombre_f] = f"+{prefijo}"
    return dict(sorted(paises_dict.items()))

# --- INTERFAZ DE LOGIN ---
def gestionar_acceso(conn, t):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("logo.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        with st.form("login_form", border=False):
            u_in = st.text_input(t.get('user_id', 'Usuario')).strip()
            p_in = st.text_input(t.get('pass', 'Contraseña'), type="password")
            if st.form_submit_button(t.get('btn_entrar', 'INGRESAR'), use_container_width=True):
                try:
                    df = conn.read(worksheet="Usuarios", ttl=0)
                    validar = df[(df['Usuario'].astype(str) == u_in) & (df['Password'].astype(str) == p_in)]
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
                except: st.error("Error de conexión")
    
    if st.button(t.get('btn_ir_registro', 'CREAR CUENTA'), use_container_width=True):
        st.session_state.mostrar_registro = True
        st.rerun()

# --- INTERFAZ DE REGISTRO ---
def interfaz_registro_legal(conn, t):
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2: st.image("logo.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{t.get('reg_tit')}</h4>", unsafe_allow_html=True)

    with st.container(border=True):
        # 1. IDENTIFICACIÓN
        st.markdown(f"##### {t.get('p1_tit')}")
        col_n, col_a = st.columns(2)
        with col_n: nombre = st.text_input(f"{t.get('nombre', 'Nombre')} *")
        with col_a: apellido = st.text_input(f"{t.get('apellido', 'Apellido')} *")
        
        empresa = st.text_input(f"{t.get('cliente')} *")
        email_new = st.text_input(f"{t.get('email')} *")

        st.markdown("---")

        # 2. PAÍS Y TELÉFONO
        st.markdown(f"##### {t.get('p2_tit')}")
        idioma = st.session_state.get('codigo_lang', 'es')
        paises_data = obtener_paises_mundo(idioma)
        nombres_p = list(paises_data.keys())
        
        # Buscar España por defecto
        busqueda = "España" if idioma == "es" else "Spain"
        idx_def = nombres_p.index(busqueda) if busqueda in nombres_p else 0
        
        c_p, c_t = st.columns([1, 2])
        with c_p:
            pais_sel = st.selectbox(t.get('pais', 'País'), nombres_p, index=idx_def)
            prefijo = paises_data[pais_sel]
        with c_t:
            tel_local = st.text_input(f"{t.get('tel')} ({prefijo}) *")

        st.markdown("---")

        # 3. SEGURIDAD
        st.markdown(f"##### {t.get('p2_tit')}")
        u_id = st.text_input(f"{t.get('user_id')} *")
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            p1 = st.text_input(t.get('pass') + " *", type="password")
        with c_p2:
            p2 = st.text_input(t.get('pass_rep', 'Repetir') + " *", type="password")
        
        if p1 and p2:
            if p1 == p2: st.success(t.get('match', '✅'))
            else: st.error(t.get('no_match', '❌'))

        # 4. LEGAL
        st.markdown("---")
        acepta = st.checkbox(t.get('acepto', 'Acepto política'))
        captcha = st.number_input("Security: 10 + 5 =", min_value=0)

    # BOTONES CON ESTILO SWARCO
    st.markdown("<style>div.stButton > button:first-child {background-color: #003366; color: white;}</style>", unsafe_allow_html=True)
    c_env, c_vol = st.columns(2)
    with c_env:
        if st.button(t.get('btn_generar'), use_container_width=True):
            # Lógica de validación
            errores = []
            if not (nombre and apellido and empresa and email_new and tel_local and p1==p2 and acepta and captcha==15):
                st.error(t.get('error_campos'))
            else:
                st.success(t.get('exito_reg'))
                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()

    with col_vol:
        if st.button(t.get('btn_volver', 'VOLVER'), use_container_width=True):
            st.session_state.mostrar_registro = False
            st.rerun()
