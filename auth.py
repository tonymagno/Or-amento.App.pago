# auth.py

import streamlit as st
import hashlib
from db import init_db, get_user

# Cria o DB (se ainda não existir) e permite criar o admin se desejado.
init_db()

def hash_password(password):
    """Retorna o hash SHA256 da senha."""
    return hashlib.sha256(password.encode()).hexdigest()

def verificar_login(username, password):
    """
    Verifica credenciais de login.
    Primeiro tenta admin definido em st.secrets, depois consulta o banco.
    """
    admin_user = st.secrets["ADMIN_USERNAME"]
    admin_pass_hash = st.secrets["ADMIN_PASSWORD"]
    # Verifica admin
    if username == admin_user and hash_password(password) == admin_pass_hash:
        return True
    # Verifica banco de usuários cadastrados
    user = get_user(username)
    return (user is not None and user[1] == hash_password(password))

def tela_login():
    """
    Exibe a tela de login estilizada. Bloqueia o app até login exitoso.
    """
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
    if not st.session_state['logged_in']:
        # Oculta UI padrão do Streamlit (barra lateral e cabeçalho)
        st.markdown("""
            <style>
            .block-container { padding-top: 1rem; padding-bottom: 1rem; }
            header, footer { visibility: hidden; }
            </style>
            """, unsafe_allow_html=True)
        # CSS personalizado para login premium
        st.markdown("""
            <style>
                .login-wrap {
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: linear-gradient(135deg, #111827, #0B1320);
                }
                .login-box {
                    background: #1F2937;
                    padding: 2rem;
                    border-radius: 16px;
                    box-shadow: 0 18px 48px rgba(0,0,0,0.28);
                    max-width: 400px;
                    width: 100%;
                }
                .shield {
                    width: 60px; height: 60px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #D4AF37, #F2D16B);
                    display: grid; place-items: center;
                    font-size: 30px; margin: 0 auto 10px;
                }
                .login-box h2 {
                    color: white;
                    text-align: center;
                    margin-bottom: 1rem;
                }
                .stTextInput>div>div>input {
                    border-radius: 8px !important;
                    border: 1px solid #374151 !important;
                    background-color: #111827 !important;
                    color: #F3F4F6 !important;
                    height: 44px;
                }
                .stButton>button {
                    width: 100%;
                    border-radius: 8px;
                    border: none;
                    padding: 12px 0;
                    font-weight: 600;
                    background: linear-gradient(90deg,#D4AF37,#F2D16B);
                    color: #111827;
                    font-size: 16px;
                }
            </style>
            """, unsafe_allow_html=True)
        # Container de login
        st.markdown("<div class='login-wrap'><div class='login-box'>", unsafe_allow_html=True)
        st.markdown("<div class='shield'>🔒</div>", unsafe_allow_html=True)
        st.markdown("<h2>ACESSO RESTRITO</h2>", unsafe_allow_html=True)
        with st.form("form_login", clear_on_submit=False):
            username = st.text_input("Usuário", placeholder="Digite seu usuário")
            password = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            entrar = st.form_submit_button("Entrar")
        if entrar:
            if verificar_login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos.")
        st.markdown("</div></div>", unsafe_allow_html=True)
        st.stop()

def logout():
    """Efetua logout do usuário atual."""
    st.session_state['logged_in'] = False
    st.session_state['username'] = ""
    st.experimental_rerun()
