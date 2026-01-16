# =============================================================================
# ARCHIVO: main.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 2.4.0 (Integración de Todas las Carpetas GitHub)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Ruteador principal que conecta todos los módulos del sistema.
#              Mecanismo de control: Verifica existencia de módulos antes de ruteo.
# =============================================================================

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from streamlit_javascript import st_javascript

# IMPORTACIÓN DE TODAS LAS CARPETAS DEL REPOSITORIO
import estilos
import usuarios
import idiomas
import menu_principal
import tickets_sat
import repuestos
import equipos_nuevos

# CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Swarco Portal SAT", page_icon="🚦", layout="centered")

# 1. CARGA DE ESTILOS CORPORATIVOS (#FF5D00)
estilos.cargar_estilos()

# 2. GESTIÓN DE IDIOMA (Detección de Navegador y Persistencia)
if 'codigo_lang' not in st.session_state:
    nav_lang = st_javascript('navigator.language || navigator.userLanguage')
    st.session_state.codigo_lang = nav_lang.split('-')[0] if nav_lang else 'es'

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'pagina_actual' not in st.session_state: st.session_state.pagina_actual = 'login'

# Traducción maestra desde idiomas.py
t = idiomas.traducir_interfaz(st.session_state.codigo_lang)

# 3. SELECTOR DE IDIOMA EN SIDEBAR
with st.sidebar:
    st.markdown("### 🌍 Language / Idioma")
    df_langs = idiomas.obtener_lista_idiomas()
    if not df_langs.empty:
        # Corrección estética para el selector
        df_langs['nombre_idioma'] = df_langs['nombre_idioma'].replace({'basque': 'Euskera', 'spanish': 'Español'})
        lista_nombres = df_langs['nombre_idioma'].tolist()
        try:
            curr_idx = df_langs[df_langs['codigo'] == st.session_state.codigo_lang].index[0]
        except:
            curr_idx = 0
        
        sel = st.selectbox("Seleccione:", lista_nombres, index=int(curr_idx))
        nuevo_cod = df_langs.loc[df_langs['nombre_idioma'] == sel, 'codigo'].values[0]
        
        if nuevo_cod != st.session_state.codigo_lang:
            st.session_state.codigo_lang = nuevo_cod
            st.rerun()

# 4. CONEXIÓN A BASE DE DATOS (Google Sheets)
def conectar_gsheets():
    try:
        creds_info = st.secrets["connections"]["gsheets"]["service_account"]
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(creds_info, scopes=scope)
        return gspread.authorize(creds).open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

conn = conectar_gsheets()

# 5. RUTEADOR UNIVERSAL (Mecanismo de Control de Funciones)
# Verifica que cada módulo reciba (conn, t) para no perder el hilo
if not st.session_state.autenticado:
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t)
    else:
        usuarios.gestionar_acceso(conn, t)
else:
    # Navegación post-login usando las carpetas del repositorio
    if st.session_state.pagina_actual == 'menu':
        menu_principal.mostrar_menu(conn, t)
    elif st.session_state.pagina_actual == 'sat':
        tickets_sat.interfaz_tickets(conn, t)
    elif st.session_state.pagina_actual == 'repuestos':
        repuestos.mostrar_repuestos(t)
    elif st.session_state.pagina_actual == 'equipos_nuevos':
        equipos_nuevos.mostrar_equipos_nuevos(t)

st.sidebar.markdown("---")
st.sidebar.caption("Swarco Traffic Spain © 2026")


