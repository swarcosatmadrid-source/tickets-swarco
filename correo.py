import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import streamlit as st

def enviar_correo_bienvenida(destinatario, nombre, usuario, password_temp):
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        remitente = st.secrets["smtp"]["email"]
        password = st.secrets["smtp"]["password"]

        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = "Bienvenido al Portal SAT - SWARCO"

        cuerpo = f"""
        Hola {nombre},
        
        Bienvenido al sistema SAT de Swarco Traffic Spain.
        Su usuario es: {usuario}
        
        Saludos,
        Equipo SAT
        """
        msg.attach(MIMEText(cuerpo, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error envio correo: {e}")
        return False

