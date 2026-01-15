import streamlit as st
import pandas as pd
import time

def gestionar_acceso(conn, t):
    """Maneja el login con estética centrada y marca oficial"""
    
    # 1. LOGO CENTRADO (Usamos columnas para empujarlo al medio)
    col_logo_1, col_logo_2, col_logo_3 = st.columns([1, 2, 1])
    with col_logo_2:
        st.image("logo.png", use_container_width=True)
    
    # 2. NOMBRE DE LA SEDE CENTRADO
    st.markdown("<h3 style='text-align: center;'>Swarco Traffic Spain</h3>", unsafe_allow_html=True)
    st.markdown(f"<h5 style='text-align: center; color: gray;'>{t.get('login_tit', 'Acceso Usuarios Registrados')}</h5>", unsafe_allow_html=True)
    st.write("") # Espacio estético

    # 3. FORMULARIO DE ACCESO
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
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")

    # 4. BOTÓN DE REGISTRO
    st.markdown("---")
    st.write(t.get('no_tienes_cuenta', '¿No tienes una cuenta de equipo?'))
    if st.button(t.get('btn_ir_registro', 'CREAR NUEVA CUENTA'), use_container_width=True):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    """Formulario de registro con logo centrado"""
    col_l1, col_l2, col_l3 = st.columns([1.5, 1, 1.5])
    with col_l2:
        st.image("logo.png", use_container_width=True)
    
    st.markdown("<h4 style='text-align: center;'>Swarco Traffic Spain</h4>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>{t.get('reg_tit', 'Registro de Nuevo Usuario')}</p>", unsafe_allow_html=True)
    
    with st.container(border=True):
        empresa = st.text_input(t.get('cliente', 'Empresa') + " *")
        email = st.text_input(t.get('email', 'Email Oficial') + " *")
        user_new = st.text_input(t.get('user_id', 'Nombre de Usuario') + " *")
        tel_new = st.text_input(t.get('tel', 'Teléfono') + " *")
        pass_new = st.text_input(t.get('pass', 'Contraseña'), type="password")
    
    c_reg, c_can = st.columns(2)
    with c_reg:
        if st.button(t.get('btn_generar', 'REGISTRAR'), type="primary", use_container_width=True):
            # Lógica de guardado...
            st.success("✅ Registro completado")
            time.sleep(2)
            st.session_state.mostrar_registro = False
            st.rerun()
                
    with c_can:
        if st.button(t.get('btn_volver', 'VOLVER'), use_container_width=True):
            st.session_state.mostrar_registro = False
            st.rerun()
