import streamlit as st
import json, requests, random, time, re
from idiomas import traducir_interfaz

URL_BRIDGE = "https://script.google.com/macros/s/AKfycbyDpHS4nU16O7YyvABvmbFYHTLv2e2J8vrpSD-iCmamjmS4Az6p9iZNUmVEwzMVyzx9/exec"

def chequear_calidad_clave(p):
    if not p: return "", ""
    puntos = 0
    if len(p) >= 8: puntos += 1
    if re.search(r"[A-Z]", p): puntos += 1
    if re.search(r"[0-9]", p): puntos += 1
    if puntos <= 1: return "🔴 Débil", "error"
    if puntos <= 2: return "🟠 Media", "warning"
    return "🟢 Fuerte", "success"

def gestionar_acceso(conn):
    t = traducir_interfaz(st.session_state.idioma)
    with st.form("login_form"):
        user_in = st.text_input(t.get('user_id', 'ID'), placeholder="Ej: UTE_Sur").strip()
        pass_in = st.text_input(t.get('pass', 'Clave'), type="password")
        if st.form_submit_button(t.get('btn_entrar', 'INGRESAR'), use_container_width=True):
            try:
                df = conn.read(worksheet="Usuarios", ttl=0)
                v = df[(df['Usuario'].astype(str) == user_in) & (df['Password'].astype(str) == pass_in)]
                if not v.empty:
                    st.session_state.autenticado = True
                    st.session_state.datos_cliente = {'Empresa': v.iloc[0]['Empresa'], 'Contacto': v.iloc[0]['Usuario'], 'Email': v.iloc[0]['Email']}
                    return True
                else: st.error(t.get('error_cred', "❌ Error"))
            except Exception as e: st.error(f"Error: {e}")
    return False

def interfaz_registro_legal(conn):
    t = traducir_interfaz(st.session_state.idioma)

    if st.session_state.get('registro_exitoso', False):
        st.success(t.get('exito_reg', "✨ **¡Usuario creado con éxito! Bienvenidos a Swarco Spain SAT.**"))
        time.sleep(3)
        st.session_state.registro_exitoso = False
        st.session_state.mostrar_registro = False
        st.rerun()
        return

    st.markdown(f"### {t.get('reg_tit', 'Registro')}")
    st.info(f"💡 {t.get('consejo', 'Validación automática al cambiar de casilla.')}")

    # PASO 1: ID (Fuera del form para validación al instante)
    with st.container(border=True):
        st.markdown(f"#### {t.get('p1_tit', 'Paso 1')}")
        usuario_id = st.text_input(t.get('user_id', 'ID') + " *")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre / Name *")
            empresa = st.text_input(t.get('cliente', 'Empresa') + " *")
        with c2:
            apellido = st.text_input("Apellidos / Last Name *")
            email = st.text_input(t.get('email', 'Email') + " *")

    # PASO 2: CLAVES (Validación instantánea)
    with st.container(border=True):
        st.markdown(f"#### {t.get('p2_tit', 'Paso 2')}")
        cp1, cp2 = st.columns(2)
        with cp1:
            pass1 = st.text_input(t.get('pass', 'Clave') + " *", type="password")
            calidad, _ = chequear_calidad_clave(pass1)
            if pass1: st.write(f"Calidad: {calidad}")
        with cp2:
            pass2 = st.text_input(t.get('pass', 'Clave') + " (Confirm) *", type="password")
            if pass1 and pass2:
                if pass1 == pass2: st.success(t.get('match', "✅ OK"))
                else: st.error(t.get('no_match', "⚠️ No coinciden"))

    # PASO 3: FORMULARIO FINAL
    with st.form("form_final"):
        st.markdown(f"#### {t.get('p3_tit', 'Paso 3')}")
        tel = st.text_input(t.get('tel', 'Teléfono') + " *")
        if 'n1' not in st.session_state:
            st.session_state.n1, st.session_state.n2 = random.randint(1,10), random.randint(1,10)
        
        captcha = st.number_input(f"{st.session_state.n1} + {st.session_state.n2} =", step=1)
        acepta = st.checkbox(t.get('rgpd', 'Acepto términos *'))
        
        if st.form_submit_button(t.get('btn_generar', 'REGISTRAR'), use_container_width=True):
            if not (usuario_id and nombre and pass1 == pass2 and acepta and captcha == (st.session_state.n1 + st.session_state.n2)):
                st.error(t.get('error_campos', "❌ Revisar campos"))
            else:
                try:
                    payload = {"Accion": "Registro", "Usuario": usuario_id, "Nombre": nombre, "Apellido": apellido, "Email": email, "Password": pass1, "Empresa": empresa, "Telefono": tel, "RGPD": "SÍ"}
                    requests.post(URL_BRIDGE, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
                    st.session_state.registro_exitoso = True
                    st.rerun()
                except: st.error("Error conexión")
