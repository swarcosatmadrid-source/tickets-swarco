# ... resto de imports ...

# CONFIGURACIÓN
EMAIL_EMISOR = "swarcosatmadrid@gmail.com"
# Importante: Usamos st.secrets para que sea seguro en la nube
PASSWORD_EMISOR = st.secrets["GMAIL_PASSWORD"] 

EMAIL_RECEPTOR = "aitor.badiola@swarco.com" 
# ... resto del código ...