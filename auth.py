import streamlit as st

USUARIOS = {
    "admin": "123",
    "tony": "1234"
}

def usuario_logado():
    return st.session_state.get("logado", False)

def tela_login():
    st.title("🔐 Acesso ao Sistema Premium")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("Login inválido")
