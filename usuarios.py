import streamlit as st
import pandas as pd
import time
import re
import pycountry
import phonenumbers
import gettext # Para localización de nombres de países

# --- FUNCIONES DE APOYO ---
def validar_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def chequear_fuerza_clave(p):
    if len(p) < 8: return "🔴 Débil", False
    if not re.search(r"[A-Z]", p) or not re.search(r"[0-9]", p): return "🟠 Media", False
    return "🟢 Fuerte", True

@st.cache_data
def obtener_paises_localizados(lang_code):
    """Obtiene la lista de países en el idioma seleccionado"""
    paises_dict = {}
    # Intentamos cargar la traducción del país
    try:
        idioma_propio = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=[lang_code])
        _ = idioma_propio.gettext
    except:
        _ = lambda x: x # Si no hay traducción, usamos el nombre estándar

    for country in pycountry.countries:
        nombre_traducido = _(country.name)
        codigo_iso = country.alpha_2
        prefijo = phonenumbers.country_code_for_region(codigo_iso)
        if prefijo != 0:
            paises_dict[nombre_traducido] = f"+{prefijo}"
    return dict(sorted(paises_dict.items()))

# --- INTERFAZ DE REGISTRO ---
def interfaz_registro_legal(conn, t):
    # Centrado de Logo y Título
    c1, c2, c3 = st.columns([1.5, 1, 1.5])
    with c2: st.image("logo.png", use_container_width=True)
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)

    # Cargamos países según el idioma de la sesión (lateral)
    paises_data = obtener_paises_localizados(st.session_state.get('codigo_lang', 'es'))

    # 1. IDENTIFICACIÓN (Validación al cambiar de campo)
    with st.expander("👤 1. Identificación", expanded=True):
        col_n, col_a = st.columns(2)
        with col_n: nombre = st.text_input("Nombre *")
        with col_a: apellido = st.text_input("Apellido *")
        empresa = st.text_input("Empresa / Cliente *")
        email_new = st.text_input("Email Oficial *")
        if email_new and not validar_email(email_new):
            st.error("❌ Formato de email incorrecto")

    # 2. PAÍS Y TELÉFONO
    with st.expander("🌍 2. País y Contacto", expanded=True):
        nombres_paises = list(paises_data.keys())
        
        # Buscador inteligente del nombre de "España" según el idioma
        idx_def = 0
        paises_referencia = ["España", "Spain", "Espagne", "Spanien", "Spagna"]
        for i, n in enumerate(nombres_paises):
            if any(ref in n for ref in paises_referencia):
                idx_def = i
                break
        
        pais_sel = st.selectbox("País *", nombres_paises, index=idx_def)
        prefijo_sel = paises_data[pais_sel]
        
        c_pre, c_tel = st.columns([1, 3])
        with c_pre: st.info(f"Cód: {prefijo_sel}")
        with c_tel: tel_local = st.text_input("Número de Teléfono *")

    # 3. SEGURIDAD (Validación en tiempo real)
    with st.expander("🔐 3. Seguridad", expanded=True):
        user_id = st.text_input("ID de Usuario *")
        p1 = st.text_input("Contraseña *", type="password")
        p2 = st.text_input("Repetir Contraseña *", type="password")
        
        es_valida = False
        if p1:
            msg, fuerte = chequear_fuerza_clave(p1)
            st.write(f"Fuerza: {msg}")
            if p2 and p1 != p2:
                st.error("❌ Las contraseñas no coinciden")
            elif p2 and p1 == p2:
                st.success("✅ Las contraseñas coinciden")
                es_valida = fuerte

    # 4. LEGAL (Documento PDF)
    with st.expander("⚖️ 4. Verificación Legal", expanded=True):
        st.markdown("""
        **Protección de Datos (GDPR)**
        Para ver el documento legal completo de Swarco Traffic Spain:
        """)
        # Aquí puedes poner el link a tu PDF real
        st.download_button(label="📄 Descargar Política de Privacidad (PDF)", 
                         data="Contenido del PDF aquí", 
                         file_name="GDPR_Swarco_Spain.pdf", 
                         mime="application/pdf")
        
        acepta = st.checkbox("Acepto los términos y la protección de datos *")
        captcha = st.number_input("Seguridad: 12 + 3 =", min_value=0)

    # BOTONES CON PALETA SWARCO
    col_env, col_vol = st.columns(2)
    
    with col_env:
        # Estilo CSS para el botón azul Swarco
        st.markdown("""
            <style>
            div.stButton > button:first-child {
                background-color: #003366;
                color: white;
            }
            </style>""", unsafe_allow_html=True)
            
        if st.button("CREAR USUARIO", use_container_width=True):
            # LISTA DE ERRORES DETALLADA
            errores = []
            if not nombre: errores.append("Nombre")
            if not apellido: errores.append("Apellido")
            if not empresa: errores.append("Empresa")
            if not email_new or not validar_email(email_new): errores.append("Email válido")
            if not tel_local: errores.append("Teléfono")
            if p1 != p2: errores.append("Coincidencia de contraseñas")
            if not acepta: errores.append("Aceptación de política")
            if captcha != 15: errores.append("Captcha correcto")

            if errores:
                st.error(f"⚠️ Faltan o son incorrectos los siguientes datos: {', '.join(errores)}")
            else:
                st.success("✅ ¡Registro Exitoso!")
                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()

    with col_vol:
        if st.button("VOLVER", use_container_width=True):
            st.session_state.mostrar_registro = False
            st.rerun()
