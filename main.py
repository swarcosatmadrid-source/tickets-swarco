import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
from streamlit_gsheets import GSheetsConnection

# --- 1. CONFIGURACIÓN DE RUTAS Y MÓDULOS ---
sys.path.append(os.path.dirname(__file__))

try:
    from usuarios import gestionar_acceso, interfaz_registro_legal
    # Asegúrate de tener estos archivos o comenta las líneas si no los usas aún
    # from estilos import cargar_estilos 
except Exception as e:
    st.error(f"❌ Error al cargar módulos: {e}")
    st.stop()

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SWARCO SAT | Portal de Tickets", layout="centered", page_icon="🚥")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. GESTIÓN DE SESIÓN (ESTADO) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []
if 'ticket_enviado' not in st.session_state:
    st.session_state.ticket_enviado = False

# --- 4. CONTROL DE ACCESO (LOGIN / REGISTRO) ---
if not st.session_state.autenticado:
    st.image("logo.png", width=250) # Asegúrate de tener el logo en la carpeta
    tab_login, tab_reg = st.tabs(["🔐 Iniciar Sesión", "📝 Registro de Técnico"])
    
    with tab_login:
        if gestionar_acceso(conn):
            st.rerun()
            
    with tab_reg:
        interfaz_registro_legal(conn)
        
    st.stop() # Bloqueo total si no está logueado

# --- 5. INTERFAZ PRINCIPAL (SOLO USUARIOS AUTENTICADOS) ---
d_cli = st.session_state.get('datos_cliente', {})

# Encabezado con datos del usuario logueado
st.sidebar.image("logo.png", width=150)
st.sidebar.success(f"Usuario: {d_cli.get('Contacto')}")
st.sidebar.info(f"Empresa: {d_cli.get('Empresa')}")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state.autenticado = False
    st.rerun()

st.title("🎫 Generador de Reportes SAT")
st.markdown("---")

# PANTALLA DE ÉXITO POST-ENVÍO
if st.session_state.ticket_enviado:
    st.balloons()
    st.success("✅ Ticket enviado correctamente al sistema central.")
    if st.button("Crear nuevo ticket"):
        st.session_state.ticket_enviado = False
        st.session_state.lista_equipos = []
        st.rerun()
    st.stop()

# --- 6. FORMULARIO DE TICKET (DATOS BLOQUEADOS POR SEGURIDAD) ---
st.subheader("📍 Datos del Servicio")
col1, col2 = st.columns(2)

with col1:
    # Estos campos vienen del login, el usuario NO puede cambiarlos
    st.text_input("Empresa Solicitante", value=d_cli.get('Empresa'), disabled=True)
    proyecto = st.text_input("Proyecto / Ubicación Exacta *", placeholder="Ej: Túnel de Somport")

with col2:
    st.text_input("Email de Confirmación", value=d_cli.get('Email'), disabled=True)
    telefono = st.text_input("Teléfono de contacto móvil *")

st.markdown("---")

# --- 7. CARGA DE EQUIPOS ---
st.subheader("🛠️ Detalle de Equipos y Averías")
ce1, ce2 = st.columns(2)
with ce1:
    ns_equipo = st.text_input("Número de Serie (N/S) *")
with ce2:
    referencia = st.text_input("Referencia del Equipo (Opcional)")

falla_desc = st.text_area("Descripción de la avería o síntoma *", placeholder="Describa brevemente qué sucede...")

if st.button("➕ Añadir Equipo a la Lista"):
    if ns_equipo and falla_desc:
        st.session_state.lista_equipos.append({
            "N.S.": ns_equipo,
            "REF": referencia,
            "Avería": falla_desc
        })
        st.toast("Equipo añadido")
    else:
        st.error("⚠️ El N/S y la descripción son obligatorios.")

# TABLA DE RESUMEN
if st.session_state.lista_equipos:
    st.write("### Equipos en este reporte:")
    df_equipos = pd.DataFrame(st.session_state.lista_equipos)
    st.table(df_equipos)
    
    if st.button("🚀 GENERAR Y ENVIAR TICKET FINAL", type="primary", use_container_width=True):
        if not proyecto or not telefono:
            st.error("⚠️ Por favor, complete la ubicación y el teléfono.")
        else:
            # Aquí irá la llamada a tu función de envío de correo/script
            # Por ahora, simulamos el éxito:
            st.session_state.ticket_enviado = True
            st.rerun()

