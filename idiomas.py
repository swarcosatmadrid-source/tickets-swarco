# ARCHIVO: idiomas.py
# VERSIÓN: v1.2 (Corrección de Códigos ISO)
# FECHA: 15-Ene-2026
# DESCRIPCIÓN: Mapea códigos conflictivos (como he->iw) para que Google Translator no falle.

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
            "exito": "✅ Ticket enviado correctamente.",
            # Claves extra para el registro
            "nombre": "Nombre",
            "apellido": "Apellido",
            "pais": "País",
            "pass_rep": "Repetir Contraseña",
            "acepto": "Acepto Política de Privacidad",
            "btn_volver": "VOLVER"
        },
        "en": {
            "login_tit": "🔐 Registered User Access",
            "user_id": "Username / Team ID",
            "pass": "Password",
            "btn_entrar": "LOGIN",
            "btn_ir_registro": "Sign up here",
            "reg_tit": "📝 New User Registration",
            "p1_tit": "Step 1: Identification",
            "p2_tit": "Step 2: Security",
            "p3_tit": "Step 3: Verification",
            "match": "✅ Passwords match",
            "no_match": "⚠️ Passwords do not match",
            "exito_reg": "✨ User created successfully!",
            "redir_login": "🔄 Redirecting...",
            "error_campos": "❌ Fill all fields (*)",
            "nombre": "Name",
            "apellido": "Surname",
            "cliente": "Company",
            "email": "Email",
            "pais": "Country",
            "tel": "Phone",
            "pass_rep": "Repeat Password",
            "acepto": "I accept Privacy Policy",
            "btn_volver": "BACK"
        }
    }

    # Si es español o inglés, usamos el manual
    if codigo_iso in traducciones_maestras:
        return traducciones_maestras[codigo_iso]

    # 2. TRADUCCIÓN GALÁCTICA
    try:
        # --- PARCHE DE CORRECCIÓN DE CÓDIGOS ---
        # Algunos códigos ISO no coinciden con los de Google. Aquí los arreglamos.
        mapa_correccion = {
            "he": "iw",     # Hebreo
            "zh": "zh-CN",  # Chino Simplificado
            "jv": "jw"      # Javanés
        }
        
        # Si el código está en la lista negra, lo cambiamos. Si no, usamos el original.
        codigo_google = mapa_correccion.get(codigo_iso, codigo_iso)
        # ---------------------------------------

        base_es = traducciones_maestras["es"]
        traductor = GoogleTranslator(source='es', target=codigo_google)
        
        diccionario_traducido = {}
        for clave, texto in base_es.items():
            if isinstance(texto, str) and len(texto) > 1:
                diccionario_traducido[clave] = traductor.translate(texto)
            else:
                diccionario_traducido[clave] = texto
        return diccionario_traducido
        
    except Exception as e:
        # Si falla, imprimimos error en consola (no en pantalla) y devolvemos inglés
        print(f"Error traducción: {e}")
        return traducciones_maestras["en"]

