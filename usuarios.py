import streamlit as st
import pandas as pd
import time
import re
import pycountry
import phonenumbers

# --- 1. MOTORES DE VALIDACIÓN ---
def validar_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def chequear_fuerza_clave(p):
    if len(p) < 8: return "🔴 Débil", False
    if not re.search(r"[A-Z]", p) or not re.search(r"[0-9]", p): return "🟠 Media", False
    return "🟢 Fuerte", True

@st.cache_data
def obtener_paises_mundo(lang_code):
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

# --- 2. INTERFAZ DE LOGIN ---
def gestionar_acceso(conn, t):
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: st.image("logo.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    
    with st.container(border=True):
        u_in = st.text_input(t.get('user_id', 'Usuario'), key="login_u").strip()
        p_in = st.text_input(t.get('pass', 'Contraseña'), type="password", key="login_p")
        
        # Respaldo de texto para evitar errores de traducción vacía
        if st.button(t.get('btn_entrar', 'INGRESAR'), use_container_width=True, key="btn_l_submit"):
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
                else: st.error("❌ Login Error")
            except: st.error("Database Connection Error")
    
    if st.button(t.get('btn_ir_registro', 'Registrarse'), use_container_width=True, key="btn_to_reg"):
        st.session_state.mostrar_registro = True
        st.rerun()

# --- 3. INTERFAZ DE REGISTRO (CORREGIDO EL ERROR NameError) ---
def interfaz_registro_legal(conn, t):
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2: st.image("logo.png", use_container_width=True)
    
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{t.get('reg_tit', 'Registro')}</h4>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f"##### {t.get('p1_tit', '1. Datos')}")
        col_n, col_a = st.columns(2)
        with col_n: nombre = st.text_input(f"{t.get('nombre', 'Nombre')} *", key="r_nom")
        with col_a: apellido = st.text_input(f"{t.get('apellido', 'Apellido')} *", key="r_ape")
        empresa = st.text_input(f"{t.get('cliente', 'Empresa')} *", key="r_emp")
        email_new = st.text_input(f"{t.get('email', 'Email')} *", key="r_mail")

        st.markdown("---")
        st.markdown(f"##### {t.get('p2_tit', '2. Contacto')}")
        idioma = st.session_state.get('codigo_lang', 'es')
        paises_data = obtener_paises_mundo(idioma)
        nombres_p = list(paises_data.keys())
        busqueda = "España" if idioma == "es" else "Spain"
        idx_def = nombres_p.index(busqueda) if busqueda in nombres_p else 0
        
        c_p, c_t = st.columns([1, 2])
        with c_p:
            pais_sel = st.selectbox(f"{t.get('pais', 'País')}", nombres_p, index=idx_def, key="r_pais")
            prefijo = paises_data[pais_sel]
        with c_t:
            tel_local = st.text_input(f"{t.get('tel', 'Teléfono')} ({prefijo}) *", key="r_tel")

        st.markdown("---")
        st.markdown(f"##### {t.get('p3_tit', '3. Seguridad')}")
        u_id = st.text_input(f"{t.get('user_id', 'Usuario')} *", key="r_uid")
        c_p1, c_p2 = st.columns(2)
        with c_p1: p1 = st.text_input(f"{t.get('pass', 'Clave')} *", type="password", key="r_p1")
        with c_p2: p2 = st.text_input(f"{t.get('pass_rep', 'Repetir')} *", type="password", key="r_p2")

        st.markdown("---")
        acepta = st.checkbox(t.get('acepto', 'Acepto GDPR'), key="r_gdpr")
        captcha = st.number_input("10 + 5 =", min_value=0, key="r_cap")

    st.markdown("<style>div.stButton > button:first-child {background-color: #003366; color: white;}</style>", unsafe_allow_html=True)
    
    # --- AQUÍ ESTABA EL ERROR DE NOMBRE DE VARIABLES ---
    c_env, c_vol = st.columns(2) # Definimos c_env y c_vol
    
    with c_env: # Usamos c_env
        if st.button(t.get('btn_generar', 'REGISTRAR'), use_container_width=True, key="r_btn_submit"):
            if not (nombre and apellido and empresa and email_new and tel_local and p1==p2 and acepta and captcha==15):
                st.error(t.get('error_campos', 'Faltan datos'))
            else:
                st.success("✅ Success")
                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()

    with c_vol: # Usamos c_vol (Antes decía col_vol y eso daba error)
        if st.button(t.get('btn_volver', 'VOLVER'), use_container_width=True, key="r_btn_back"):
            st.session_state.mostrar_registro = False
            st.rerun()
