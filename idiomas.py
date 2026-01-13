# idiomas.py
from deep_translator import GoogleTranslator

def traducir_interfaz(idioma_destino):
    # Nuestra base de datos de textos en Español
    textos_base = {
        "titulo": "SAT SWARCO TRAFFIC SPAIN",
        "sub": "Portal de Soporte Técnico",
        "cat1": "IDENTIFICACIÓN DEL CLIENTE",
        "cat2": "IDENTIFICACIÓN DEL EQUIPO",
        "cat3": "DESCRIPCIÓN DEL PROBLEMA",
        "cliente": "Empresa *",
        "contacto": "Persona de Contacto *",
        "proyecto": "Proyecto (Opcional)",
        "email": "Email *",
        "pais": "País *",
        "tel": "Teléfono *",
        "pegatina": "Localice la REF y N.S en la etiqueta del equipo:",
        "serie_titulo": "Serie",
        "ns_titulo": "N.S * (Obligatorio)",
        "prioridad": "Urgencia",
        "desc": "Detalle de la Avería *",
        "fotos": "📸 Fotos (Máx. 3)",
        "btn": "GENERAR TICKET",
        "exito": "¡Ticket enviado con éxito!",
        "msg_tecnico": "En breve un técnico se contactará. Recibirá un resumen en su correo."
    }
    
    if "Español" in idioma_destino:
        return textos_base
    
    mapeo_favoritos = {
        "English 🇬🇧": "en", 
        "Deutsch 🇩🇪": "de", 
        "Français 🇫🇷": "fr", 
        "Català 🚩": "ca", 
        "Euskara 🟢": "eu", 
        "Galego ⚪": "gl",
        "Mandarin 🇨🇳": "zh-CN", 
        "עברית 🇮🇱": "iw", 
        "العربية 🇸🇦": "ar"
    }
    
    target_lang = mapeo_favoritos.get(idioma_destino, idioma_destino)

    try:
        translator = GoogleTranslator(source='es', target=target_lang)
        textos_traducidos = {}
        for clave, valor in textos_base.items():
            textos_traducidos[clave] = translator.translate(valor)
        return textos_traducidos
    except Exception as e:
        return textos_base