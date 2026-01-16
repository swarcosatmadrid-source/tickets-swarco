# =============================================================================
# ARCHIVO: idiomas.py
# PROYECTO: Sistema de Gestión SAT - SWARCO Traffic Spain
# VERSIÓN: 3.2.0 (Recuperación de Deep Translator + Estructura Rígida)
# FECHA: 16-Ene-2026
# DESCRIPCIÓN: Gestión de diccionario base y traducción dinámica universal.
# =============================================================================

import pandas as pd

# Intentamos importar la librería que ya tenías instalada
try:
    from deep_translator import GoogleTranslator
    TIENE_TRADUCTOR = True
except ImportError:
    TIENE_TRADUCTOR = False

def obtener_lista_idiomas():
    """Devuelve el DataFrame con los idiomas soportados (Universal)."""
    return pd.DataFrame({
        'nombre': ['Español', 'English', 'Deutsch', 'Français', 'Italiano', 'Русский', '中文', 'עברית'],
        'codigo': ['es', 'en', 'de', 'fr', 'it', 'ru', 'zh-CN', 'he']
    })

def traducir_interfaz(target_lang='es'):
    """
    Traduce el diccionario base al idioma destino.
    Si deep-translator está instalado, usa Google Translate.
    Si no, devuelve español para evitar errores.
    """
    base = {
        'login_tit': 'Acceso Usuarios',
        'reg_tit': 'Registro de Usuario',
        'p1_tit': '1. Identificación',
        'p2_tit': '2. Ubicación y Contacto',
        'p3_tit': '3. Seguridad',
        'p4_tit': '4. Validación Legal',
        'user_id': 'Usuario / Email',
        'pass': 'Contraseña',
        'nombre': 'Nombre',
        'apellido': 'Apellido',
        'cliente': 'Empresa / Cliente',
        'pais': 'País',
        'email': 'Email',
        'tel': 'Teléfono',
        'pass_rep': 'Repetir Contraseña',
        'acepto': 'He leído y acepto los términos',
        'btn_entrar': 'INGRESAR',
        'btn_ir_registro': 'Crear Cuenta',
        'btn_registro_final': 'REGISTRAR',
        'btn_volver': 'VOLVER AL LOGIN',
        'error_campos': 'Por favor, rellene los campos marcados en rojo',
        'no_match': 'Las contraseñas no coinciden',
        'exito_reg': 'Registro exitoso',
        'menu_tit': 'Menú Principal'
    }

    if target_lang == 'es': return base

    if TIENE_TRADUCTOR:
        try:
            tr = GoogleTranslator(source='es', target=target_lang)
            keys = list(base.keys())
            values = list(base.values())
            # Traducción en lote para optimizar tiempo
            tr_values = tr.translate_batch(values)
            return dict(zip(keys, tr_values))
        except:
            return base
    return base

