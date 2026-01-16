# =============================================================================
# ARCHIVO: usuarios.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 3.2.0 (Visualización por Zonas Enmarcadas + Validación Roja)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Módulo de Login y Registro con separación visual de 4 pasos.
# =============================================================================

import streamlit as st
import pandas as pd
import hashlib
import estilos
import correo

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def interfaz_registro_legal(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "Registro")}</p>', unsafe_allow_html=True)
    
    # Inicialización de estado de errores
    if 'err' not in st.session_state: st.session_state.err = []
    
    # Helper para marcar texto en rojo
    def lbl(txt, k): return f":red[{txt} *]" if k in st.session_state.err else f"{txt} *"

    with st.form("reg_form_visual"):
        
        # ZONA 1: IDENTIFICACIÓN (Caja con Borde)
        with st.container(border=True):
            st.markdown(f"**{t.get('p1_tit', 'Identificación')}**")
            c1, c2 = st.columns(2)
            n = c1.text_input(lbl(t.get("nombre", "Nombre"), "n"))
            a = c2.text_input(lbl(t.get("apellido", "Apellido"), "a"))

        # ZONA 2: UBICACIÓN (Caja con Borde)
        with st.container(border=True):
            st.markdown(f"**{t.get('p2_tit', 'Ubicación')}**")
            e = st.text_input(lbl(t.get("cliente", "Empresa"), "e"))
            c3, c4 = st.columns(2)
            p = c3.text_input(lbl(t.get("pais", "País"), "p"))
            tl = c4.text_input(lbl(t.get("tel", "Teléfono"), "tl"))
            m = st.text_input(lbl(t.get("email", "Email"), "m")).lower().strip()

        # ZONA 3: SEGURIDAD (Caja con Borde)
        with st.container(border=True):
            st.markdown(f"**{t.get('p3_tit', 'Seguridad')}**")
            p1 = st.text_input(lbl(t.get("pass", "Pass"), "p1"), type='password')
            p2 = st.text_input(lbl(t.get("pass_rep", "Repetir"), "p2"), type='password')

        # ZONA 4: LEGAL (Caja con Borde)
        with st.container(border=True):
            st.markdown(f"**{t.get('p4_tit', 'Validación')}**")
            chk = st.checkbox(t.get("acepto", "Acepto"))

        st.markdown("---")
        
        if st.form_submit_button(t.get("btn_registro_final", "REGISTRAR")):
            st.session_state.err = []
            # Validación estricta
            if not n: st.session_state.err.append("n")
            if not a: st.session_state.err.append("a")
            if not e: st.session_state.err.append("e")
            if not p: st.session_state.err.append("p")
            if not m: st.session_state.err.append("m")
            if not tl: st.session_state.err.append("tl")
            if not p1: st.session_state.err.append("p1")
            if not chk: st.session_state.err.append("chk")

            if st.session_state.err:
                st.error("⚠️ " + t.get("error_campos", "Rojos"))
                st.rerun()
            elif p1 != p2:
                st.error(t.get("no_match", "Clave Mal"))
            else:
                try:
                    conn.worksheet("Usuarios").append_row([n, a, e, p, m, tl, encriptar_password(p1)])
                    # Intento de envío de correo
                    try:
                        correo.enviar_correo_bienvenida(m, n, m, "******")
                    except: pass
                    
                    st.success(t.get("exito_reg", "OK"))
                    st.session_state.mostrar_registro = False
                    st.rerun()
                except Exception as ex: st.error(f"Error BD: {ex}")

    if st.button(t.get("btn_volver", "Volver")):
        st.session_state.mostrar_registro = False
        st.session_state.err = []
        st.rerun()

def gestionar_acceso(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("login_tit", "Acceso")}</p>', unsafe_allow_html=True)
    
    with st.container(border=True):
        with st.form("login_master"):
            u = st.text_input(t.get("user_id", "User")).lower().strip()
            p = st.text_input(t.get("pass", "Pass"), type='password')
            
            if st.form_submit_button(t.get("btn_entrar", "ENTRAR")):
                try:
                    df = pd.DataFrame(conn.worksheet("Usuarios").get_all_records())
                    if not df.empty and u in df['email'].values:
                        real = df.loc[df['email']==u, 'password'].values[0]
                        if encriptar_password(p) == real:
                            st.session_state.autenticado = True
                            st.session_state.user_email = u
                            st.session_state.pagina_actual = 'menu'
                            st.rerun()
                        else: st.error("Password incorrecto")
                    else: st.error("Usuario no encontrado")
                except: st.error("Error conexión BD")

    if st.button(t.get("btn_ir_registro", "Registro")):
        st.session_state.mostrar_registro = True
        st.rerun()
