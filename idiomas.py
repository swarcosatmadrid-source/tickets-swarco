from deep_translator import GoogleTranslator

def traducir_interfaz(idioma_sel):
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
        "ns_titulo": "N.S * (Obligatorio)",
        "prioridad": "Urgencia",
        "desc": "Detalle de la Avería *",
        "fotos": "📸 Fotos / Videos (Máx. 3)",
        "btn": "GENERAR TICKET",
        "exito": "¡Ticket enviado con éxito!",
        "msg_tecnico": "En breve un técnico se contactará. Recibirá un resumen en su correo.",
        "btn_agregar": "➕ AGREGAR AL TICKET"
    }

    mapeo = {
        "Castellano": "es", "English": "en", "Deutsch": "de", 
        "Français": "fr", "Català": "ca", "Euskara": "eu", "Galego": "gl"
    }
    
    target = mapeo.get(idioma_sel, "es")
    if target == "es": return textos_base

    try:
        translator = GoogleTranslator(source='es', target=target)
        return {k: (v if k in ["titulo", "fotos"] else translator.translate(v)) for k, v in textos_base.items()}
    except:
        return textos_base