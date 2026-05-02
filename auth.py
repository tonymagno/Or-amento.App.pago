import streamlit as st

USUARIOS = {
    "admin": "123",
    "tony": "1234"
}

def usuario_logado():
    return st.session_state.get("logado", False)


def tela_login():

    st.markdown("""
    <style>
    
    /* FUNDO */
    .stApp {
        background: linear-gradient(135deg, #020617, #020617 60%, #0f172a);
        color: white;
    }

    /* CENTRALIZAÇÃO */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
    }

    /* CARD */
    .login-card {
        background: rgba(255,255,255,0.05);
        padding: 40px;
        border-radius: 20px;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        width: 380px;
        text-align: center;
        box-shadow: 0 0 40px rgba(0,0,0,0.6);
    }

    /* TÍTULO */
    .login-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .login-sub {
        color: #cbd5e1;
        font-size: 14px;
        margin-bottom: 25px;
    }

    /* INPUT */
    input {
        background-color: #020617 !important;
        border: 1px solid #334155 !important;
        color: white !important;
        border-radius: 10px !important;
    }

    /* BOTÃO */
    .stButton button {
        width: 100%;
        background: linear-gradient(90deg, #d4af37, #facc15);
        color: black;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 12px;
        margin-top: 10px;
    }

    .stButton button:hover {
        background: linear-gradient(90deg, #facc15, #d4af37);
    }

    </style>
    """, unsafe_allow_html=True)

    # CONTAINER CENTRAL
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        st.markdown('<div class="login-title">🔐 Acesso ao Sistema</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-sub">Entre com suas credenciais</div>', unsafe_allow_html=True)

        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar no Sistema"):
            if usuario in USUARIOS and USUARIOS[usuario] == senha:
                st.session_state.logado = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
