# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 5.2.0 (Seguridad: Antiduplicados + Medidor de Fuerza + Regex)
# =============================================================================
import streamlit as st
import pandas as pd
import hashlib
import re
import time
import estilos
import correo

# --- Lógica de Validación Avanzada ---
def limpiar_telefono(texto):
    if not texto: return ""
    return re.sub(r'[^0-9+]', '', texto)

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def validar_fuerza_clave(password):
    """
    Analiza la contraseña y devuelve:
    - Score (0-4)
    - Mensaje
    - Color
    """
    score = 0
    if len(password) >= 8: score += 1
    if re.search(r"[A-Z]", password): score += 1
    if re.search(r"[a-z]", password): score += 1
    if re.search(r"[0-9]", password): score += 1
    if re.search(r"[@$!%*?&#]", password): score += 1 # Carácter especial
    
    # Normalizamos a porcentaje para la barra
    if score < 3:
        return 20, "Débil 🔴", "#ff4b4b" # Rojo
    elif score < 5:
        return 60, "Media 🟡", "#ffa500" # Naranja
    else:
        return 100, "Robusta 🟢", "#21c354" # Verde

def usuario_existe(conn, email_input):
    """Verifica en Google Sheets si el email ya está registrado"""
    try:
        df = pd.DataFrame(conn.worksheet("Usuarios").get_all_records())
        # Convertimos a minúsculas para comparar peras con peras
        if not df.empty and email_input.lower() in df['email'].astype(str).str.lower().values:
            return True
    except:
        return False # Si falla la lectura, asumimos que no existe para no bloquear (o manejar error)
    return False

# --- Interfaz ---
def interfaz_registro_legal(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "REGISTRO OFICIAL")}</p>', unsafe_allow_html=True)

    if 'err' not in st.session_state: st.session_state.err = []
    def check_err(k): return k in st.session_state.err

    with st.form("registro_blindado"):
        
        # ZONA 1: IDENTIFICACIÓN
        with st.container(border=True):
            st.markdown(f"#### 👤 {t.get('p1_tit', 'Identificación')}")
            c1, c2 = st.columns(2)
            n = c1.text_input(t.get("nombre", "Nombre"))
            if check_err("n"): c1.error("Requerido")
            a = c2.text_input(t.get("apellido", "Apellido"))
            if check_err("a"): c2.error("Requerido")

        # ZONA 2: UBICACIÓN
        with st.container(border=True):
            st.markdown(f"#### 🌍 {t.get('p2_tit', 'Ubicación')}")
            e = st.text_input(t.get("cliente", "Empresa"))
            if check_err("e"): st.error("Falta Empresa")
            
            c3, c4 = st.columns(2)
            p = c3.text_input(t.get("pais", "País"))
            if check_err("p"): c3.error("Requerido")
            
            # Teléfono
            raw_tel = c4.text_input(t.get("tel", "Teléfono"), help="Solo números")
            tl = limpiar_telefono(raw_tel)
            if check_err("tl"): c4.error("Mínimo 5 dígitos")
            
            m = st.text_input(t.get("email", "Email")).lower().strip()
            if check_err("m"): st.error("Email inválido")
            if check_err("duplicado"): st.error("⛔ Este correo ya está registrado en el sistema.")

        # ZONA 3: SEGURIDAD (CON MEDIDOR VISUAL)
        with st.container(border=True):
            st.markdown(f"#### 🔒 {t.get('p3_tit', 'Seguridad')}")
            st.caption("Requisito: 8 caracteres, Mayúscula, Minúscula, Número y Símbolo (@$!%*?&)")
            
            p1 = st.text_input(t.get("pass", "Contraseña"), type='password')
            
            # --- BARRA DE FUERZA ---
            if p1:
                progreso, etiqueta, color = validar_fuerza_clave(p1)
                # Barra visual customizada con HTML
                st.markdown(f"""
                    <div style="background-color: #ddd; border-radius: 5px; height: 10px; width: 100%;">
                        <div style="background-color: {color}; width: {progreso}%; height: 100%; border-radius: 5px; transition: width 0.5s;"></div>
                    </div>
                    <p style="color:{color}; font-weight:bold; margin-top:5px; font-size:0.9em;">Fortaleza: {etiqueta}</p>
                """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="background-color: #eee; border-radius: 5px; height: 10px; width: 100%;"></div>', unsafe_allow_html=True)
            # -----------------------

            p2 = st.text_input(t.get("pass_rep", "Repetir"), type='password')
            
            if check_err("p1_req"): st.error("La contraseña no cumple los requisitos de seguridad.")

        # ZONA 4: LEGAL
        with st.container(border=True):
            link = "https://www.swarco.com/privacy-policy"
            st.markdown(f"Acepto la [Política de Privacidad]({link}) de SWARCO.")
            chk = st.checkbox(t.get("acepto", "He leído y acepto"))
            if check_err("chk"): st.error("Obligatorio aceptar")

        st.divider()
        
        # BOTÓN
        submitted = st.form_submit_button(t.get("btn_registro_final", "REGISTRAR AHORA"))
        
        if submitted:
            errores = []
            
            # 1. Validaciones Básicas
            if not n: errores.append("n")
            if not a: errores.append("a")
            if not e: errores.append("e")
            if not p: errores.append("p")
            if not m or "@" not in m: errores.append("m")
            if not tl or len(tl) < 5: errores.append("tl")
            if not chk: errores.append("chk")
            
            # 2. Validación de Fuerza de Clave
            fuerza, _, _ = validar_fuerza_clave(p1)
            if fuerza < 100: # Exigimos el 100% (Verde)
                errores.append("p1_req")
            
            # 3. Validación de Duplicados (Solo si el email es válido)
            if m and usuario_existe(conn, m):
                errores.append("duplicado")

            if errores:
                st.session_state.err = errores
                st.error("⚠️ Revise las alertas rojas.")
                st.rerun()
            
            elif p1 != p2:
                st.error("Las contraseñas no coinciden.")
            
            else:
                try:
                    # ÉXITO
                    conn.worksheet("Usuarios").append_row([n, a, e, p, m, tl, encriptar_password(p1)])
                    correo.enviar_correo_bienvenida(m, n, m, "******")
                    
                    st.success(f"✅ Usuario {n} registrado correctamente.")
                    
                    st.session_state.err = []
                    st.session_state.mostrar_registro = False
                    time.sleep(1.5)
                    st.rerun()
                    
                except Exception as ex:
                    st.error(f"Error técnico: {ex}")

    if st.button("Cancelar"):
        st.session_state.mostrar_registro = False
        st.session_state.err = []
        st.rerun()

# Mantenemos gestionar_acceso igual
def gestionar_acceso(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("login_tit", "Acceso")}</p>', unsafe_allow_html=True)
    with st.container(border=True):
        with st.form("login_pro"):
            u = st.text_input(t.get("user_id", "Usuario")).lower().strip()
            p = st.text_input(t.get("pass", "Contraseña"), type='password')
            if st.form_submit_button(t.get("btn_entrar", "INICIAR SESIÓN")):
                 try:
                    df = pd.DataFrame(conn.worksheet("Usuarios").get_all_records())
                    if not df.empty and u in df['email'].values:
                        real = df.loc[df['email']==u, 'password'].values[0]
                        if encriptar_password(p) == real:
                            st.session_state.autenticado = True
                            st.session_state.user_email = u
                            st.session_state.pagina_actual = 'menu'
                            st.rerun()
                        else: st.error("Contraseña incorrecta")
                    else: st.error("Usuario no encontrado")
                 except: st.error("Error conexión")
    st.markdown("---")
    if st.button(t.get("btn_ir_registro", "Solicitar Nueva Cuenta")):
        st.session_state.mostrar_registro = True
        st.rerun()
