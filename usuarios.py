# ARCHIVO: usuarios.py
# VERSIÓN: v1.1 (Con Traducción de Países)
# FECHA: 15-Ene-2026
# DESCRIPCIÓN: Ahora traduce la lista de países dinámicamente según el idioma seleccionado.

import streamlit as st
import pandas as pd
import time
import re
from deep_translator import GoogleTranslator # Importamos el traductor aquí también

# --- 1. IMPORTACIÓN DE TUS MÓDULOS MAESTROS ---
import estilos
from paises import PAISES_DATA
import correo

# --- 2. FUNCIONES DE AYUDA ---
def validar_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def chequear_fuerza_clave(p):
    if len(p) < 8: return "🔴 Muy corta", False
    if not re.search(r"[A-Z]", p) or not re.search(r"[0-9]", p): return "🟠 Media", False
    return "🟢 Fuerte", True

# --- 3. FUNCIÓN ESPECIAL DE TRADUCCIÓN DE PAÍSES (CACHÉ) ---
@st.cache_data(show_spinner=False)
def obtener_paises_traducidos(diccionario_original, codigo_idioma):
    """
    Traduce las claves (nombres de países) del diccionario original al idioma destino.
    Usa caché para no traducir cada vez que se recarga la página.
    """
    # Si es inglés, no hacemos nada (ahorramos tiempo)
    if codigo_idioma == 'en':
        return diccionario_original

    # Corrección de códigos para Google (igual que en idiomas.py)
    mapa_correccion = {"he": "iw", "zh": "zh-CN", "jv": "jw"}
    codigo_google = mapa_correccion.get(codigo_idioma, codigo_idioma)

    nombres_en = list(diccionario_original.keys())
    prefijos = list(diccionario_original.values())

    try:
        # TRADUCCIÓN POR LOTES (Mucho más rápido que uno por uno)
        traductor = GoogleTranslator(source='en', target=codigo_google)
        nombres_traducidos = traductor.translate_batch(nombres_en)
        
        # Reconstruimos el diccionario: {Nombre Traducido: Prefijo Original}
        # Usamos zip para unir nombre nuevo con prefijo viejo
        nuevo_dict = dict(zip(nombres_traducidos, prefijos))
        
        # Lo ordenamos alfabéticamente según el nuevo idioma
        return dict(sorted(nuevo_dict.items()))
        
    except Exception as e:
        # Si falla (ej. sin internet), devolvemos la lista en inglés
        return diccionario_original

# ==========================================
# A. PANTALLA DE LOGIN
# ==========================================
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
                        st.error("❌ Credenciales incorrectas")
                else:
                    st.error("⚠️ Base de datos vacía")
            except Exception as e:
                st.error(f"⚠️ Error de conexión: {e}")

    st.markdown("---")
    if st.button(t.get('btn_ir_registro', 'Crear Cuenta Nueva'), key="goto_reg", use_container_width=True):
        st.session_state.mostrar_registro = True
        st.rerun()

# ==========================================
# B. PANTALLA DE REGISTRO
# ==========================================
def interfaz_registro_legal(conn, t):
    estilos.cargar_estilos()
    estilos.mostrar_logo()
    
    st.markdown("<h3>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4>{t.get('reg_tit', 'Registro de Nuevo Usuario')}</h4>", unsafe_allow_html=True)

    with st.container(border=True):
        # 1. DATOS PERSONALES
        st.markdown(f"<div class='section-header'>{t.get('p1_tit', 'Datos Personales')}</div>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1: nombre = st.text_input(f"{t.get('nombre', 'Nombre')} *", key="r_nom")
        with c2: apellido = st.text_input(f"{t.get('apellido', 'Apellido')} *", key="r_ape")
        
        empresa = st.text_input(f"{t.get('cliente', 'Empresa')} *", key="r_emp")
        email = st.text_input(f"{t.get('email', 'Email')} *", key="r_mail")

        # 2. UBICACIÓN (¡AHORA CON TRADUCCIÓN!)
        st.markdown(f"<div class='section-header'>{t.get('p2_tit', 'Ubicación')}</div>", unsafe_allow_html=True)
        
        # --- AQUÍ OCURRE LA MAGIA ---
        # Detectamos el idioma actual desde la sesión (viene de main.py)
        codigo_actual = st.session_state.get('codigo_lang', 'es')
        
        # Llamamos a la función que traduce el diccionario PAISES_DATA
        with st.spinner("🌍 Cargando lista de países..."):
            paises_localizados = obtener_paises_traducidos(PAISES_DATA, codigo_actual)
        
        lista_nombres_paises = list(paises_localizados.keys())
        
        # Intentamos buscar "España" o "Spain" o la traducción correspondiente para ponerla por defecto
        # Truco: buscamos si hay algún país que contenga "Spa", "Esp", "Isr" (para Israel) etc, o por defecto el primero
        idx_def = 0
        target_default = "Spain" if codigo_actual == 'en' else "España"
        if codigo_actual == 'he': target_default = "ספרד" # España en Hebreo (aprox)

        if target_default in lista_nombres_paises:
            idx_def = lista_nombres_paises.index(target_default)
            
        col_p, col_t = st.columns([1, 2])
        with col_p:
            pais_sel = st.selectbox(t.get('pais', 'País'), lista_nombres_paises, index=idx_def, key="r_pais")
            # Obtenemos el prefijo del diccionario traducido
            prefijo = paises_localizados[pais_sel] 
        with col_t:
            tel = st.text_input(f"{t.get('tel', 'Teléfono')} ({prefijo}) *", key="r_tel")
        # ----------------------------

        # 3. SEGURIDAD
        st.markdown(f"<div class='section-header'>{t.get('p3_tit', 'Seguridad')}</div>", unsafe_allow_html=True)
        uid = st.text_input(f"{t.get('user_id', 'Usuario Deseado')} *", key="r_uid")
        
        cp1, cp2 = st.columns(2)
        with cp1: p1 = st.text_input(f"{t.get('pass', 'Contraseña')} *", type="password", key="r_p1")
        with cp2: p2 = st.text_input(f"{t.get('pass_rep', 'Repetir')} *", type="password", key="r_p2")
        
        if p1:
            msg, fuerte = chequear_fuerza_clave(p1)
            st.caption(f"Nivel: {msg}")

        # 4. LEGAL
        st.markdown("---")
        acepta = st.checkbox(t.get('acepto', 'Acepto Política de Privacidad'), key="r_ok")

        # BOTONES
        c_reg, c_vol = st.columns(2)
        with c_reg:
            if st.button(t.get('btn_generar', 'REGISTRAR'), use_container_width=True, key="btn_save_reg"):
                errores = []
                if not (nombre and apellido and empresa and email and tel and uid): errores.append("Campos vacíos")
                if p1 != p2: errores.append("Contraseñas no coinciden")
                if not acepta: errores.append("Aceptar política")
                
                if errores:
                    st.error(f"⚠️ {errores}")
                else:
                    try:
                        # Guardamos en BD
                        nuevo_usuario = pd.DataFrame([{
                            "Usuario": uid,
                            "Password": p1,
                            "Empresa": empresa,
                            "Email": email,
                            "Telefono": f"{prefijo} {tel}",
                            "Pais": pais_sel, # Guardará el nombre traducido (ej: "Alemania" o "Germany")
                            "Fecha": time.strftime("%Y-%m-%d")
                        }])
                        
                        # conn.create(worksheet="Usuarios", data=nuevo_usuario)
                        st.info("ℹ️ Simulando guardado en BD...")

                        # Enviar Correo
                        with st.spinner("📧 Enviando credenciales..."):
                            exito_mail = correo.enviar_correo_bienvenida(email, nombre, uid, p1)

                        if exito_mail:
                            st.success(t.get('exito_reg', '¡Cuenta creada!'))
                            st.balloons()
                            time.sleep(3)
                            st.session_state.mostrar_registro = False
                            st.rerun()
                        else:
                            st.warning("Usuario guardado, pero falló el envío del correo (Revise Secrets).")
                            time.sleep(4)
                            st.session_state.mostrar_registro = False
                            st.rerun()

                    except Exception as e:
                        st.error(f"Error técnico: {e}")
        
        with c_vol:
            if st.button(t.get('btn_volver', 'VOLVER'), use_container_width=True, key="btn_back_reg"):
                st.session_state.mostrar_registro = False
                st.rerun()
