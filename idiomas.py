from deep_translator import GoogleTranslator
from deep_translator import GoogleTranslator

def traducir_interfaz(idioma_destino_codigo):
    # Nuestra base de datos de textos en Español (La Fuente)
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

    # Si es español, no gastamos recursos traduciendo
    if idioma_destino_codigo == "es":
        return textos_base

    try:
        # Traducimos todo el diccionario al idioma que el usuario eligió
        translator = GoogleTranslator(source='es', target=idioma_destino_codigo)
        textos_traducidos = {}
        for clave, valor in textos_base.items():
            if clave in ["titulo", "fotos"]: # Mantener marca e iconos
                textos_traducidos[clave] = valor
            else:
                textos_traducidos[clave] = translator.translate(valor)
        return textos_traducidos
    except Exception:
        return textos_base