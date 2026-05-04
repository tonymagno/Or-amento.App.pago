# auth.py

import streamlit as st
import hashlib
from db import init_db, get_user, add_user

# Inicializa DB (caso ainda não exista)
init_db()

def hash_password(password):
    """Retorna hash SHA256 da senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_login(username, password):
    """Verifica credenciais: compara com usuário admin nos secrets ou DB."""
    # Usuário administrador definido em secrets
    admin_user = st.secrets["ADMIN_USERNAME"]
    admin_pass = st.secrets["ADMIN_PASSWORD"]
    # Hash da senha informada
    password_hash = hash_password(password)
    # Se for o admin
    if username == admin_user and password_hash == admin_pass:
        return True
    # Senão, verifica banco local (usuários adicionais)
    user = get_user(username)
    return (user is not None and user[1] == password_hash)

def login_widget():
    """Exibe interface de login e mantém estado na sessão."""
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
    if not st.session_state['logged_in']:
        st.title("Faça login")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if verificar_login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos")
        st.stop()

def logout():
    """Efetua logout do usuário."""
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""
    st.experimental_rerun()
