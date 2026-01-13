# paises.py
import phonenumbers
from phonenumbers import region_code_for_country_code
import pycountry

def obtener_paises_mundo():
    # Diccionario para guardar Nombre: Prefijo
    paises_dict = {}
    
    # Recorremos todos los países del mundo conocidos por la norma ISO
    for country in pycountry.countries:
        # Obtenemos el nombre del país y su código (ej: 'VE' para Venezuela)
        nombre = country.name
        codigo_iso = country.alpha_2
        
        # Buscamos el prefijo telefónico para ese código ISO
        # phonenumbers nos da el prefijo (ej: 58)
        prefijo = phonenumbers.country_code_for_region(codigo_iso)
        
        if prefijo != 0:
            paises_dict[nombre] = f"+{prefijo}"
            
    # Retornamos la lista ordenada alfabéticamente
    return dict(sorted(paises_dict.items()))

# Generamos la data una sola vez
PAISES_DATA = obtener_paises_mundo()