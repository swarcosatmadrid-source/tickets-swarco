def traducir_interfaz(idioma):
    traducciones = {
        "Castellano": {
            # --- TICKET (Lo que ya tenías) ---
            "titulo_portal": "Portal de Reporte Técnico SAT",
            "cliente": "Empresa / Entidad",
            # ... (todos tus campos actuales) ...
            
            # --- NUEVO: ACCESO Y REGISTRO ---
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
            "error_campos": "❌ Todos los campos marcados con (*) son obligatorios."
        },
        "English": {
            # --- TICKET (Lo que ya tenías) ---
            "titulo_portal": "SAT Technical Reporting Portal",
            "cliente": "Company / Entity",
            # ... (todos tus campos actuales) ...

            # --- NUEVO: ACCESS & REGISTRATION ---
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
            "error_campos": "❌ All fields marked with (*) are required."
        }
    }
    
    if idioma in traducciones:
        return traducciones[idioma]
    else:
        return traducciones["English"]

