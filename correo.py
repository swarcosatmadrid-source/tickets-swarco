import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import streamlit as st

def enviar_email_outlook(empresa, contacto, proyecto, lista_equipos, email_usr, ticket_id, telefono):
    try:
        remitente = st.secrets["email_user"]
        password = st.secrets["email_password"]
    except:
        st.error("❌ Error: Configure 'email_user' y 'email_password' en los Secrets.")
        return False

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = remitente
    msg['Cc'] = "sfr.support@swarco.com"
    msg['Subject'] = f"NUEVO TICKET SAT: {ticket_id} - {empresa}"

    filas = ""
    for i, eq in enumerate(lista_equipos):
        bg = "#ffffff" if i % 2 == 0 else "#f9f9f9"
        filas += f"<tr style='background:{bg};'><td>{i+1}</td><td><b>{eq['ns']}</b></td><td>{eq['ref']}</td><td>{eq['urgencia']}</td><td>{eq['desc']}</td></tr>"

    cuerpo_html = f"""
    <html><body style='font-family: Arial;'>
        <div style='border: 2px solid #00549F; max-width: 800px; margin: auto;'>
            <div style='background:#00549F; color:white; padding:20px; text-align:center;'><h2>SWARCO SUPPORT SPAIN</h2></div>
            <div style='padding:20px;'>
                <p><b>Ticket ID:</b> {ticket_id} | <b>Empresa:</b> {empresa}</p>
                <p><b>Contacto:</b> {contacto} | <b>Tel:</b> {telefono}</p>
                <table border='1' style='width:100%; border-collapse:collapse;'>
                    <tr style='background:#009FE3; color:white;'><th>#</th><th>S/N</th><th>REF</th><th>Urgencia</th><th>Falla</th></tr>
                    {filas}
                </table>
            </div>
        </div>
    </body></html>"""
    
    msg.attach(MIMEText(cuerpo_html, 'html'))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error envío: {e}")
        return False