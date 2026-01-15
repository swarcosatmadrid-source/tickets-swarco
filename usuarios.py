import streamlit as st
import time

def interfaz_registro_white_hat(conn):
    st.info("📝 **Registro de Usuario SAT**")
    
    with st.form("form_registro_blindado"):
        # --- CAPA 1: HONEYPOT (Trampa para bots) ---
        # Este campo no lo verá el humano por el CSS que pondremos
        honeypot = st.text_input("Leave this empty", key="hp_field", label_visibility="collapsed")
        
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre").strip()
            apellido = st.text_input("Primer Apellido").strip()
        with c2:
            empresa = st.text_input("Empresa").strip()
            email = st.text_input("Correo Corporativo").strip()
            
        # --- CAPA 2: CAPTCHA LÓGICO ---
        st.write("🛡️ **Validación de Seguridad**")
        pregunta_seguridad = st.number_input("¿Cuánto es 12 + 8?", step=1)
        
        st.markdown("---")
        pass1 = st.text_input("Defina su Clave", type="password")
        pass2 = st.text_input("Repita su Clave", type="password")
            
        btn_reg = st.form_submit_button("REGISTRAR CUENTA", use_container_width=True)

    # --- LÓGICA DE VALIDACIÓN WHITE HAT ---
    if btn_reg:
        # 1. ¿Llenó el honeypot? -> Es un Bot
        if honeypot:
            print("🚨 BOT DETECTADO: Intento de registro automatizado bloqueado.")
            st.error("Error de validación de seguridad.") # Mensaje genérico para no dar pistas
            return
        
        # 2. ¿Falló la suma? -> Es un Bot o alguien muy distraído
        if pregunta_seguridad != 20:
            st.error("❌ Validación de seguridad incorrecta.")
            return

        # 3. ¿Es correo corporativo? (Opcional pero recomendado)
        dominios_prohibidos = ["yopmail.com", "tempmail.com", "10minutemail.com"]
        if any(dom in email.lower() for dom in dominios_prohibidos):
            st.error("❌ No se permiten correos temporales.")
            return

        # Validaciones normales de ticketV0
        if pass1 != pass2:
            st.error("❌ Las contraseñas no coinciden.")
        elif len(pass1) < 8:
            st.error("❌ Por seguridad, la clave debe tener al menos 8 caracteres.")
        else:
            # Aquí va el envío exitoso al Google Sheet
            st.success("✅ ¡Registro validado! Bienvenido al sistema.")

# CSS para esconder el Honeypot (Agrégalo a estilos.py)
# div[data-testid="stTextInput"]:has(input[name="hp_field"]) { display: none; }
