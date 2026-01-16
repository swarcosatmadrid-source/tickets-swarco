# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 8.6.0 (Limpieza automática de errores + Aviso Clave Débil)
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
    """
    Retorna: Score (numérico), Etiqueta (Texto), Color (Hex)
    """
    score = 0
    if len(password) >= 8: score += 1
    if re.search(r"[A-Z]", password): score += 1
    if re.search(r"[a-z]", password): score += 1
    if re.search(r"[0-9]", password): score += 1
    if re.search(r"[@$!%*?&#]", password): score += 1
    
    # 0-2: Débil (Rojo)
    # 3-4: Media (Amarillo) -> ACEPTABLE
    # 5:   Robusta (Verde) -> IDEAL
    
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

    # HELPER: Limpia el error de la lista si el campo ya tiene datos
    def limpiar_error_si_existe(campo):
        if campo in st.session_state.campos_error:
            st.session_state.campos_error.remove(campo)

    # 1. ZONA IDENTIFICACIÓN
    with st.container(border=True):
        st.markdown(f"#### 👤 {t.get('p1_tit', 'Identificación')}")
        c1, c2 = st.columns(2)
        
        # Nombre
        n = c1.text_input("Nombre *")
        if n: limpiar_error_si_existe("n") # Auto-limpieza
        if "n" in st.session_state.campos_error: c1.error("Falta Nombre")
        
        # Apellido
        a = c2.text_input("Apellido *")
        if a: limpiar_error_si_existe("a") # Auto-limpieza
        if "a" in st.session_state.campos_error: c2.error("Falta Apellido")

    # 2. ZONA UBICACIÓN Y DATOS
    with st.container(border=True):
        st.markdown(f"#### 🌍 {t.get('p2_tit', 'Datos Profesionales')}")
        
        c_cargo, c_empresa = st.columns(2)
        
        # Cargo
        cargo = c_cargo.text_input("Cargo / Puesto *")
        if cargo: limpiar_error_si_existe("cargo")
        if "cargo" in st.session_state.campos_error: c_cargo.error("Falta Cargo")
        
        # Empresa
        e = c_empresa.text_input("Empresa / Entidad *")
        if e: limpiar_error_si_existe("e")
        if "e" in st.session_state.campos_error: c_empresa.error("Falta Empresa")
        
        # Email
        m = st.text_input("Email Corporativo *").lower().strip()
        
        # Lógica Email
        if m:
            if "@" not in m:
                # Si formato malo, no limpiamos error 'm'
                pass 
            elif usuario_existe(conn, m):
                st.error("⛔ Correo ya registrado.")
                if "duplicado" not in st.session_state.campos_error:
                    st.session_state.campos_error.append("duplicado")
            else:
                # Si todo OK, limpiamos errores
                limpiar_error_si_existe("m")
                limpiar_error_si_existe("duplicado")
                st.success("✅ Disponible")
        
        if "m" in st.session_state.campos_error: st.error("Email inválido")

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
            tl_num = st.text_input("Nº Móvil *", placeholder="Ej: 600123456")
            
            # Validación en vivo
            if tl_num:
                if not tl_num.isdigit():
                    st.error("⚠️ Solo números", icon="🚫")
                elif len(tl_num) >= 6:
                    limpiar_error_si_existe("tl") # Auto-limpieza
            
            if "tl" in st.session_state.campos_error: st.error("Mínimo 6 dígitos")

    # 3. ZONA SEGURIDAD
    with st.container(border=True):
        st.markdown(f"#### 🔒 {t.get('p3_tit', 'Seguridad')}")
        st.caption("Requisitos: Mínimo 8 caracteres + Mayúscula + Número.")
        
        p1 = st.text_input("Contraseña *", type='password')
        
        # BARRA DE FUERZA + AVISO
        clave_es_segura = False
        if p1:
            prog, etiq, col = validar_fuerza_clave(p1)
            # Pintamos la barra
            st.markdown(f"""
                <div style="background-color:#ddd;height:5px;border-radius:2px;">
                    <div style="width:{prog}%;background-color:{col};height:100%;"></div>
                </div>
                <small style="color:{col}; font-weight:bold;">Nivel actual: {etiq}</small>
            """, unsafe_allow_html=True)

            # AVISO EXPLÍCITO SI ES DÉBIL
            if prog < 60: # Menos de Nivel Medio
                st.warning("⚠️ La contraseña es insegura. Debe alcanzar al menos el Nivel Medio 🟡.")
            else:
                clave_es_segura = True
                limpiar_error_si_existe("p1") # Se quita el rojo si ya es segura

        p2 = st.text_input("Repetir Contraseña *", type='password')
        
        if p2 and p1 == p2: limpiar_error_si_existe("no_match")
        
        # Mensajes de error (Al darle al botón)
        if "p1" in st.session_state.campos_error: st.error("Contraseña muy débil. Mejore la seguridad.")
        if "no_match" in st.session_state.campos_error: st.error("Las contraseñas no coinciden")

    # 4. ZONA LEGAL
    with st.container(border=True):
        st.markdown(f"#### ⚖️ {t.get('p4_tit', 'Términos Legales')}")
        link_gdpr = "https://www.swarco.com/privacy-policy"
        st.markdown(f"Debe leer y aceptar la [Política de Privacidad]({link_gdpr}).", unsafe_allow_html=True)
        chk = st.checkbox("He leído, comprendo y acepto los términos.")
        
        if chk: limpiar_error_si_existe("chk") # Auto-limpieza
        if "chk" in st.session_state.campos_error: st.error("Debe aceptar para continuar")

    st.divider()

    # --- BOTÓN DE REGISTRO ---
    if st.button("REGISTRAR USUARIO", type="primary", use_container_width=True):
        errores_detectados = []
        
        # Validaciones de vacío
        if not n: errores_detectados.append("n")
        if not a: errores_detectados.append("a")
        if not cargo: errores_detectados.append("cargo")
        if not e: errores_detectados.append("e")
        if not m or "@" not in m: errores_detectados.append("m")
        if not chk: errores_detectados.append("chk")
        
        # Validación Teléfono
        if not tl_num or not tl_num.isdigit() or len(tl_num) < 6:
            errores_detectados.append("tl")

        # Validaciones Password
        if not p1 or not p2: 
            errores_detectados.append("p1")
        elif p1 != p2:
            errores_detectados.append("no_match")
        else:
            # Validación de Fuerza (Mínimo Medio = 60)
            fuerza, _, _ = validar_fuerza_clave(p1)
            if fuerza < 60: 
                errores_detectados.append("p1")

        # Duplicado
        if m and usuario_existe(conn, m):
            errores_detectados.append("duplicado")

        # RESULTADO
        if errores_detectados:
            st.session_state.campos_error = errores_detectados
            st.error("⚠️ Revise los campos marcados en rojo.") # Alerta general al click
            st.rerun()
        else:
            try:
                conn.worksheet("Usuarios").append_row([
                    n, a, cargo, e, pais_sel, pref_auto, tl_num, m, encriptar_password(p1)
                ])
                correo.enviar_correo_bienvenida(m, n, m, p1)
                
                st.success("✅ USUARIO REGISTRADO EXITOSAMENTE")
                st.session_state.campos_error = []
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
            except: 
                st.error("Error conexión")
    
    st.write("")
    if st.button("Crear cuenta nueva"):
        st.session_state.mostrar_registro = True
        st.rerun()
