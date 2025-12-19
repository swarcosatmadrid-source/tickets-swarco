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
NOMBRE_ADJUNTO_EXCEL = "temp_ticket_envio.xlsx"

# Lista de países
LISTA_PAISES = [
    "España", "Portugal", "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", 
    "Costa Rica", "Cuba", "Ecuador", "El Salvador", "Estados Unidos", "Guatemala", 
    "Honduras", "México", "Nicaragua", "Panamá", "Paraguay", "Perú", 
    "Puerto Rico", "República Dominicana", "Uruguay", "Venezuela", "Otro"
]

st.set_page_config(page_title="Soporte SWARCO", page_icon="🚦", layout="centered")

# --- ESTILOS CSS (DISEÑO PRO) ---
st.markdown("""
    <style>
    /* Fondo General */
    .stApp { background-color: #F8F9FA; }

    /* Ocultar elementos de Streamlit */
    #MainMenu, footer, header {visibility: hidden;}

    /* DISEÑO DEL FORMULARIO (BORDE NARANJA) */
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 3px solid #FF6600; /* BORDE NARANJA SWARCO */
    }

    /* Títulos de secciones */
    h3 { color: #333; font-size: 1.2rem; border-bottom: 2px solid #eee; padding-bottom: 5px; margin-top: 20px;}

    /* BOTÓN CENTRADO Y ESTILIZADO */
    .stButton {
        display: flex;
        justify-content: center;
    }
    .stButton>button {
        width: 60%; /* No ocupa todo el ancho, queda centrado */
        background-color: #009FE3;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 25px;
        height: 50px;
        font-size: 18px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        background-color: #007BB5;
        transform: scale(1.02);
    }
    
    /* Ajuste Logo */
    [data-testid="stImage"] { display: flex; justify_content: center; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
# Logo SWARCO (Versión negra/oscura limpia)
st.image("https://www.swarco.com/themes/custom/swarco/logo.svg", width=280)

st.markdown("<h1 style='text-align: center; color: #333;'>Apertura de Incidencia</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>Complete el formulario para solicitar asistencia técnica.</p>", unsafe_allow_html=True)

# --- FORMULARIO ---
with st.form("form_cliente"):
    
    # SECCIÓN 1: SOLICITANTE
    st.markdown("### 👤 Datos del Solicitante")
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Empresa / Cliente *")
        contacto = st.text_input("Nombre y Apellidos *")
    with col2:
        email_contacto = st.text_input("Email de Contacto *")
        telf_contacto = st.text_input("Teléfono (Opcional)")

    # SECCIÓN 2: PANEL / EQUIPO
    st.markdown("### 📟 Datos del Panel / Equipo")
    col3, col4 = st.columns(2)
    with col3:
        pais = st.selectbox("País *", LISTA_PAISES)
        serie = st.text_input("Número de Serie *")
    with col4:
        proyecto = st.text_input("Proyecto / Ubicación (Opcional)")
        modelo = st.text_input("Modelo de Panel (Opcional)")

    # SECCIÓN 3: DETALLE
    st.markdown("### ⚠️ Detalle de la Incidencia")
    prioridad = st.selectbox("Prioridad", ["Normal", "Alta", "Urgente / Crítica"])
    descripcion = st.text_area("Descripción del problema *", height=150, placeholder="Explique el fallo, códigos de error, qué estaba haciendo cuando ocurrió...")
    
    # SUBIDA DE ARCHIVOS
    st.markdown("---")
    adjuntos = st.file_uploader("Adjuntar fotos o archivos (Máx 3)", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'pdf', 'xlsx'])
    
    st.write("") # Espacio
    # Botón (Se centra por CSS)
    enviar = st.form_submit_button("🚀 ENVIAR SOLICITUD")

# --- LÓGICA DE ENVÍO ---
if enviar:
    # Validaciones de campos obligatorios
    if not cliente or not contacto or not email_contacto or not pais or not serie or not descripcion:
        st.error("❌ Por favor, revise los campos marcados con asterisco (*). Son obligatorios.")
    else:
        with st.spinner("Procesando solicitud y enviando archivos..."):
            try:
                # 1. Crear Excel de Datos
                fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                datos_dict = {
                    'ID': ['WEB'], 
                    'Fecha': [fecha],
                    'Cliente': [cliente],
                    'Proyecto': [proyecto],
                    'País': [pais],
                    'Serie': [serie], # Dato Crítico
                    'Modelo': [modelo],
                    'Contacto': [contacto],
                    'Email': [email_contacto],
                    'Teléfono': [telf_contacto],
                    'Prioridad': [prioridad],
                    'Estado': ['Abierto'],
                    'Problema': [descripcion]
                }
                df = pd.DataFrame(datos_dict)
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                excel_bytes = buffer.getvalue()

                # 2. Configurar Email
                msg = MIMEMultipart()
                msg['From'] = EMAIL_EMISOR
                msg['To'] = EMAIL_RECEPTOR
                msg['Subject'] = f"{ASUNTO_CLAVE}: {cliente} - {pais}"

                # Cuerpo HTML
                cuerpo_html = f"""
                <div style="font-family: Arial, sans-serif; color: #333; padding: 20px;">
                    <h2 style="color: #FF6600; border-bottom: 2px solid #FF6600;">Nueva Incidencia Web</h2>
                    
                    <p><b>📅 Fecha:</b> {fecha}</p>
                    
                    <h3 style="background-color: #eee; padding: 5px;">👤 Contacto</h3>
                    <ul>
                        <li><b>Cliente:</b> {cliente}</li>
                        <li><b>Persona:</b> {contacto}</li>
                        <li><b>Email:</b> <a href="mailto:{email_contacto}">{email_contacto}</a></li>
                        <li><b>Teléfono:</b> {telf_contacto}</li>
                    </ul>

                    <h3 style="background-color: #eee; padding: 5px;">📟 Equipo</h3>
                    <ul>
                        <li><b>País:</b> {pais}</li>
                        <li><b>Nº Serie:</b> {serie}</li>
                        <li><b>Proyecto:</b> {proyecto}</li>
                    </ul>

                    <div style="border: 1px solid #ddd; padding: 15px; margin-top: 15px; background-color: #fff9f5;">
                        <b style="color: #FF6600;">DESCRIPCIÓN:</b><br>
                        {descripcion}
                    </div>
                </div>
                """
                msg.attach(MIMEText(cuerpo_html, 'html'))

                # 3. Adjuntar el Excel (Obligatorio para tu Monitor)
                part_excel = MIMEBase('application', "octet-stream")
                part_excel.set_payload(excel_bytes)
                encoders.encode_base64(part_excel)
                part_excel.add_header('Content-Disposition', f'attachment; filename="{NOMBRE_ADJUNTO_EXCEL}"')
                msg.attach(part_excel)

                # 4. Adjuntar FOTOS/ARCHIVOS del cliente
                if adjuntos:
                    for archivo in adjuntos:
                        # Leer archivo de memoria
                        bytes_archivo = archivo.getvalue()
                        part_file = MIMEBase('application', "octet-stream")
                        part_file.set_payload(bytes_archivo)
                        encoders.encode_base64(part_file)
                        part_file.add_header('Content-Disposition', f'attachment; filename="{archivo.name}"')
                        msg.attach(part_file)

                # 5. Enviar por SMTP Gmail
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(EMAIL_EMISOR, PASSWORD_EMISOR)
                server.sendmail(EMAIL_EMISOR, EMAIL_RECEPTOR, msg.as_string())
                server.quit()

                st.success("✅ ¡Solicitud enviada con éxito! Su número de serie ha sido registrado.")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error de conexión al enviar: {e}")

