import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import io
import datetime

# --- 1. PRIMERO: CONFIGURACIÓN DE PÁGINA (OBLIGATORIO AQUÍ) ---
st.set_page_config(page_title="SWARCO SAT Form", page_icon="🎫", layout="centered")

# --- 2. SEGUNDO: LEER SECRETOS ---
# (Si ponemos esto antes de set_page_config, sale pantalla blanca)
if "GMAIL_PASSWORD" in st.secrets:
    PASSWORD_EMISOR = st.secrets["GMAIL_PASSWORD"]
else:
    st.error("⚠️ Error: No se ha configurado el secreto GMAIL_PASSWORD en la nube.")
    st.stop()

# --- 3. VARIABLES Y RESTO DEL CÓDIGO ---
EMAIL_EMISOR = "swarcosatmadrid@gmail.com"
EMAIL_RECEPTOR = "aitor.badiola@swarco.com" 

# Estilos CSS...
st.markdown("""
    <style>
    .stApp {background-color: white;}
    .stButton>button {width: 100%; background-color: #009FE3; color: white; border-radius: 5px;}
    </style>
    """, unsafe_allow_html=True)

# ... AQUÍ SIGUE EL RESTO DE TU CÓDIGO IGUAL QUE ANTES ...
