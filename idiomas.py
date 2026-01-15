import streamlit as st
# Nota: Para que funcione el traductor automático, debes poner deep-translator en tu requirements.txt
try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

def traducir_interfaz(idioma):
    # 1. TU DICCIONARIO BASE (El que tú controlas)
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
            "msg_tecnico": "Su solicitud está siendo procesada por nuestro equipo técnico.",
            "login_tit": "🔐 Acceso Usuarios Registrados",
            "user_id": "Nombre de Usuario / ID de Equipo",
            "pass": "Contraseña",
            "btn_entrar": "INGRESAR AL SISTEMA",
            "btn_ir_registro": "No tengo cuenta, quiero registrarme",
            "reg_tit": "📝 Registro de Nuevo Usuario / Equipo",
            "p1_tit": "Paso 1: Identificación",
            "p2_tit": "Paso 2: Seguridad",
            "p3_tit": "Paso 3: Verificación y Legal",
            "match": "✅ Las claves coinciden",
            "no_match": "⚠️ Las claves NO coinciden",
            "exito_reg": "✨ ¡Usuario creado con éxito! Bienvenidos a Swarco Spain SAT.",
            "redir_login": "🔄 Redirigiendo al inicio de sesión...",
            "error_campos": "❌ Todos los campos marcados con (*) son obligatorios.",
            "consejo": "💡 Los campos se validan automáticamente al cambiar de casilla."
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
            "msg_tecnico": "Your request is being processed by our technical team.",
            "login_tit": "🔐 Registered User Access",
            "user_id": "Username / Team ID",
            "pass": "Password",
            "btn_entrar": "LOG IN TO SYSTEM",
            "btn_ir_registro": "I don't have an account, sign me up",
            "reg_tit": "📝 New User / Team Registration",
            "p1_tit": "Step 1: Identification",
            "p2_tit": "Step 2: Security",
            "p3_tit": "Step 3: Verification & Legal",
            "match": "✅ Passwords match",
            "no_match": "⚠️ Passwords DO NOT match",
            "exito_reg": "✨ User created successfully! Welcome to Swarco Spain SAT.",
            "redir_login": "🔄 Redirecting to login...",
            "error_campos": "❌ All fields marked with (*) are required.",
            "consejo": "💡 Fields are automatically validated when switching boxes."
        }
    }

    # 2. LÓGICA UNIVERSAL
    if idioma in traducciones:
        return traducciones[idioma]
    
    # 3. TRADUCCIÓN AUTOMÁTICA (Si el idioma no es ES o EN)
    elif GoogleTranslator:
        try:
            # Mapeamos nombres de idiomas a códigos ISO
            codigos_iso = {
                "Français": "fr", "Deutsch": "de", "Italiano": "it", 
                "Português": "pt", "Chino": "zh-CN", "Ruso": "ru", "Japonés": "ja"
            }
            target_lang = codigos_iso.get(idioma, "en") # Por defecto inglés si no sabemos el código
            
            # Usamos el Castellano como base para traducir
            base = traducciones["Castellano"]
            translator = GoogleTranslator(source='es', target=target_lang)
            
            # Traducimos todo el diccionario "al vuelo"
            # (Nota: Esto puede tardar 1-2 segundos la primera vez)
            traducido = {k: translator.translate(v) if isinstance(v, str) else v for k, v in base.items()}
            return traducido
        except:
            return traducciones["English"] # Si falla internet, inglés de seguridad
    else:
        return traducciones["English"]


