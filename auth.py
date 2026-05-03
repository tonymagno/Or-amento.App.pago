import streamlit as st

# 🔐 LOGIN SIMPLES (PODE EVOLUIR DEPOIS)
USUARIO = "admin"
SENHA = "1234"

def usuario_logado():
    return st.session_state.get("logado", False)

def usuario_atual():
    return st.session_state.get("usuario", "")

def fazer_logout():
    st.session_state["logado"] = False
    st.rerun()

def tela_login():
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)

    st.markdown("## 🔐 Acesso ao Sistema")

    usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")

    if st.button("Entrar"):
        if usuario == USUARIO and senha == SENHA:
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos")

    st.markdown("</div>", unsafe_allow_html=True)
