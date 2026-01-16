# =============================================================================
# ARCHIVO: correo.py
# VERSIÓN: 5.1.0 (Texto Personalizado Madrid)
# =============================================================================
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

def enviar_correo_bienvenida(destinatario, nombre, usuario, password_temp):
    try:
        # Configuración SMTP (Toma los datos de secrets)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        remitente = st.secrets["smtp"]["email"]
        password = st.secrets["smtp"]["password"]

        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = "Bienvenida - Gestión de Tickets SWARCO Traffic Madrid"

        # CUERPO DEL CORREO EXACTO QUE PEDISTE
        cuerpo = f"""
        Estimado/a {nombre},

        Le damos la bienvenida a la página de gestión de tickets de Swarco Traffic Madrid.
        
        Sus credenciales de acceso son:
        Usuario: {usuario}
        Contraseña: {password_temp} (Por favor, cámbiela al acceder si es provisional)

        Atentamente,
        El Equipo de Soporte Técnico
        SWARCO Traffic Spain
        """
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Envío
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error envio correo: {e}")
        return False
