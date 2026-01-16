import streamlit as st
import pandas as pd
import hashlib
import estilos
import correo

def encriptar_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def gestionar_acceso(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("login_tit", "Acceso")}</p>', unsafe_allow_html=True)
    
    with st.form("login"):
        user = st.text_input(t.get("user_id", "Usuario")).lower().strip()
        pwd = st.text_input(t.get("pass", "Pass"), type='password')
        if st.form_submit_button(t.get("btn_entrar", "Entrar")):
            try:
                df = pd.DataFrame(conn.worksheet("Usuarios").get_all_records())
                if not df.empty and user in df['email'].values:
                    real_pass = df.loc[df['email']==user, 'password'].values[0]
                    if encriptar_password(pwd) == real_pass:
                        st.session_state.autenticado = True
                        st.session_state.user_email = user
                        st.session_state.pagina_actual = 'menu'
                        st.rerun()
                    else: st.error("Password incorrecto")
                else: st.error("Usuario no encontrado")
            except Exception as e: st.error(f"Error conexión: {e}")

    if st.button(t.get("btn_ir_registro", "Registro")):
        st.session_state.mostrar_registro = True
        st.rerun()

def interfaz_registro_legal(conn, t):
    estilos.mostrar_logo()
    st.markdown(f'<p class="swarco-title">{t.get("reg_tit", "Registro")}</p>', unsafe_allow_html=True)
    
    if 'err' not in st.session_state: st.session_state.err = []
    def lbl(txt, k): return f":red[{txt} *]" if k in st.session_state.err else f"{txt} *"

    with st.form("reg"):
        c1, c2 = st.columns(2)
        n = c1.text_input(lbl(t.get("nombre", "Nombre"), "n"))
        a = c2.text_input(lbl(t.get("apellido", "Apellido"), "a"))
        e = st.text_input(lbl(t.get("cliente", "Empresa"), "e"))
        p = st.text_input(lbl(t.get("pais", "País"), "p"))
        m = st.text_input(lbl(t.get("email", "Email"), "m")).lower().strip()
        tl = st.text_input(lbl(t.get("tel", "Teléfono"), "tl"))
        p1 = st.text_input(lbl(t.get("pass", "Pass"), "p1"), type='password')
        p2 = st.text_input(lbl(t.get("pass_rep", "Repetir"), "p2"), type='password')
        chk = st.checkbox(t.get("acepto", "Legal"))

        if st.form_submit_button(t.get("btn_registro_final", "REGISTRAR")):
            st.session_state.err = []
            if not n: st.session_state.err.append("n")
            if not a: st.session_state.err.append("a")
            if not e: st.session_state.err.append("e")
            if not p: st.session_state.err.append("p")
            if not m: st.session_state.err.append("m")
            if not tl: st.session_state.err.append("tl")
            if not p1: st.session_state.err.append("p1")
            if not chk: st.session_state.err.append("chk")

            if st.session_state.err:
                st.error("⚠️ " + t.get("error_campos", "Rojos"))
                st.rerun()
            elif p1 != p2:
                st.error(t.get("no_match", "Error Pass"))
            else:
                try:
                    conn.worksheet("Usuarios").append_row([n, a, e, p, m, tl, encriptar_password(p1)])
                    correo.enviar_correo_bienvenida(m, n, m, "******")
                    st.success(t.get("exito_reg", "Exito"))
                    st.session_state.mostrar_registro = False
                    st.rerun()
                except Exception as ex: st.error(f"Error Guardando: {ex}")

    if st.button(t.get("btn_volver", "Volver")):
        st.session_state.mostrar_registro = False
        st.session_state.err = []
        st.rerun()
