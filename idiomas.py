from deep_translator import GoogleTranslator

def traducir_interfaz(nombre_idioma_usuario):
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
        "fotos": "📸 Fotos / Videos (Máx. 200MB)",
        "btn": "GENERAR TICKET",
        "exito": "¡Ticket enviado con éxito!",
        "msg_tecnico": "En breve un técnico se contactará.",
        "btn_agregar": "➕ AGREGAR EQUIPO AL TICKET"
    }

    # Casos especiales de la casa
    idioma_low = nombre_idioma_usuario.lower()
    if "castellano" in idioma_low or "español" in idioma_low or "es" == idioma_low:
        return textos_base
    if "eusk" in idioma_low: target = "eu"
    elif "catal" in idioma_low: target = "ca"
    elif "galleg" in idioma_low or "galic" in idioma_low: target = "gl"
    else:
        try:
            # MAGIA: Traducimos el nombre del idioma al inglés para sacar el código ISO
            # Esto permite que si pones "Japonés", Google nos diga que el código es "ja"
            cod_detectado = GoogleTranslator(source='auto', target='en').translate(nombre_idioma_usuario)
            # Buscamos el código ISO 639-1
            from deep_translator import constants
            langs_dict = constants.GOOGLE_LANGUAGES_TO_CODES
            target = langs_dict.get(cod_detectado.lower(), "en")
        except:
            target = "en"

    try:
        translator = GoogleTranslator(source='es', target=target)
        return {k: (v if k in ["titulo", "fotos"] else translator.translate(v)) for k, v in textos_base.items()}
    except:
        return textos_base
