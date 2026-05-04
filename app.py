# app.py

import streamlit as st
from auth import login_widget, logout
from billing import verificar_acesso
from db import init_db, add_quote, recent_quotes
from urllib.parse import quote
from pdf_generator import gerar_pdf_bytes

# Inicialização (inclui a criação das tabelas)
init_db()

# Autenticação
login_widget()
username = st.session_state['username']
st.sidebar.button("Logout", on_click=logout)

st.title("Sistema de Orçamento Premium")
st.write(f"**Bem-vindo(a), {username}!**")

# Formulário de dados principais
st.header("Dados do Orçamento")
negocio = st.text_input("Nome do Negócio", "")
cliente = st.text_input("Nome do Cliente", "")
whatsapp = st.text_input("WhatsApp do Cliente", "")
if negocio.strip() and cliente.strip():
    st.success("Dados principais preenchidos.")

# Adicionar serviços
st.header("Adicionar serviço")
servico = st.text_input("Descrição do serviço")
quantidade = st.number_input("Quantidade", value=1, min_value=1, step=1)
preco_unit = st.number_input("Preço unitário", value=0.0, min_value=0.0, step=0.01)
if st.button("Adicionar serviço"):
    if servico.strip():
        if 'itens' not in st.session_state:
            st.session_state.itens = []
        st.session_state.itens.append({
            "servico": servico,
            "quantidade": quantidade,
            "preco_unitario": preco_unit
        })
        st.experimental_rerun()  # reexibe a lista atualizada
    else:
        st.error("Descrição do serviço não pode ficar em branco.")

# Exibir lista de serviços adicionados
if 'itens' in st.session_state and st.session_state.itens:
    st.subheader("Serviços adicionados")
    for idx, item in enumerate(st.session_state.itens, 1):
        st.write(f"{idx}. {item['servico']} - Qtd: {item['quantidade']} - R$ {item['preco_unitario']:.2f}")

# Cálculo de valores
desconto = st.number_input("Desconto", min_value=0.0, step=0.01, value=0.0)
taxa_extra = st.number_input("Taxa extra", min_value=0.0, step=0.01, value=0.0)
subtotal = sum(i["quantidade"]*i["preco_unitario"] for i in st.session_state.itens) if 'itens' in st.session_state else 0.0
total = max(subtotal - desconto + taxa_extra, 0.0)
st.markdown(f"**TOTAL FINAL:** R$ {total:.2f}")

# Botão Gerar Orçamento
if st.button("🚀 Gerar orçamento"):
    if not negocio.strip() or not cliente.strip() or not whatsapp.strip() or not st.session_state.itens:
        st.error("Preencha todos os dados principais e adicione ao menos um serviço.")
    else:
        # Salvar no banco
        add_quote(username, cliente, total)
        st.success(f"Orçamento gerado para **{cliente}**.")

        # Montar mensagem WhatsApp
        mensagem = gerar_mensagem_whatsapp(
            cliente, negocio, st.session_state.itens,
            subtotal, desconto, taxa_extra, total
        )
        # Gerar link WA
        numero = "".join(filter(str.isdigit, whatsapp))
        if not numero.startswith("55"):
            numero = "55" + numero
        link_wa = f"https://wa.me/{numero}?text={quote(mensagem)}"

        # Gerar PDF
        pdf_buffer = gerar_pdf_bytes(cliente, negocio, st.session_state.itens,
                                    subtotal, desconto, taxa_extra, total)

        # Mostrar mensagem e botões
        st.text_area("Mensagem WhatsApp", mensagem, height=200)
        # Botão para abrir WhatsApp (usa anchor HTML para compatibilidade)
        st.markdown(f'''
            <a href="{link_wa}" target="_blank">
                <button style="
                    background: linear-gradient(90deg,#25D366,#128C7E);
                    border:none; padding:12px 20px; color:white;
                    font-size:16px; border-radius:8px; cursor:pointer;">
                    📲 Enviar via WhatsApp
                </button>
            </a>
        ''', unsafe_allow_html=True)
        # Botão de download do PDF
        st.download_button(
            label="📄 Baixar PDF",
            data=pdf_buffer,
            file_name=f"orcamento_{cliente}.pdf",
            mime="application/pdf"
        )

# Histórico recente
st.subheader("Histórico recente")
for row in recent_quotes(username, limit=5):
    st.write(f"- {row['client_name']} | R$ {float(row['total']):.2f} | {row['created_at']}")
