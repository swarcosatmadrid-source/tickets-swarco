# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 8.0.0 (Importando módulo externo 'paises.py')
# =============================================================================
import streamlit as st
import pandas as pd
import hashlib
import re
import time
import estilos
import correo
import paises  # <--- AQUÍ LLAMAMOS A TU ARCHIVO EXISTENTE

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

    # 1. ZONA IDENTIFICACIÓN
    with st.container(border=True):
        st.markdown(f"#### 👤 {t.get('p1_tit', 'Identificación')}")
        c1, c2 = st.columns(2)
        n = c1.text_input("Nombre *")
        a = c2.text_input("Apellido *")
        cargo = st.text_input("Cargo / Puesto *", placeholder="Ej: Jefe de Sala, Técnico")

    # 2. ZONA UBICACIÓN (Usando paises.py)
    with st.container(border=True):
        st.markdown(f"#### 🌍 {t.get('p2_tit', 'Ubicación')}")
        e = st.text_input("Empresa / Entidad *")
        
        # Email con validación inmediata
        m = st.text_input("Email Corporativo *").lower().strip()
        email_valido = False
        if m:
            if "@" not in m:
                st.warning("⚠️ Formato incorrecto")
            elif usuario_existe(conn, m):
                st.error("⛔ USUARIO DUPLICADO: Correo ya registrado.")
            else:
                st.success("✅ Disponible")
                email_valido = True
        
        st.divider()
        st.caption("Contacto Internacional")
        
        # --- LLAMADA A TU ARCHIVO PAISES.PY ---
        col_pais, col_pref, col_tel = st.columns([3, 1.5, 3])
        
        with col_pais:
            # Función 1 de tu archivo: Obtener nombres
            lista_paises = paises.obtener_lista_nombres()
            
            # Intentamos seleccionar España por defecto si existe en tu lista
            idx = lista_paises.index("España") if "España" in lista_paises else 0
            pais_sel = st.selectbox("País *", lista_paises, index=idx)
        
        with col_pref:
            # Función 2 de tu archivo: Obtener prefijo del país seleccionado
            pref_auto = paises.obtener_prefijo(pais_sel)
            st.text_input("Prefijo", value=pref_auto, disabled=True)
        
        with col_tel:
            raw_tel = st.text_input("Nº Móvil *", placeholder="Solo números")
            tl_num = limpiar_telefono_simple(raw_tel)

    # 3. ZONA SEGURIDAD
    with st.container(border=True):
        st.markdown(f"#### 🔒 {t.get('p3_tit', 'Seguridad')}")
        st.caption("Requisitos: 8 caracteres, Mayús, Minús, Núm y Símbolo.")
        
        p1 = st.text_input("Contraseña *", type='password')
        if p1:
            prog, etiq, col = validar_fuerza_clave(p1)
            st.markdown(f"""
                <div style="background-color:#ddd;height:5px;border-radius:2px;"><div style="width:{prog}%;background-color:{col};height:100%;"></div></div>
                <small style="color:{col}">{etiq}</small>
            """, unsafe_allow_html=True)

        p2 = st.text_input("Repetir Contraseña *", type='password')
        clave_valida = False
        if p2:
            if p1 == p2:
                st.success("✅ Coinciden")
                clave_valida = True
            else:
                st.error("❌ No coinciden")

    # 4. ZONA LEGAL
    with st.container(border=True):
        st.markdown(f"#### ⚖️ {t.get('p4_tit', 'Términos Legales')}")
        link_gdpr = "https://www.swarco.com/privacy-policy"
        st.markdown(f"Debe leer y aceptar la [Política de Privacidad]({link_gdpr}).", unsafe_allow_html=True)
        chk = st.checkbox("He leído, comprendo y acepto los términos.")

    st.divider()

    # --- BOTÓN FINAL ---
    if st.button("REGISTRAR USUARIO", type="primary", use_container_width=True):
        errores = []
        if not n: errores.append("Falta Nombre")
        if not a: errores.append("Falta Apellido")
        if not cargo: errores.append("Falta Cargo")
        if not e: errores.append("Falta Empresa")
        if not email_valido: errores.append("Email inválido o duplicado")
        if not tl_num or len(tl_num) < 6: errores.append("Teléfono inválido")
        if not clave_valida: errores.append("Contraseñas no válidas")
        if not chk: errores.append("Debe aceptar política")

        if errores:
            st.error("⛔ Faltan datos:")
            for err in errores: st.error(f"- {err}")
        else:
            try:
                # GUARDADO CON COLUMNAS SEPARADAS
                # Orden: Nombre | Apellido | Cargo | Empresa | País | Prefijo | Teléfono | Email | Password
                conn.worksheet("Usuarios").append_row([
                    n, 
                    a, 
                    cargo, 
                    e, 
                    pais_sel,   # Dato de paises.py
                    pref_auto,  # Dato de paises.py
                    tl_num,     # Teléfono limpio
                    m, 
                    encriptar_password(p1)
                ])
                
                # ENVÍO DE CORREO
                correo.enviar_correo_bienvenida(m, n, m, p1)
                
                st.success("✅ REGISTRO EXITOSO")
                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()
                
            except Exception as ex:
                st.error(f"Error técnico: {ex}")

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
