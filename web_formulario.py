import streamlit as st  # <--- ESTA TIENE QUE SER LA PRIMERA
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io
import datetime

# --- AHORA SÍ PODEMOS LEER LOS SECRETOS ---
# (Porque ya hemos importado streamlit arriba)
EMAIL_EMISOR = "swarcosatmadrid@gmail.com"
PASSWORD_EMISOR = st.secrets["GMAIL_PASSWORD"] 
EMAIL_RECEPTOR = "aitor.badiola@swarco.com" 

# --- RESTO DEL CÓDIGO A PARTIR DE AQUÍ ---
# ...
