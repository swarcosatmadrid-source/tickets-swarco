import streamlit as st
from deep_translator import GoogleTranslator

def traducir_interfaz(codigo_iso):
    # 1. TUS TRADUCCIONES MANUALES (El ADN sagrado)
    traducciones_maestras = {
        "es": {
            "login_tit": "🔐 Acceso Usuarios Registrados",
            "user_id": "Usuario / ID de Equipo",
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
            "redir_login": "🔄 Redirigiendo...",
            "error_campos": "❌ Rellene todos los campos (*)",
            "consejo": "💡 Los campos se validan al cambiar de casilla.",
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
            "btn_ir_registro": "Sign up here",
            "reg_tit": "📝 New User Registration",
            # ... (Aquí va el resto de tu inglés que ya tenemos)
        }
    }

    # Si es español o inglés, no gastamos internet, tiramos de lo manual
    if codigo_iso in traducciones_maestras:
        return traducciones_maestras[codigo_iso]

    # 2. TRADUCCIÓN GALÁCTICA (Cualquier idioma de la tierra)
    try:
        base_es = traducciones_maestras["es"]
        # El traductor recibe el código ISO (eu para euskera, he para hebreo, sk para eslovaco)
        traductor = GoogleTranslator(source='es', target=codigo_iso)
        
        diccionario_traducido = {}
        for clave, texto in base_es.items():
            # Traducimos solo si es texto largo, respetando iconos
            if isinstance(texto, str) and len(texto) > 1:
                diccionario_traducido[clave] = traductor.translate(texto)
            else:
                diccionario_traducido[clave] = texto
        return diccionario_traducido
    except Exception as e:
        # Si el mundo se acaba o no hay internet, el inglés nos salva
        return traducciones_maestras["en"]


