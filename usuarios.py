import streamlit as st
import pandas as pd

def gestionar_acceso(conn):
    # 1. Inicializar variables de sesión si no existen
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.datos_cliente = {}

    # 2. Si no está autenticado, mostrar pantalla de acceso
    if not st.session_state.autenticado:
        st.image("logo.png", width=300)
        tab_login, tab_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
        
        with tab_login:
            u = st.text_input("Usuario", key="u_login")
            p = st.text_input("Contraseña", type="password", key="p_login")
            if st.button("Entrar", use_container_width=True):
                try:
                    # Intentamos leer la pestaña "Clientes"
                    # Si da error 400, leemos la pestaña por defecto (la primera)
                    try:
                        df = conn.read(worksheet="Clientes", ttl=0)
                    except:
                        df = conn.read(ttl=0)
                    
                    # Validamos credenciales
                    validar = df[(df['Usuario'].astype(str) == u) & (df['Clave'].astype(str) == p)]
                    
                    if not validar.empty:
                        st.session_state.autenticado = True
                        st.session_state.datos_cliente = validar.iloc[0].to_dict()
                        st.rerun()
                    else:
                        st.error("❌ Usuario o clave incorrectos.")
                except Exception as e:
                    st.error(f"Error de conexión con la base de datos: {e}")
                    
        with tab_registro:
            st.info("Cree su cuenta para autorellenar sus reportes SAT.")
            r_usr = st.text_input("Defina Usuario", key="r_u")
            r_clv = st.text_input("Defina Contraseña", type="password", key="r_p")
            r_emp = st.text_input("Empresa", key="r_e")
            r_con = st.text_input("Persona de Contacto", key="r_c")
            r_ema = st.text_input("Email Corporativo", key="r_m")
            
            if st.button("Finalizar Registro", use_container_width=True):
                if r_usr and r_clv and r_emp and r_ema:
                    try:
                        # Leemos la base actual (con bypass de error de pestaña)
                        try:
                            df = conn.read(worksheet="Clientes", ttl=0)
                        except:
                            df = conn.read(ttl=0)
                        
                        # Verificamos si las columnas existen, si no, las creamos
                        columnas_necesarias = ['Usuario', 'Clave', 'Empresa', 'Contacto', 'Email']
                        if df.empty or not all(col in df.columns for col in columnas_necesarias):
                            df = pd.DataFrame(columns=columnas_necesarias)

                        if r_usr in df['Usuario'].values:
                            st.warning("⚠️ El usuario ya existe.")
                        else:
                            # Añadimos el nuevo registro
                            nuevo = pd.DataFrame([{
                                "Usuario": str(r_usr), 
                                "Clave": str(r_clv), 
                                "Empresa": str(r_emp), 
                                "Contacto": str(r_con), 
                                "Email": str(r_ema)
                            }])
                            
                            df_final = pd.concat([df, nuevo], ignore_index=True)
                            
                            # Intentamos actualizar la pestaña específica o la primera por defecto
                            try:
                                conn.update(worksheet="Clientes", data=df_final)
                            except:
                                conn.update(data=df_final)
                                
                            st.success("✅ ¡Registro completado! Ya puedes entrar por la pestaña de 'Iniciar Sesión'.")
                    except Exception as e:
                        st.error(f"No se pudo escribir en la hoja de Google: {e}")
                else:
                    st.error("⚠️ Por favor, rellene todos los campos.")
        return False
    return True
