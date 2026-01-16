# =============================================================================
# ARCHIVO: paises.py
# VERSIÓN: Con traducción manual EN -> ES para evitar "Spain"
# =============================================================================
import pycountry
import phonenumbers

# Diccionario de traducción manual para los nombres más comunes
# (pycountry viene en inglés por defecto, esto lo fuerza a español)
TRADUCCIONES = {
    "Spain": "España",
    "Germany": "Alemania",
    "United Kingdom": "Reino Unido",
    "France": "Francia",
    "Italy": "Italia",
    "Portugal": "Portugal",
    "United States": "Estados Unidos",
    "Venezuela": "Venezuela",
    "Colombia": "Colombia",
    "Mexico": "México",
    "Argentina": "Argentina",
    "Chile": "Chile",
    "Peru": "Perú",
    "Ecuador": "Ecuador",
    "Brazil": "Brasil",
    "Russian Federation": "Rusia",
    "China": "China",
    "Japan": "Japón",
    "Switzerland": "Suiza",
    "Austria": "Austria",
    "Belgium": "Bélgica",
    "Netherlands": "Países Bajos",
    "Sweden": "Suecia",
    "Norway": "Noruega",
    "Denmark": "Dinamarca",
    "Poland": "Polonia",
    "Israel": "Israel",
    "Ireland": "Irlanda"
}

def obtener_paises_mundo():
    paises_dict = {}
    for country in pycountry.countries:
        try:
            nombre_original = country.name
            codigo_iso = country.alpha_2
            
            # Obtenemos el prefijo
            prefijo = phonenumbers.country_code_for_region(codigo_iso)
            
            if prefijo != 0:
                # TRADUCCIÓN: Si el nombre está en nuestra lista, lo cambiamos a Español
                # Si no, se queda con el nombre original (fallback)
                nombre_final = TRADUCCIONES.get(nombre_original, nombre_original)
                
                # Guardamos formato: "+34"
                paises_dict[nombre_final] = f"+{prefijo}"
        except Exception:
            continue
            
    # Ordenamos alfabéticamente según el nombre en ESPAÑOL
    return dict(sorted(paises_dict.items()))

# Generamos la data
PAISES_DATA = obtener_paises_mundo()

# --- FUNCIONES CONECTORAS PARA USUARIOS.PY ---
def obtener_lista_nombres():
    return list(PAISES_DATA.keys())

def obtener_prefijo(nombre_pais):
    return PAISES_DATA.get(nombre_pais, "")
