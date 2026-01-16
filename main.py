import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from streamlit_javascript import st_javascript

# === IMPORTACIONES SEGURAS ===
try:
    import estilos
    import idiomas
    import usuarios
    import menu_principal
    import correo # Vital para el registro
except ImportError as e:
    st.error(f"❌ Error Crítico: Falta el archivo {e.name}.py")
    st.stop()

# === CONFIGURACIÓN ===
st.set_page_config(page_title="Swarco Portal SAT", page_icon="🚦", layout="centered")

# === ESTADO INICIAL ===
if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'pagina_actual' not in st.session_state: st.session_state.pagina_actual = 'login'
if 'codigo_lang' not in st.session_state:
    # Detección automática del navegador
    js_lang = st_javascript('navigator.language')
    st.session_state.codigo_lang = js_lang.split('-')[0] if js_lang else 'es'

# === CARGA DE RECURSOS ===
estilos.cargar_estilos()
t = idiomas.traducir_interfaz(st.session_state.codigo_lang)

# === CONEXIÓN BD ===
@st.cache_resource
def conectar_db():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["connections"]["gsheets"]["service_account"], scopes=scope)
        client = gspread.authorize(creds)
        return client.open_by_url(st.secrets["connections"]["gsheets"]["spreadsheet"])
    except: return None

conn = conectar_db()

# === SELECTOR DE IDIOMA (SIDEBAR) ===
with st.sidebar:
    st.write("🌐 Language")
    langs = idiomas.obtener_lista_idiomas()
    idx = 0
    if st.session_state.codigo_lang in langs['codigo'].values:
        idx = int(langs[langs['codigo'] == st.session_state.codigo_lang].index[0])
    sel = st.selectbox("Idioma", langs['nombre'], index=idx, label_visibility="collapsed")
    new_code = langs[langs['nombre'] == sel]['codigo'].values[0]
    if new_code != st.session_state.codigo_lang:
        st.session_state.codigo_lang = new_code
        st.rerun()

# === RUTEADOR PRINCIPAL ===
if not conn:
    st.error("🚨 Error: No hay conexión con Google Sheets.")
else:
    if not st.session_state.autenticado:
        if st.session_state.get('mostrar_registro', False):
            usuarios.interfaz_registro_legal(conn, t)
        else:
            usuarios.gestionar_acceso(conn, t)
    else:
        if st.session_state.pagina_actual == 'menu':
            menu_principal.mostrar_menu(conn, t)
        # Aquí se añaden el resto de módulos (SAT, Repuestos) cuando lleguemos a ese paso

