import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st

def enviar_email_outlook(empresa, contacto, proyecto, lista_equipos, email_usr, ticket_id, telefono):
    # Datos de los Secrets
    try:
        remitente = st.secrets["email_user"] 
        password = st.secrets["email_password"] 
    except KeyError:
        st.error("❌ Falta configurar los Secrets en Streamlit.")
        return False

    # Configuración específica para GMAIL
    servidor_smtp = "smtp.gmail.com"
    puerto = 587

    try:
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = remitente # Te llega a ti el aviso
        msg['Cc'] = "sfr.support@swarco.com"
        msg['Cco'] = "aitor.badiola@swarco.com"
        msg['Subject'] = f"NUEVO TICKET SAT: {ticket_id} - {empresa}"

        fecha_envio = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Tabla con marcos reforzados
        filas_html = ""
        for i, eq in enumerate(lista_equipos):
            bg = "#ffffff" if i % 2 == 0 else "#f9f9f9"
            filas_html += f"""
            <tr style="background-color: {bg}; border: 1px solid #cccccc;">
                <td style="padding: 10px; border: 1px solid #cccccc; text-align: center;">{i+1}</td>
                <td style="padding: 10px; border: 1px solid #cccccc;"><b>{eq['ns']}</b></td>
                <td style="padding: 10px; border: 1px solid #cccccc;">{eq['ref']}</td>
                <td style="padding: 10px; border: 1px solid #cccccc;">{eq['urgencia']}</td>
                <td style="padding: 10px; border: 1px solid #cccccc;">{eq['desc']}</td>
            </tr>"""

        cuerpo_html = f"""
        <html><body style="font-family: Arial, sans-serif;">
            <div style="border: 2px solid #00549F; max-width: 850px; margin: auto; border-radius: 8px; overflow: hidden;">
                <div style="background: #00549F; color: white; padding: 20px; text-align: center;">
                    <h1 style="margin:0; font-size: 24px;">SWARCO SUPPORT SPAIN</h1>
                </div>
                <div style="padding: 20px;">
                    <p style="font-size: 16px;"><b>Ticket ID:</b> <span style="color: #009FE3;">{ticket_id}</span></p>
                    <p><b>Fecha de Reporte:</b> {fecha_envio}</p>
                    <hr style="border: 0; border-top: 1px solid #eee;">
                    <p><b>Empresa:</b> {empresa} | <b>Contacto:</b> {contacto} | <b>Tel:</b> {telefono}</p>
                    <p><b>Email Cliente:</b> {email_usr}</p>
                    
                    <h3 style="color: #00549F;">Relación de Equipos:</h3>
                    <table style="width: 100%; border-collapse: collapse; border: 1px solid #cccccc;">
                        <tr style="background: #009FE3; color: white;">
                            <th style="padding: 10px; border: 1px solid #cccccc;">#</th>
                            <th style="padding: 10px; border: 1px solid #cccccc;">N.S / Serial</th>
                            <th style="padding: 10px; border: 1px solid #cccccc;">REF / Part Number</th>
                            <th style="padding: 10px; border: 1px solid #cccccc;">Urgencia</th>
                            <th style="padding: 10px; border: 1px solid #cccccc;">Falla Detectada</th>
                        </tr>
                        {filas_html}
                    </table>
                </div>
                <div style="background: #f8f9fa; padding: 15px; text-align: center; font-size: 12px; color: #777;">
                    Este es un mensaje automático generado por el Portal SAT de SWARCO.
                </div>
            </div>
        </body></html>"""
        
        msg.attach(MIMEText(cuerpo_html, 'html'))

        # Conexión Segura con Gmail
        server = smtplib.SMTP(servidor_smtp, puerto)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Error de Gmail: {e}")
        return False