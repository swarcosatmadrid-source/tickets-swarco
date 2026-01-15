import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
from streamlit_gsheets import GSheetsConnection
from idiomas import traducir_interfaz
import usuarios

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="SWARCO SAT | Portal", layout="centered", page_icon="🚥")

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'mostrar_registro' not in st.session_state: st.session_state.mostrar_registro = False
if 'idioma' not in st.session_state: st.session_state.idioma = "Castellano"
if 'lista_equipos' not in st.session_state: st.session_state.lista_equipos = []
if 'ticket_enviado' not in st.session_state: st.session_state.ticket_enviado = False

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 2. SELECTOR DE IDIOMA SEGURO ---
if not st.session_state.autenticado:
    st.sidebar.markdown("### 🌐 Language / Idioma")
    idiomas_soporte = ["Castellano", "English", "Français", "Deutsch"]
    
    # Si el idioma actual no está en la lista, forzamos Castellano
    idx_sel = idiomas_soporte.index(st.session_state.idioma) if st.session_state.idioma in idiomas_soporte else 0
    
    st.session_state.idioma = st.sidebar.selectbox(
        "Select Language:", 
        idiomas_soporte,
        index=idx_sel
    )

# --- 3. TRADUCCIÓN ROBUSTA ---
# Si tu función traducir_interfaz no tiene el idioma, ella devolverá English por defecto
t = traducir_interfaz(st.session_state.idioma)

# --- 4. PÁGINA DE ACCESO ---
if not st.session_state.autenticado:
    # LOGO CENTRADO
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2: 
        st.image("logo.png", use_container_width=True)

    if st.session_state.mostrar_registro:
        usuarios.interfaz_registro_legal(conn)
        if st.button("⬅️ " + ("Volver" if st.session_state.idioma == "Castellano" else "Back")):
            st.session_state.mostrar_registro = False
            st.rerun()
    else:
        st.markdown(f"<h2 style='text-align: center;'>{t.get('login_tit', 'Acceso')}</h2>", unsafe_allow_html=True)
        if usuarios.gestionar_acceso(conn):
            st.rerun()
        
        st.markdown("---")
        if st.button(t.get("btn_ir_registro", "Registro"), use_container_width=True):
            st.session_state.mostrar_registro = True
            st.rerun()
    st.stop()

# --- 5. PORTAL POST-LOGIN ---
d_cli = st.session_state.get('datos_cliente', {})
st.sidebar.image("logo.png", width=150)
st.sidebar.success(f"{t.get('contacto', 'User')}: {d_cli.get('Contacto')}")

if st.sidebar.button(t.get("btn_salir", "EXIT")):
    st.session_state.autenticado = False
    st.rerun()

st.title(f"🎫 {t.get('titulo_portal', 'Portal SAT')}")

if st.session_state.ticket_enviado:
    st.success(t.get("exito", "✅ OK"))
    if st.button("Nuevo ticket"):
        st.session_state.ticket_enviado = False
        st.session_state.lista_equipos = []
        st.rerun()
    st.stop()

# Formulario simplificado para probar
with st.expander(t.get("cat1", "Datos"), expanded=True):
    proyecto = st.text_input(t.get("proyecto", "Ubicación") + " *")
    telefono = st.text_input(t.get("tel", "Teléfono") + " *")

st.subheader(f"🛠️ {t.get('cat2', 'Equipos')}")
ns = st.text_input(t.get("ns_titulo", "N.S.") + " *")
falla = st.text_area(t.get("desc_instruccion", "Fallo") + " *")
archivos = st.file_uploader(t.get("fotos", "Adjuntos"), accept_multiple_files=True)

if st.button(t.get("btn_agregar", "Añadir")):
    if ns and falla:
        st.session_state.lista_equipos.append({"N.S.": ns, "Fallo": falla})
        st.rerun()

if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))
    if st.button(t.get("btn_generar", "ENVIAR"), type="primary", use_container_width=True):
        st.session_state.ticket_enviado = True
        st.rerun()

