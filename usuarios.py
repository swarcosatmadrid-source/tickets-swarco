# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 2.2.0 (Validación Visual en Rojo)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# =============================================================================

import streamlit as st
import pandas as pd
import hashlib
import estilos
import correo 

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def interfaz_registro_legal(conn, t):
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "Registro")}</p>', unsafe_allow_html=True)
    
    # Inicializamos el estado de error si no existe
    if 'errores_registro' not in st.session_state:
        st.session_state.errores_registro = []

    # Función auxiliar para pintar el label de rojo si falta
    def label_error(texto, clave):
        if clave in st.session_state.errores_registro:
            return f":red[**{texto} ***]"
        return f"{texto} *"

    with st.form("registro_maestro"):
        st.subheader(t.get("p1_tit", "1. Identificación"))
        c1, c2 = st.columns(2)
        with c1: nombre = st.text_input(label_error(t.get("nombre", "Nombre"), "nombre"))
        with c2: apellido = st.text_input(label_error(t.get("apellido", "Apellido"), "apellido"))
        
        st.subheader(t.get("p2_tit", "2. Ubicación"))
        c3, c4 = st.columns(2)
        with c3: empresa = st.text_input(label_error(t.get("cliente", "Empresa"), "empresa"))
        with c4: pais = st.text_input(label_error(t.get("pais", "País"), "pais"))
        
        email = st.text_input(label_error(t.get("email", "Email"), "email")).lower().strip()
        tel = st.text_input(label_error(t.get("tel", "Teléfono"), "tel"))

        st.subheader(t.get("p3_tit", "3. Seguridad"))
        pass1 = st.text_input(label_error(t.get("pass", "Contraseña"), "pass1"), type="password")
        pass2 = st.text_input(label_error(t.get("pass_rep", "Repetir Contraseña"), "pass2"), type="password")

        st.subheader(t.get("p4_tit", "4. Validación"))
        acepta = st.checkbox(t.get("acepto", "Acepto") + t.get("link_texto", " Política"))

        # El botón ahora usa explícitamente la clave de registro
        btn_texto = t.get("btn_registro_final", "REGISTRAR")
        
        if st.form_submit_button(btn_texto):
            # Limpiamos errores previos
            st.session_state.errores_registro = []
            
            # Chequeo de campos uno a uno
            if not nombre: st.session_state.errores_registro.append("nombre")
            if not apellido: st.session_state.errores_registro.append("apellido")
            if not empresa: st.session_state.errores_registro.append("empresa")
            if not pais: st.session_state.errores_registro.append("pais")
            if not email: st.session_state.errores_registro.append("email")
            if not tel: st.session_state.errores_registro.append("tel")
            if not pass1: st.session_state.errores_registro.append("pass1")
            if not acepta: st.session_state.errores_registro.append("acepta")

            if st.session_state.errores_registro:
                st.error("⚠️ Rellene los campos que se encuentran en rojo")
                st.rerun()
            elif pass1 != pass2:
                st.error(t.get("no_match", "Las contraseñas no coinciden"))
            else:
                # Proceso de guardado (Igual que antes)
                try:
                    ws = conn.worksheet("Usuarios")
                    ws.append_row([nombre, apellido, empresa, pais, email, tel, encriptar_password(pass1)])
                    correo.enviar_correo_bienvenida(email, nombre, email, "********")
                    st.success(t.get("exito_reg", "¡Éxito!"))
                    st.session_state.mostrar_registro = False
                    st.rerun()
                except: st.error("Error de conexión con la base de datos")

    if st.button(t.get("btn_volver", "VOLVER")):
        st.session_state.mostrar_registro = False
        st.session_state.errores_registro = []
        st.rerun()
