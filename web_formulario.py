import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io
import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA (ESTO DEBE SER LO PRIMERO) ---
st.set_page_config(page_title="SWARCO SAT Form", page_icon="🎫", layout="centered")

# --- 2. VERIFICACIÓN DE SEGURIDAD (Para evitar pantalla blanca) ---
# Intentamos leer la clave. Si falla, mostramos un error visible.
try:
    if "GMAIL_PASSWORD" in st.secrets:
        PASSWORD_EMISOR = st.secrets["GMAIL_PASSWORD"]
    else:
        st.error("❌ ERROR CRÍTICO: No se encuentra 'GMAIL_PASSWORD' en los Secrets de la App.")
        st.info("Ve a Settings -> Secrets y asegúrate de haberlo escrito bien.")
        st.stop()
except FileNotFoundError:
    # Esto pasa si lo pruebas en tu PC sin archivo de secretos
    st.warning("⚠️ Aviso: Estás ejecutando en local sin archivo de secretos.")
    PASSWORD_EMISOR = "CLAVE_FALSA_PARA_LOCAL" 

# --- 3. VARIABLES Y DISEÑO ---
EMAIL_EMISOR = "swarcosatmadrid@gmail.com"
EMAIL_RECEPTOR = "aitor.badiola@swarco.com" 

# Estilos
st.markdown("""
    <style>
    .stApp {background-color: white;}
    .stButton>button {width: 100%; background-color: #009FE3; color: white; border-radius: 5px;}
    </style>
    """, unsafe_allow_html=True)

st.title("🚦 Alta de Ticket SAT")
st.info("Sistema de reporte de incidencias SWARCO.")

# --- 4. FORMULARIO ---
with st.form("mi_formulario", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        cliente = st.text_input("Cliente / Compañía")
        proyecto = st.text_input("Proyecto")
        contacto = st.text_input("Persona de Contacto")
    
    with col2:
        serie = st.text_input("Número de Serie (Panel)")
        pais = st.selectbox("País", ["España", "Portugal", "Otro"])
        prioridad = st.selectbox("Prioridad", ["Normal", "Alta", "Crítica"])
        mail_contacto = st.text_input("Email de Contacto")

    descripcion = st.text_area("Descripción del fallo")
    
    # Botón Enviar
    enviar = st.form_submit_button("🚀 ENVIAR TICKET A CENTRAL")

# --- 5. LÓGICA DE ENVÍO ---
if enviar:
    if not cliente or not descripcion:
        st.error("⚠️ Faltan datos obligatorios (Cliente o Descripción).")
    else:
        try:
            # A) Crear Excel
            data = {
                'Fecha': [fecha], 'Cliente': [cliente], 'Proyecto': [proyecto],
                'País': [pais], 'Serie': [serie], 'Contacto': [contacto],
                'Email': [mail_contacto], 'Prioridad': [prioridad],
                'Problema': [descripcion]
            }
            df = pd.DataFrame(data)
            excel_buffer = io.BytesIO()
            # Usamos xlsxwriter como motor
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            excel_bytes = excel_buffer.getvalue()

            # B) Preparar Email
            msg = MIMEMultipart()
            msg['From'] = EMAIL_EMISOR
            msg['To'] = EMAIL_RECEPTOR
            msg['Subject'] = f"TICKET WEB - {cliente}"

            cuerpo = f"""<h3>Ticket SWARCO</h3><p>Cliente: {cliente}</p><p>Fallo: {descripcion}</p>"""
            msg.attach(MIMEText(cuerpo, 'html'))

            part = MIMEBase('application', "octet-stream")
            part.set_payload(excel_bytes)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="Tickets_Soporte.xlsx"')
            msg.attach(part)

            # C) Enviar
            with st.spinner("Enviando..."):
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(EMAIL_EMISOR, PASSWORD_EMISOR)
                server.sendmail(EMAIL_EMISOR, EMAIL_RECEPTOR, msg.as_string())
                server.quit()

            st.success("✅ ¡Enviado con éxito!")
            st.balloons()

        except Exception as e:
            st.error(f"❌ Error: {e}")
