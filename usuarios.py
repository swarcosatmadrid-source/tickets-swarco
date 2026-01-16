# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 8.3.0 (Teléfono: Aviso de error en vez de borrado automático)
# =============================================================================
import streamlit as st
import pandas as pd
import hashlib
import re
import time
import estilos
import correo
import paises

# --- Lógica Auxiliar ---
def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def validar_fuerza_clave(password):
    score = 0
    if len(password) >= 8: score += 1
    if re.search(r"[A-Z]", password): score += 1
    if re.search(r"[a-z]", password): score += 1
    if re.search(r"[0-9]", password): score += 1
    if re.search(r"[@$!%*?&#]", password): score += 1
    
    if score < 3: return 20, "Débil 🔴", "#ff4b4b"
    elif score < 5: return 60, "Media 🟡", "#ffa500"
    else: return 100, "Robusta 🟢", "#21c354"

def usuario_existe(conn, email_input):
    try:
        df = pd.DataFrame(conn.worksheet("Usuarios").get_all_records())
        if not df.empty and email_input.lower() in df['email'].astype(str).str.lower().values:
            return True
    except: return False
    return False

# --- Interfaz de Registro ---
def interfaz_registro_legal(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "ALTA DE USUARIO")}</p>', unsafe_allow_html=True)

    if 'campos_error' not in st.session_state: st.session_state.campos_error = []

    # 1. ZONA IDENTIFICACIÓN
    with st.container(border=True):
        st.markdown(f"#### 👤 {t.get('p1_tit', 'Identificación')}")
        c1, c2 = st.columns(2)
        
        n = c1.text_input("Nombre *")
        if "n" in st.session_state.campos_error: c1.error("Falta Nombre")
        
        a = c2.text_input("Apellido *")
        if "a" in st.session_state.campos_error: c2.error("Falta Apellido")

    # 2. ZONA UBICACIÓN Y DATOS
    with st.container(border=True):
        st.markdown(f"#### 🌍 {t.get('p2_tit', 'Datos Profesionales')}")
        
        c_cargo, c_empresa = st.columns(2)
        cargo = c_cargo.text_input("Cargo / Puesto *")
        if "cargo" in st.session_state.campos_error: c_cargo.error("Falta Cargo")
        
        e = c_empresa.text_input("Empresa / Entidad *")
        if "e" in st.session_state.campos_error: c_empresa.error("Falta Empresa")
        
        # Email
        m = st.text_input("Email Corporativo *").lower().strip()
        
        if "m" in st.session_state.campos_error:
            st.error("Email obligatorio o formato incorrecto")
        elif "duplicado" in st.session_state.campos_error:
            st.error("⛔ Este correo ya está registrado.")
        
        if m and "duplicado" not in st.session_state.campos_error:
            if "@" not in m: st.warning("Formato incorrecto")
            elif usuario_existe(conn, m): st.error("Ya existe")
            else: st.success("Disponible")
        
        # --- TELÉFONO (LÓGICA CORREGIDA) ---
        st.caption("Teléfono Móvil")
        col_pais, col_pref, col_tel = st.columns([3, 1.2, 3])
        
        with col_pais:
            lista_paises = paises.obtener_lista_nombres()
            idx = lista_paises.index("España") if "España" in lista_paises else 0
            pais_sel = st.selectbox("País *", lista_paises, index=idx)
        
        with col_pref:
            pref_auto = paises.obtener_prefijo(pais_sel)
            st.text_input("Prefijo", value=pref_auto, disabled=True)
        
        with col_tel:
            # YA NO borramos letras automáticamente. Dejamos que el usuario escriba.
            tl_num = st.text_input("Nº Móvil *", placeholder="Ej: 600123456")
            
            # VALIDACIÓN EN SITIO: Si detectamos letras, mostramos error INMEDIATO
            if tl_num and not tl_num.isdigit():
                st.error("⚠️ Solo se permiten números", icon="🚫")
            elif "tl" in st.session_state.campos_error:
                st.error("Mínimo 6 dígitos requeridos")

    # 3. ZONA SEGURIDAD
    with st.container(border=True):
        st.markdown(f"#### 🔒 {t.get('p3_tit', 'Seguridad')}")
        
        p1 = st.text_input("Contraseña *", type='password')
        if p1:
            prog, etiq, col = validar_fuerza_clave(p1)
            st.markdown(f"""<div style="background-color:#ddd;height:5px;"><div style="width:{prog}%;background-color:{col};height:100%;"></div></div><small style="color:{col}">{etiq}</small>""", unsafe_allow_html=True)
        
        p2 = st.text_input("Repetir Contraseña *", type='password')
        
        if "p1" in st.session_state.campos_error: st.error("Contraseña inválida o débil")
        if "no_match" in st.session_state.campos_error: st.error("Las contraseñas no coinciden")

    # 4. ZONA LEGAL
    with st.container(border=True):
        st.markdown(f"#### ⚖️ {t.get('p4_tit', 'Términos Legales')}")
        link_gdpr = "https://www.swarco.com/privacy-policy"
        st.markdown(f"Debe leer y aceptar la [Política de Privacidad]({link_gdpr}).", unsafe_allow_html=True)
        chk = st.checkbox("He leído,
