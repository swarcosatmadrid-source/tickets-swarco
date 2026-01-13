from deep_translator import GoogleTranslator

def traducir_interfaz(idioma_usuario):
    # Diccionario Maestro con todas las etiquetas del portal
    textos_base = {
        "titulo": "SAT SWARCO TRAFFIC SPAIN",
        "sub": "Portal de Soporte Técnico",
        "cat1": "IDENTIFICACIÓN DEL CLIENTE",
        "cat2": "IDENTIFICACIÓN DEL EQUIPO",
        "cat3": "DESCRIPCIÓN DEL PROBLEMA",
        "cliente": "Empresa *",
        "contacto": "Persona de Contacto *",
        "proyecto": "Proyecto / Ubicación (Opcional)",
        "email": "Email *",
        "pais": "País *",
        "tel": "Teléfono *",
        "pegatina": "Localice la REF y N.S en la etiqueta del equipo:",
        "ns_titulo": "N.S * (Obligatorio)",
        "urg_titulo": "Nivel de Urgencia / Priority Level",
        "urg_instruccion": "Deslice para indicar la prioridad de la incidencia",
        "desc_instruccion": "Por favor, describa de forma concisa la naturaleza de la incidencia y sus síntomas observados.",
        "desc_placeholder": "Indique brevemente el fallo técnico detectado...",
        "fotos": "Multimedia (Límite total: 200MB)",
        "btn_agregar": "AGREGAR EQUIPO AL TICKET",
        "btn_generar": "GENERAR TICKET",
        "btn_salir": "SALIR",
        "exito": "¡Ticket enviado con éxito!",
        "msg_tecnico": "En breve un técnico se contactará.",
        "error_tel": "Error: Solo se permiten números. Las letras serán descartadas.",
        "salir_aviso": "Sesión finalizada. Ya puede cerrar la pestaña.",
        # Niveles de urgencia
        "u1": "Mínima", "u2": "Baja", "u3": "Normal", "u4": "Alta", "u5": "Muy Alta", "u6": "CRÍTICA"
    }

    idioma_low = idioma_usuario.lower()
    # Si es español, devolvemos el base de una vez
    if any(x in idioma_low for x in ["castellano", "español", "es"]):
        return textos_base
    
    # Mapeos forzados para idiomas regionales
    if "eusk" in idioma_low: target = "eu"
    elif "catal" in idioma_low: target = "ca"
    elif "gall" in idioma_low: target = "gl"
    else:
        try:
            # Traducimos lo que el usuario escribió para sacar el código ISO (ej: "Japonés" -> "ja")
            detectado = GoogleTranslator(source='auto', target='en').translate(idioma_usuario)
            from deep_translator import constants
            target = constants.GOOGLE_LANGUAGES_TO_CODES.get(detectado.lower(), "en")
        except:
            target = "en"

    try:
        translator = GoogleTranslator(source='es', target=target)
        # Traducimos cada valor del diccionario
        return {k: (v if k == "titulo" else translator.translate(v)) for k, v in textos_base.items()}
    except:
        return textos_base

