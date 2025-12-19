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
EMAIL_EMISOR = "swarcosatmadrid@gmail.com"
PASSWORD_EMISOR = "hrga nnuz hxtd mbck"
EMAIL_RECEPTOR = "aitor.badiola@swarco.com" 

ASUNTO_CLAVE = "NUEVO TICKET" 
NOMBRE_ADJUNTO = "temp_ticket_envio.xlsx"

# Configuración de página con icono
st.set_page_config(page_title="Soporte SWARCO", page_icon="🚦", layout="centered")

# --- ESTILOS CSS PRO (AQUÍ ESTÁ LA MAGIA VISUAL) ---
st.markdown("""
    <style>
    /* 1. Fondo general de la web (Gris suave profesional) */
    .stApp {
        background-color: #F0F2F6;
    }

    /* 2. Ocultar elementos molestos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 3. Diseño del FORMULARIO (Efecto Tarjeta) */
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); /* Sombra elegante */
        border-top: 5px solid #009FE3; /* Línea azul Swarco arriba */
    }

    /* 4. Estilo del BOTÓN de envío */
    .stButton>button {
        width: 100%;
        background-color: #009FE3; /* Azul SWARCO */
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        height: 50px;
        font-size: 18px !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #007BB5; /* Azul más oscuro al pasar ratón */
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }

    /* 5. Títulos y Textos */
    h1 {
        color: #333333;
        text-align: center;
        font-family: 'Helvetica', sans-serif;
    }
    p {
        text-align: center;
        color: #666;
    }
    
    /* 6. Centrar el Logo */
    [data-testid="stImage"] {
        display: flex;
        justify_content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
# Usamos columnas vacías a los lados para centrar el logo perfectamente
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.image("https://www.swarco.com/themes/custom/swarco/logo.svg", width=250)

st.title("Portal de Soporte Técnico")
st.markdown("Por favor, complete el formulario para registrar su incidencia. Nuestro equipo técnico recibirá el aviso de inmediato.")

st.write("") # Espacio en blanco

# --- FORMULARIO ---
with st.form("form_cliente"):
    st.subheader("📝 Datos del Solicitante")
    
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Empresa / Cliente 🏢")
        contacto = st.text_input("Persona de Contacto 👤")
    with col2:
        email_contacto = st.text_input("Email de Contacto 📧")
        serie = st.text_input("Nº Serie Equipo (Opcional) 🔢")
    
    st.markdown("---") # Línea separadora
    st.subheader("⚠️ Detalle de la Incidencia")
    
    col3, col4 = st.columns(2)
    with col3:
        proyecto = st.text_input("Proyecto / Ubicación 📍")
    with col4:
        prioridad = st.selectbox("Prioridad", ["Normal", "Alta", "Urgente 🚨"])
    
    descripcion = st.text_area("Descripción detallada del problema", height=150, placeholder="Describa qué sucede, códigos de error, etc.")
    
    st.write("") # Espacio antes del botón
    enviar = st.form_submit_button("🚀 ENVIAR SOLICITUD DE SOPORTE")

# --- LÓGICA DE ENVÍO (IGUAL QUE ANTES) ---
if enviar:
    if not cliente or not contacto or not email_contacto or not descripcion:
        st.error("❌ Por favor, complete los campos obligatorios para poder ayudarle.")
    else:
        with st.spinner("Conectando con la central de SWARCO..."):
            try:
                # 1. Crear Excel
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

                # 2. Configurar Email
                msg = MIMEMultipart()
                msg['From'] = EMAIL_EMISOR
                msg['To'] = EMAIL_RECEPTOR
                msg['Subject'] = f"{ASUNTO_CLAVE}: {cliente} (Web)"

                cuerpo = f"""
                <div style="font-family: Arial, sans-serif; color: #333;">
                    <h2 style="color: #009FE3;">Nueva Incidencia Web</h2>
                    <p>Un cliente ha reportado un problema desde el portal web:</p>
                    <hr>
                    <ul>
                        <li><b>Cliente:</b> {cliente}</li>
                        <li><b>Contacto:</b> {contacto} (<a href="mailto:{email_contacto}">{email_contacto}</a>)</li>
                        <li><b>Ubicación:</b> {proyecto}</li>
                        <li><b>Equipo:</b> {serie}</li>
                        <li><b>Prioridad:</b> {prioridad}</li>
                    </ul>
                    <div style="background-color: #f9f9f9; padding: 15px; border-left: 5px solid #009FE3;">
                        <b>Descripción:</b><br>
                        {descripcion}
                    </div>
                </div>
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

                st.success("✅ Ticket enviado correctamente. Hemos recibido su solicitud y un técnico le contactará pronto.")
                st.balloons()
                
            except Exception as e:
                st.error(f"Error de conexión: {e}")
