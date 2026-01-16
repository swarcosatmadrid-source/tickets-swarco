# =============================================================================
# ARCHIVO: main.py
# VERSIÓN: 2.3.0 (Detección de Navegador y Estabilidad de Idioma)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# =============================================================================

import streamlit as st
from streamlit_javascript import st_javascript
import estilos, usuarios, idiomas, menu_principal, tickets_sat, repuestos, equipos_nuevos

st.set_page_config(page_title="Swarco Portal SAT", page_icon="🚦", layout="centered")
estilos.cargar_estilos()

# --- 1. DETECCIÓN AUTOMÁTICA DEL IDIOMA DEL NAVEGADOR ---
if 'codigo_lang' not in st.session_state:
    # Lee el idioma del navegador (ej: 'es-ES' -> 'es')
    nav_lang = st_javascript('navigator.language || navigator.userLanguage')
    if nav_lang:
        st.session_state.codigo_lang = nav_lang.split('-')[0]
    else:
        st.session_state.codigo_lang = 'es'

if 'autenticado' not in st.session_state: st.session_state.autenticado = False
if 'pagina_actual' not in st.session_state: st.session_state.pagina_actual = 'login'

# --- 2. SELECTOR DE IDIOMA ESTABLE ---
with st.sidebar:
    st.markdown("### 🌍 Language / Idioma")
    df_idiomas = idiomas.obtener_lista_idiomas()
    
    if not df_idiomas.empty:
        # Corrección: Cambiar 'Basque' por 'Euskera' en la lista
        df_idiomas['nombre_idioma'] = df_idiomas['nombre_idioma'].replace({'basque': 'Euskera', 'spanish': 'Español'})
        
        lista_nombres = df_idiomas['nombre_idioma'].tolist()
        lista_codigos = df_idiomas['codigo'].tolist()

        # Encontrar el índice actual de forma segura
        try:
            current_idx = lista_codigos.index(st.session_state.codigo_lang)
        except:
            current_idx = 0

        seleccion = st.selectbox("Seleccione:", lista_nombres, index=current_idx)
        
        # Actualizar solo si el usuario cambia la selección
        nuevo_codigo = df_idiomas.loc[df_idiomas['nombre_idioma'] == seleccion, 'codigo'].values[0]
        if nuevo_codigo != st.session_state.codigo_lang:
            st.session_state.codigo_lang = nuevo_codigo
            st.rerun()

# --- 3. PROCESO DE TRADUCCIÓN ---
t = idiomas.traducir_interfaz(st.session_state.codigo_lang)

# --- 4. RUTEADOR ---
if not st.session_state.autenticado:
    if st.session_state.get('mostrar_registro', False):
        usuarios.interfaz_registro_legal(None, t) # conn se define luego
    else:
        usuarios.gestionar_acceso(None, t)
else:
    # Lógica de navegación (Menu, SAT, etc.)
    if st.session_state.pagina_actual == 'menu':
        menu_principal.mostrar_menu(None, t)
    # ... resto del ruteador igual ...

