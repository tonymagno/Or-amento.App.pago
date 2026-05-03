import streamlit as st
from auth import tela_login, usuario_logado, usuario_atual, fazer_logout
from faturamento import verificar_acesso

st.set_page_config(page_title="Orçamento Premium", layout="wide")

# 🔥 CSS CORRIGIDO (SEM ESPAÇO EM CIMA)
st.markdown("""
<style>
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

[data-testid="stAppViewContainer"] {
    padding-top: 0 !important;
}

.login-wrap {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}
</style>
""", unsafe_allow_html=True)


# 🔐 LOGIN
if not usuario_logado():
    tela_login()
    st.stop()

# 🔐 PAGAMENTO
if not verificar_acesso():
    st.warning("Acesso bloqueado. Assinatura necessária.")
    st.stop()

# 🚀 APP PRINCIPAL
st.title("Sistema de Orçamento Premium")

st.success(f"Bem-vindo, {usuario_atual()}")

if st.button("Logout"):
    fazer_logout()

st.write("Aqui entra seu sistema de orçamento...")
