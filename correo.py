import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st

def enviar_email_outlook(empresa, contacto, proyecto, lista_equipos, email_usr, ticket_id, telefono):
    # Esto lee los datos que pusiste en los "Secrets" de la web de Streamlit
    try:
        remitente = st.secrets["email_user"] 
        password = st.secrets["email_password"] 
    except KeyError:
        st.error("❌ Error: No se han configurado los Secrets (email_user / email_password).")
        return False

    servidor_smtp = "smtp.office365.com" 
    puerto = 587

    try:
        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = remitente # Te llega a ti la notificación
        msg['Cc'] = "aitor.badiola@swarco.com"
        msg['Subject'] = f"NUEVO TICKET SAT: {ticket_id} - {empresa}"

        fecha_envio = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # Diseño de la tabla con marcos (IDÉNTICO al que querías)
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

        cuerpo = f"""
        <html><body style="font-family: Arial, sans-serif;">
            <div style="border: 1px solid #00549F; max-width: 850px; margin: auto;">
                <div style="background: #00549F; color: white; padding: 20px; text-align: center;">
                    <h2 style="margin:0;">SWARCO SUPPORT</h2>
                </div>
                <div style="padding: 20px;">
                    <p><b>Ticket ID:</b> {ticket_id} | <b>Fecha:</b> {fecha_envio}</p>
                    <p><b>Empresa:</b> {empresa} | <b>Contacto:</b> {contacto} | <b>Tel:</b> {telefono}</p>
                    <table style="width: 100%; border-collapse: collapse; border: 1px solid #cccccc;">
                        <tr style="background: #009FE3; color: white;">
                            <th style="padding: 10px; border: 1px solid #cccccc;">#</th>
                            <th style="padding: 10px; border: 1px solid #cccccc;">N.S</th>
                            <th style="padding: 10px; border: 1px solid #cccccc;">REF</th>
                            <th style="padding: 10px; border: 1px solid #cccccc;">Urgencia</th>
                            <th style="padding: 10px; border: 1px solid #cccccc;">Falla</th>
                        </tr>
                        {filas_html}
                    </table>
                </div>
            </div>
        </body></html>"""
        
        msg.attach(MIMEText(cuerpo, 'html'))
        server = smtplib.SMTP(servidor_smtp, puerto)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Error de conexión SMTP: {e}")
        return False