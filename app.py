import streamlit as st
from auth import tela_login, usuario_logado
from faturamento import verificar_acesso

st.set_page_config(page_title="Orçamento Premium", layout="wide")

# 🔐 LOGIN
if not usuario_logado():
    tela_login()
    st.stop()

# 💰 VERIFICA SE PAGOU
if not verificar_acesso():
    st.warning("🔒 Acesso bloqueado. Assinatura necessária.")
    st.stop()

# 🚀 SISTEMA LIBERADO
st.success("Sistema liberado 🚀")

st.title("💎 Sistema de Orçamento Premium")

cliente = st.text_input("Cliente")
servico = st.text_input("Serviço")
valor = st.number_input("Valor", min_value=0.0)

if st.button("Gerar orçamento"):
    st.success(f"Orçamento gerado para {cliente} - R$ {valor}")
