import streamlit as st
# Intentamos importar el traductor automático
try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

def traducir_interfaz(codigo_iso):
    """
    Esta función recibe un código de dos letras (es, en, sk, he...)
    y devuelve el diccionario de palabras para toda la página.
    """
    
    # 1. TU ADN: Traducciones manuales (Las que quedan perfectas)
    traducciones_maestras = {
        "es": {
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
            "consejo": "💡 Los campos se validan automáticamente al cambiar de casilla.",
            "titulo_portal": "Portal de Reporte Técnico SAT",
            "cat1": "Datos del Servicio",
            "cat2": "Detalle de Equipos",
            "proyecto": "Proyecto / Ubicación",
            "cliente": "Empresa",
            "email": "Correo Electrónico",
            "tel": "Teléfono",
            "ns_titulo": "N.S. (Número de Serie)",
            "desc_instruccion": "Descripción del fallo",
            "fotos": "Adjuntar fotos/vídeos",
            "btn_agregar": "Añadir Equipo",
            "btn_generar": "GENERAR TICKET",
            "btn_salir": "SALIR",
            "exito": "✅ Ticket enviado correctamente."
        },
        "en": {
            "login_tit": "🔐 Registered User Access",
            "user_id": "Username / Team ID",
            "pass": "Password",
            "btn_entrar": "LOGIN",
            "btn_ir_registro": "I don't have an account, sign me up",
            "reg_tit": "📝 New User Registration",
            "p1_tit": "Step 1: Identification",
            "p2_tit": "Step 2: Security",
            "p3_tit": "Step 3: Legal",
            "match": "✅ Passwords match",
            "no_match": "⚠️ Passwords DO NOT match",
            "exito_reg": "✨ User created successfully!",
            "redir_login": "🔄 Redirecting...",
            "error_campos": "❌ All fields with (*) are required.",
            "consejo": "💡 Fields validate on change.",
            "titulo_portal": "SAT Technical Portal",
            "cat1": "Service Data",
            "cat2": "Equipment Details",
            "proyecto": "Project / Location",
            "cliente": "Company",
            "email": "Email",
            "tel": "Phone",
            "ns_titulo": "S.N. (Serial Number)",
            "desc_instruccion": "Fault description",
            "fotos": "Attach photos/videos",
            "btn_agregar": "Add Equipment",
            "btn_generar": "GENERATE TICKET",
            "btn_salir": "EXIT",
            "exito": "✅ Ticket sent successfully."
        }
    }

    # 2. LÓGICA DE SELECCIÓN
    # Si el idioma es español o inglés, usamos lo manual
    if codigo_iso in traducciones_maestras:
        return traducciones_maestras[codigo_iso]

    # 3. TRADUCCIÓN AUTOMÁTICA (Para el resto del mundo: sk, he, fr, de...)
    if GoogleTranslator:
        try:
            # Usamos el diccionario de Castellano como base para traducir
            base_es = traducciones_maestras["es"]
            traductor = GoogleTranslator(source='es', target=codigo_iso)
            
            # Traducimos cada palabra del diccionario automáticamente
            diccionario_traducido = {}
            for clave, texto in base_es.items():
                # Solo traducimos si es un texto, no iconos o códigos
                if isinstance(texto, str) and len(texto) > 1:
                    diccionario_traducido[clave] = traductor.translate(texto)
                else:
                    diccionario_traducido[clave] = texto
            return diccionario_traducido
        except:
            # Si falla el internet o Google, devolvemos inglés por seguridad
            return traducciones_maestras["en"]
    
    return traducciones_maestras["en"]


