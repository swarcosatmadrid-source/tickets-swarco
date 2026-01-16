# =============================================================================
# ARCHIVO: estilos.py
# VERSIÓN: 3.4.0 (Anti-Crash + Logo Online Fallback)
# =============================================================================
import streamlit as st
import os

def cargar_estilos():
    """CSS Corporativo Naranja Swarco #FF5D00"""
    st.markdown("""
        <style>
        .swarco-title {
            color: #FF5D00 !important;
            font-size: 28px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 25px;
        }
        .stButton>button {
            background-color: #FF5D00 !important;
            color: white !important;
            font-weight: bold;
            border-radius: 5px;
            border: none;
            height: 45px;
        }
        /* Corrección para inputs inválidos en rojo */
        div[data-testid="stForm"] .stTextInput input[aria-invalid="true"] {
            border: 2px solid #FF0000 !important;
            background-color: #FFF5F5 !important;
        }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo():
    """Intenta cargar logo local, si falla usa web, si falla usa texto."""
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        ruta_local = "logo/logo.png"
        url_respaldo = "https://www.swarco.com/themes/custom/swarco_theme/logo.svg" 
        # (Ojo: Si prefieres PNG, usa una url de imagen estática fiable)
        
        # 1. INTENTO LOCAL
        if os.path.exists(ruta_local):
            try:
                st.image(ruta_local, use_container_width=True)
                return # Si carga, nos vamos
            except: pass # Si falla, seguimos al plan B

        # 2. INTENTO ONLINE (Para que no se quede sin foto)
        try:
            st.image(url_respaldo, use_container_width=True)
            # Si esto funciona, añadimos un aviso pequeño para que sepas que es la web
            # st.caption("Cargado desde web (no local)") 
            return
        except: pass

        # 3. DIAGNÓSTICO (Solo si todo falló)
        st.markdown("<h2 class='swarco-title'>SWARCO</h2>", unsafe_allow_html=True)
        st.error(f"⚠️ No se pudo cargar el logo.")
        
        # Chivato: Nos dice qué hay realmente en la carpeta
        try:
            if os.path.exists("logo"):
                st.info(f"Archivos en carpeta 'logo': {os.listdir('logo')}")
            else:
                st.error("No existe la carpeta 'logo' en la raíz.")
                st.info(f"Archivos en raíz: {os.listdir('.')}")
        except: pass
