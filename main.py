# =============================================================================
# ARCHIVO: main.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 2.2.0 (Universalidad Total Restaurada)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Ruteador principal corregido. Ahora detecta dinámicamente
#              TODOS los idiomas disponibles en el módulo idiomas.
# =============================================================================

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import estilos, usuarios, idiomas, menu_principal, tickets_sat, repuestos, equipos_nuevos

st.set_page_config(page_title="Swarco Portal SAT", page_icon="🚦", layout="centered")
estilos.cargar_estilos()

# 1. GESTIÓN DE ESTADOS
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'pagina_actual' not in st.session_state: st.session_state.pagina_actual = 'login'
if 'codigo_lang' not in st.session_state: st.session_state.codigo_lang = 'es'

# --- SIDEBAR: SELECTOR DINÁMICO DE IDIOMAS (PUNTO CRÍTICO) ---
with st.sidebar:
    st.markdown("### 🌍 Language / Idioma")
    
    # AQUÍ ESTÁ EL CAMBIO: Traemos la lista completa (Chino, Hebreo, etc.)
    df_idiomas = idiomas.obtener_lista_idiomas() # Esta función debe estar en tu idiomas.py
    
    if not df_idiomas.empty:
        # Creamos una lista de nombres de idiomas para el selectbox
        lista_nombres = df_idiomas['nombre_idioma'].tolist()
        
        # Buscamos el índice del idioma actual para que no se resetee
        try:
            current_idx = df_idiomas[df_idiomas['codigo'] == st.session_state.codigo_lang].index[0]
        except:
            current_idx = 0
            
        seleccion = st.selectbox("Seleccione:", lista_nombres, index=int(current_idx))
        
        # Actualizamos el código de idioma global
        st.session_state.codigo_lang = df_idiomas.loc[df_idiomas['nombre_idioma'] == seleccion, 'codigo'].values[0]
    
    st.markdown("---")
    st.caption("Swarco Traffic Spain v2.2")

# 2. CARGA DEL DICCIONARIO TRADUCIDO
t = idiomas.traducir_interfaz(st.session_state.codigo_lang)

# 3. CONEXIÓN A DATOS
def conectar_gsheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_dict = dict(st.secrets["connections"]["gsheets"]["service_account"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        return gspread.authorize(creds).open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    except: return None

conn = conectar_gsheets()

# 4. RUTEADOR (Se asegura de pasar 't' actualizado siempre)
if not st.session_state.autenticado:
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(conn, t)
    else:
        usuarios.gestionar_acceso(conn, t)
else:
    if st.session_state.pagina_actual == 'menu':
        menu_principal.mostrar_menu(conn, t)
    elif st.session_state.pagina_actual == 'sat':
        tickets_sat.interfaz_tickets(conn, t)
    elif st.session_state.pagina_actual == 'repuestos':
        repuestos.mostrar_repuestos(t)
    elif st.session_state.pagina_actual == 'equipos_nuevos':
        equipos_nuevos.mostrar_equipos_nuevos(t)
