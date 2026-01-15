import streamlit as st

def interfaz_registro_legal(conn):
    st.info("📝 **Registro de Usuario SAT**")
    
    with st.form("form_registro_v0"):
        # ... (Campos de nombre, apellido, empresa que ya tenemos) ...
        
        st.markdown("---")
        st.write("⚖️ **Aspectos Legales**")
        
        # El Checkbox de aceptación
        acepta_terminos = st.checkbox("He leído y acepto la Política de Protección de Datos (RGPD) de SWARCO SAT.")
        
        # El rectángulo con el texto legal (con scroll si es largo)
        with st.expander("Ver términos y condiciones de manejo de datos"):
            st.write("""
                **SWARCO TRAFFIC SPAIN - Protección de Datos:**
                Los datos personales recogidos en este portal serán tratados con la exclusiva finalidad de 
                gestionar las incidencias técnicas (tickets) y la comunicación con el cliente.
                - **Responsable:** Swarco Traffic Spain.
                - **Finalidad:** Gestión de servicio técnico SAT.
                - **Derechos:** Puede solicitar el acceso, rectificación o supresión de sus datos enviando 
                  un correo a la administración del portal.
                - **Seguridad:** Sus datos no serán cedidos a terceros fuera del ecosistema de gestión Swarco (Jira/SAP).
            """)
        
        btn_reg = st.form_submit_button("REGISTRAR CUENTA", use_container_width=True)

    if btn_reg:
        # VALIDACIÓN WHITE HAT: Si no acepta, no pasa
        if not acepta_terminos:
            st.error("❌ Debe aceptar los términos y condiciones para crear una cuenta.")
            return
        
        # ... (Aquí sigue tu lógica de validación de contraseñas y registro) ...
        st.success("✅ Registro procesado correctamente.")
