import streamlit as st
import streamlit.components.v1 as components
import os
import random
import datetime
import re
from idiomas import traducir_interfaz
from paises import PAISES_DATA
from estilos import aplicar_estilos_swarco
from correo import enviar_email_outlook

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="SAT SWARCO", layout="centered", page_icon="🚦")
aplicar_estilos_swarco() 

# Inicialización de la lista de equipos en la sesión
if 'lista_equipos' not in st.session_state:
    st.session_state.lista_equipos = [{'ref': '', 'ns': '', 'urgencia': 'Normal', 'desc': ''}]

# --- LOGO SUPERIOR ---
if os.path.exists("logo.png"):
    _, col_logo, _ = st.columns([1, 1, 1])
    col_logo.image("logo.png", use_container_width=True)

# 2. SELECTOR DE IDIOMA
opciones_lang = ["Español 🇪🇸", "English 🇬🇧", "Deutsch 🇩🇪", "Français 🇫🇷", "עברית 🇮🇱", "العربية 🇸🇦"]
idioma_sel = st.sidebar.selectbox("🌐 Idioma / Language", opciones_lang)
T = traducir_interfaz(idioma_sel)

# ==========================================
# 3. PANTALLA DE ÉXITO (MENSAJE UNIVERSAL)
# ==========================================
if st.session_state.get('enviado'):
    html_exito = f"""
        <div style="text-align: center; font-family: sans-serif; border: 1px solid #009FE3; padding: 30px; border-radius: 4px; background-color: #ffffff;">
            <div style="font-size: 50px; color: #28a745;">✔</div>
            <h2 style="color: #00549F; margin-top: 10px;">{T['exito']}</h2>
            <p style="font-size: 18px; color: #333;">Su solicitud ha sido registrada correctamente en nuestro sistema.</p>
            
            <div style="background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; display: inline-block; margin: 20px 0; min-width: 320px;">
                <span style="font-size: 13px; color: #666; text-transform: uppercase;">Número de Ticket generado:</span><br>
                <b style="font-size: 24px; color: #00549F;">{st.session_state.last_id}</b>
            </div>

            <p style="font-size: 16px; color: #555; max-width: 500px; margin: 0 auto; line-height: 1.5;">
                Próximamente, uno de nuestros técnicos especializados se pondrá en contacto con usted 
                para dar seguimiento a su caso.
            </p>
            <p style="font-size: 18px; color: #00549F; margin-top: 25px; font-weight: bold;">Gracias por confiar en SWARCO.</p>
        </div>
    """
    components.html(html_exito, height=450)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col_v, col_c = st.columns(2)
    with col_v:
        if st.button("⬅️ Crear otra solicitud", use_container_width=True):
            st.session_state.enviado = False
            st.session_state.lista_equipos = [{'ref': '', 'ns': '', 'urgencia': 'Normal', 'desc': ''}]
            st.rerun()
    with col_c:
        st.markdown('<div class="btn-cerrar">', unsafe_allow_html=True)
        if st.button("❌ Finalizar y salir", use_container_width=True):
            st.markdown("<script>window.parent.window.close();</script>", unsafe_allow_html=True)
            st.stop()
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 4. FORMULARIO DE CREACIÓN DE TICKET
# ==========================================
else:
    st.markdown(f'<h1 style="text-align:center; color:#00549F; margin-top:0;">{T["titulo"]}</h1>', unsafe_allow_html=True)

    # --- ZONA 1: DATOS DEL CLIENTE ---
    st.markdown(f'<div class="section-header">{T["cat1"]}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        empresa = st.text_input(T["cliente"])
        contacto = st.text_input(T["contacto"])
        lista_paises = list(PAISES_DATA.keys())
        pais_sel = st.selectbox(T["pais"], lista_paises, index=lista_paises.index("Spain") if "Spain" in lista_paises else 0)
    with c2:
        proyecto = st.text_input(T["proyecto"])
        email_usr = st.text_input(T["email"])
        # Filtro de teléfono: Solo números y el signo +
        tel_raw = st.text_input(T["tel"], value=f"{PAISES_DATA[pais_sel]} ")
        tel_usr = re.sub(r'[^0-9+]', '', tel_raw)

    # --- ZONA 2: DATOS DEL EQUIPO ---
    st.markdown(f'<div class="section-header">{T["cat2"]}</div>', unsafe_allow_html=True)
    
    if os.path.exists("etiqueta.jpeg"):
        _, col_img, _ = st.columns([1, 2, 1])
        with col_img: st.image("etiqueta.jpeg", caption=T["pegatina"], use_container_width=True)

    for i, equipo in enumerate(st.session_state.lista_equipos):
        st.subheader(f"📍 Equipo #{i+1}")
        ce1, ce2 = st.columns(2)
        st.session_state.lista_equipos[i]['ref'] = ce1.text_input(f"REF #{i+1}", value=equipo['ref'], key=f"ref_{i}")
        st.session_state.lista_equipos[i]['ns'] = ce2.text_input(f"N.S * #{i+1}", value=equipo['ns'], key=f"ns_{i}")
        
        st.session_state.lista_equipos[i]['urgencia'] = st.select_slider(f"Urgencia #{i+1}", options=["Normal", "Alta", "Crítica"], value=equipo['urgencia'], key=f"prio_{i}")
        st.session_state.lista_equipos[i]['desc'] = st.text_area(f"Descripción falla #{i+1} *", value=equipo['desc'], key=f"desc_{i}")
        
        if len(st.session_state.lista_equipos) > 1:
            if st.button(f"🗑️ Quitar Equipo #{i+1}", key=f"del_{i}"):
                st.session_state.lista_equipos.pop(i)
                st.rerun()
        st.markdown("---")

    if st.button("➕ Adicionar otro equipo a este ticket", use_container_width=True):
        st.session_state.lista_equipos.append({'ref': '', 'ns': '', 'urgencia': 'Normal', 'desc': ''})
        st.rerun()

    # --- BOTONES FINALES ---
    st.markdown("<br>", unsafe_allow_html=True)
    col_enviar, col_cerrar = st.columns(2)
    
    with col_enviar:
        st.markdown('<div class="btn-generar">', unsafe_allow_html=True)
        btn_enviar = st.button("🚀 " + T["btn"])
        st.markdown('</div>', unsafe_allow_html=True)

    with col_cerrar:
        st.markdown('<div class="btn-cerrar">', unsafe_allow_html=True)
        btn_cierre = st.button("❌ Cerrar Página")
        st.markdown('</div>', unsafe_allow_html=True)

    if btn_cierre:
        st.markdown("<script>window.parent.window.close();</script>", unsafe_allow_html=True)
        st.stop()

    if btn_enviar:
        # Validación
        faltan_datos = not empresa or not contacto or not email_usr or any(not eq['ns'] or not eq['desc'] for eq in st.session_state.lista_equipos)
        if faltan_datos:
            st.error("❌ Por favor, rellene todos los campos obligatorios (*).")
        else:
            ahora = datetime.datetime.now()
            ticket_id = ahora.strftime("SW-%Y%m%d-%H%M") + f"-{random.randint(10, 99)}"
            
            # Enviar con el nuevo correo.py (incluye tel_usr)
            if enviar_email_outlook(empresa, contacto, proyecto, st.session_state.lista_equipos, email_usr, ticket_id, tel_usr):
                st.session_state.last_id = ticket_id
                st.session_state.enviado = True
                st.rerun()
            else:
                st.error("Error al procesar el ticket. Verifique Outlook.")