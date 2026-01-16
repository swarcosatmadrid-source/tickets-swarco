# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 6.0.0 (Validación En Tiempo Real + Prefijos + Cargo)
# =============================================================================
import streamlit as st
import pandas as pd
import hashlib
import re
import time
import estilos
import correo

# --- Lógica Auxiliar ---
def limpiar_telefono_simple(texto):
    if not texto: return ""
    return re.sub(r'[^0-9]', '', texto) # Solo números, el + va en el prefijo

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
    """Chequeo rápido de duplicados"""
    try:
        df = pd.DataFrame(conn.worksheet("Usuarios").get_all_records())
        if not df.empty and email_input.lower() in df['email'].astype(str).str.lower().values:
            return True
    except: return False
    return False

# --- Interfaz Interactiva ---
def interfaz_registro_legal(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "ALTA DE USUARIO")}</p>', unsafe_allow_html=True)

    # 1. ZONA IDENTIFICACIÓN
    with st.container(border=True):
        st.markdown(f"#### 👤 {t.get('p1_tit', 'Identificación')}")
        c1, c2 = st.columns(2)
        n = c1.text_input("Nombre *")
        a = c2.text_input("Apellido *")
        
        # NUEVO CAMPO: CARGO
        cargo = st.text_input("Cargo / Puesto *", placeholder="Ej: Jefe de Sala, Operador, Técnico")

    # 2. ZONA UBICACIÓN (Validación Email Inmediata)
    with st.container(border=True):
        st.markdown(f"#### 🌍 {t.get('p2_tit', 'Ubicación')}")
        e = st.text_input("Empresa / Entidad *")
        
        # EMAIL CON VALIDACIÓN AL VUELO
        m = st.text_input("Email Corporativo *").lower().strip()
        email_valido = False
        if m:
            if "@" not in m:
                st.warning("⚠️ Formato de correo inválido")
            elif usuario_existe(conn, m):
                st.error("⛔ ESTE USUARIO YA EXISTE. Por favor use otro correo o recupere contraseña.")
            else:
                st.success("✅ Correo disponible")
                email_valido = True
        
        # TELÉFONO CON PREFIJO SEPARADO
        st.caption("Teléfono de Contacto")
        cp1, cp2 = st.columns([1, 2])
        prefijo = cp1.selectbox("Prefijo", ["+34 (ES)", "+58 (VE)", "+1 (US)", "+57 (CO)", "+54 (AR)", "+49 (DE)"])
        raw_tel = cp2.text_input("Número Móvil *", placeholder="Sin prefijo")
        tl_num = limpiar_telefono_simple(raw_tel)
        
        telefono_completo = f"{prefijo.split()[0]} {tl_num}"

    # 3. ZONA SEGURIDAD (Validación Clave Inmediata)
    with st.container(border=True):
        st.markdown(f"#### 🔒 {t.get('p3_tit', 'Seguridad')}")
        
        p1 = st.text_input("Contraseña *", type='password')
        clave_valida = False
        
        # Barra de fuerza en tiempo real
        if p1:
            prog, etiq, col = validar_fuerza_clave(p1)
            st.markdown(f"""
                <div style="background-color:#ddd;height:5px;border-radius:2px;"><div style="width:{prog}%;background-color:{col};height:100%;"></div></div>
                <small style="color:{col}">{etiq}</small>
            """, unsafe_allow_html=True)

        p2 = st.text_input("Repetir Contraseña *", type='password')
        
        # Chequeo inmediato de coincidencia
        if p2:
            if p1 == p2:
                st.success("✅ Las contraseñas coinciden")
                clave_valida = True
            else:
                st.error("❌ LAS CONTRASEÑAS NO COINCIDEN")

    # 4. ZONA LEGAL
    with st.container(border=True):
        chk = st.checkbox("He leído y acepto la Política de Privacidad de SWARCO")

    st.divider()

    # --- BOTÓN DE REGISTRO (Solo funciona si todo está OK) ---
    if st.button("REGISTRAR USUARIO AHORA", type="primary", use_container_width=True):
        errores = []
        
        # Validaciones finales de obligatoriedad
        if not n: errores.append("Falta Nombre")
        if not a: errores.append("Falta Apellido")
        if not cargo: errores.append("Falta Cargo")
        if not e: errores.append("Falta Empresa")
        if not email_valido: errores.append("Email inválido o duplicado")
        if not tl_num or len(tl_num) < 6: errores.append("Teléfono inválido")
        if not clave_valida: errores.append("Contraseñas no coinciden o inseguras")
        if not chk: errores.append("Debe aceptar términos")

        if errores:
            st.error("⚠️ NO SE PUEDE REGISTRAR:")
            for err in errores: st.error(f"- {err}")
        else:
            try:
                # Guardar en Google Sheets (Ojo: Añadí la columna CARGO)
                # Orden: Nombre, Apellido, Cargo, Empresa, Prefijo+Tel, Email, Password
                conn.worksheet("Usuarios").append_row([
                    n, a, cargo, e, telefono_completo, m, encriptar_password(p1)
                ])
                
                # Enviar Correo
                envio_ok = correo.enviar_correo_bienvenida(m, n, m, p1)
                
                if envio_ok:
                    st.success("✅ ¡USUARIO CREADO Y CORREO ENVIADO!")
                else:
                    st.warning("✅ Usuario creado, pero el correo falló (revisar consola).")

                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()
                
            except Exception as ex:
                st.error(f"Error crítico: {ex}")

    if st.button("Cancelar"):
        st.session_state.mostrar_registro = False
        st.rerun()

# --- Login (Sin cambios) ---
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
