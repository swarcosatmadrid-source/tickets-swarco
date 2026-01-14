import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# 1. SEGURIDAD Y CONFIGURACIÓN DE RUTAS
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection

# Configuración de página con identidad corporativa
st.set_page_config(page_title="SWARCO TRAFFIC SPAIN | Portal SAT", layout="centered", page_icon="🚥")
cargar_estilos()

# --- CONEXIÓN A GOOGLE SHEETS ---
# Recuerda que en st.secrets debe estar la URL de tu hoja
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SISTEMA DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.datos_cliente = {}
if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# --- FUNCIONES DE BASE DE DATOS ---
def login_usuario(usuario, clave):
    try:
        df_clientes = conn.read(worksheet="Clientes", ttl=0)
        validar = df_clientes[(df_clientes['Usuario'] == usuario) & (df_clientes['Clave'] == clave)]
        if not validar.empty:
            st.session_state.autenticado = True
            st.session_state.datos_cliente = validar.iloc[0].to_dict()
            st.rerun()
        else:
            st.error("❌ Usuario o clave incorrectos.")
    except Exception as e:
        st.error(f"Error al conectar con la base de datos de clientes: {e}")

def registrar_usuario(nuevo_usr, nueva_clv, empresa, contacto, email):
    try:
        df_clientes = conn.read(worksheet="Clientes", ttl=0)
        if nuevo_usr in df_clientes['Usuario'].values:
            st.warning("⚠️ Este usuario ya existe.")
        else:
            nueva_data = pd.DataFrame([{
                "Usuario": nuevo_usr, "Clave": nueva_clv, 
                "Empresa": empresa, "Contacto": contacto, "Email": email
            }])
            df_final = pd.concat([df_clientes, nueva_data], ignore_index=True)
            conn.update(worksheet="Clientes", data=df_final)
            st.success("✅ Registro exitoso. Ya puede entrar.")
    except Exception as e:
        st.error(f"Error al guardar registro: {e}")

# --- INTERFAZ DE ACCESO ---
if not st.session_state.autenticado:
    st.image("logo.png", width=300)
    tab_login, tab_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
    
    with tab_login:
        u_login = st.text_input("Nombre de Usuario")
        p_login = st.text_input("Contraseña", type="password")
        if st.button("Entrar", use_container_width=True):
            login_usuario(u_login, p_login)
            
    with tab_registro:
        st.info("Regístrese para que no tenga que rellenar sus datos en cada reporte.")
        r_usr = st.text_input("Elija Usuario")
        r_clv = st.text_input("Elija Contraseña", type="password")
        r_emp = st.text_input("Empresa")
        r_con = st.text_input("Nombre de Contacto")
        r_ema = st.text_input("Email de Contacto")
        if st.button("Finalizar Registro", use_container_width=True):
            if r_usr and r_clv and r_emp and r_ema:
                registrar_usuario(r_usr, r_clv, r_emp, r_con, r_ema)
            else:
                st.error("⚠️ Rellene todos los campos obligatorios.")
    st.stop()

# --- INTERFAZ DE PORTAL (CLIENTE LOGUEADO) ---
t = traducir_interfaz("Castellano")
d_cli = st.session_state.datos_cliente

# Encabezado
col_logo, col_logout = st.columns([4, 1])
with col_logo:
    st.image("logo.png", width=200)
with col_logout:
    if st.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.rerun()

st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #00549F;">SWARCO TRAFFIC SPAIN</h2>
        <p style="font-size: 18px;">Bienvenido/a, <b>{d_cli['Contacto']}</b></p>
    </div>
""", unsafe_allow_html=True)

# --- BLOQUE 1: DATOS AUTOMÁTICOS ---
st.markdown(f'<div class="section-header">INFORMACIÓN DEL REPORTE</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.text_input("Empresa", value=d_cli['Empresa'], disabled=True)
    proyecto_ub = st.text_input("Proyecto / Ubicación exacta")
with c2:
    st.text_input("Email", value=d_cli['Email'], disabled=True)
    tel_raw = st.text_input("Teléfono de contacto móvil")
    tel_final = "".join(filter(str.isdigit, tel_raw))

# --- BLOQUE 2: EQUIPO Y FALLA ---
st.markdown(f'<div class="section-header">DETALLES DEL EQUIPO</div>', unsafe_allow_html=True)
ce1, ce2 = st.columns(2)
with ce1:
    ns_in = st.text_input("Número de Serie (N.S.)", key="ns_input")
with ce2:
    ref_in = st.text_input("Referencia (REF.)", key="ref_input")

urg_val = st.select_slider("Prioridad del problema", options=[t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']], value=t['u3'])
falla_in = st.text_area("Descripción de la avería", placeholder="Explique brevemente el fallo...", key="desc_input")

# --- GESTIÓN DE EQUIPOS Y ENVÍO ---
col_add, col_send = st.columns(2)
with col_add:
    if st.button("➕ Añadir otro equipo", use_container_width=True):
        if len(ns_in) >= 3 and len(falla_in) >= 10:
            st.session_state.lista_equipos.append({
                "ID": str(uuid.uuid4())[:8], "N.S.": ns_in, "REF": ref_in, "Prioridad": urg_val, "Descripción": falla_in
            })
            st.rerun()

with col_send:
    if st.button("🚀 GENERAR TICKET", type="primary", use_container_width=True):
        data_final = st.session_state.lista_equipos.copy()
        if not data_final and ns_in and falla_in:
            data_final.append({"ID": str(uuid.uuid4())[:8], "N.S.": ns_in, "REF": ref_in, "Prioridad": urg_val, "Descripción": falla_in})
        
        if data_final and proyecto_ub:
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            
            # 1. Enviar Correo
            if enviar_email_outlook(d_cli['Empresa'], d_cli['Contacto'], proyecto_ub, data_final, d_cli['Email'], ticket_id, tel_final):
                
                # 2. Registrar en Google Sheets (Pestaña Sheet1)
                try:
                    resumen_equipos = " | ".join([f"NS:{e['N.S.']}" for e in data_final])
                    nueva_fila = pd.DataFrame([{
                        "Ticket_ID": ticket_id,
                        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Cliente": d_cli['Empresa'],
                        "Usuario": d_cli['Usuario'],
                        "Ubicacion": proyecto_ub,
                        "Equipos": resumen_equipos,
                        "Estado": "OPEN"
                    }])
                    df_historico = conn.read(worksheet="Sheet1", ttl=0)
                    df_updated = pd.concat([df_historico, nueva_fila], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=df_updated)
                    
                    st.success(f"Ticket {ticket_id} enviado con éxito.")
                    st.balloons()
                    st.session_state.lista_equipos = []
                except Exception as e:
                    st.warning(f"Ticket enviado por mail, pero error en base de datos: {e}")
        else:
            st.error("⚠️ Debe indicar la ubicación y al menos un equipo.")

# Mostrar lista actual
if st.session_state.lista_equipos:
    st.markdown("### Equipos en este reporte:")
    st.table(pd.DataFrame(st.session_state.lista_equipos).drop(columns=["ID"]))

st.markdown("<p style='text-align:center; color:#999; margin-top:50px;'>© 2024 SWARCO TRAFFIC SPAIN</p>", unsafe_allow_html=True)


