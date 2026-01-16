# =============================================================================
# ARCHIVO: usuarios.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 2.2.4 (Campos Completos + Alerta Roja)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Gestión de acceso y registro detallado de usuarios.
# =============================================================================

import streamlit as st
import hashlib
import estilos
import pandas as pd

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("login_tit", "Acceso Usuarios")}</p>', unsafe_allow_html=True)
    with st.form("login_form"):
        email = st.text_input(t.get("user_id", "Usuario")).lower().strip()
        passw = st.text_input(t.get("pass", "Contraseña"), type='password')
        if st.form_submit_button(t.get("btn_entrar", "INGRESAR")):
            # Lógica de validación con conn...
            pass
    if st.button(t.get("btn_ir_registro", "Crear cuenta")):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "Registro")}</p>', unsafe_allow_html=True)
    
    if 'err_reg' not in st.session_state: st.session_state.err_reg = []
    def l_e(txt, k): return f":red[{txt} *]" if k in st.session_state.err_reg else f"{txt} *"

    with st.form("reg_form"):
        st.subheader(t.get("p1_tit", "1. Identificación"))
        c1, c2 = st.columns(2)
        nom = c1.text_input(l_e(t.get("nombre", "Nombre"), "n"))
        ape = c2.text_input(l_e(t.get("apellido", "Apellido"), "a"))
        
        st.subheader(t.get("p2_tit", "2. Ubicación"))
        emp = st.text_input(l_e(t.get("cliente", "Empresa"), "e"))
        pai = st.text_input(l_e(t.get("pais", "País"), "p"))
        eml = st.text_input(l_e(t.get("email", "Email"), "m")).lower().strip()
        tel = st.text_input(l_e(t.get("tel", "Teléfono"), "t"))

        st.subheader(t.get("p3_tit", "3. Seguridad"))
        p1 = st.text_input(l_e(t.get("pass", "Contraseña"), "p1"), type='password')
        p2 = st.text_input(l_e(t.get("pass_rep", "Repetir"), "p2"), type='password')

        st.subheader(t.get("p4_tit", "4. Validación"))
        acc = st.checkbox(t.get("acepto", "Acepto los términos"))

        if st.form_submit_button(t.get("btn_registro_final", "REGISTRAR")):
            st.session_state.err_reg = []
            if not nom: st.session_state.err_reg.append("n")
            if not ape: st.session_state.err_reg.append("a")
            if not emp: st.session_state.err_reg.append("e")
            if not pai: st.session_state.err_reg.append("p")
            if not eml: st.session_state.err_reg.append("m")
            if not tel: st.session_state.err_reg.append("t")
            if not p1: st.session_state.err_reg.append("p1")
            if not acc: st.session_state.err_reg.append("p2") # Usamos p2 para el checkbox

            if st.session_state.err_reg:
                st.error("⚠️ Rellene los campos que se encuentran en rojo")
                st.rerun()
            elif p1 != p2:
                st.error(t.get("no_match", "Las claves no coinciden"))
            else:
                # Aquí va el guardado en Sheets...
                pass

    if st.button(t.get("btn_volver", "VOLVER")):
        st.session_state.mostrar_registro = False
        st.session_state.err_reg = []
        st.rerun()

