def traducir_interfaz(idioma):
    # Diccionario de traducciones
    traducciones = {
        "Castellano": {
            "titulo_portal": "Portal de Reporte Técnico SAT",
            "instruccion_final": "¿Cómo enviar su reporte?",
            "cat1": "1. IDENTIFICACIÓN DEL CLIENTE",
            "cliente": "Empresa / Entidad",
            "contacto": "Persona de Contacto",
            "proyecto": "Proyecto / Ubicación",
            "email": "Correo Electrónico",
            "pais": "País",
            "tel": "Teléfono de contacto",
            "error_tel": "Por favor, introduzca solo números",
            "cat2": "2. IDENTIFICACIÓN DEL EQUIPO",
            "pegatina": "Localice la pegatina plateada en el equipo",
            "ns_titulo": "N.S. (Número de Serie)",
            "cat3": "3. DESCRIPCIÓN DEL PROBLEMA",
            "urg_titulo": "Prioridad de la incidencia",
            "urg_instruccion": "Deslice para indicar la prioridad",
            "u1": "Mínima", "u2": "Baja", "u3": "Normal", 
            "u4": "Alta", "u5": "Muy Alta", "u6": "CRÍTICA",
            "desc_instruccion": "Descripción detallada del fallo",
            "desc_placeholder": "Describa qué sucede con el equipo...",
            "fotos": "Adjuntar fotos o vídeos (Máx. 200MB)",
            "btn_agregar": "Añadir otro equipo a la lista",
            "btn_generar": "GENERAR TICKET",
            "btn_salir": "SALIR",
            "exito": "Ticket generado con éxito. Revise su correo.",
            "salir_aviso": "Asegúrese de haber enviado el ticket antes de salir.",
            "msg_tecnico": "Su solicitud está siendo procesada por nuestro equipo técnico."
        },
        "English": {
            "titulo_portal": "SAT Technical Reporting Portal",
            "instruccion_final": "How to submit your report?",
            "cat1": "1. CUSTOMER IDENTIFICATION",
            "cliente": "Company / Entity",
            "contacto": "Contact Person",
            "proyecto": "Project / Location",
            "email": "Email Address",
            "pais": "Country",
            "tel": "Contact Phone",
            "error_tel": "Please enter numbers only",
            "cat2": "2. EQUIPMENT IDENTIFICATION",
            "pegatina": "Locate the silver sticker on the equipment",
            "ns_titulo": "S.N. (Serial Number)",
            "cat3": "3. PROBLEM DESCRIPTION",
            "urg_titulo": "Incident Priority",
            "urg_instruccion": "Slide to indicate priority",
            "u1": "Minimal", "u2": "Low", "u3": "Normal", 
            "u4": "High", "u5": "Very High", "u6": "CRITICAL",
            "desc_instruccion": "Detailed description of the fault",
            "desc_placeholder": "Describe what is happening with the equipment...",
            "fotos": "Attach photos or videos (Max. 200MB)",
            "btn_agregar": "Add another equipment to the list",
            "btn_generar": "GENERATE TICKET",
            "btn_salir": "EXIT",
            "exito": "Ticket generated successfully. Check your email.",
            "salir_aviso": "Make sure you have sent the ticket before exiting.",
            "msg_tecnico": "Your request is being processed by our technical team."
        }
    }

    # Lógica para detectar idiomas fuera de la lista (Hebreo, Japonés, etc.)
    if idioma in traducciones:
        return traducciones[idioma]
    else:
        # Si escribe algo raro, devolvemos Inglés por defecto para que no explote
        return traducciones["English"]


