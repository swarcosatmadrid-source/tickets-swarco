# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 8.7.0 (Debug Mode: No cierra ventana + Bloqueo Duplicados Real)
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
    """Revisa si el email existe en la hoja de cálculo"""
    if not email_input: return False
    try:
        # Descargamos datos frescos
        records = conn.worksheet("Usuarios").get_all_records()
        df = pd.DataFrame(records)
        
        # Si el dataframe está vacío o no tiene columnas, no existe nadie
        if df.empty: return False
        
        # Buscamos el email
        if email_input.lower().strip() in df['email'].astype(str).str.lower().str.strip().values:
            return True
    except Exception as e:
        print(f"Error leyendo usuarios: {e}")
        return False
    return False

# --- Interfaz de Registro ---
def interfaz_registro_legal(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "ALTA DE USUARIO")}</p>', unsafe_allow_html=True)
    
    # Aviso de MODO DEBUG
    st.info("🛠️ MODO DEBUG ACTIVADO: La ventana NO se cerrará automáticamente para que puedas leer los errores.", icon="🛠️")

    if 'campos_error' not in st.session_state: st.session_state.campos_error = []

    def limpiar_error(campo):
        if campo in st.session_state.campos_error:
            st.session_state.campos_error.remove(campo)

    # 1. ZONA IDENTIFICACIÓN
    with st.container(border=True):
        st.markdown(f"#### 👤 {t.get('p1_tit', 'Identificación')}")
        c1, c2 = st.columns(2)
        
        n = c1.text_input("Nombre *")
        if n: limpiar_error("n")
        if "n" in st.session_state.campos_error: c1.error("Falta Nombre")
        
        a = c2.text_input("Apellido *")
        if a: limpiar_error("a")
        if "a" in st.session_state.campos_error: c2.error("Falta Apellido")

    # 2. ZONA UBICACIÓN Y DATOS
    with st.container(border=True):
        st.markdown(f"#### 🌍 {t.get('p2_tit', 'Datos Profesionales')}")
        
        c_cargo, c_empresa = st.columns(2)
        cargo = c_cargo.text_input("Cargo / Puesto *")
        if cargo: limpiar_error("cargo")
        if "cargo" in st.session_state.campos_error: c_cargo.error("Falta Cargo")
        
        e = c_empresa.text_input("Empresa / Entidad *")
        if e: limpiar_error("e")
        if "e" in st.session_state.campos_error: c_empresa.error("Falta Empresa")
        
        # Email
        m = st.text_input("Email Corporativo *").lower().strip()
        
        # Lógica de Duplicados Visual
        ya_existe = False
        if m:
            if "@" not in m:
                pass
            elif usuario_existe(conn, m):
                st.error("⛔ USUARIO DUPLICADO: Este correo ya está en la base de datos.")
                ya_existe = True
            else:
                st.success("✅ Disponible")
                limpiar_error("m")

        if "m" in st.session_state.campos_error: st.error("Email requerido")

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
            if tl_num:
                if not tl_num.isdigit():
                    st.error("⚠️ Solo números", icon="🚫")
                else:
                    limpiar_error("tl")
            if "tl" in st.session_state.campos_error: st.error("Mínimo 6 dígitos")

    # 3. ZONA SEGURIDAD
    with st.container(border=True):
        st.markdown(f"#### 🔒 {t.get('p3_tit', 'Seguridad')}")
        st.caption("Requisitos: Mínimo 8 caracteres + Mayúscula + Número.")
        
        p1 = st.text_input("Contraseña *", type='password')
        
        # BARRA DE FUERZA
        if p1:
            prog, etiq, col = validar_fuerza_clave(p1)
            st.markdown(f"""
                <div style="background-color:#ddd;height:5px;border-radius:2px;">
                    <div style="width:{prog}%;background-color:{col};height:100%;"></div>
                </div>
                <small style="color:{col}; font-weight:bold;">Nivel: {etiq}</small>
            """, unsafe_allow_html=True)

            if prog < 60:
                st.warning("⚠️ Contraseña insegura. Debe llegar al menos a Nivel Medio 🟡")
            else:
                limpiar_error("p1")

        p2 = st.text_input("Repetir Contraseña *", type='password')
        if p2 and p1 == p2: limpiar_error("no_match")
        
        if "p1" in st.session_state.campos_error: st.error("Contraseña muy débil")
        if "no_match" in st.session_state.campos_error: st.error("Las contraseñas no coinciden")

    # 4. ZONA LEGAL
    with st.container(border=True):
        st.markdown(f"#### ⚖️ {t.get('p4_tit', 'Términos Legales')}")
        link_gdpr = "https://www.swarco.com/privacy-policy"
        st.markdown(f"Debe leer y aceptar la [Política de Privacidad]({link_gdpr}).", unsafe_allow_html=True)
        chk = st.checkbox("He leído, comprendo y acepto los términos.")
        if chk: limpiar_error("chk")
        if "chk" in st.session_state.campos_error: st.error("Debe aceptar para continuar")

    st.divider()

    # --- BOTÓN DE REGISTRO ---
    if st.button("REGISTRAR USUARIO", type="primary", use_container_width=True):
        errores_detectados = []
        
        # 1. Validaciones de Vacío (Para Autofill confiamos en st.text_input directo)
        if not n: errores_detectados.append("n")
        if not a: errores_detectados.append("a")
        if not cargo: errores_detectados.append("cargo")
        if not e: errores_detectados.append("e")
        if not m or "@" not in m: errores_detectados.append("m")
        if not chk: errores_detectados.append("chk")
        
        # 2. Validación Teléfono
        if not tl_num or not tl_num.isdigit() or len(tl_num) < 6:
            errores_detectados.append("tl")

        # 3. Validaciones Password
        if not p1 or not p2: 
            errores_detectados.append("p1")
        elif p1 != p2:
            errores_detectados.append("no_match")
        else:
            fuerza, _, _ = validar_fuerza_clave(p1)
            if fuerza < 60: errores_detectados.append("p1")

        # 4. VALIDACIÓN CRÍTICA DE DUPLICADOS (BLOQUEO FINAL)
        # Aunque el visual diga error, esto evita que se guarde
        if m and usuario_existe(conn, m):
            st.error(f"🛑 ERROR CRÍTICO: El usuario {m} YA EXISTE. No se puede crear de nuevo.")
            st.stop() # Frena el código aquí mismo

        # DECISIÓN FINAL
        if errores_detectados:
            st.session_state.campos_error = errores_detectados
            # cartel gigante de aviso
            st.error("⚠️ NO SE PUDO CREAR: Revise los campos marcados en ROJO arriba.", icon="🚨")
            st.rerun()
        else:
            # INTENTO DE GUARDADO
            try:
                # Guardar en Sheets
                conn.worksheet("Usuarios").append_row([
                    n, a, cargo, e, pais_sel, pref_auto, tl_num, m, encriptar_password(p1)
                ])
                
                # Enviar Correo
                st.info("Intentando enviar correo...") # Debug info
                envio_ok = correo.enviar_correo_bienvenida(m, n, m, p1)
                
                if envio_ok:
                    st.success("✅ USUARIO REGISTRADO Y CORREO ENVIADO CORRECTAMENTE")
                    st.success("Puede cerrar esta ventana manualmente o crear otro usuario.")
                else:
                    st.warning("⚠️ Usuario guardado en Excel, pero el CORREO FALLÓ. Revise el error arriba (si lo imprimió el archivo de correo).")

                # NO cerramos la página para que leas
                st.session_state.campos_error = []
                
            except Exception as ex:
                st.error(f"❌ Error Técnico Grave: {ex}")

    if st.button("Cancelar y Limpiar"):
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
