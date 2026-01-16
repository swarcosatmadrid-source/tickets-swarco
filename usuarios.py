# =============================================================================
# ARCHIVO: usuarios.py
# VERSIÓN: 2.3.0 (Validación Visual con Bordes Rojos)
# =============================================================================

import streamlit as st
import estilos
# ... (encriptar_password y el resto igual)

def interfaz_registro_legal(conn, t):
    estilos.aplicar_bordes_rojos() # Llamamos a la artillería pesada de estilos
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "Registro")}</p>', unsafe_allow_html=True)
    
    if 'errores_registro' not in st.session_state:
        st.session_state.errores_registro = []

    with st.form("registro_maestro"):
        st.subheader(t.get("p1_tit", "1. Identificación"))
        c1, c2 = st.columns(2)
        
        # Si el campo está en la lista de errores, le pasamos un parámetro invisible
        # para que el CSS de estilos.py lo agarre y lo ponga rojo.
        nombre = c1.text_input(f"{t.get('nombre', 'Nombre')} *", 
                              key="reg_nom", 
                              help="Obligatorio" if "nombre" in st.session_state.errores_registro else None)
        
        apellido = c2.text_input(f"{t.get('apellido', 'Apellido')} *", 
                                key="reg_ape")

        st.subheader(t.get("p2_tit", "2. Ubicación"))
        empresa = st.text_input(f"{t.get('cliente', 'Empresa')} *")
        pais = st.text_input(f"{t.get('pais', 'País')} *")
        
        email = st.text_input(f"{t.get('email', 'Email')} *").lower().strip()
        tel = st.text_input(f"{t.get('tel', 'Teléfono')} *")

        st.subheader(t.get("p3_tit", "3. Seguridad"))
        pass1 = st.text_input(f"{t.get('pass', 'Contraseña')} *", type="password")
        pass2 = st.text_input(f"{t.get('pass_rep', 'Repetir Contraseña')} *", type="password")

        acepta = st.checkbox(t.get("acepto", "Acepto") + t.get("link_texto", " Política"))

        if st.form_submit_button(t.get("btn_registro_final", "REGISTRAR")):
            st.session_state.errores_registro = []
            
            # Verificamos campos
            if not nombre: st.session_state.errores_registro.append("nombre")
            if not empresa: st.session_state.errores_registro.append("empresa")
            # ... (así con todos)

            if st.session_state.errores_registro:
                # AQUÍ ESTÁ TU MENSAJE EXACTO
                st.error("⚠️ Rellene los campos que se encuentran en rojo")
                st.rerun()
            else:
                # Guardar y enviar correo...
                pass
