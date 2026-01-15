import smtplib
import streamlit as st # Importante para leer los secretos
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIGURACIÓN SEGURA ---
# En lugar de escribir la clave aquí, la llamamos de los Secrets
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = st.secrets["emails"]["user"]
SMTP_PASS = st.secrets["emails"]["password"]

def enviar_ticket_soporte(datos_cliente, proyecto, telefono, lista_equipos, idioma_t):
    """
    Construye y envía un correo profesional con el reporte.
    """
    destinatario = "sfr.support@swarco.com" # Correo de la oficina
    
    # 1. Crear el cuerpo del mensaje en HTML
    # Usamos el ADN de Swarco (Azul y Naranja)
    html_equipos = ""
    for eq in lista_equipos:
        html_equipos += f"""
        <tr>
            <td style='border: 1px solid #ddd; padding: 8px;'>{eq['N.S.']}</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>{eq['Referencia']}</td>
            <td style='border: 1px solid #ddd; padding: 8px;'>{eq['Avería']}</td>
        </tr>
        """

    cuerpo_html = f"""
    <html>
    <body style='font-family: Arial, sans-serif;'>
        <div style='background-color: #003366; color: white; padding: 20px; text-align: center;'>
            <h2>NUEVO REPORTE TÉCNICO - SWARCO SAT</h2>
        </div>
        <div style='padding: 20px;'>
            <p><strong>Cliente:</strong> {datos_cliente['Empresa']}</p>
            <p><strong>Contacto:</strong> {datos_cliente['Contacto']} ({datos_cliente['Email']})</p>
            <p><strong>Ubicación/Proyecto:</strong> {proyecto}</p>
            <p><strong>Teléfono:</strong> {telefono}</p>
            <hr>
            <h3>Detalle de Equipos:</h3>
            <table style='width: 100%; border-collapse: collapse;'>
                <thead>
                    <tr style='background-color: #f2f2f2;'>
                        <th style='border: 1px solid #ddd; padding: 8px;'>N.S.</th>
                        <th style='border: 1px solid #ddd; padding: 8px;'>Referencia</th>
                        <th style='border: 1px solid #ddd; padding: 8px;'>Descripción Avería</th>
                    </tr>
                </thead>
                <tbody>
                    {html_equipos}
                </tbody>
            </table>
        </div>
        <div style='background-color: #f8f8f8; color: #777; padding: 10px; text-align: center; font-size: 12px;'>
            Este es un mensaje automático generado por el Portal SAT de Swarco Spain.
        </div>
    </body>
    </html>
    """

    # 2. Configurar el objeto del mensaje
    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = destinatario
    msg['Cc'] = datos_cliente['Email'] # Copia al técnico que lo envía
    msg['Subject'] = f"🎫 Ticket SAT: {datos_cliente['Empresa']} - {proyecto}"

    msg.attach(MIMEText(cuerpo_html, 'html'))

    # 3. Envío Real
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False
