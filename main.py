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
            u = st.text_input("Usuario", key="u_login")
            p = st.text_input("Contraseña", type="password", key="p_login")
            if st.button("Entrar", use_container_width=True):
                try:
                    df = conn.read(worksheet="Clientes", ttl=0)
                    validar = df[(df['Usuario'] == u) & (df['Clave'] == p)]
                    if not validar.empty:
                        st.session_state.autenticado = True
                        st.session_state.datos_cliente = validar.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas.")
                except Exception as e:
                    st.error(f"Error al conectar con la pestaña 'Clientes': {e}")
                    
        with tab_registro:
            st.info("Cree su cuenta para autorellenar sus datos en el futuro.")
            r_usr = st.text_input("Defina Usuario", key="r_u")
            r_clv = st.text_input("Defina Contraseña", type="password", key="r_p")
            r_emp = st.text_input("Empresa", key="r_e")
            r_con = st.text_input("Persona de Contacto", key="r_c")
            r_ema = st.text_input("Email Corporativo", key="r_m")
            if st.button("Finalizar Registro", use_container_width=True):
                if r_usr and r_clv and r_emp and r_ema:
                    try:
                        df = conn.read(worksheet="Clientes", ttl=0)
                        if r_usr in df['Usuario'].values:
                            st.warning("⚠️ El usuario ya existe.")
                        else:
                            nuevo = pd.DataFrame([{"Usuario": r_usr, "Clave": r_clv, "Empresa": r_emp, "Contacto": r_con, "Email": r_ema}])
                            df_final = pd.concat([df, nuevo], ignore_index=True)
                            conn.update(worksheet="Clientes", data=df_final)
                            st.success("✅ Registro completado. ¡Inicie sesión!")
                    except Exception as e:
                        st.error(f"Error al guardar en Google Sheets: {e}")
                else:
                    st.error("⚠️ Rellene todos los campos.")
        return False
    return True

