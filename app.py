from __future__ import annotations

from datetime import datetime
from io import BytesIO
from urllib.parse import quote
import textwrap
streamlit
reportlab


from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import streamlit as st

from auth import fazer_logout, tela_login, usuario_atual, usuario_logado
from billing import verificar_acesso
from db import add_quote, init_db, recent_quotes

st.set_page_config(page_title="Orçamento Premium", page_icon="💼", layout="wide")
init_db()

def format_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def calcular_total(itens: list[dict], desconto: float, taxa_extra: float) -> tuple[float, float]:
    subtotal = sum(item["quantidade"] * item["preco_unitario"] for item in itens)
    total = subtotal - desconto + taxa_extra
    return subtotal, max(total, 0.0)


def gerar_mensagem_whatsapp(cliente, negocio, itens, subtotal, desconto, taxa_extra, total):
    linhas = [
        "*ORÇAMENTO PREMIUM*",
        "",
        f"Cliente: {cliente}",
        f"Negócio: {negocio}",
        "",
        "Serviços:"
    ]

    for item in itens:
        total_item = item["quantidade"] * item["preco_unitario"]
        linhas.append(
            f"- {item['servico']} | Qtd: {item['quantidade']} | R$ {total_item}"
        )

    linhas.append("")
    linhas.append(f"Subtotal: R$ {subtotal}")
    linhas.append(f"Desconto: R$ {desconto}")
    linhas.append(f"Taxa extra: R$ {taxa_extra}")
    linhas.append(f"TOTAL: R$ {total}")

    return "\n".join(linhas)

def gerar_pdf_bytes(
    cliente: str,
    negocio: str,
    itens: list[dict],
    subtotal: float,
    desconto: float,
    taxa_extra: float,
    total: float,
) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4

    x = 50
    y = altura - 60

    c.setFont("Helvetica-Bold", 18)
    c.drawString(x, y, "ORÇAMENTO PREMIUM")
    y -= 28

    c.setFont("Helvetica", 11)
    c.drawString(x, y, f"Cliente: {cliente}")
    y -= 18
    c.drawString(x, y, f"Negócio: {negocio}")
    y -= 24

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x, y, "Serviços")
    y -= 18

    c.setFont("Helvetica", 10)
    for i, item in enumerate(itens, start=1):
        total_item = item["quantidade"] * item["preco_unitario"]
        texto = (
            f"{i}. {item['servico']} | Qtd: {item['quantidade']} | "
            f"Unit: {format_brl(item['preco_unitario'])} | Total: {format_brl(total_item)}"
        )
        linhas = textwrap.wrap(texto, width=95)

        for linha in linhas:
            if y < 70:
                c.showPage()
                y = altura - 60
                c.setFont("Helvetica", 10)
            c.drawString(x, y, linha)
            y -= 14
        y -= 4

    y -= 8
    if y < 120:
        c.showPage()
        y = altura - 60

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x, y, f"Subtotal: {format_brl(subtotal)}")
    y -= 16
    c.drawString(x, y, f"Desconto: {format_brl(desconto)}")
    y -= 16
    c.drawString(x, y, f"Taxa extra: {format_brl(taxa_extra)}")
    y -= 16
    c.drawString(x, y, f"Total final: {format_brl(total)}")

    c.save()
    buffer.seek(0)
    return buffer


def gerar_link_whatsapp(telefone: str, mensagem: str) -> str:
    numero = "".join(ch for ch in telefone if ch.isdigit())
    if not numero.startswith("55"):
        numero = "55" + numero
    return f"https://wa.me/{numero}?text={quote(mensagem)}"

st.markdown(
    """
    <style>
        .stApp { background: linear-gradient(180deg, #070B11 0%, #0C1420 100%); }
        .block-container { padding-top: 1rem; max-width: 1250px; }
        .hero {
            with right:
    desconto = st.number_input("Desconto", min_value=0.0, step=1.0, value=0.0)
    taxa_extra = st.number_input("Taxa extra", min_value=0.0, step=1.0, value=0.0)

    subtotal, total = (
        calcular_total(st.session_state.itens, desconto, taxa_extra)
        if st.session_state.itens
        else (0.0, 0.0)
    )

    st.markdown(
        f"<div class='total-box'>TOTAL FINAL: {format_brl(total)}</div>",
        unsafe_allow_html=True,
    )

    if st.button("🚀 Gerar orçamento"):
        if not negocio.strip() or not cliente.strip() or not whatsapp.strip() or not st.session_state.itens:
            st.error("Preencha os dados principais e adicione pelo menos um serviço.")
        else:
            add_quote(username, cliente, total)

            mensagem = gerar_mensagem_whatsapp(
                cliente=cliente,
                negocio=negocio,
                itens=st.session_state.itens,
                subtotal=subtotal,
                desconto=desconto,
                taxa_extra=taxa_extra,
                total=total,
            )
            link_whatsapp = gerar_link_whatsapp(whatsapp, mensagem)
            pdf_bytes = gerar_pdf_bytes(
                cliente=cliente,
                negocio=negocio,
                itens=st.session_state.itens,
                subtotal=subtotal,
                desconto=desconto,
                taxa_extra=taxa_extra,
                total=total,
            )

            st.success(f"Orçamento gerado para {cliente}.")
            st.text_area("Mensagem pronta para WhatsApp", mensagem, height=220)

            st.link_button("📲 Enviar via WhatsApp", link_whatsapp)

            st.download_button(
                label="📄 Baixar PDF",
                data=pdf_bytes.getvalue(),
                file_name=f"orcamento_{cliente.strip().replace(' ', '_').lower()}.pdf",
                mime="application/pdf",
            )

    st.subheader("Histórico recente")
    for row in recent_quotes(username, limit=5):
        st.write(f"- {row['client_name']} | {format_brl(float(row['total']))} | {row['created_at']}")
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

if "itens" not in st.session_state:
    st.session_state.itens = []

if not usuario_logado():
    tela_login()

username = usuario_atual()

if not verificar_acesso(username):
    st.warning("Acesso bloqueado. Assinatura necessária.")
    st.stop()

st.markdown(
    """
    <div class='hero'>
        <h1 style='margin:0;color:white;'>Sistema de Orçamento Premium</h1>
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
            add_quote(username, cliente, total)
            st.success(f"Orçamento gerado para {cliente}.")

    st.subheader("Histórico recente")
    for row in recent_quotes(username, limit=5):
        st.write(f"- {row['client_name']} | {format_brl(float(row['total']))} | {row['created_at']}")
