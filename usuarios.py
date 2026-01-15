# ARCHIVO: usuarios.py
# VERSIÓN: v1.0 (Integración Inicial)
# FECHA: 15-Ene-2026
# DESCRIPCIÓN: Conecta estilos, paises y correo. Elimina código duplicado.

import streamlit as st
import pandas as pd
import time
import re

# --- 1. IMPORTACIÓN DE TUS MÓDULOS MAESTROS ---
import estilos                # Para el diseño Naranja/Azul y el Logo
from paises import PAISES_DATA # Para la lista automática de países
import correo                  # Para enviar el mail de bienvenida

# --- 2. FUNCIONES DE AYUDA ---
def validar_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

def chequear_fuerza_clave(p):
    if len(p) < 8: return "🔴 Muy corta", False
    if not re.search(r"[A-Z]", p) or not re.search(r"[0-9]", p): return "🟠 Media", False
    return "🟢 Fuerte", True

# ==========================================
# A. PANTALLA DE LOGIN
# ==========================================
def gestionar_acceso(conn, t):
    # Cargar diseño global y logo desde estilos.py
    estilos.cargar_estilos()
    estilos.mostrar_logo()
    
    # Títulos usando tus estilos
    st.markdown(f"<h3>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h5>{t.get('login_tit', 'Acceso Usuarios')}</h5>", unsafe_allow_html=True)

    with st.container(border=True):
        user_in = st.text_input(t.get('user_id', 'Usuario'), key="login_u")
        pass_in = st.text_input(t.get('pass', 'Contraseña'), type="password", key="login_p")
        
        # El botón tomará el color Naranja de estilos.py automáticamente
        if st.button(t.get('btn_entrar', 'INGRESAR'), use_container_width=True, key="btn_login"):
            try:
                # Lectura de Google Sheets
                df = conn.read(worksheet="Usuarios", ttl=0)
                if not df.empty:
                    # Validar credenciales
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
                    st.error("⚠️ Base de datos vacía o desconectada")
            except Exception as e:
                st.error(f"⚠️ Error de conexión: {e}")

    st.markdown("---")
    if st.button(t.get('btn_ir_registro', 'Crear Cuenta Nueva'), key="goto_reg", use_container_width=True):
        st.session_state.mostrar_registro = True
        st.rerun()

# ==========================================
# B. PANTALLA DE REGISTRO (INTEGRADA)
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
        # Usamos t.get con texto por defecto por si falta la traducción en idiomas.py
        with c1: nombre = st.text_input(f"{t.get('nombre', 'Nombre')} *", key="r_nom")
        with c2: apellido = st.text_input(f"{t.get('apellido', 'Apellido')} *", key="r_ape")
        
        empresa = st.text_input(f"{t.get('cliente', 'Empresa')} *", key="r_emp")
        email = st.text_input(f"{t.get('email', 'Email')} *", key="r_mail")

        # 2. UBICACIÓN (Conectado a paises.py)
        st.markdown(f"<div class='section-header'>{t.get('p2_tit', 'Ubicación')}</div>", unsafe_allow_html=True)
        
        # Traemos las llaves del diccionario de tu archivo paises.py
        lista_paises = list(PAISES_DATA.keys())
        
        # Intentamos seleccionar Spain por defecto
        try: idx_def = lista_paises.index("Spain")
        except: idx_def = 0
            
        col_p, col_t = st.columns([1, 2])
        with col_p:
            pais_sel = st.selectbox(t.get('pais', 'País'), lista_paises, index=idx_def, key="r_pais")
            # Obtenemos el prefijo automáticamente de tu archivo
            prefijo = PAISES_DATA[pais_sel] 
        with col_t:
            tel = st.text_input(f"{t.get('tel', 'Teléfono')} ({prefijo}) *", key="r_tel")

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
                # Validaciones locales
                errores = []
                if not (nombre and apellido and empresa and email and tel and uid): errores.append("Campos vacíos")
                if p1 != p2: errores.append("Contraseñas no coinciden")
                if not acepta: errores.append("Aceptar política")
                
                if errores:
                    st.error(f"⚠️ Error: {', '.join(errores)}")
                else:
                    # PROCESO DE GUARDADO
                    try:
                        # 1. Crear DataFrame para enviar a Google Sheets
                        nuevo_usuario = pd.DataFrame([{
                            "Usuario": uid,
                            "Password": p1,
                            "Empresa": empresa,
                            "Email": email,
                            "Telefono": f"{prefijo} {tel}",
                            "Pais": pais_sel,
                            "Fecha": time.strftime("%Y-%m-%d")
                        }])
                        
                        # --- IMPORTANTE: DESCOMENTAR ESTA LÍNEA CUANDO TENGAS LA HOJA CONECTADA ---
                        # conn.create(worksheet="Usuarios", data=nuevo_usuario)
                        st.info("ℹ️ Simulando guardado en BD...")

                        # 2. Enviar Correo (Usando tu archivo correo.py)
                        with st.spinner("📧 Enviando credenciales..."):
                            # Llamamos a la función nueva que agregamos al cartero
                            exito_mail = correo.enviar_correo_bienvenida(email, nombre, uid, p1)

                        if exito_mail:
                            st.success(t.get('exito_reg', '¡Cuenta creada y correo enviado!'))
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
            
