import streamlit as st
import re
import time
import pandas as pd

# --- FUNCIONES DE APOYO (ADN de Seguridad) ---

def validar_email(email):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, email)

def chequear_fuerza_clave(p):
    if not p: return "", ""
    puntos = 0
    if len(p) >= 8: puntos += 1
    if re.search(r"[A-Z]", p): puntos += 1
    if re.search(r"[0-9]", p): puntos += 1
    
    if puntos >= 3: return "🟢 Fuerte", "success"
    if puntos >= 2: return "🟠 Media", "warning"
    return "🔴 Débil", "error"

# --- 1. MÓDULO DE LOGIN ---

def gestionar_acceso(conn, t):
    """Maneja el ingreso de usuarios existentes"""
    with st.form("login_form"):
        st.markdown(f"### {t.get('login_tit', 'Acceso')}")
        
        user_in = st.text_input(t.get('user_id', 'Usuario')).strip()
        pass_in = st.text_input(t.get('pass', 'Contraseña'), type="password")
        
        btn_login = st.form_submit_button(t.get('btn_entrar', 'INGRESAR'), use_container_width=True)
        
        if btn_login:
            if not user_in or not pass_in:
                st.error("⚠️ Rellene todos los campos")
            else:
                try:
                    # Leemos la pestaña de Usuarios
                    df = conn.read(worksheet="Usuarios", ttl=0)
                    
                    # Validamos credenciales
                    validar = df[(df['Usuario'].astype(str) == user_in) & (df['Password'].astype(str) == pass_in)]
                    
                    if not validar.empty:
                        # Guardamos datos en sesión para los tickets
                        st.session_state.autenticado = True
                        st.session_state.datos_cliente = {
                            'Empresa': validar.iloc[0]['Empresa'],
                            'Contacto': validar.iloc[0]['Usuario'],
                            'Email': validar.iloc[0]['Email']
                        }
                        st.success("✅ Acceso concedido")
                        time.sleep(1)
                        return True
                    else:
                        st.error("❌ Usuario o Contraseña incorrectos")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
    return False

# --- 2. MÓDULO DE REGISTRO ---

def interfaz_registro_legal(conn, t):
    """Maneja la creación de nuevos usuarios/equipos"""
    st.markdown(f"### {t.get('reg_tit', 'Registro')}")
    
    with st.expander(t.get('p1_tit', 'Paso 1'), expanded=True):
        empresa = st.text_input(t.get('cliente', 'Empresa') + " *")
        email = st.text_input(t.get('email', 'Email') + " *")
    
    with st.expander(t.get('p2_tit', 'Paso 2'), expanded=True):
        new_user = st.text_input(t.get('user_id', 'Usuario ID') + " *")
        p1 = st.text_input(t.get('pass', 'Clave') + " *", type="password")
        p2 = st.text_input(t.get('pass', 'Repetir Clave') + " *", type="password")
        
        if p1:
            msg, tipo = chequear_fuerza_clave(p1)
            st.info(f"Seguridad: {msg}")
            if p1 == p2:
                st.success(t.get('match', '✅ Coinciden'))
            elif p2:
                st.error(t.get('no_match', '❌ No coinciden'))

    if st.button(t.get('btn_generar', 'REGISTRAR'), type="primary", use_container_width=True):
        if not empresa or not email or not new_user or p1 != p2 or not p1:
            st.error(t.get('error_campos', 'Faltan datos'))
        else:
            # Aquí iría la lógica de conn.update para guardar en el Sheets
            # (Lo completaremos cuando verifiquemos tu Bridge de Google)
            st.success(t.get('exito_reg', 'Usuario creado'))
            time.sleep(2)
            st.session_state.mostrar_registro = False
            st.rerun()
