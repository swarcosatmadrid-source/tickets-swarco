import streamlit as st
import pandas as pd
import time

def gestionar_acceso(conn, t):
    """Maneja el login y el botón para ir al registro"""
    # 1. LOGO DE BIENVENIDA
    st.image("logo.png", width=250)
    st.markdown(f"## {t.get('login_tit', 'Bienvenido al Portal SAT')}")

    # 2. FORMULARIO DE ACCESO
    with st.form("login_form"):
        user_in = st.text_input(t.get('user_id', 'Usuario / Email')).strip()
        pass_in = st.text_input(t.get('pass', 'Contraseña'), type="password")
        
        btn_login = st.form_submit_button(t.get('btn_entrar', 'INGRESAR'), use_container_width=True)
        
        if btn_login:
            if not user_in or not pass_in:
                st.warning("⚠️ Rellene todos los campos")
            else:
                try:
                    df = conn.read(worksheet="Usuarios", ttl=0)
                    validar = df[(df['Usuario'].astype(str) == user_in) & (df['Password'].astype(str) == pass_in)]
                    
                    if not validar.empty:
                        st.session_state.autenticado = True
                        st.session_state.datos_cliente = {
                            'Empresa': validar.iloc[0]['Empresa'],
                            'Contacto': validar.iloc[0]['Usuario'],
                            'Email': validar.iloc[0]['Email'],
                            'Telefono': validar.iloc[0].get('Telefono', '')
                        }
                        st.success("✅ Acceso concedido")
                        time.sleep(1)
                        return True
                    else:
                        st.error("❌ Credenciales incorrectas")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    # 3. EL BOTÓN DE REGISTRO (Fuera del formulario de login)
    st.markdown("---")
    st.write(t.get('no_tienes_cuenta', '¿No tienes una cuenta de equipo?'))
    if st.button(t.get('btn_ir_registro', 'CREAR NUEVA CUENTA'), use_container_width=True):
        st.session_state.mostrar_registro = True
        st.rerun()
    return False

def interfaz_registro_legal(conn, t):
    """Maneja la creación de nuevos técnicos/clientes"""
    st.image("logo.png", width=150)
    st.markdown(f"### 📝 {t.get('reg_tit', 'Registro de Nuevo Usuario')}")
    
    with st.container(border=True):
        empresa = st.text_input(t.get('cliente', 'Empresa / Cliente') + " *")
        email = st.text_input(t.get('email', 'Email Oficial') + " *")
        user_new = st.text_input(t.get('user_id', 'Nombre de Usuario') + " *")
        tel_new = st.text_input(t.get('tel', 'Teléfono') + " *")
        pass_new = st.text_input(t.get('pass', 'Contraseña'), type="password")
    
    col_reg, col_can = st.columns(2)
    with col_reg:
        if st.button(t.get('btn_generar', 'REGISTRAR'), type="primary", use_container_width=True):
            if not empresa or not email or not pass_new:
                st.error("⚠️ Faltan datos obligatorios")
            else:
                # AQUÍ CONECTAS CON TU GSHEETS PARA GUARDAR
                # nueva_fila = [empresa, email, user_new, pass_new, tel_new]
                # conn.create(worksheet="Usuarios", data=nueva_fila)
                st.success("✅ Usuario registrado. Ahora puedes loguearte.")
                time.sleep(2)
                st.session_state.mostrar_registro = False
                st.rerun()
                
    with col_can:
        if st.button(t.get('btn_volver', 'VOLVER'), use_container_width=True):
            st.session_state.mostrar_registro = False
            st.rerun()
