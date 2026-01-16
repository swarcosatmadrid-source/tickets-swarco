# =============================================================================
# ARCHIVO: idiomas.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 1.6.0 (Traductor Automático Infinito)
# FECHA ÚLTIMA MODIF: 16-Ene-2026
# DESCRIPCIÓN: Restauración del motor deep-translator para soporte universal 
#              de idiomas sin depender de tablas manuales.
# =============================================================================

from deep_translator import GoogleTranslator
import streamlit as st
import pandas as pd

def obtener_lista_idiomas():
    """
    Genera la lista de idiomas disponibles en Google Translator 
    para que el sidebar del main.py pueda mostrarlos todos.
    """
    try:
        # Obtenemos los idiomas soportados por la librería
        langs_dict = GoogleTranslator().get_supported_languages(as_dict=True)
        # Convertimos a DataFrame para que el main.py lo maneje fácil
        df = pd.DataFrame(list(langs_dict.items()), columns=['nombre_idioma', 'codigo'])
        # Ponemos los principales arriba para comodidad del usuario
        prioritarios = ['spanish', 'english', 'german', 'french']
        df['prioridad'] = df['nombre_idioma'].apply(lambda x: 0 if x in prioritarios else 1)
        return df.sort_values(['prioridad', 'nombre_idioma']).drop(columns=['prioridad'])
    except:
        # Fallback si no hay internet
        return pd.DataFrame([
            {"nombre_idioma": "spanish", "codigo": "es"},
            {"nombre_idioma": "english", "codigo": "en"}
        ])

def traducir_interfaz(codigo_iso):
    """Lógica original del usuario con diccionario maestro y traducción automática."""
    traducciones_maestras = {
        "es": {
            "reg_tit": "📝 Registro de Nuevo Usuario / Equipo",
            "p1_tit": "1. Identificación Personal",
            "p2_tit": "2. Ubicación y Contacto",
            "p3_tit": "3. Seguridad de la Cuenta",
            "p4_tit": "4. Validación Legal",
            "guia_titulo": "📘 Guía de Llenado (Clic para desplegar)",
            "guia_desc": "• Todos los campos marcados con (*) son obligatorios.\n• El teléfono añade el prefijo del país automáticamente.\n• La contraseña debe tener mayúsculas y números.",
            "help_empresa": "Nombre fiscal de su compañía u organismo.",
            "help_user": "Este será su ID único para iniciar sesión.",
            "help_pass": "Mínimo 8 caracteres, 1 mayúscula, 1 número.",
            "acepto": "He leído y acepto la ",
            "link_texto": "Política de Privacidad y Protección de Datos",
            "msg_legal": "Consulte nuestro documento PDF para saber cómo tratamos sus datos.",
            "login_tit": "🔐 Acceso Usuarios Registrados",
            "user_id": "Usuario / ID",
            "pass": "Contraseña",
            "btn_entrar": "INGRESAR AL SISTEMA",
            "btn_ir_registro": "No tengo cuenta, quiero registrarme",
            "match": "✅ Las claves coinciden",
            "no_match": "⚠️ Las claves NO coinciden",
            "exito_reg": "✨ ¡Usuario creado con éxito! Revise su correo.",
            "redir_login": "🔄 Redirigiendo...",
            "error_campos": "❌ Rellene todos los campos (*)",
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
            "nombre": "Nombre",
            "apellido": "Apellido",
            "pais": "País",
            "pass_rep": "Repetir Contraseña",
            "btn_volver": "VOLVER",
            "btn_repuestos": "Solicitud de Repuestos",
            "btn_equipos_nuevos": "Equipos Nuevos"
        },
        "en": {
            "reg_tit": "📝 New User Registration",
            "p1_tit": "1. Personal Identification",
            "p2_tit": "2. Location & Contact",
            "p3_tit": "3. Account Security",
            "p4_tit": "4. Legal Validation",
            "guia_titulo": "📘 User Guide (Click to expand)",
            "guia_desc": "• All fields with (*) are mandatory.\n• Phone prefix is added automatically.\n• Password must include uppercase and numbers.",
            "help_empresa": "Fiscal name of your company.",
            "help_user": "This will be your unique Login ID.",
            "help_pass": "Min 8 chars, 1 uppercase, 1 number.",
            "acepto": "I have read and accept the ",
            "link_texto": "Privacy Policy & Data Protection",
            "msg_legal": "Check our PDF document regarding data treatment.",
            "login_tit": "🔐 Registered User Access",
            "user_id": "Username / ID",
            "pass": "Password",
            "btn_entrar": "LOGIN",
            "btn_ir_registro": "Sign up here",
            "match": "✅ Passwords match",
            "no_match": "⚠️ Passwords do not match",
            "exito_reg": "✨ User created! Check your email.",
            "redir_login": "🔄 Redirecting...",
            "error_campos": "❌ Fill all fields (*)",
            "titulo_portal": "Technical Report Portal",
            "cat1": "Service Data",
            "cat2": "Equipment Details",
            "proyecto": "Project / Location",
            "cliente": "Company",
            "email": "Email",
            "tel": "Phone",
            "ns_titulo": "S.N. (Serial Number)",
            "desc_instruccion": "Failure description",
            "fotos": "Attach photos/videos",
            "btn_agregar": "Add Equipment",
            "btn_generar": "GENERATE TICKET",
            "btn_salir": "LOGOUT",
            "exito": "✅ Ticket sent successfully.",
            "nombre": "Name",
            "apellido": "Surname",
            "pais": "Country",
            "pass_rep": "Repeat Password",
            "btn_volver": "BACK",
            "btn_repuestos": "Spare Parts Request",
            "btn_equipos_nuevos": "New Equipment"
        }
    }

    if codigo_iso in traducciones_maestras:
        return traducciones_maestras[codigo_iso]

    try:
        mapa_correccion = {"he": "iw", "zh": "zh-CN", "jv": "jw"}
        codigo_google = mapa_correccion.get(codigo_iso, codigo_iso)
        base_es = traducciones_maestras["es"]
        traductor = GoogleTranslator(source='es', target=codigo_google)
        
        diccionario_traducido = {}
        for clave, texto in base_es.items():
            if isinstance(texto, str) and len(texto) > 1:
                diccionario_traducido[clave] = traductor.translate(texto)
            else:
                diccionario_traducido[clave] = texto
        return diccionario_traducido
    except:
        return traducciones_maestras["en"]
