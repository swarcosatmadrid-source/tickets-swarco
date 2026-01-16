# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 8.2.0 (Errores en sitio - Adiós lista gigante)
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
def limpiar_telefono_simple(texto):
    if not texto: return ""
    return re.sub(r'[^0-9]', '', texto)

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

    # Inicializamos la lista de errores en memoria si no existe
    if 'campos_error' not in st.session_state: st.session_state.campos_error = []

    # Función helper para mostrar error justo debajo del input
    def mostrar_error(campo):
        if campo in st.session_state.campos_error:
            st.error(f"⚠️ Campo requerido o inválido", icon="🚨")

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
        email_valido = False
        if "m" in st.session_state.campos_error:
            st.error("Email obligatorio o formato incorrecto")
        elif "duplicado" in st.session_state.campos_error:
            st.error("⛔ Este correo ya está registrado.")
        
        # Validación visual inmediata (solo si escribe algo)
        if m and "duplicado" not in st.session_state.campos_error:
            if "@" not in m: st.warning("Formato incorrecto")
            elif usuario_existe(conn, m): st.error("Ya existe")
            else: 
                st.success("Disponible")
                email_valido = True
        
        # Teléfono
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
            raw_tel = st.text_input("Nº Móvil *", placeholder="Solo números")
            tl_num = limpiar_telefono_simple(raw_tel)
            if "tl" in st.session_state.campos_error: st.error("Mínimo 6 dígitos")

    # 3. ZONA SEGURIDAD
    with st.container(border=True):
        st.markdown(f"#### 🔒 {t.get('p3_tit', 'Seguridad')}")
        
        p1 = st.text_input("Contraseña *", type='password')
        if p1:
            prog, etiq, col = validar_fuerza_clave(p1)
            st.markdown(f"""<div style="background-color:#ddd;height:5px;"><div style="width:{prog}%;background-color:{col};height:100%;"></div></div><small style="color:{col}">{etiq}</small>""", unsafe_allow_html=True)
        
        p2 = st.text_input("Repetir Contraseña *", type='password')
        
        # Errores de seguridad
        if "p1" in st.session_state.campos_error: st.error("Contraseña inválida o débil")
        if "no_match" in st.session_state.campos_error: st.error("Las contraseñas no coinciden")

    # 4. ZONA LEGAL
    with st.container(border=True):
        st.markdown(f"#### ⚖️ {t.get('p4_tit', 'Términos Legales')}")
        link_gdpr = "https://www.swarco.com/privacy-policy"
        st.markdown(f"Debe leer y aceptar la [Política de Privacidad]({link_gdpr}).", unsafe_allow_html=True)
        chk = st.checkbox("He leído, comprendo y acepto los términos.")
        if "chk" in st.session_state.campos_error: st.error("Debe aceptar para continuar")

    st.divider()

    # --- BOTÓN DE REGISTRO ---
    if st.button("REGISTRAR USUARIO", type="primary", use_container_width=True):
        # 1. Recopilamos errores
        errores_detectados = []
        
        if not n: errores_detectados.append("n")
        if not a: errores_detectados.append("a")
        if not cargo: errores_detectados.append("cargo")
        if not e: errores_detectados.append("e")
        if not m or "@" not in m: errores_detectados.append("m")
        if not tl_num or len(tl_num) < 6: errores_detectados.append("tl")
        if not chk: errores_detectados.append("chk")
        
        # Validaciones complejas
        if not p1 or not p2: 
            errores_detectados.append("p1")
        elif p1 != p2:
            errores_detectados.append("no_match")
        else:
            # Fuerza
            fuerza, _, _ = validar_fuerza_clave(p1)
            if fuerza < 100: errores_detectados.append("p1")

        # Duplicado (Validación final)
        if m and usuario_existe(conn, m):
            errores_detectados.append("duplicado")

        # 2. DECISIÓN
        if errores_detectados:
            # Si hay errores, los guardamos en estado y RECARGAMOS
            # Esto hace que aparezcan los mensajes rojos DEBAJO de cada campo
            st.session_state.campos_error = errores_detectados
            st.rerun()
        else:
            # TODO OK
            try:
                conn.worksheet("Usuarios").append_row([
                    n, a, cargo, e, pais_sel, pref_auto, tl_num, m, encriptar_password(p1)
                ])
                correo.enviar_correo_bienvenida(m, n, m, p1)
                
                st.success("✅ USUARIO REGISTRADO EXITOSAMENTE")
                st.session_state.campos_error = [] # Limpiamos errores
                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()
            except Exception as ex:
                st.error(f"Error técnico: {ex}")

    if st.button("Cancelar"):
        st.session_state.mostrar_registro = False
        st.session_state.campos_error = []
        st.rerun()

def gestionar_acceso(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("login_tit", "Acceso")}</p>', unsafe_allow_html=True)
    with st.container(border=True):
        u = st.text_input("Usuario")
        p = st.text_input("Contraseña", type='password')
        if st.button("ENTRAR", use_container_width=True):
             try:
                df = pd.DataFrame(conn.worksheet("Usuarios").get_all_records())
                if not df.empty and u.lower().strip() in df['email'].astype(str).str.lower().values:
                    real = df.loc[df['email']==u.lower().strip(), 'password'].values[0]
                    if encriptar_password(p) == real:
                        st.session_state.autenticado = True
                        st.session_state.user_email = u
                        st.session_state.pagina_actual = 'menu'
                        st.rerun()
                    else: st.error("Contraseña incorrecta")
                else: st.error("Usuario no encontrado")
             except: st.error("Error conexión")
    st.write("")
    if st.button("Crear cuenta nueva"):
        st.session_state.mostrar_registro = True
        st.rerun()
