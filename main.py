import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
from streamlit_gsheets import GSheetsConnection
from idiomas import traducir_interfaz # Importamos tu traductor

# --- 1. CONFIGURACIÓN DE RUTAS Y MÓDULOS ---
sys.path.append(os.path.dirname(__file__))

try:
    import usuarios # Cambiamos la importación para manejar mejor las funciones
except Exception as e:
    st.error(f"❌ Error al cargar módulos: {e}")
    st.stop()

# --- 2. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="SWARCO SAT | Portal", layout="centered", page_icon="🚥")

# --- 3. GESTIÓN DE SESIÓN (ESTADO) ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'mostrar_registro' not in st.session_state:
    st.session_state.mostrar_registro = False
if 'idioma' not in st.session_state:
    st.session_state.idioma = "Castellano"
if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []
if 'ticket_enviado' not in st.session_state:
    st.session_state.ticket_enviado = False

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 4. SELECTOR DE IDIOMA Y TRADUCCIONES (Universal) ---
if not st.session_state.autenticado:
    st.sidebar.markdown("### 🌐 Language / Idioma")
    # Agregamos los idiomas que quieras. Tu función ya maneja si no existen.
    idiomas_disponibles = ["Castellano", "English", "Français", "Deutsch"]
    st.session_state.idioma = st.sidebar.selectbox(
        "Select / Seleccione:", 
        idiomas_disponibles,
        index=idiomas_disponibles.index(st.session_state.idioma) if st.session_state.idioma in idiomas_disponibles else 0,
        key="lang_selector"
    )

t = traducir_interfaz(st.session_state.idioma)

# --- 5. CONTROL DE ACCESO (LOGIN / REGISTRO) ---
if not st.session_state.autenticado:
    
    # LOGO CENTRADO (Usando columnas como pediste)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image("logo.png", use_container_width=True)

    # SI EL USUARIO PIDE REGISTRO (Pantalla secundaria)
    if st.session_state.mostrar_registro:
        usuarios.interfaz_registro_legal(conn)
        if st.button("⬅️ " + ("Volver" if st.session_state.idioma == "Castellano" else "Back")):
            st.session_state.mostrar_registro = False
            st.rerun()
    
    # PANTALLA DE LOGIN (Principal)
    else:
        st.markdown(f"<h2 style='text-align: center;'>{t.get('login_tit', 'Acceso')}</h2>", unsafe_allow_html=True)
        if usuarios.gestionar_acceso(conn):
            st.rerun()
        
        st.markdown("---")
        if st.button(t.get("btn_ir_registro", "No tengo cuenta, quiero registrarme"), use_container_width=True):
            st.session_state.mostrar_registro = True
            st.rerun()
            
    st.stop() 

# --- 6. INTERFAZ PRINCIPAL (AUTENTICADO) ---
d_cli = st.session_state.get('datos_cliente', {})

st.sidebar.image("logo.png", width=150)
st.sidebar.success(f"{t.get('contacto', 'Usuario')}: {d_cli.get('Contacto')}")
st.sidebar.info(f"{t.get('cliente', 'Empresa')}: {d_cli.get('Empresa')}")

if st.sidebar.button(t.get("btn_salir", "SALIR")):
    st.session_state.autenticado = False
    st.rerun()

st.title(f"🎫 {t.get('titulo_portal', 'Generador de Reportes SAT')}")
st.markdown("---")

# PANTALLA DE ÉXITO POST-ENVÍO
if st.session_state.ticket_enviado:
    st.success(t.get("exito", "✅ Ticket enviado correctamente."))
    if st.button("Crear nuevo ticket" if st.session_state.idioma == "Castellano" else "New ticket"):
        st.session_state.ticket_enviado = False
        st.session_state.lista_equipos = []
        st.rerun()
    st.stop()

# --- 7. FORMULARIO DE TICKET ---
st.subheader(f"📍 {t.get('cat1', 'Datos del Servicio')}")
col1, col2 = st.columns(2)

with col1:
    st.text_input(t.get("cliente", "Empresa"), value=d_cli.get('Empresa'), disabled=True)
    proyecto = st.text_input(t.get("proyecto", "Ubicación") + " *")

with col2:
    st.text_input(t.get("email", "Email"), value=d_cli.get('Email'), disabled=True)
    telefono = st.text_input(t.get("tel", "Teléfono") + " *")

st.markdown("---")

# --- 8. CARGA DE EQUIPOS Y ARCHIVOS ---
st.subheader(f"🛠️ {t.get('cat2', 'Detalle de Equipos')}")
ce1, ce2 = st.columns(2)
with ce1:
    ns_equipo = st.text_input(t.get("ns_titulo", "N.S.") + " *")
with ce2:
    referencia = st.text_input("Referencia / Ref")

falla_desc = st.text_area(t.get("desc_instruccion", "Descripción") + " *")

# ADJUNTAR ARCHIVOS (Fotos/Vídeos)
archivos = st.file_uploader(t.get("fotos", "Adjuntar archivos"), accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4', 'pdf'])

if st.button(t.get("btn_agregar", "➕ Añadir Equipo")):
    if ns_equipo and falla_desc:
        st.session_state.lista_equipos.append({
            "N.S.": ns_equipo,
            "REF": referencia,
            "Avería": falla_desc,
            "Adjuntos": len(archivos) if archivos else 0
        })
        st.toast("Equipo añadido")
    else:
        st.error("⚠️")

# TABLA Y ENVÍO
if st.session_state.lista_equipos:
    st.write("### Equipos en este reporte:")
    df_equipos = pd.DataFrame(st.session_state.lista_equipos)
    st.table(df_equipos)
    
    if st.button(t.get("btn_generar", "🚀 ENVIAR TICKET"), type="primary", use_container_width=True):
        if not proyecto or not telefono:
            st.error("⚠️")
        else:
            # Lógica de envío final (aquí conectarás el correo.py luego)
            st.session_state.ticket_enviado = True
            st.rerun()

