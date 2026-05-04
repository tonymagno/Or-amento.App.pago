import streamlit as st
from auth import tela_login, usuario_logado, usuario_atual, fazer_logout
from billing import verificar_acesso

st.markdown(
    """
    <div style='background: linear-gradient(135deg, #111827, #0B1320);
                border: 1px solid #253244;
                border-radius: 24px;
                padding: 22px;
                margin-top: 12px;
                margin-bottom: 18px;'>
        <h1 style='margin:0;color:#fff;'>Sistema de Orçamento Premium</h1>
        <p style='margin-top:6px;color:#94A3B8;'>
            Painel elegante para múltiplos serviços, histórico e PDF profissional.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# 🔐 LOGIN
if not usuario_logado():
    tela_login()
    st.stop()

# 🔐 PAGAMENTO
if not verificar_acesso(usuario_atual()):
    st.warning("Acesso bloqueado. Assinatura necessária.")
    st.stop()

# 🚀 APP PRINCIPAL
st.title("Sistema de Orçamento Premium")

st.success(f"Bem-vindo, {usuario_atual()}")

if st.button("Logout"):
    fazer_logout()

st.write("Aqui entra seu sistema de orçamento...")
