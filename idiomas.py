# ARCHIVO: idiomas.py
# VERSIÓN: v1.1-DEBUG
# FECHA: 15-Ene-2026
# DESCRIPCIÓN: Incluye un chivato (st.error) para mostrar en pantalla por qué falla la traducción.

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
            # Faltantes del registro para evitar errores de llave
            "nombre": "Nombre",
            "apellido": "Apellido",
            "pais": "País",
            "pass_rep": "Repetir Contraseña",
            "acepto": "Acepto Política de Privacidad"
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
            "acepto": "I accept Privacy Policy"
        }
    }

    # Si es español o inglés, no gastamos internet, tiramos de lo manual
    if codigo_iso in traducciones_maestras:
        return traducciones_maestras[codigo_iso]

    # 2. TRADUCCIÓN GALÁCTICA (Cualquier idioma de la tierra)
    try:
        base_es = traducciones_maestras["es"]
        # El traductor recibe el código ISO
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
        # --- MODO DEBUG: CHIVATO DE ERROR ---
        st.error(f"⚠️ ERROR CRÍTICO DEL TRADUCTOR: {e}")
        # ------------------------------------
        # Si falla, devolvemos inglés por seguridad
        return traducciones_maestras["en"]


