import streamlit as st
import uuid
import pandas as pd  # <--- Agregado para el mostrador
from datetime import datetime
from correo import enviar_email_outlook
from estilos import cargar_estilos
from idiomas import textos
from paises import obtener_paises
import streamlit.components.v1 as components

# 1. Configuración de página y estilos
st.set_page_config(page_title="SWARCO SAT Portal", layout="wide", page_icon="🔧")
cargar_estilos()

# --- LÓGICA DE IDIOMAS (LO VIEJO) ---
if 'lang' not in st.session_state:
    st.session_state.lang = 'Español'

# --- BARRA LATERAL (NAVEGACIÓN) ---
st.sidebar.image("logo.png", use_container_width=True)
st.sidebar.markdown("---")
# Selector de idioma en la barra lateral para que no estorbe
st.session_state.lang = st.sidebar.selectbox("🌐 Idioma / Language", ["Español", "English", "Deutsch", "Français"])
t = textos[st.session_state.lang]

st.sidebar.markdown("---")
menu = st.sidebar.radio("🚀 MENÚ", ["📋 Nuevo Ticket", "📊 Mostrador Admin"])
st.sidebar.markdown("---")

# ---------------------------------------------------------
# OPCIÓN 1: FORMULARIO PARA EL CLIENTE (TODO LO VIEJO)
# ---------------------------------------------------------
if menu == "📋 Nuevo Ticket":
    st.title(t['titulo'])
    st.write(t['subtitulo'])
    
    # Imagen de referencia (Pegatina)
    st.image("etiqueta.jpeg", caption=t['instrucciones_img'], width=400)

    # Inicializar estados
    if 'lista_equipos' not in st.session_state:
        st.session_state.lista_equipos = []

    # Datos del Cliente
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            empresa = st.text_input(t['empresa'] + " *")
            contacto = st.text_input(t['contacto'] + " *")
            proyecto = st.text_input("Proyecto / Instalación")
        with col2:
            email_usr = st.text_input("Email *")
            tel_input = st.text_input(t['telefono'] + " *")
            tel_usr = "".join(filter(str.isdigit, tel_input))

    st.markdown("---")
    st.subheader("🛠️ " + t['seccion_equipos'])

    # Añadir equipos
    with st.expander(t['btn_agregar'], expanded=True):
        ce1, ce2, ce3 = st.columns([2, 2, 1])
        ns = ce1.text_input("S/N *")
        ref = ce2.text_input("REF")
        urgencia = ce3.selectbox("Prioridad", ["Normal", "Alta", "Crítica"])
        desc = st.text_area(t['falla'] + " *")
        
        if st.button(t['btn_agregar']):
            if ns and desc:
                st.session_state.lista_equipos.append({
                    "ns": ns, "ref": ref, "urgencia": urgencia, "desc": desc
                })
                st.toast("✅ Equipo añadido")
            else:
                st.warning("S/N y Descripción son obligatorios")

    # Tabla de equipos
    if st.session_state.lista_equipos:
        st.write("### Lista de equipos:")
        df_temp = pd.DataFrame(st.session_state.lista_equipos)
        st.table(df_temp)
        if st.button("🗑️ Borrar lista"):
            st.session_state.lista_equipos = []
            st.rerun()

    # ENVÍO
    if st.button("🚀 " + t['btn_enviar'], type="primary"):
        if not empresa or not contacto or not email_usr or not tel_usr or not st.session_state.lista_equipos:
            st.error("❌ " + t['error_campos'])
        else:
            ticket_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
            
            if enviar_email_outlook(empresa, contacto, proyecto, st.session_state.lista_equipos, email_usr, ticket_id, tel_usr):
                html_exito = f"""
                <div style="border: 2px solid #28a745; border-radius: 10px; padding: 20px; text-align: center; font-family: Arial; background-color: #f8fff9;">
                    <h1 style="color: #28a745;">✔️ {t['exito_titulo']}</h1>
                    <p style="font-size: 18px;">ID: <strong>{ticket_id}</strong></p>
                    <p>Enviado a: <strong>{email_usr}</strong></p>
                </div>
                """
                components.html(html_exito, height=250)
                st.balloons()
                st.session_state.lista_equipos = [] # Limpiar para el siguiente
            else:
                st.error("Error SMTP. Revise Secrets.")

# ---------------------------------------------------------
# OPCIÓN 2: MOSTRADOR ADMIN (LO NUEVO)
# ---------------------------------------------------------
else:
    st.title("📊 Panel de Control SAT")
    clave = st.text_input("Clave de Acceso", type="password")
    
    if clave == st.secrets["admin_password"]:
        st.success("Acceso Autorizado")
        
        # Datos para el mostrador (Esto vendrá de GSheets luego)
        st.subheader("Tickets del día")
        # Simulación de tabla de control
        mostrador_data = {
            "ID Ticket": ["SAT-20260113-X1", "SAT-20260113-Y2"],
            "Cliente": [empresa if 'empresa' in locals() else "Pendiente", "Ejemplo"],
            "Estado": ["🔴 Recibido", "🟡 En revisión"],
            "Hora": [datetime.now().strftime("%H:%M"), "09:00"]
        }
        df_admin = pd.DataFrame(mostrador_data)
        st.dataframe(df_admin, use_container_width=True)

        # Botón para descargar reporte
        csv = df_admin.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descargar histórico para Excel", csv, "reporte.csv", "text/csv")
    else:
        st.info("Ingrese la clave para ver el mostrador.")