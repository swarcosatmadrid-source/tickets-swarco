import pycountry
import phonenumbers

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