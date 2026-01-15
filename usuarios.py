import streamlit as st
import pandas as pd
import uuid
import requests
import json

# URL de tu Google Apps Script (El mismo que usas en el main)
URL_BRIDGE = "https://script.google.com/macros/s/AKfycbyDpHS4nU16O7YyvABvmbFYHTLv2e2J8vrpSD-iCmamjmS4Az6p9iZNUmVEwzMVyzx9/exec"

def gestionar_acceso(conn):
    """Maneja el inicio de sesión de usuarios existentes"""
    if st.session_state.get('autenticado', False):
        return True

    st.markdown("<h2 style='text-align: center; color: #00549F;'>🔐 Acceso al Portal SAT</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        user_in = st.text_input("Usuario (Nombre Apellido)").strip().lower()
        pass_in = st.text_input("Contraseña", type="password")
        
        if st.form_submit_button("ENTRAR AL SISTEMA", use_container_width=True):
            try:
                # Leemos la pestaña 'Usuarios' del Google Sheet
                df = conn.read(worksheet="Usuarios", ttl=0)
                
                # Validación de credenciales
                validado = df[(df['Usuario'].str.lower() == user_in) & (df['Password'].astype(str) == pass_in)]
                
                if not validado.empty:
                    st.session_state.autenticado = True
                    st.session_state.datos_cliente = {
                        'Empresa': validado.iloc[0]['Empresa'],
                        'Contacto': validado.iloc[0]['Usuario'],
                        'Email': validado.iloc[0]['Email']
                    }
                    st.success(f"✅ Bienvenido {validado.iloc[0]['Nombre']}")
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas o usuario no registrado.")
            except Exception as e:
                st.error(f"Error al conectar con la base de datos: {e}")
    return False

def interfaz_registro_legal(conn):
    """Maneja el registro de nuevos usuarios con seguridad White Hat y RGPD"""
    st.markdown("<h3 style='color: #F29400;'>📝 Registro de Nuevo Usuario</h3>", unsafe_allow_html=True)
    
    with st.form("form_registro_blindado"):
        # --- CAPA 1: HONEYPOT (Trampa invisible para Bots) ---
        # Este campo se oculta mediante CSS en estilos.py
        honeypot = st.text_input("Extra Info", key="hp_field", label_visibility="collapsed")
        
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre *").strip()
            apellido = st.text_input("Primer Apellido *").strip()
            empresa = st.text_input("Empresa *").strip()
        with c2:
            email = st.text_input("Email Corporativo *").strip()
            telefono = st.text_input("Teléfono de Contacto")
            # --- CAPA 2: CAPTCHA LÓGICO ---
            pregunta_seguridad = st.number_input("Seguridad: ¿Cuánto es 10 + 5?", step=1)
            
        st.markdown("---")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            pass1 = st.text_input("Defina su Clave *", type="password")
        with col_p2:
            pass2 = st.text_input("Repita su Clave *", type="password")
            
        st.markdown("---")
        # --- CAPA 3: PROTECCIÓN DE DATOS (RGPD) ---
        acepta_rgpd = st.checkbox("He leído y acepto la Política de Protección de Datos de SWARCO SAT.")
        
        with st.expander("Ver aviso legal y términos de uso"):
            st.write("""
                Sus datos serán tratados por SWARCO TRAFFIC SPAIN para la gestión de tickets técnicos. 
                No se cederán datos a terceros salvo obligación legal o integración con sistemas internos (Jira/SAP). 
                Puede ejercer sus derechos de acceso y rectificación contactando al administrador.
            """)

        btn_registrar = st.form_submit_button("CREAR MI CUENTA", use_container_width
