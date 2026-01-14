import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# 1. SEGURIDAD Y CONFIGURACIÓN
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection

# Configuración de página
st.set_page_config(page_title="SWARCO TRAFFIC SPAIN | Portal SAT", layout="centered", page_icon="🚥")
cargar_estilos()

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- SISTEMA DE AUTENTICACIÓN Y REGISTRO ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.datos_cliente = {}

def login_usuario(usuario, clave):
    try:
        df_clientes = conn.read(worksheet="Clientes")
        # Buscamos que coincidan Usuario y Clave
        validar = df_clientes[(df_clientes['Usuario'] == usuario) & (df_clientes['Clave'] == clave)]
        
        if not validar.empty:
            st.session_state.autenticado = True
            st.session_state.datos_cliente = validar.iloc[0].to_dict()
            st.rerun()
        else:
            st.error("❌ Usuario o clave incorrectos.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")

def registrar_usuario(nuevo_usr, nueva_clv, empresa, contacto, email):
    try:
        df_clientes = conn.read(worksheet="Clientes")
        if nuevo_usr in df_clientes['Usuario'].values:
            st.warning("⚠️ Este nombre de usuario ya existe. Elija otro.")
        else:
            nueva_data = pd.DataFrame([{
                "Usuario": nuevo_usr, "Clave": nueva_clv, 
                "Empresa": empresa, "Contacto": contacto, "Email": email
            }])
            df_final = pd.concat([df_clientes, nueva_data], ignore_index=True)
            conn.update(worksheet="Clientes", data=df_final)
            st.success("✅ Registro completado. ¡Ahora puede entrar!")
    except Exception as e:
        st.error(f"Error al registrar: {e}")

# --- PANTALLA DE ENTRADA / REGISTRO ---
if not st.session_state.autenticado:
    st.image("logo.png", width=300)
    tab_login, tab_registro = st.tabs(["🔑 Entrar", "📝 Registrarse"])
    
    with tab_login:
        u_login = st.text_input("Usuario")
        p_login = st.text_input("Contraseña", type="password")
        if st.button("Acceder", use_container_width=True):
            login_usuario(u_login, p_login)
            
    with tab_registro:
        st.info("Cree su cuenta para que sus datos se rellenen automáticamente en el futuro.")
        r_usr = st.text_input("Defina su Usuario")
        r_clv = st.text_input("Defina su Contraseña", type="password")
        r_emp = st.text_input("Empresa / Entidad")
        r_con = st.text_input("Persona de Contacto")
        r_ema = st.text_input("Email Corporativo")
        if st.button("Crear Cuenta", use_container_width=True):
            if r_usr and r_clv and r_emp and r_ema:
                registrar_usuario(r_usr, r_clv, r_emp, r_con, r_ema)
            else:
                st.error("⚠️ Por favor, rellene todos los campos.")
    st.stop()

# --- INICIO DE LA APP (UNA VEZ LOGUEADO) ---
t = traducir_interfaz("Castellano") 
d_cli = st.session_state.datos_cliente

st.image("logo.png", width=250)
st.title(f"Bienvenido, {d_cli['Contacto']}")

# --- CATEGORÍA 1: CLIENTE (AUTO-RELLENADA) ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    # Estos campos son de solo lectura porque ya los puso el cliente al registrarse
    empresa = st.text_input(t['cliente'], value=d_cli['Empresa'], disabled=True)
    contacto = st.text_input(t['contacto'], value=d_cli['Contacto'], disabled=True)
    proyecto_ub = st.text_input(t['proyecto']) # Este sí lo llenan por reporte

with c2:
    email_usr = st.text_input(t['email'], value=d_cli['Email'], disabled=True)
    p_nombres = list(PAISES_DATA.keys())
    pais_sel = st.selectbox(t['pais'], p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
    tel_raw = st.text_input(f"{t['tel']}", placeholder="Solo números")
    tel_final = "".join(filter(str.isdigit, tel_raw))

# --- CATEGORÍA 2: EQUIPO ---
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
ce1, ce2 = st.columns(2)
with ce1:
    ns_in = st.text_input(t['ns_titulo'], key="ns_input")
with ce2:
    ref_in = st.text_input("REF.", key="ref_input")

# --- CATEGORÍA 3: PROBLEMA ---
st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
urg_val = st.select_slider(t['urg_instruccion'], options=[t['u1'], t['u2'], t['u3'], t['u4'], t['u5'], t['u6']], value=t['u3'])
falla_in = st.text_area(t['desc_instruccion'], key="desc_input")

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

# ACCIONES
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button(f"➕ {t['btn_agregar']}", use_container_width=True):
        if len(ns_in) >= 3 and len(falla_in) >= 10:
            st.session_state.lista_equipos.append({
                "ID": str(uuid.uuid4())[:8], "N.S.": ns_in, "REF": ref_in, "Prioridad": urg_val, "Descripción": falla_in
            })
            st.rerun()

with col_btn2:
    if st.button(f"🚀 {t['btn_generar']}", type="primary", use_container_width=True):
        data_final = st.session_state.lista_equipos.copy()
        if not data_final and ns_in and falla_in:
            data_final.append({"ID": str(uuid.uuid4())[:8], "N.S.": ns_in, "REF": ref_in, "Prioridad": urg_val, "Descripción": falla_in})
        
        if empresa and data_final:
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            if enviar_email_outlook(empresa, d_cli['Contacto'], proyecto_ub, data_final, d_cli['Email'], ticket_id, tel_final):
                st.success(t['exito'])
                st.balloons()
                st.session_state.lista_equipos = []
        else:
            st.error("⚠️ No hay equipos para reportar.")

# CIERRE DE SESIÓN
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

st.markdown("<p style='text-align:center; font-size:12px; color:#999; margin-top:50px;'>© 2024 SWARCO TRAFFIC SPAIN</p>", unsafe_allow_html=True)


