# ARCHIVO: usuarios.py
# PROYECTO: TicketV0
# VERSIÓN: v1.3 (Diseño Final)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Gestiona el Login y el Registro con 4 pasos (Datos, Ubicación, Seguridad, Legal) y Manualito.

import streamlit as st
import pandas as pd
import time
import re
from deep_translator import GoogleTranslator
import estilos
from paises import PAISES_DATA
import correo

# --- AYUDAS ---
def chequear_fuerza_clave(p):
    if len(p) < 8: return "🔴 Débil/Weak", False
    if not re.search(r"[A-Z]", p) or not re.search(r"[0-9]", p): return "🟠 Media/Medium", False
    return "🟢 Fuerte/Strong", True

# --- CACHÉ PAÍSES ---
@st.cache_data(show_spinner=False)
def obtener_paises_traducidos(diccionario_original, codigo_idioma):
    if codigo_idioma == 'en': return diccionario_original
    mapa_correccion = {"he": "iw", "zh": "zh-CN", "jv": "jw"}
    codigo_google = mapa_correccion.get(codigo_idioma, codigo_idioma)
    
    nombres_en = list(diccionario_original.keys())
    prefijos = list(diccionario_original.values())
    try:
        traductor = GoogleTranslator(source='en', target=codigo_google)
        nombres_traducidos = traductor.translate_batch(nombres_en)
        nuevo_dict = dict(zip(nombres_traducidos, prefijos))
        return dict(sorted(nuevo_dict.items()))
    except:
        return diccionario_original

# --- LOGIN ---
def gestionar_acceso(conn, t):
    estilos.cargar_estilos()
    estilos.mostrar_logo()
    st.markdown(f"<h3>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h5>{t.get('login_tit', 'Acceso Usuarios')}</h5>", unsafe_allow_html=True)

    with st.container(border=True):
        user_in = st.text_input(t.get('user_id', 'Usuario'), key="login_u")
        pass_in = st.text_input(t.get('pass', 'Contraseña'), type="password", key="login_p")
        
        if st.button(t.get('btn_entrar', 'INGRESAR'), use_container_width=True, key="btn_login"):
            try:
                df = conn.read(worksheet="Usuarios", ttl=0)
                if not df.empty:
                    df['Usuario'] = df['Usuario'].astype(str)
                    df['Password'] = df['Password'].astype(str)
                    validar = df[(df['Usuario'] == user_in) & (df['Password'] == pass_in)]
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
                        st.error("❌ Credenciales incorrectas")
                else:
                    st.error("⚠️ BD Vacía")
            except Exception as e:
                st.error(f"⚠️ Error Conexión: {e}")

    st.markdown("---")
    if st.button(t.get('btn_ir_registro', 'Crear Cuenta Nueva'), key="goto_reg", use_container_width=True):
        st.session_state.mostrar_registro = True
        st.rerun()

# --- REGISTRO ---
def interfaz_registro_legal(conn, t):
    estilos.cargar_estilos()
    estilos.mostrar_logo()
    st.markdown("<h3>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4>{t.get('reg_tit', 'Registro')}</h4>", unsafe_allow_html=True)

    # 0. Manualito
    with st.expander(t.get('guia_titulo', '📘 Guía')):
        st.info(t.get('guia_desc', 'Instrucciones...'))

    with st.container(border=True):
        # 1. Datos
        st.markdown(f"<div class='section-header'>{t.get('p1_tit', '1. Identificación')}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: nombre = st.text_input(f"{t.get('nombre', 'Nombre')} *", key="r_nom")
        with c2: apellido = st.text_input(f"{t.get('apellido', 'Apellido')} *", key="r_ape")
        empresa = st.text_input(f"{t.get('cliente', 'Empresa')} *", key="r_emp", help=t.get('help_empresa', ''))
        email = st.text_input(f"{t.get('email', 'Email')} *", key="r_mail")

        # 2. Ubicación
        st.markdown(f"<div class='section-header'>{t.get('p2_tit', '2. Ubicación')}</div>", unsafe_allow_html=True)
        codigo_actual = st.session_state.get('codigo_lang', 'es')
        with st.spinner("🌍 ..."):
            paises_localizados = obtener_paises_traducidos(PAISES_DATA, codigo_actual)
        
        lista_nombres_paises = list(paises_localizados.keys())
        idx_def = 0
        target_default = "Spain" if codigo_actual == 'en' else "España"
        if codigo_actual == 'he': target_default = "ספרד"
        if target_default in lista_nombres_paises: idx_def = lista_nombres_paises.index(target_default)
            
        col_p, col_t = st.columns([1, 2])
        with col_p:
            pais_sel = st.selectbox(t.get('pais', 'País'), lista_nombres_paises, index=idx_def, key="r_pais")
            prefijo = paises_localizados[pais_sel] 
        with col_t:
            tel = st.text_input(f"{t.get('tel', 'Teléfono')} ({prefijo}) *", key="r_tel")

        # 3. Seguridad
        st.markdown(f"<div class='section-header'>{t.get('p3_tit', '3. Seguridad')}</div>", unsafe_allow_html=True)
        uid = st.text_input(f"{t.get('user_id', 'Usuario')} *", key="r_uid", help=t.get('help_user', ''))
        cp1, cp2 = st.columns(2)
        with cp1: p1 = st.text_input(f"{t.get('pass', 'Contraseña')} *", type="password", key="r_p1", help=t.get('help_pass', ''))
        with cp2: p2 = st.text_input(f"{t.get('pass_rep', 'Repetir')} *", type="password", key="r_p2")
        if p1:
            msg, fuerte = chequear_fuerza_clave(p1)
            st.caption(f"Nivel: {msg}")

        # 4. Legal
        st.markdown(f"<div class='section-header'>{t.get('p4_tit', '4. Legal')}</div>", unsafe_allow_html=True)
        link_url = "https://www.swarco.com/privacy-policy"
        texto_link = t.get('link_texto', 'Política de Privacidad')
        st.markdown(f"📄 [{texto_link}]({link_url})")
        acepta = st.checkbox(f"{t.get('acepto', 'Acepto')} {texto_link}", key="r_ok")

        # Botones
        st.markdown("---")
        c_reg, c_vol = st.columns(2)
        with c_reg:
            if st.button(t.get('btn_generar', 'REGISTRAR'), use_container_width=True, key="btn_save_reg"):
                errores = []
                if not (nombre and apellido and empresa and email and tel and uid): errores.append("Faltan campos")
                if p1 != p2: errores.append("Claves no coinciden")
                if not acepta: errores.append("Aceptar política")
                
                if errores:
                    st.error(f"⚠️ {errores}")
                else:
                    try:
                        nuevo_usuario = pd.DataFrame([{
                            "Usuario": uid, "Password": p1, "Empresa": empresa,
                            "Email": email, "Telefono": f"{prefijo} {tel}",
                            "Pais": pais_sel, "Fecha": time.strftime("%Y-%m-%d")
                        }])
                        conn.create(worksheet="Usuarios", data=nuevo_usuario)
                        
                        with st.spinner("📧 ..."):
                            exito_mail = correo.enviar_correo_bienvenida(email, nombre, uid, p1)

                        if exito_mail:
                            st.success(t.get('exito_reg', 'Cuenta creada'))
                            st.balloons()
                            time.sleep(3)
                            st.session_state.mostrar_registro = False
                            st.rerun()
                        else:
                            st.warning("Guardado, pero falló correo.")
                            time.sleep(4)
                            st.session_state.mostrar_registro = False
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        with c_vol:
            if st.button(t.get('btn_volver', 'VOLVER'), use_container_width=True, key="btn_back_reg"):
                st.session_state.mostrar_registro = False
                st.rerun()
