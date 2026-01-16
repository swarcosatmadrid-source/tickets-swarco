# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 8.8.0 (Optimizado para Autofill + Aviso final claro)
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
    if not email_input: return False
    try:
        records = conn.worksheet("Usuarios").get_all_records()
        df = pd.DataFrame(records)
        if df.empty: return False
        if email_input.lower().strip() in df['email'].astype(str).str.lower().str.strip().values:
            return True
    except: return False
    return False

# --- Interfaz de Registro ---
def interfaz_registro_legal(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "ALTA DE USUARIO")}</p>', unsafe_allow_html=True)
    
    # Inicializar lista de errores
    if 'campos_error' not in st.session_state: st.session_state.campos_error = []

    # HELPER: Limpieza silenciosa (Sin rerun)
    # Esto permite que el autofill funcione sin que la página parpadee
    def limpiar_si_hay_dato(dato, key_error):
        if dato and key_error in st.session_state.campos_error:
            st.session_state.campos_error.remove(key_error)

    # 1. ZONA IDENTIFICACIÓN
    with st.container(border=True):
        st.markdown(f"#### 👤 {t.get('p1_tit', 'Identificación')}")
        c1, c2 = st.columns(2)
        
        n = c1.text_input("Nombre *")
        limpiar_si_hay_dato(n, "n") # Si el autofill pone algo, quitamos el error
        if "n" in st.session_state.campos_error: c1.error("Campo obligatorio")
        
        a = c2.text_input("Apellido *")
        limpiar_si_hay_dato(a, "a")
        if "a" in st.session_state.campos_error: c2.error("Campo obligatorio")

    # 2. ZONA UBICACIÓN
    with st.container(border=True):
        st.markdown(f"#### 🌍 {t.get('p2_tit', 'Datos Profesionales')}")
        
        c_cargo, c_empresa = st.columns(2)
        
        cargo = c_cargo.text_input("Cargo / Puesto *")
        limpiar_si_hay_dato(cargo, "cargo")
        if "cargo" in st.session_state.campos_error: c_cargo.error("Falta Cargo")
        
        e = c_empresa.text_input("Empresa / Entidad *")
        limpiar_si_hay_dato(e, "e")
        if "e" in st.session_state.campos_error: c_empresa.error("Falta Empresa")
        
        # Email
        m = st.text_input("Email Corporativo *").lower().strip()
        
        # Validación Email
        if m:
            if "@" not in m:
                pass # Formato visual se maneja con warning
            elif usuario_existe(conn, m):
                st.error("⛔ DUPLICADO: Correo ya registrado.")
                # No limpiamos error si es duplicado
            else:
                limpiar_si_hay_dato(m, "m")
                st.success("✅ Disponible")

        if "m" in st.session_state.campos_error: st.error("Email requerido o inválido")

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
            if tl_num and tl_num.isdigit():
                limpiar_si_hay_dato(tl_num, "tl")
            
            if tl_num and not tl_num.isdigit():
                st.error("⚠️ Solo números")
            if "tl" in st.session_state.campos_error: st.error("Mínimo 6 dígitos")

    # 3. ZONA SEGURIDAD
    with st.container(border=True):
        st.markdown(f"#### 🔒 {t.get('p3_tit', 'Seguridad')}")
        st.caption("Requisitos: Mínimo 8 caracteres + Mayúscula + Número.")
        
        p1 = st.text_input("Contraseña *", type='password')
        
        # Visualización de fuerza
        if p1:
            prog, etiq, col = validar_fuerza_clave(p1)
            st.markdown(f"""
                <div style="background-color:#ddd;height:5px;border-radius:2px;">
                    <div style="width:{prog}%;background-color:{col};height:100%;"></div>
                </div>
                <small style="color:{col}; font-weight:bold;">Nivel: {etiq}</small>
            """, unsafe_allow_html=True)

            if prog >= 60: # Nivel Medio o superior
                limpiar_si_hay_dato(p1, "p1")
            else:
                st.warning("⚠️ Contraseña insegura. Debe ser al menos Nivel Medio 🟡")

        p2 = st.text_input("Repetir Contraseña *", type='password')
        if p2 and p1 == p2: limpiar_si_hay_dato(p2, "no_match")
        
        if "p1" in st.session_state.campos_error: st.error("Contraseña débil o vacía")
        if "no_match" in st.session_state.campos_error: st.error("Las contraseñas no coinciden")

    # 4. ZONA LEGAL
    with st.container(border=True):
        st.markdown(f"#### ⚖️ {t.get('p4_tit', 'Términos Legales')}")
        link_gdpr = "https://www.swarco.com/privacy-policy"
        st.markdown(f"Debe leer y aceptar la [Política de Privacidad]({link_gdpr}).", unsafe_allow_html=True)
        chk = st.checkbox("He leído, comprendo y acepto los términos.")
        
        if chk: limpiar_si_hay_dato(True, "chk")
        if "chk" in st.session_state.campos_error: st.error("Debe aceptar para continuar")

    st.divider()

    # --- BOTÓN DE REGISTRO ---
    if st.button("REGISTRAR USUARIO", type="primary", use_container_width=True):
        errores_detectados = []
        
        # Validaciones Finales
        if not n: errores_detectados.append("n")
        if not a: errores_detectados.append("a")
        if not cargo: errores_detectados.append("cargo")
        if not e: errores_detectados.append("e")
        if not m or "@" not in m: errores_detectados.append("m")
        if not chk: errores_detectados.append("chk")
        
        if not tl_num or not tl_num.isdigit() or len(tl_num) < 6:
            errores_detectados.append("tl")

        if not p1 or not p2: 
            errores_detectados.append("p1")
        elif p1 != p2:
            errores_detectados.append("no_match")
        else:
            fuerza, _, _ = validar_fuerza_clave(p1)
            if fuerza < 60: errores_detectados.append("p1")

        # Bloqueo Duplicados
        if m and usuario_existe(conn, m):
            st.error(f"🛑 EL USUARIO {m} YA EXISTE. Operación cancelada.")
            # Frenamos aquí
            st.stop()

        # DECISIÓN
        if errores_detectados:
            st.session_state.campos_error = errores_detectados
            # AVISO QUE PEDISTE ABAJO DEL BOTÓN
            st.error("⚠️ FALTAN DATOS: Por favor, rellena los espacios marcados en rojo.", icon="🚨")
            st.rerun() # Recargamos para que salgan los rojos
        else:
            try:
                # Guardar
                conn.worksheet("Usuarios").append_row([
                    n, a, cargo, e, pais_sel, pref_auto, tl_num, m, encriptar_password(p1)
                ])
                # Correo
                st.info("Enviando correo...")
                envio_ok = correo.enviar_correo_bienvenida(m, n, m, p1)
                
                if envio_ok:
                    st.success("✅ USUARIO CREADO CORRECTAMENTE")
                else:
                    st.warning("⚠️ Usuario creado, pero hubo error en el envío del correo.")

                st.session_state.campos_error = []
                
            except Exception as ex:
                st.error(f"Error Técnico: {ex}")

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
