import streamlit as st
import uuid
import pandas as pd
from datetime import datetime
import os
import sys
import pycountry # Para buscar códigos de países por nombre

sys.path.append(os.path.dirname(__file__))

from estilos import cargar_estilos
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from correo import enviar_email_outlook

# 1. Configuración de página
st.set_page_config(page_title="SWARCO SAT GLOBAL", layout="centered", page_icon="🚥")
cargar_estilos()

# --- HEADER: LOGO | BUSCADOR LIBRE | SEMÁFORO ---
col_logo, col_lang, col_sem = st.columns([1, 2, 0.5])

with col_logo:
    st.image("logo.png", width=120)

with col_lang:
    # EL BUSCADOR QUE PEDISTE: El cliente escribe lo que sea (Ruso, Euskara, etc.)
    idioma_escrito = st.text_input("Escriba su idioma / Type your language", value="Castellano")
    
    # LÓGICA DE MATCH DE BANDERA Y TRADUCCIÓN
    def obtener_recursos_idioma(nombre):
        nombre = nombre.strip().capitalize()
        
        # 1. EXCEPCIONES FIJAS (Lo que no es país ISO)
        if "Eusk" in nombre or "Basque" in nombre:
            return "eu", "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Flag_of_the_Basque_Country.svg/80px-Flag_of_the_Basque_Country.svg.png"
        if "Catal" in nombre:
            return "ca", "https://flagcdn.com/w80/es-ct.png"
        if "Galleg" in nombre or "Galic" in nombre:
            return "gl", "https://flagcdn.com/w80/es-ga.png"
            
        # 2. BÚSQUEDA AUTOMÁTICA MUNDIAL (Rusia, China, Arabia, etc.)
        try:
            # Buscamos el país por el nombre que escribió el cliente
            pais = pycountry.countries.search_fuzzy(nombre)[0]
            cod_pais = pais.alpha_2.lower()
            # Intentamos sacar el idioma de ese país para la traducción
            # Nota: deep-translator usa códigos de 2 letras (en, ru, ar)
            return cod_pais, f"https://flagcdn.com/w80/{cod_pais}.png"
        except:
            # Si no encuentra el país, intentamos match directo de idioma
            match_comun = {"English": "gb", "Ruso": "ru", "Russian": "ru", "Arabe": "sa", "Arabic": "sa", "Chino": "cn", "Chinese": "cn"}
            cod_f = match_comun.get(nombre, "es")
            return cod_f, f"https://flagcdn.com/w80/{cod_f}.png"

    # Ejecutamos el motor de búsqueda
    cod_iso, url_bandera = obtener_recursos_idioma(idioma_escrito)
    
    # Mostramos la bandera resultante
    st.image(url_bandera, width=45)
    
    # Traducimos todo el portal usando el código detectado
    t = traducir_interfaz(cod_iso)

with col_sem:
    st.markdown("<h3 style='text-align:right; margin:0;'>🚥</h3>", unsafe_allow_html=True)

# --- CUERPO DEL PORTAL ---
st.markdown(f"<h1 style='text-align: center; color: #00549F;'>{t['titulo']}</h1>", unsafe_allow_html=True)

# SECCIÓN 1: CLIENTE
st.markdown(f'<div class="section-header">{t["cat1"]}</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    empresa = st.text_input(t['cliente'])
    contacto = st.text_input(t['contacto'])
with c2:
    email_usr = st.text_input(t['email'])
    p_nombres = list(PAISES_DATA.keys())
    pais_sel = st.selectbox(t['pais'], p_nombres, index=p_nombres.index("Spain") if "Spain" in p_nombres else 0)
    tel_usr = f"{PAISES_DATA[pais_sel]} {st.text_input(t['tel'])}"

# SECCIÓN 2: EQUIPO (LA PEGATINA)
st.markdown(f'<div class="section-header">{t["cat2"]}</div>', unsafe_allow_html=True)
st.info(t['pegatina'])
st.image("etiqueta.jpeg", use_container_width=True)

if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = []

with st.container():
    ce1, ce2, ce3 = st.columns([2, 2, 1])
    ns_in = ce1.text_input(t['ns_titulo'])
    ref_in = ce2.text_input("REF / PN")
    urg_in = ce3.selectbox(t['prioridad'], ["Normal", "Alta", "Crítica"])
    
    # SECCIÓN 3: PROBLEMA
    st.markdown(f'<div class="section-header">{t["cat3"]}</div>', unsafe_allow_html=True)
    st.markdown(f"**{t['desc']}**")
    falla_in = st.text_area("", key="falla_area", label_visibility="collapsed")
    
    if st.button(t['btn_agregar'] if 'btn_agregar' in t else "➕ ADD", use_container_width=True):
        if ns_in and falla_in:
            st.session_state.lista_equipos.append({"ns": ns_in, "ref": ref_in, "urgencia": urg_in, "desc": falla_in})
            st.rerun()

if st.session_state.lista_equipos:
    st.table(pd.DataFrame(st.session_state.lista_equipos))

# ENVÍO FINAL (BOTÓN NARANJA)
st.markdown("<br>", unsafe_allow_html=True)
if st.button(t['btn'], type="primary", use_container_width=True):
    if empresa and st.session_state.lista_equipos:
        st.success(t['exito'])
        st.balloons()