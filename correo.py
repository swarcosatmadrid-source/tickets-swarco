# =============================================================================
# ARCHIVO: correo.py
# VERSIÓN: 6.0.0 (Debug Extremo)
# =============================================================================
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

def enviar_correo_bienvenida(destinatario, nombre, usuario, password_real):
    try:
        # 1. Recuperar secretos
        email_sender = st.secrets["smtp"]["email"]
        email_pass = st.secrets["smtp"]["password"]
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # 2. Construir Mensaje
        msg = MIMEMultipart()
        msg['From'] = email_sender
        msg['To'] = destinatario
        msg['Subject'] = "Bienvenida - Gestión de Tickets SWARCO Traffic Madrid"

        cuerpo = f"""
        Estimado/a {nombre},

        Le damos la bienvenida a la plataforma de gestión SAT de Swarco Traffic Madrid.
        
        Sus credenciales de acceso son:
        ------------------------------------------------
        Usuario:    {usuario}
        Contraseña: {password_real}
        ------------------------------------------------
        
        Por favor, conserve estas credenciales en un lugar seguro.

        Atentamente,
        Soporte Técnico SWARCO
        """
        msg.attach(MIMEText(cuerpo, 'plain'))

        # 3. Conexión SMTP con Depuración
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.set_debuglevel(1) # ESTO IMPRIMIRÁ EL LOG EN TU CONSOLA
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(email_sender, email_pass)
        server.send_message(msg)
        server.quit()
        
        return True

    except Exception as e:
        # Esto imprimirá el error real en la consola de Streamlit para que sepamos qué pasa
        print(f"❌ ERROR SMTP DETALLADO: {e}")
        st.error(f"Error técnico enviando correo: {e}")
        return False
