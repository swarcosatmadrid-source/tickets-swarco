import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys

# Asegurar ruta de archivos locales
sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SWARCO SAT GLOBAL", layout="centered", page_icon="🚥")
cargar_estilos()

# Conexión a base de datos (GSheets)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except:
    pass

# --- HEADER: LOGO | BUSCADOR MUNDIAL | SEMÁFORO ---
col_logo, col_lang, col_sem = st.columns([1.2, 1.5, 0.5])

with col_logo:
    st.image("logo.png", width=130)

with col_lang:
    # Mapeo de idiomas del mundo (Códigos ISO)
    mundo_idiomas = {
        "Castellano 🇪🇸": "es",
        "Euskara (Ikurriña)": "eu",
        "Català (Senyera)": "ca",
        "English 🇬🇧": "en",
        "Arabic (العربية) 🇸🇦": "ar",
        "Deutsch 🇩🇪": "de",
        "Français 🇫🇷": "fr",
        "Japonés (日本語) 🇯🇵": "ja",
        "Hebreo (עברית) 🇮🇱": "iw",
        "Chino (中文) 🇨🇳": "zh-CN"
    }
    
    # Selector que permite BUSCAR escribiendo
    opcion_elegida = st.selectbox("Seleccione Idioma / Language", list(mundo_idiomas.keys()), label_visibility="collapsed")
    codigo_iso = mundo_idiomas[opcion_elegida]
    
    # LÓGICA DE IMAGEN REAL PARA BANDERAS (Para que no fallen como los emojis)
    if "Euskara" in opcion_elegida:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Flag_of_the_Basque_Country.svg/320px-Flag_of_the_Basque_Country.svg.png", width=40)
    elif "Castellano" in opcion_elegida:
        st.image("https://flagcdn.com/w80/es.png", width=40)
    elif "Català" in opcion_elegida:
        st.image("https://flagcdn.com/w80/es-ct.png", width=40)
    else:
        # Para el resto del mundo usamos flagcdn por código ISO
        st.image(f"https://flagcdn.com/w80/{codigo_iso if codigo_iso != 'en' else 'gb'}.png", width=40)

    # LLAMADA AL SEGMENTO DE IDIOMAS (Segmentación real)
    t = traducir_interfaz(codigo_iso)

with col_sem:
    st.markdown("<h2 style='text-align:right; margin:0;'>🚥</h2>", unsafe_allow_html=True)

# Título Principal centrado (Azul Swarco)
st.markdown(f"<h1 style='text-align: center; color: #00549F; margin-top: 0;'>{t['titulo']}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #666;'>{t['sub']}</p>", unsafe_allow_html=True)

# --- CATEGORÍA 1: IDENTIFICACIÓN DEL CLIENTE ---
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
    proyecto = st.text_input(t['proyecto'])
with c2:
    email_usr = st.text_input(t['email'])
    p_nombres = list(PAISES_DATA.keys())
    idx_sp = p_nombres.index("Spain") if "Spain" in p_nombres else 0
    pais_sel = st.selectbox(t['pais'], p_nombres, index=idx_sp)
    prefijo = PAISES_DATA[pais_sel]
    tel_raw = st.text_input(f"{t['tel']} ({prefijo})")
    tel_usr = f"{prefijo} {tel_raw}"

# --- CATEGORÍA 2: IDENTIFICACIÓN DEL EQUIPO ---
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(f"💡 {t['pegatina']}")
st.image("etiqueta.jpeg", use_container_width=True)

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

with st.container():
    ce1, ce2, ce3 = st.columns([2, 2, 1.2])
    ns_in = ce1.text_input(t['ns_titulo'])
    ref_in = ce2.text_input("REF / PN")
    urg_in = ce3.selectbox(t['prioridad'], ["Normal", "Alta", "Crítica"])
    
    # --- CATEGORÍA 3: DESCRIPCIÓN DEL PROBLEMA (Orden corregido) ---
    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**{t['desc']}**")
    falla_in = st.text_area("", key="falla_area", label_visibility="collapsed")
    
    st.markdown(f"**{t['fotos']}**")
    st.file_uploader("", accept_multiple_files=True, type=['png', 'jpg', 'jpeg', 'mp4'], label_visibility="collapsed")

    if st.button(t['btn_agregar'] if 'btn_agregar' in t else "➕ AGREGAR AL TICKET", use_container_width=True):
        if ns_in and falla_in:
            st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_in, "desc": falla_in})
            st.rerun()

# Tabla de equipos añadidos
if st.session_state.lista_equipos:
    st.markdown("---")
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# --- BOTÓN DE ENVÍO FINAL (Naranja Corporativo) ---
st.markdown("<br>", unsafe_allow_html=True)
if st.button(t['btn'], type="primary", use_container_width=True):
    if not empresa or not email_usr or not st.session_state.lista_equipos:
        st.error("Rellene los campos obligatorios (*) y agregue al menos un equipo.")
    else:
        t_id = f"SAT-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:4].upper()}"
        if enviar_email_outlook(empresa, contacto, proyecto, st.session_state.lista_equipos, email_usr, t_id, tel_usr):
            try:
                # Guardar en base de datos
                fila = pd.DataFrame([{"ID": t_id, "Fecha": datetime.now().strftime("%d/%m/%Y"), "Empresa": empresa, "Estado": "Pendiente"}])
                df_ex = conn.read(worksheet="Sheet1")
                conn.update(worksheet="Sheet1", data=pd.concat([df_ex, fila], ignore_index=True))
            except:
                pass
            st.success(t['exito'])
            st.info(t['msg_tecnico'])
            st.balloons()
            st.session_state.lista_equipos = []

# --- FOOTER CORPORATIVO ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #999; font-size: 12px; padding-bottom: 30px;'>
        <p>© 2024 SWARCO TRAFFIC SPAIN | The Better Way. Every Day.</p>
        <p><a href='https://www.swarco.com/es/aviso-legal' target='_blank' style='color: #F29400;'>Aviso Legal</a> | <a href='https://www.swarco.com/es/privacidad' target='_blank' style='color: #F29400;'>Privacidad</a></p>
    </div>
""", unsafe_allow_html=True)