# app.py

import streamlit as st
from auth import tela_login, logout
from billing import verificar_acesso
from db import init_db, add_quote, recent_quotes
from urllib.parse import quote
from pdf_generator import gerar_pdf_bytes

st.set_page_config(page_title="Orçamento Premium", page_icon="💼", layout="wide")
# Garante a criação das tabelas antes de usar
init_db()

# Login
tela_login()
username = st.session_state['username']
st.sidebar.write(f"**Usuário:** {username}")
st.sidebar.button("Logout", on_click=logout)

st.markdown("""
    <div style="background: linear-gradient(135deg, #111827, #0B1320);
                padding: 22px; border-radius: 24px; margin-bottom: 18px;">
        <h1 style="margin:0;color:#F3F4F6;">Sistema de Orçamento Premium</h1>
        <p style="margin-top:6px;color:#9CA3AF;">
            Bem-vindo(a), administrador! Gere orçamentos elegantes e profissionais.
        </p>
    </div>
""", unsafe_allow_html=True)

left, right = st.columns([2, 1], gap="small")
with left:
    st.subheader("Dados do Orçamento")
    negocio = st.text_input("Nome do Negócio", placeholder="Ex.: Karine Lashes")
    cliente = st.text_input("Cliente", placeholder="Ex.: Marcia")
    whatsapp = st.text_input("WhatsApp", placeholder="Ex.: 551299999999")

    st.subheader("Adicionar serviço")
    servico = st.text_input("Serviço (descrição)")
    qtd = st.number_input("Quantidade", min_value=1, step=1, value=1)
    preco = st.number_input("Preço unitário (R$)", min_value=0.0, step=0.01, value=0.0)
    if st.button("➕ Adicionar serviço"):
        if servico.strip():
            if 'itens' not in st.session_state:
                st.session_state['itens'] = []
            st.session_state.itens.append({
                "servico": servico.strip(),
                "quantidade": int(qtd),
                "preco_unitario": float(preco)
            })
            st.experimental_rerun()
        else:
            st.error("Informe a descrição do serviço.")

    # Lista de serviços adicionados
    if 'itens' in st.session_state and st.session_state.itens:
        st.subheader("Serviços adicionados")
        for item in st.session_state.itens:
            st.write(f"- {item['servico']} | Qtd: {item['quantidade']} | R$ {item['preco_unitario']:.2f}")
        if st.button("🧹 Limpar itens"):
            st.session_state['itens'] = []
            st.experimental_rerun()

with right:
    desconto = st.number_input("Desconto (R$)", min_value=0.0, step=0.01, value=0.0)
    taxa_extra = st.number_input("Taxa extra (R$)", min_value=0.0, step=0.01, value=0.0)
    subtotal = sum(i["quantidade"]*i["preco_unitario"] for i in st.session_state.get('itens', []))
    total = max(subtotal - desconto + taxa_extra, 0.0)
    st.markdown(f"<div style='font-weight:bold; font-size: 1.2em; color:#D4AF37;'>TOTAL: R$ {total:.2f}</div>", unsafe_allow_html=True)

    if st.button("🚀 Gerar Orçamento"):
        if not negocio.strip() or not cliente.strip() or not whatsapp.strip() or not st.session_state.get('itens'):
            st.error("Preencha todos os dados principais e adicione pelo menos um serviço.")
        else:
            # Registra no DB
            add_quote(username, cliente, total)
            st.success(f"Orçamento gerado para **{cliente}**.")

            # Monta mensagem WhatsApp
            mensagem = f"*ORÇAMENTO PREMIUM*\n\nCliente: {cliente}\nNegócio: {negocio}\n\nServiços:\n"
            for item in st.session_state['itens']:
                total_item = item["quantidade"] * item["preco_unitario"]
                mensagem += f"- {item['servico']} | Qtd: {item['quantidade']} | R$ {total_item:.2f}\n"
            mensagem += f"\nSubtotal: R$ {subtotal:.2f}\nDesconto: R$ {desconto:.2f}\nTaxa extra: R$ {taxa_extra:.2f}\n"
            mensagem += f"*TOTAL: R$ {total:.2f}*"

            numero = "".join(filter(str.isdigit, whatsapp))
            if not numero.startswith("55"):
                numero = "55" + numero
            link_wa = f"https://wa.me/{numero}?text={quote(mensagem)}"

            # Gera PDF
            pdf_buffer = gerar_pdf_bytes(cliente, negocio, st.session_state['itens'],
                                        subtotal, desconto, taxa_extra, total)

            st.text_area("Mensagem para WhatsApp", mensagem, height=200)
            st.markdown(f'''
                <a href="{link_wa}" target="_blank">
                  <button style="
                      background: linear-gradient(90deg,#25D366,#128C7E);
                      border:none; padding:12px 20px; color:white;
                      font-size:16px; border-radius:8px; cursor:pointer; margin-top:10px;">
                    📲 Enviar via WhatsApp
                  </button>
                </a>
            ''', unsafe_allow_html=True)
            st.download_button(
                label="📄 Baixar PDF",
                data=pdf_buffer,
                file_name=f"orcamento_{cliente}.pdf",
                mime="application/pdf"
            )

st.subheader("Histórico recente")
for row in recent_quotes(username, limit=5):
    st.write(f"- {row['client_name']} | R$ {float(row['total']):.2f} | {row['created_at']}")
