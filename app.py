from __future__ import annotations

from datetime import datetime

import streamlit as st

from auth import fazer_logout, tela_login, usuario_atual, usuario_logado
from billing import verificar_acesso
from db import add_quote, init_db, recent_quotes

st.set_page_config(page_title="Orçamento Premium", page_icon="💼", layout="wide")

init_db()

if not usuario_logado():
    tela_login()

username = usuario_atual()

if not verificar_acesso(username):
    st.warning("Acesso bloqueado. Assinatura necessária.")
    st.stop()

st.markdown(
    """
    <style>
        .stApp { background: linear-gradient(180deg, #070B11 0%, #0C1420 100%); }
        .block-container { padding-top: 1rem; max-width: 1250px; }
        .hero {
            background: linear-gradient(135deg, rgba(17,24,39,.98), rgba(10,14,22,.98));
            border: 1px solid #253244;
            border-radius: 24px;
            padding: 22px;
            margin-bottom: 18px;
        }
        .card-box {
            background: linear-gradient(180deg, #0F1722, #0B1320);
            border: 1px solid #253244;
            border-radius: 16px;
            padding: 14px 16px;
            margin-bottom: 10px;
        }
        .total-box {
            background: linear-gradient(90deg, rgba(212,175,55,.18), rgba(52,211,153,.12));
            border: 1px solid rgba(212,175,55,.45);
            border-radius: 18px;
            padding: 16px 18px;
            font-size: 1.15rem;
            font-weight: 800;
            color: #F2D16B;
            margin: 10px 0 18px 0;
        }
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            font-weight: 800;
            background: linear-gradient(90deg, #6D5EF7, #8B7CFF);
            color: white;
            border: none;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def format_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_total(itens: list[dict], desconto: float, taxa_extra: float) -> tuple[float, float]:
    subtotal = sum(item["quantidade"] * item["preco_unitario"] for item in itens)
    total = subtotal - desconto + taxa_extra
    return subtotal, max(total, 0.0)

if "itens" not in st.session_state:
    st.session_state.itens = []

st.markdown(
    """
    <div class='hero'>
        <h1 style='margin:0;color:white;'>Orçamento Premium</h1>
        <p style='margin:6px 0 0 0;color:#94A3B8;'>Painel elegante para múltiplos serviços, histórico e PDF profissional.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

top_left, top_right = st.columns([5, 1.2])
with top_right:
    st.markdown(f"**Usuário:** {username}")
    if st.button("Sair"):
        fazer_logout()

left, right = st.columns([1.35, 0.95], gap="large")

with left:
    st.subheader("Dados principais")
    negocio = st.text_input("Nome do negócio", placeholder="Ex.: Karine Lashes Designer")
    cliente = st.text_input("Cliente", placeholder="Ex.: Marcia")
    whatsapp = st.text_input("WhatsApp", placeholder="Ex.: 5512999999999")

    st.subheader("Adicionar serviço")
    with st.form("form_servico", clear_on_submit=True):
        servico = st.text_input("Descrição do serviço", placeholder="Ex.: Extensão de cílios")
        qtd = st.number_input("Quantidade", min_value=1, step=1, value=1)
        preco = st.number_input("Preço unitário", min_value=0.0, step=1.0, value=0.0)
        add = st.form_submit_button("➕ Adicionar serviço")

    if add:
        if not servico.strip():
            st.error("Informe a descrição do serviço.")
        else:
            st.session_state.itens.append(
                {
                    "id": str(datetime.now().timestamp()),
                    "servico": servico.strip(),
                    "quantidade": int(qtd),
                    "preco_unitario": float(preco),
                }
            )
            st.rerun()

    if st.session_state.itens:
        st.subheader("Serviços adicionados")
        for item in st.session_state.itens.copy():
            total_item = item["quantidade"] * item["preco_unitario"]
            c1, c2, c3, c4, c5 = st.columns([4.2, 1.0, 1.3, 1.3, 0.5])
            with c1:
                st.markdown(f"<div class='card-box'><b>{item['servico']}</b></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='card-box'>Qtd<br><b>{item['quantidade']}</b></div>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='card-box'>Unit<br><b>{format_brl(item['preco_unitario'])}</b></div>", unsafe_allow_html=True)
            with c4:
                st.markdown(f"<div class='card-box'>Total<br><b>{format_brl(total_item)}</b></div>", unsafe_allow_html=True)
            with c5:
                if st.button("✖", key=f"rm_{item['id']}"):
                    st.session_state.itens = [i for i in st.session_state.itens if i["id"] != item["id"]]
                    st.rerun()

        if st.button("🧹 Limpar itens"):
            st.session_state.itens = []
            st.rerun()

with right:
    desconto = st.number_input("Desconto", min_value=0.0, step=1.0, value=0.0)
    taxa_extra = st.number_input("Taxa extra", min_value=0.0, step=1.0, value=0.0)

    subtotal, total = calcular_total(st.session_state.itens, desconto, taxa_extra) if st.session_state.itens else (0.0, 0.0)
    st.markdown(f"<div class='total-box'>TOTAL FINAL: {format_brl(total)}</div>", unsafe_allow_html=True)

    if st.button("🚀 Gerar orçamento"):
        if not negocio.strip() or not cliente.strip() or not whatsapp.strip() or not st.session_state.itens:
            st.error("Preencha os dados principais e adicione pelo menos um serviço.")
        else:
            texto = f"{cliente} - {format_brl(total)}"
            add_quote(username, cliente, total)
            st.success(f"Orçamento gerado para {cliente}.")

    st.subheader("Histórico recente")
    for row in recent_quotes(username, limit=5):
        st.write(f"- {row['client_name']} | {format_brl(float(row['total']))} | {row['created_at']}")
