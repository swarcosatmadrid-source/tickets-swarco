import streamlit as st
import pandas as pd
import correo 
import pycountry
import phonenumbers

# --- 1. FUNCIÓN DE ADN: OBTENER PAÍSES Y PREFIJOS ---
@st.cache_data
def obtener_paises_mundo():
    paises_dict = {}
    for country in pycountry.countries:
        nombre = country.name
        codigo_iso = country.alpha_2
        prefijo = phonenumbers.country_code_for_region(codigo_iso)
        if prefijo != 0:
            paises_dict[nombre] = f"+{prefijo}"
    return dict(sorted(paises_dict.items()))

PAISES_DATA = obtener_paises_mundo()

# --- 2. INTERFAZ PRINCIPAL ---
def interfaz_tickets(conn, t):
    # Recuperamos datos del técnico logueado
    d_cli = st.session_state.get('datos_cliente', {})
    
    # Sidebar Corporativa
    st.sidebar.image("logo.png", width=150)
    st.sidebar.markdown(f"**{t.get('cliente', 'Empresa')}:**\n{d_cli.get('Empresa', 'N/A')}")
    st.sidebar.markdown(f"**{t.get('user_id', 'Usuario')}:**\n{d_cli.get('Contacto', 'N/A')}")
    
    if st.sidebar.button(t.get('btn_salir', 'SALIR'), use_container_width=True):
        st.session_state.autenticado = False
        st.session_state.lista_equipos = []
        st.rerun()

    # Pantalla de éxito (confirmación de envío)
    if st.session_state.get('ticket_enviado', False):
        st.markdown(f"### ✔️ {t.get('exito', 'Reporte Enviado con Éxito')}")
        st.info("La confirmación ha sido enviada a su correo electrónico y al departamento de soporte técnico.")
        if st.button("Crear nuevo reporte técnico"):
            st.session_state.ticket_enviado = False
            st.session_state.lista_equipos = []
            st.rerun()
        return

    st.title(f"🎫 {t.get('titulo_portal', 'Portal de Reportes')}")

    # --- SECCIÓN 1: DATOS DE LOCALIZACIÓN ---
    with st.container(border=True):
        st.markdown(f"#### 📍 {t.get('cat1', 'Datos del Servicio')}")
        col1, col2 = st.columns(2)
        
        with col1:
            proyecto = st.text_input(t.get("proyecto", "Ubicación / Proyecto") + " *")
        
        with col2:
            # Lógica inteligente de teléfono: aparece el del registro pero es editable
            telf_registrado = str(d_cli.get('Telefono', ''))
            
            c_pre, c_num = st.columns([1.2, 2])
            with c_pre:
                nombres_paises = list(PAISES_DATA.keys())
                # Intentamos pre-seleccionar España por defecto o el país del técnico
                try:
                    idx_def = nombres_paises.index("Spain")
                except:
                    idx_def = 0
                
                pais_sel = st.selectbox("País", nombres_paises, index=idx_def)
                prefijo = PAISES_DATA[pais_sel]
            
            with c_num:
                # Quitamos el prefijo del número guardado para mostrar solo el local
                numero_limpio = telf_registrado.replace(prefijo, "").strip()
                numero_local = st.text_input(t.get("tel", "Teléfono") + " *", value=numero_limpio)
            
            telefono_completo = f"{prefijo} {numero_local}"

    # --- SECCIÓN 2: CARGA DE EQUIPOS ---
    st.markdown(f"#### 🛠️ {t.get('cat2', 'Detalle de Equipos')}")
    with st.container(border=True):
        ce1, ce2 = st.columns([3, 2])
        with ce1:
            ns_equipo = st.text_input(t.get("ns_titulo", "N.S. (Número de Serie)") + " *")
        with ce2:
            referencia = st.text_input("Referencia / Modelo")
        
        falla_desc = st.text_area(t.get("desc_instruccion", "Descripción de la avería") + " *")
        archivos = st.file_uploader(t.get("fotos", "Adjuntar evidencias (Fotos/Videos)"), accept_multiple_files=True)

        if st.button(t.get("btn_agregar", "➕ Añadir Equipo a la lista"), use_container_width=True):
            if ns_equipo and falla_desc:
                if 'lista_equipos' not in st.session_state:
                    st.session_state.lista_equipos = []
                
                st.session_state.lista_equipos.append({
                    "N.S.": ns_equipo,
                    "Referencia": referencia,
                    "Avería": falla_desc,
                    "Evidencias": len(archivos) if archivos else 0
                })
                st.toast(f"Equipo {ns_equipo} añadido correctamente")
                st.rerun()
            else:
                st.error("⚠️ El N.S. y la descripción son campos obligatorios.")

    # --- SECCIÓN 3: RESUMEN Y ENVÍO ---
    if st.session_state.get('lista_equipos'):
        st.markdown("---")
        st.write(f"### 📋 {t.get('resumen', 'Equipos en este reporte')}")
        
        df_resumen = pd.DataFrame(st.session_state.lista_equipos)
        st.table(df_resumen)
        
        if st.button(t.get("btn_generar", "🚀 ENVIAR REPORTE FINAL"), type="primary", use_container_width=True):
            if not proyecto or not numero_local:
                st.error("⚠️ Por favor, rellene la ubicación y el teléfono de contacto.")
            else:
                with st.spinner('Enviando reporte oficial...'):
                    # Llamada al mensajero
                    exito = correo.enviar_ticket_soporte(
                        datos_cliente=d_cli,
                        proyecto=proyecto,
                        telefono=telefono_completo,
                        lista_equipos=st.session_state.lista_equipos,
                        idioma_t=t
                    )
                
                if exito:
                    st.session_state.ticket_enviado = True
                    st.rerun()
                else:
                    st.error("❌ Error al enviar el correo. Contacte con administración.")
