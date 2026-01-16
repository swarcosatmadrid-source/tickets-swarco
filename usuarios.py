# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 5.1.0 (Sin Globos + Cierre Automático + Validación Rápida)
# =============================================================================
import streamlit as st
import pandas as pd
import hashlib
import re
import estilos
import correo
import time # Para dar un micro-segundo de feedback antes de cerrar

# --- Lógica de Negocio ---
def limpiar_telefono(texto):
    if not texto: return ""
    return re.sub(r'[^0-9+]', '', texto)

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- Interfaz ---
def interfaz_registro_legal(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "REGISTRO OFICIAL")}</p>', unsafe_allow_html=True)

    if 'err' not in st.session_state: st.session_state.err = []
    def check_err(k): return k in st.session_state.err

    # Usamos st.form para evitar recargas constantes, pero cerramos rápido al final
    with st.form("registro_pro"):
        
        # ZONA 1
        with st.container(border=True):
            st.markdown(f"#### 👤 {t.get('p1_tit', 'Identificación')}")
            c1, c2 = st.columns(2)
            n = c1.text_input(t.get("nombre", "Nombre"))
            if check_err("n"): c1.error("Requerido")
            a = c2.text_input(t.get("apellido", "Apellido"))
            if check_err("a"): c2.error("Requerido")

        # ZONA 2
        with st.container(border=True):
            st.markdown(f"#### 🌍 {t.get('p2_tit', 'Ubicación')}")
            e = st.text_input(t.get("cliente", "Empresa"))
            if check_err("e"): st.error("Falta Empresa")
            
            c3, c4 = st.columns(2)
            p = c3.text_input(t.get("pais", "País"))
            if check_err("p"): c3.error("Requerido")
            
            # Teléfono con limpieza
            raw_tel = c4.text_input(t.get("tel", "Teléfono"), help="Solo números")
            tl = limpiar_telefono(raw_tel)
            if check_err("tl"): c4.error("Mínimo 5 dígitos")
            
            m = st.text_input(t.get("email", "Email")).lower().strip()
            if check_err("m"): st.error("Email inválido")

        # ZONA 3
        with st.container(border=True):
            st.markdown(f"#### 🔒 {t.get('p3_tit', 'Seguridad')}")
            p1 = st.text_input(t.get("pass", "Contraseña"), type='password')
            p2 = st.text_input(t.get("pass_rep", "Repetir"), type='password')
            if check_err("p1"): st.error("Contraseña requerida (min 6)")

        # ZONA 4
        with st.container(border=True):
            link = "https://www.swarco.com/privacy-policy"
            st.markdown(f"Acepto la [Política de Privacidad]({link}) de SWARCO.")
            chk = st.checkbox(t.get("acepto", "He leído y acepto"))
            if check_err("chk"): st.error("Obligatorio aceptar")

        st.divider()
        
        # BOTÓN DE ACCIÓN
        submitted = st.form_submit_button(t.get("btn_registro_final", "REGISTRAR AHORA"))
        
        if submitted:
            errores = []
            # Validación
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
                st.error("⚠️ Revise los campos marcados en rojo.")
                st.rerun() # Recarga inmediata para mostrar los rojos
            
            elif p1 != p2:
                st.error("Las contraseñas no coinciden.")
            
            else:
                # --- ÉXITO ---
                try:
                    conn.worksheet("Usuarios").append_row([n, a, e, p, m, tl, encriptar_password(p1)])
                    
                    # Enviar correo
                    correo.enviar_correo_bienvenida(m, n, m, "******")
                    
                    # Feedback sutil (Sin globos)
                    st.success(f"✅ Usuario {n} creado. Enviando correo...")
                    
                    # LIMPIEZA Y CIERRE AUTOMÁTICO
                    st.session_state.err = []
                    st.session_state.mostrar_registro = False
                    time.sleep(1.5) # Pausa breve para leer el mensaje verde
                    st.rerun() # ¡PUM! Se cierra el formulario y vuelve al inicio
                    
                except Exception as ex:
                    st.error(f"Error técnico: {ex}")

    # Botón cancelar fuera del form
    if st.button("Cancelar"):
        st.session_state.mostrar_registro = False
        st.session_state.err = []
        st.rerun()

def gestionar_acceso(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("login_tit", "Acceso")}</p>', unsafe_allow_html=True)
    
    with st.container(border=True):
        with st.form("login_pro"):
            u = st.text_input(t.get("user_id", "Usuario (Email)"))
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
                except: st.error("Error de conexión")
    
    st.markdown("---")
    if st.button(t.get("btn_ir_registro", "Solicitar Nueva Cuenta")):
        st.session_state.mostrar_registro = True
        st.rerun()
