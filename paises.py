# =============================================================================
# ARCHIVO: paises.py
# DESCRIPCIÓN: Generador dinámico de prefijos (pycountry + phonenumbers)
# =============================================================================
import pycountry
import phonenumbers
from phonenumbers import geocoder

# --- TU CÓDIGO ORIGINAL (INTACTO) ---
def obtener_paises_mundo():
    paises_dict = {}
    for country in pycountry.countries:
        try:
            nombre = country.name
            codigo_iso = country.alpha_2
            # Obtenemos el prefijo usando phonenumbers
            prefijo = phonenumbers.country_code_for_region(codigo_iso)
            
            if prefijo != 0:
                # Guardamos formato: "+34"
                paises_dict[nombre] = f"+{prefijo}"
        except Exception:
            continue
            
    # Ordenamos alfabéticamente
    return dict(sorted(paises_dict.items()))

# Generamos la data una sola vez al cargar el archivo
PAISES_DATA = obtener_paises_mundo()

# --- EL PUENTE QUE FALTA (AGREGA ESTO AL FINAL) ---
# Estas son las funciones que usuarios.py está intentando llamar

def obtener_lista_nombres():
    """Devuelve la lista de nombres para el selectbox"""
    return list(PAISES_DATA.keys())

def obtener_prefijo(nombre_pais):
    """Devuelve el prefijo (+34) dado el nombre"""
    return PAISES_DATA.get(nombre_pais, "")
