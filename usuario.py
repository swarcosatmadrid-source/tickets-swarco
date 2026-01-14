import streamlit as st
import pandas as pd

def gestionar_acceso(conn):
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.datos_cliente = {}

    if not st.session_state.autenticado:
        st.image("logo.png", width=300)
        tab_login, tab_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
        
        with tab_login:
            u = st.text_input("Usuario")
            p = st.text_input("Contraseña", type="password")
            if st.button("Entrar", use_container_width=True):
                df = conn.read(worksheet="Clientes", ttl=0)
                validar = df[(df['Usuario'] == u) & (df['Clave'] == p)]
                if not validar.empty:
                    st.session_state.autenticado = True
                    st.session_state.datos_cliente = validar.iloc[0].to_dict()
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas.")
                    
        with tab_registro:
            st.info("Regístrese para autorellenar sus reportes.")
            r_usr = st.text_input("Nuevo Usuario")
            r_clv = st.text_input("Nueva Contraseña", type="password")
            r_emp = st.text_input("Empresa")
            r_con = st.text_input("Contacto")
            r_ema = st.text_input("Email")
            if st.button("Crear Cuenta", use_container_width=True):
                df = conn.read(worksheet="Clientes", ttl=0)
                if r_usr in df['Usuario'].values:
                    st.warning("⚠️ Usuario ya existe.")
                else:
                    nuevo = pd.DataFrame([{"Usuario": r_usr, "Clave": r_clv, "Empresa": r_emp, "Contacto": r_con, "Email": r_ema}])
                    conn.update(worksheet="Clientes", data=pd.concat([df, nuevo], ignore_index=True))
                    st.success("✅ ¡Listo! Ya puede iniciar sesión.")
        return False
    return True
