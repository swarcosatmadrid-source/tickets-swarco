import streamlit as st
try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None

def traducir_interfaz(codigo_idioma):
    # Diccionario con códigos ISO (estándar mundial)
    traducciones = {
        "es": {
            "login_tit": "🔐 Acceso Usuarios Registrados",
            "user_id": "Usuario (ID)",
            "pass": "Contraseña",
            "btn_entrar": "INGRESAR",
            "btn_ir_registro": "No tengo cuenta, quiero registrarme",
            "reg_tit": "📝 Registro de Nuevo Usuario / Equipo",
            "p1_tit": "Paso 1: Identificación",
            "match": "✅ Las claves coinciden",
            "exito_reg": "✨ ¡Usuario creado con éxito!",
            "titulo_portal": "Portal de Reporte Técnico SAT",
            "proyecto": "Proyecto / Ubicación",
            "tel": "Teléfono",
            "ns_titulo": "N.S. (Número de Serie)",
            "btn_generar": "GENERAR TICKET",
            "exito": "✅ Ticket enviado correctamente."
        },
        "en": {
            "login_tit": "🔐 Registered User Access",
            "user_id": "Username (ID)",
            "pass": "Password",
            "btn_entrar": "LOGIN",
            "btn_ir_registro": "Create an account",
            "reg_tit": "📝 New User Registration",
            "p1_tit": "Step 1: Identification",
            "match": "✅ Passwords match",
            "exito_reg": "✨ User created successfully!",
            "titulo_portal": "SAT Technical Portal",
            "proyecto": "Project / Location",
            "tel": "Phone",
            "ns_titulo": "S.N. (Serial Number)",
            "btn_generar": "GENERATE TICKET",
            "exito": "✅ Ticket sent successfully."
        }
    }

    # Si es español o inglés, devolvemos lo manual (que es perfecto)
    if codigo_idioma in traducciones:
        return traducciones[codigo_idioma]

    # Si es cualquier otro (sk, he, fr...), usamos Google Translate
    if GoogleTranslator:
        try:
            base = traducciones["es"]
            # Traducimos de 'es' al código que venga (sk, he, etc.)
            translator = GoogleTranslator(source='es', target=codigo_idioma)
            return {k: translator.translate(v) if isinstance(v, str) else v for k, v in base.items()}
        except:
            return traducciones["en"]
    return traducciones["en"]


