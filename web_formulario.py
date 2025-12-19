import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io
import datetime

# --- CONFIGURACIÓN ---
# Aquí usamos la cuenta de Gmail "robot"
EMAIL_EMISOR = "swarcosatmadrid@gmail.com"
PASSWORD_EMISOR = "hrga nnuz hxtd mbck"
# A este correo le llegarán los avisos (TU CORREO)
EMAIL_RECEPTOR = "aitor.badiola@swarco.com" 

ASUNTO_CLAVE = "NUEVO TICKET" 
NOMBRE_ADJUNTO = "temp_ticket_envio.xlsx"

st.set_page_config(page_title="Soporte SWARCO", page_icon="🚦", layout="centered")

# Estilo para ocultar marcas de Streamlit y limpiar la vista
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp {background-color: #f0f2f6;}
    .stButton>button {width: 100%; background-color: #009FE3; color: white; border: none; font-weight: bold;}
    </style>
    """, unsafe_allow_html=True)

# Logo (Usamos uno público de internet para no tener líos de archivos)
st.image("https://www.swarco.com/themes/custom/swarco/logo.svg", width=200)

st.title("🚦 Apertura de Incidencia")
st.markdown("Formulario de reporte para clientes.")

with st.form("form_cliente"):
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Empresa / Cliente*")
        contacto = st.text_input("Su Nombre*")
    with col2:
        email_contacto = st.text_input("Su Email de contacto*")
        serie = st.text_input("Nº Serie Equipo (Opcional)")
    
    proyecto = st.text_input("Proyecto / Ubicación")
    prioridad = st.selectbox("Prioridad", ["Normal", "Alta", "Urgente"])
    descripcion = st.text_area("Descripción detallada del problema*", height=150)
    
    enviar = st.form_submit_button("🚀 ENVIAR SOLICITUD")

if enviar:
    if not cliente or not contacto or not email_contacto or not descripcion:
        st.error("Por favor, complete los campos obligatorios (*).")
    else:
        with st.spinner("Enviando datos a la central..."):
            try:
                # 1. Crear Excel en Memoria (RAM)
                fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                datos = {
                    'ID': ['WEB'], 
                    'Fecha': [fecha],
                    'Cliente': [cliente],
                    'Proyecto': [proyecto],
                    'País': ['Web/Remoto'],
                    'Serie': [serie],
                    'Contacto': [contacto],
                    'Email': [email_contacto],
                    'Prioridad': [prioridad],
                    'Estado': ['Abierto'],
                    'Problema': [descripcion]
                }
                df = pd.DataFrame(datos)
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                excel_bytes = buffer.getvalue()

                # 2. Configurar Email (SMTP GMAIL)
                msg = MIMEMultipart()
                msg['From'] = EMAIL_EMISOR
                msg['To'] = EMAIL_RECEPTOR
                # ASUNTO CLAVE para que tu Monitor lo detecte
                msg['Subject'] = f"{ASUNTO_CLAVE}: {cliente} (Web)"

                cuerpo = f"""
                <h3>Nueva Incidencia Reportada vía Web</h3>
                <ul>
                    <li><b>Cliente:</b> {cliente}</li>
                    <li><b>Contacto:</b> {contacto} ({email_contacto})</li>
                    <li><b>Equipo:</b> {serie}</li>
                    <li><b>Descripción:</b> {descripcion}</li>
                </ul>
                """
                msg.attach(MIMEText(cuerpo, 'html'))

                # Adjuntar Excel
                part = MIMEBase('application', "octet-stream")
                part.set_payload(excel_bytes)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{NOMBRE_ADJUNTO}"')
                msg.attach(part)

                # 3. Enviar
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(EMAIL_EMISOR, PASSWORD_EMISOR)
                server.sendmail(EMAIL_EMISOR, EMAIL_RECEPTOR, msg.as_string())
                server.quit()

                st.success("✅ Ticket enviado correctamente. Nuestro equipo técnico ha sido notificado.")
                st.balloons()
                
            except Exception as e:
                st.error(f"Error de conexión: {e}")
