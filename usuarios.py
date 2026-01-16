# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 5.0.0 (Validaciones, Prefijos, Limpieza de Input y Legal)
# =============================================================================
import streamlit as st
import pandas as pd
import hashlib
import re # Para limpiar teléfonos y validar email
import estilos
import correo

# --- Lógica de Negocio ---
def limpiar_telefono(texto):
    """Elimina letras, deja solo números y el símbolo +"""
    if not texto: return ""
    return re.sub(r'[^0-9+]', '', texto)

def validar_clave_segura(clave):
    """Reglas: Mínimo 6 caracteres"""
    if len(clave) < 6: return False
    return True

def obtener_prefijo_pais(pais_input):
    """Diccionario básico de prefijos para autocompletar"""
    prefijos = {
        'españa': '+34', 'spain': '+34',
        'venezuela': '+58',
        'colombia': '+57',
        'mexico': '+52', 'méxico': '+52',
        'usa': '+1', 'eeuu': '+1',
        'argentina': '+54',
        'alemania': '+49', 'germany': '+49'
    }
    p = pais_input.lower().strip()
    return prefijos.get(p, '')

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- Interfaz ---
def interfaz_registro_legal(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "REGISTRO OFICIAL")}</p>', unsafe_allow_html=True)

    # Inicialización de errores
    if 'err' not in st.session_state: st.session_state.err = []

    # Función para inyectar estilo de error
    def check_err(campo_key):
        return campo_key in st.session_state.err

    with st.form("registro_pro"):
        
        # --- ZONA 1: IDENTIFICACIÓN ---
        with st.container(border=True):
            st.markdown(f"#### 👤 {t.get('p1_tit', 'Identificación')}")
            st.info("Ingrese sus datos tal como aparecen en su identificación corporativa.", icon="ℹ️")
            
            c1, c2 = st.columns(2)
            # Nombre
            nom_err = "Nombre es obligatorio" if check_err("n") else None
            n = c1.text_input(t.get("nombre", "Nombre"), help="Ej: Juan", placeholder="Su nombre")
            if check_err("n"): c1.error("Campo obligatorio")

            # Apellido
            a = c2.text_input(t.get("apellido", "Apellido"), help="Ej: Pérez", placeholder="Su apellido")
            if check_err("a"): c2.error("Campo obligatorio")

        # --- ZONA 2: UBICACIÓN Y CONTACTO (Inteligente) ---
        with st.container(border=True):
            st.markdown(f"#### 🌍 {t.get('p2_tit', 'Ubicación')}")
            
            e = st.text_input(t.get("cliente", "Empresa / Entidad"), placeholder="Ej: Ayuntamiento de Madrid")
            if check_err("e"): st.error("Falta la empresa")

            c3, c4 = st.columns(2)
            # País
            p = c3.text_input(t.get("pais", "País"), placeholder="Ej: España")
            if check_err("p"): c3.error("Falta país")
            
            # Lógica de Teléfono Inteligente
            prefijo_sugerido = obtener_prefijo_pais(p) if p else ""
            label_tel = t.get("tel", "Teléfono Móvil")
            if prefijo_sugerido: label_tel += f" (Sugerido: {prefijo_sugerido})"
            
            raw_tel = c4.text_input(label_tel, value=prefijo_sugerido, help="Solo números. Se eliminan letras automáticamente.")
            tl = limpiar_telefono(raw_tel) # AUTO-LIMPIEZA DE LETRAS
            if check_err("tl"): c4.error("Teléfono inválido")
            
            # Email
            m = st.text_input(t.get("email", "Correo Corporativo"), help="Se enviará validación").lower().strip()
            if check_err("m"): st.error("Email inválido o vacío")

        # --- ZONA 3: SEGURIDAD (Niveles) ---
        with st.container(border=True):
            st.markdown(f"#### 🔒 {t.get('p3_tit', 'Seguridad')}")
            p1 = st.text_input(t.get("pass", "Contraseña"), type='password', help="Mínimo 6 caracteres")
            p2 = st.text_input(t.get("pass_rep", "Repetir Contraseña"), type='password')
            
            if p1 and len(p1) < 6:
                st.warning("⚠️ La contraseña es muy corta (mínimo 6)")
            if check_err("p1"): st.error("Falta contraseña")

        # --- ZONA 4: LEGAL (Enlace Real) ---
        with st.container(border=True):
            st.markdown(f"#### ⚖️ {t.get('p4_tit', 'Legal')}")
            
            # ENLACE REAL A PROTECCIÓN DE DATOS
            link_gdpr = "https://www.swarco.com/privacy-policy"
            st.markdown(f"He leído y acepto la [Política de Privacidad y Protección de Datos]({link_gdpr}) de SWARCO.", unsafe_allow_html=True)
            
            chk = st.checkbox(t.get("acepto", "Acepto los términos legales"))
            if check_err("chk"): st.error("Debe aceptar los términos para continuar")

        st.divider()
        
        # --- BOTÓN FINAL ---
        if st.form_submit_button(t.get("btn_registro_final", "REGISTRAR CUENTA OFICIAL")):
            errores = []
            
            # Validaciones
            if not n: errores.append("n")
            if not a: errores.append("a")
            if not e: errores.append("e")
            if not p: errores.append("p")
            if not m or "@" not in m: errores.append("m")
            if not tl or len(tl) < 5: errores.append("tl")
            if not p1 or len(p1) < 6: errores.append("p1")
            if not chk: errores.append("chk")
            
            if errores:
                st.session_state.err = errores
                st.error(f"⛔ {t.get('error_campos', 'Error en el formulario. Revise las alertas rojas.')}")
                st.rerun()
            
            elif p1 != p2:
                st.error("⛔ Las contraseñas no coinciden.")
            
            else:
                # ÉXITO
                try:
                    conn.worksheet("Usuarios").append_row([n, a, e, p, m, tl, encriptar_password(p1)])
                    correo.enviar_correo_bienvenida(m, n, m, "******")
                    st.balloons()
                    st.success(f"✅ {t.get('exito_reg', 'Cuenta creada correctamente.')}")
                    st.session_state.mostrar_registro = False
                    st.session_state.err = []
                    # st.rerun() # Opcional: esperar a que el usuario lea
                except Exception as ex:
                    st.error(f"Error de Servidor: {ex}")

    if st.button("⬅ " + t.get("btn_volver", "Cancelar y Volver")):
        st.session_state.mostrar_registro = False
        st.session_state.err = []
        st.rerun()

# Función de Login para mantener coherencia
def gestionar_acceso(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("login_tit", "Acceso")}</p>', unsafe_allow_html=True)
    
    with st.container(border=True):
        with st.form("login_pro"):
            u = st.text_input(t.get("user_id", "Usuario (Email)"))
            p = st.text_input(t.get("pass", "Contraseña"), type='password')
            
            if st.form_submit_button(t.get("btn_entrar", "INICIAR SESIÓN")):
                # Lógica de login (igual que siempre)
                pass 
    
    st.markdown("---")
    st.caption("¿No tiene credenciales?")
    if st.button(t.get("btn_ir_registro", "Solicitar Nueva Cuenta")):
        st.session_state.mostrar_registro = True
        st.rerun()
