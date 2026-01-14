import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def enviar_email_outlook(empresa, contacto, proyecto, lista_equipos, email_usuario, ticket_id, telefono):
    # NOTA: Aunque la función se llame "enviar_email_outlook", ahora usa GMAIL
    try:
        # Configuración para GMAIL
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Sacamos los datos de st.secrets (Asegúrate de que coincidan con tu archivo .toml)
        sender_email = st.secrets["emails"]["smtp_user"]
        sender_password = st.secrets["emails"]["smtp_pass"]

        # Crear el mensaje
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = "swarcosatmadrid@gmail.com" # El correo donde quieres recibir los tickets
        msg['Subject'] = f"🚥 NUEVO TICKET SAT: {ticket_id} - {empresa}"

        # Cuerpo de equipos (Blindado contra errores de nombres)
        cuerpo_equipos = ""
        for i, equipo in enumerate(lista_equipos, 1):
            sn = equipo.get('N.S.', 'No indicado')
            ref = equipo.get('REF', 'No indicado')
            urg = equipo.get('Prioridad', 'Normal')
            desc = equipo.get('Descripción', 'Sin descripción')

            cuerpo_equipos += f"""
            <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; border-left: 5px solid #F29400;">
                <p><b>Equipo {i}:</b></p>
                <ul>
                    <li><b>N.S.:</b> {sn}</li>
                    <li><b>REF:</b> {ref}</li>
                    <li><b>Prioridad:</b> {urg}</li>
                    <li><b>Descripción:</b> {desc}</li>
                </ul>
            </div>
            """

        html = f"""
        <html>
        <body style="font-family: sans-serif; color: #333;">
            <h2 style="color: #00549F;">Reporte Técnico SAT - SWARCO</h2>
            <p>Se ha generado un nuevo ticket con el ID: <b>{ticket_id}</b></p>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #f8f8f8;"><td style="padding:10px; border:1px solid #ddd;"><b>Cliente:</b></td><td style="padding:10px; border:1px solid #ddd;">{empresa}</td></tr>
                <tr><td style="padding:10px; border:1px solid #ddd;"><b>Contacto:</b></td><td style="padding:10px; border:1px solid #ddd;">{contacto}</td></tr>
                <tr style="background-color: #f8f8f8;"><td style="padding:10px; border:1px solid #ddd;"><b>Ubicación:</b></td><td style="padding:10px; border:1px solid #ddd;">{proyecto}</td></tr>
                <tr><td style="padding:10px; border:1px solid #ddd;"><b>Teléfono:</b></td><td style="padding:10px; border:1px solid #ddd;">{telefono}</td></tr>
            </table>
            <h3 style="color: #00549F; margin-top: 20px;">Detalle de los Equipos:</h3>
            {cuerpo_equipos}
        </body>
        </html>
        """
        msg.attach(MIMEText(html, 'html'))

        # Conexión y envío
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls() # Seguridad necesaria para Gmail
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, msg['To'], msg.as_string())
        server.quit()
        return True

    except Exception as e:
        st.error(f"Error enviando correo: {e}")
        return False

