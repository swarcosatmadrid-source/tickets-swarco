import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def enviar_email_outlook(empresa, contacto, proyecto, lista_equipos, email_usuario, ticket_id, telefono):
    # Configuración del servidor (Asegúrate de tener estos secretos en tu .toml)
    try:
        smtp_server = "smtp.office365.com"
        smtp_port = 587
        sender_email = st.secrets["emails"]["smtp_user"]
        sender_password = st.secrets["emails"]["smtp_pass"]

        # Crear el mensaje
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = "tu_correo_destino@swarco.com" # Cambia esto por el correo que recibe los SAT
        msg['Subject'] = f"NUEVO TICKET SAT: {ticket_id} - {empresa}"

        # Construcción del cuerpo del mensaje en HTML para que se vea Pro
        cuerpo_equipos = ""
        for i, equipo in enumerate(lista_equipos, 1):
            # BUSQUEDA BLINDADA: Busca 'N.S.', luego 'ns', y si no hay nada pone 'No indicado'
            # Esto mata el error 'ns' para siempre
            sn = equipo.get('N.S.', equipo.get('ns', equipo.get('SN', 'No indicado')))
            ref = equipo.get('REF', equipo.get('ref', 'No indicado'))
            urg = equipo.get('Prioridad', equipo.get('urgencia', 'Normal'))
            desc = equipo.get('Descripción', equipo.get('desc', 'Sin descripción'))

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
            <p>Se ha generado un nuevo ticket con la siguiente información:</p>
            
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #f8f8f8;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>Ticket ID:</b></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{ticket_id}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>Cliente / Empresa:</b></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{empresa}</td>
                </tr>
                <tr style="background-color: #f8f8f8;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>Contacto:</b></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{contacto}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>Email:</b></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{email_usuario}</td>
                </tr>
                <tr style="background-color: #f8f8f8;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>Teléfono:</b></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{telefono}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><b>Ubicación/Proyecto:</b></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{proyecto}</td>
                </tr>
            </table>

            <h3 style="color: #00549F; margin-top: 20px;">Detalle de los Equipos:</h3>
            {cuerpo_equipos}

            <p style="font-size: 12px; color: #999; margin-top: 30px;">
                © 2026 SWARCO TRAFFIC SPAIN | Enviado desde el Portal SAT.
            </p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        # Conexión al servidor y envío
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, msg['To'], msg.as_string())
        server.quit()

        return True

    except Exception as e:
        print(f"Error enviando correo: {e}")
        return False
