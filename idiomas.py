# =============================================================================
# ARCHIVO: idiomas.py
# VERSIÓN: 5.0.0 (Universal Real)
# =============================================================================
import pandas as pd

try:
    from deep_translator import GoogleTranslator
    TIENE_TRADUCTOR = True
except:
    TIENE_TRADUCTOR = False

def obtener_lista_idiomas():
    # Lista base amplia
    return pd.DataFrame({
        'nombre': ['Español', 'English', 'Deutsch', 'Français', 'Italiano', 'Português', 'Русский', '中文 (Chino)', '日本語 (Japonés)', 'العربية (Árabe)', 'עברית (Hebreo)'],
        'codigo': ['es', 'en', 'de', 'fr', 'it', 'pt', 'ru', 'zh-CN', 'ja', 'ar', 'he']
    })

def traducir_interfaz(target_lang='es'):
    base = {
        'login_tit': 'Portal SAT',
        'reg_tit': 'Alta de Usuario',
        'p1_tit': 'Datos Personales',
        'p2_tit': 'Datos de Contacto',
        'p3_tit': 'Seguridad',
        'p4_tit': 'Términos Legales',
        'nombre': 'Nombre',
        'apellido': 'Apellido',
        'cliente': 'Organización / Empresa',
        'pais': 'País de Residencia',
        'tel': 'Teléfono Móvil',
        'email': 'Correo Electrónico',
        'pass': 'Contraseña',
        'pass_rep': 'Confirmar Contraseña',
        'acepto': 'He leído y acepto los términos',
        'btn_entrar': 'Acceder',
        'btn_ir_registro': 'Crear Cuenta',
        'btn_registro_final': 'Finalizar Registro',
        'btn_volver': 'Regresar',
        'error_campos': 'Por favor corrija los campos marcados en rojo',
        'exito_reg': 'Registro completado exitosamente'
    }

    if target_lang == 'es': return base

    if TIENE_TRADUCTOR:
        try:
            tr = GoogleTranslator(source='es', target=target_lang)
            keys = list(base.keys())
            values = list(base.values())
            tr_values = tr.translate_batch(values)
            return dict(zip(keys, tr_values))
        except: return base
    return base

