import pandas as pd
# Intentamos importar deep_translator, si falla, usamos modo seguro
try:
    from deep_translator import GoogleTranslator
    TIENE_TRADUCTOR = True
except ImportError:
    TIENE_TRADUCTOR = False

def obtener_lista_idiomas():
    # Lista base
    data = {
        'nombre': ['Español', 'English', 'Deutsch', 'Français', 'Italiano', 'Português'],
        'codigo': ['es', 'en', 'de', 'fr', 'it', 'pt']
    }
    return pd.DataFrame(data)

def traducir_interfaz(target_lang='es'):
    # Diccionario Base (Español)
    base = {
        'login_tit': 'Acceso Usuarios',
        'reg_tit': 'Registro de Usuario',
        'user_id': 'Correo Electrónico',
        'pass': 'Contraseña',
        'pass_rep': 'Repetir Contraseña',
        'btn_entrar': 'INGRESAR',
        'btn_ir_registro': 'Crear cuenta nueva',
        'btn_registro_final': 'REGISTRAR',
        'btn_volver': 'VOLVER',
        'nombre': 'Nombre',
        'apellido': 'Apellido',
        'cliente': 'Empresa / Cliente',
        'pais': 'País',
        'email': 'Email',
        'tel': 'Teléfono',
        'acepto': 'He leído y acepto la política de privacidad',
        'no_match': 'Las contraseñas no coinciden',
        'error_campos': 'Por favor, rellene los campos marcados en rojo',
        'exito_reg': 'Usuario registrado correctamente.',
        'menu_tit': 'Menú Principal'
    }
    
    if target_lang == 'es' or not TIENE_TRADUCTOR:
        return base
    
    # Traducción Dinámica
    traducido = {}
    try:
        tr = GoogleTranslator(source='es', target=target_lang)
        keys = list(base.keys())
        values = list(base.values())
        # Traducimos en lote para velocidad
        tr_values = tr.translate_batch(values)
        traducido = dict(zip(keys, tr_values))
        return traducido
    except:
        return base # Fallback a español si falla la API
