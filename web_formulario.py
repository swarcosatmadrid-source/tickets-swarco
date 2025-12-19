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

LISTA_PAISES = [
    "España", "Portugal", "Argentina", "Bolivia", "Brasil", "Chile", "Colombia", 
    "Costa Rica", "Cuba", "Ecuador", "El Salvador", "Estados Unidos", "Guatemala", 
    "Honduras", "México", "Nicaragua", "Panamá", "Paraguay", "Perú", 
    "Puerto Rico", "República Dominicana", "Uruguay", "Venezuela", "Otro"
]

st.set_page_config(page_title="Soporte SWARCO", page_icon="🚦", layout="centered")

# --- ESTILOS CSS (DISEÑO PERSONALIZADO) ---
st.markdown("""
    <style>
    /* 1. FONDO AZUL SWARCO */
    .stApp {
        background: linear-gradient(180deg, #009FE3 0%, #005F87 100%);
        background-attachment: fixed;
    }

    /* Ocultar elementos */
    #MainMenu, footer, header {visibility: hidden;}

    /* 2. DISEÑO DEL FORMULARIO (TARJETA) */
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        padding: 3rem;
        border-radius: 10px; /* Bordes de la tarjeta menos redondos */
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 4px solid #FF6600; 
    }

    /* 3. TÍTULOS CENTRADOS */
    h1, h2, h3, p { text-align: center !important; }
    
    /* 4. BOTÓN CUADRADO Y GRANDE */
    .stButton {
        display: flex;
        justify-content: center;
    }
    .stButton>button {
        width: 100%; /* Ocupa todo el ancho disponible */
        background-color: #009FE3;
        color: white;
        font-weight: bold;
        border: none;
        
        /* AQUÍ ESTÁ EL CAMBIO A CUADRADO */
        border-radius: 5px; /* 0px sería puntas afiladas, 5px es cuadrado estándar */
        
        height: 60px; /* Más alto para que destaque */
        font-size: 20px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        transition: all 0.2s;
        text-transform: uppercase; /* Letras en mayúscula para más fuerza */
    }
    .stButton>button:hover {
        background-color: #004d80;
        color: #FF6600;
        border: 2px solid #FF6600; /* Borde naranja al pasar ratón */
    }
    
    /* 5. ESTILO ICONOS VMS */
    .vms-icon {
        background-color: #111;
        color: #FFCC00;
        font-family: 'Courier New', monospace;
        padding: 5px 12px;
        border-radius: 4px;
        border: 2px solid #444;
        font-weight: bold;
        font-size: 24px;
        display: inline-block;
        box-shadow: 0 0 10px rgba(255, 204, 0, 0.3);
        margin-bottom: 10px;
    }

    /* 6. LOGO CENTRADO */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    [data-testid="stImage"] img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    
    label { font-weight: bold !important; color: #444 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CABECERA ---
c_logo1, c_logo2, c_logo3 = st.columns([1, 2, 1]) 
with c_logo2:
    st.image("https://www.swarco.com/themes/custom/swarco/logo.svg", use_column_width=True)

st.markdown("<h1 style='color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.3);'>Portal de Soporte Técnico</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #E6F4FA; font-size: 18px;'>Complete el formulario para registrar su incidencia.</p>", unsafe_allow_html=True)

# --- FORMULARIO ---
with st.form("form_cliente"):
    
    # SECCIÓN 1
    st.markdown("""
        <div style="text-align: center;">
            <div class="vms-icon">ℹ INFO</div>
            <h3 style="border:none; margin-top:0;">Datos de Contacto</h3>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        cliente = st.text_input("Empresa / Cliente *")
        contacto = st.text_input("Nombre y Apellidos *")
    with col2:
        email_contacto = st.text_input("Email de Contacto *")
        telf_contacto = st.text_input("Teléfono (Opcional)")

    # SECCIÓN 2
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center;">
            <div class="vms-icon">📟 VMS</div>
            <h3 style="border:none; margin-top:0;">Datos del Equipo</h3>
        </div>
        """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        pais = st.selectbox("País *", LISTA_PAISES)
        serie = st.text_input("Número de Serie *")
    with col4:
        proyecto = st.text_input("Proyecto / Ubicación")
        modelo = st.text_input("Modelo de Panel")

    # SECCIÓN 3
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center;">
            <div class="vms-icon">⚠ FALLO</div>
            <h3 style="border:none; margin-top:0;">Detalle de Incidencia</h3>
        </div>
        """, unsafe_allow_html=True)
        
    prioridad = st.selectbox("Prioridad", ["Normal", "Alta", "Urgente / Crítica"])
    descripcion = st.text_area("Descripción del problema *", height=150)
    
    st.markdown("<div style='text-align: center; margin-bottom: 10px;'><b>Adjuntar archivos (Fotos/PDF)</b></div>", unsafe_allow_html=True)
    adjuntos = st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'pdf', 'xlsx'], label_visibility="collapsed")
    
    st.write("") 
    # El botón ahora será cuadrado y ancho gracias al CSS
    enviar = st.form_submit_button("🚀 ENVIAR SOLICITUD")

# --- LÓGICA DE ENVÍO ---
if enviar:
    if not cliente or not contacto or not email_contacto or not pais or not serie or not descripcion:
        st.error("❌ Faltan datos obligatorios (*)")
    else:
        with st.spinner("Enviando datos a la central..."):
            try:
                # 1. Crear Excel
                fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                datos_dict = {
                    'ID': ['WEB'], 
                    'Fecha': [fecha],
                    'Cliente': [cliente],
                    'Proyecto': [proyecto],
                    'País': [pais],
                    'Serie': [serie],
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

                # 2. Email
                msg = MIMEMultipart()
                msg['From'] = EMAIL_EMISOR
                msg['To'] = EMAIL_RECEPTOR
                msg['Subject'] = f"{ASUNTO_CLAVE}: {cliente} - {pais}"

                cuerpo_html = f"""
                <div style="font-family: Arial, sans-serif; color: #333; padding: 20px; border: 2px solid #009FE3;">
                    <h2 style="color: #009FE3; text-align: center;">Nueva Incidencia Web</h2>
                    <p style="text-align: center;"><b>📅 {fecha}</b></p>
                    <hr>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr><td style="padding: 5px;"><b>Cliente:</b></td><td>{cliente}</td></tr>
                        <tr><td style="padding: 5px;"><b>Contacto:</b></td><td>{contacto}</td></tr>
                        <tr><td style="padding: 5px;"><b>Email:</b></td><td>{email_contacto}</td></tr>
                        <tr><td style="padding: 5px;"><b>Teléfono:</b></td><td>{telf_contacto}</td></tr>
                        <tr style="background-color: #f2f2f2;"><td style="padding: 5px;"><b>Nº Serie:</b></td><td><b>{serie}</b></td></tr>
                        <tr><td style="padding: 5px;"><b>País:</b></td><td>{pais}</td></tr>
                    </table>
                    <br>
                    <div style="background-color: #FFEEE0; padding: 15px; border-left: 5px solid #FF6600;">
                        <b>DESCRIPCIÓN:</b><br>{descripcion}
                    </div>
                </div>
                """
                msg.attach(MIMEText(cuerpo_html, 'html'))

                # Adjuntos
                part_excel = MIMEBase('application', "octet-stream")
                part_excel.set_payload(excel_bytes)
                encoders.encode_base64(part_excel)
                part_excel.add_header('Content-Disposition', f'attachment; filename="{NOMBRE_ADJUNTO_EXCEL}"')
                msg.attach(part_excel)

                if adjuntos:
                    for archivo in adjuntos:
                        bytes_archivo = archivo.getvalue()
                        part_file = MIMEBase('application', "octet-stream")
                        part_file.set_payload(bytes_archivo)
                        encoders.encode_base64(part_file)
                        part_file.add_header('Content-Disposition', f'attachment; filename="{archivo.name}"')
                        msg.attach(part_file)

                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.login(EMAIL_EMISOR, PASSWORD_EMISOR)
                server.sendmail(EMAIL_EMISOR, EMAIL_RECEPTOR, msg.as_string())
                server.quit()

                st.success("✅ Solicitud enviada correctamente.")
                st.balloons()
                
            except Exception as e:
                st.error(f"Error: {e}")
