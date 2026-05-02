from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4
import json
import os
import re
import unicodedata

import streamlit as st

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except ModuleNotFoundError:
    REPORTLAB_AVAILABLE = False


# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Orçamento Premium", page_icon="💼", layout="wide")

USUARIOS = {
    "admin": "123456",
    "karine": "lashes2024",
    "Danilo": "123456",
}

ARQUIVO_HISTORICO = "historico_orcamentos.json"
LOGO_PADRAO = "logo.png"

COR_FUNDO = "#070B11"
COR_CARD = "#0F1722"
COR_BORDA = "#253244"
COR_TEXTO = "#F8FAFC"
COR_MUTED = "#94A3B8"
COR_PRIMARIA = "#6D5EF7"
COR_PRIMARIA_2 = "#8B7CFF"
COR_SUCESSO = "#34D399"
COR_DOURADO = "#D4AF37"
COR_DOURADO_2 = "#F2D16B"


# =========================
# ESTADO
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "itens" not in st.session_state:
    st.session_state.itens = []
if "historico" not in st.session_state:
    st.session_state.historico = []


# =========================
# UTILITÁRIOS
# =========================
def format_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def safe_filename(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    texto = re.sub(r"_+", "_", texto).strip("_")
    return texto or "orcamento"


def gerar_link_whatsapp(numero: str, mensagem: str) -> str:
    numero_limpo = "".join(ch for ch in numero if ch.isdigit())
    return f"https://wa.me/{numero_limpo}?text={quote(mensagem)}"


def calcular_total(itens: list[dict], desconto: float, taxa_extra: float) -> tuple[float, float]:
    subtotal = sum(item["quantidade"] * item["preco_unitario"] for item in itens)
    total = subtotal - desconto + taxa_extra
    return subtotal, max(total, 0.0)


def validar_campos_basicos(negocio: str, cliente: str, telefone: str, itens: list[dict]) -> str | None:
    if not negocio.strip():
        return "Informe o nome do negócio."
    if not cliente.strip():
        return "Informe o nome do cliente."
    if not telefone.strip():
        return "Informe o WhatsApp."
    if not itens:
        return "Adicione pelo menos um serviço."
    return None


def gerar_mensagem(
    cliente: str,
    negocio: str,
    itens: list[dict],
    subtotal: float,
    desconto: float,
    taxa_extra: float,
    total: float,
) -> str:
    linhas = [f"Olá, {cliente}! Segue seu orçamento da {negocio}:", ""]
    for i, item in enumerate(itens, start=1):
        total_item = item["quantidade"] * item["preco_unitario"]
        linhas.append(
            f"{i}. {item['servico']} | Qtd: {item['quantidade']} | "
            f"Unit: {format_brl(item['preco_unitario'])} | Total: {format_brl(total_item)}"
        )
    linhas += [
        "",
        f"Subtotal: {format_brl(subtotal)}",
        f"Desconto: {format_brl(desconto)}",
        f"Taxa extra: {format_brl(taxa_extra)}",
        f"Total final: {format_brl(total)}",
        "",
        f"{negocio}",
    ]
    return "\n".join(linhas)


# =========================
# HISTÓRICO
# =========================
def carregar_historico() -> list[dict]:
    if not os.path.exists(ARQUIVO_HISTORICO):
        return []
    try:
        with open(ARQUIVO_HISTORICO, "r", encoding="utf-8") as f:
            dados = json.load(f)
        return dados if isinstance(dados, list) else []
    except Exception:
        return []


def salvar_historico(registro: dict) -> None:
    dados = carregar_historico()
    dados.append(registro)
    with open(ARQUIVO_HISTORICO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


# =========================
# PDF
# =========================
def gerar_pdf_profissional(
    negocio: str,
    cliente: str,
    whatsapp: str,
    itens: list[dict],
    subtotal: float,
    desconto: float,
    taxa_extra: float,
    total: float,
    pasta_saida: str = "pdf_orcamentos",
    logo_path: str | None = LOGO_PADRAO,
) -> str:
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab não está instalado. Execute: pip install reportlab")

    pasta = Path(pasta_saida)
    pasta.mkdir(parents=True, exist_ok=True)
    nome_arquivo = f"orcamento_{safe_filename(cliente)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    caminho_pdf = pasta / nome_arquivo

    doc = SimpleDocTemplate(
        str(caminho_pdf),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TituloCentro",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            alignment=1,
            textColor=colors.HexColor("#111827"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubtituloCentro",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            alignment=1,
            textColor=colors.HexColor("#4B5563"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Info",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#111827"),
            spaceAfter=4,
        )
    )

    story: list = []
    if logo_path and os.path.exists(logo_path):
        try:
            img = Image(logo_path, width=38 * mm, height=38 * mm)
            img.hAlign = "CENTER"
            story.append(img)
            story.append(Spacer(1, 6))
        except Exception:
            pass

    story.append(Paragraph("ORÇAMENTO", styles["TituloCentro"]))
    story.append(Paragraph(negocio, styles["SubtituloCentro"]))
    story.append(Spacer(1, 4))

    top_data = [
        ["Cliente", cliente],
        ["WhatsApp", whatsapp],
        ["Data", datetime.now().strftime("%d/%m/%Y %H:%M")],
    ]
    top_table = Table(top_data, colWidths=[25 * mm, 155 * mm])
    top_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#111827")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(top_table)
    story.append(Spacer(1, 10))

    tabela_data = [["Serviço", "Qtd", "Valor unit.", "Total"]]
    for item in itens:
        total_item = item["quantidade"] * item["preco_unitario"]
        tabela_data.append(
            [
                Paragraph(item["servico"], styles["Normal"]),
                Paragraph(str(item["quantidade"]), styles["Normal"]),
                Paragraph(format_brl(item["preco_unitario"]), styles["Normal"]),
                Paragraph(format_brl(total_item), styles["Normal"]),
            ]
        )

    tabela = Table(tabela_data, colWidths=[86 * mm, 16 * mm, 32 * mm, 30 * mm])
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(tabela)
    story.append(Spacer(1, 12))

    resumo = [
        ["Subtotal", format_brl(subtotal)],
        ["Desconto", format_brl(desconto)],
        ["Taxa extra", format_brl(taxa_extra)],
        ["Total final", format_brl(total)],
    ]
    resumo_tabela = Table(resumo, colWidths=[130 * mm, 45 * mm])
    resumo_tabela.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E5E7EB")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, -1), (1, -1), "Helvetica-Bold"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(resumo_tabela)
    story.append(Spacer(1, 10))
    story.append(Paragraph("Obrigado pela preferência.", styles["Info"]))

    doc.build(story)
    return str(caminho_pdf)


# =========================
# LOGIN
# =========================
def aplicar_estilo_login() -> None:
    st.markdown(
        f"""
        <style>
            html, body, [class*="css"] {{
                margin: 0 !important;
                padding: 0 !important;
            }}

            .stApp {{
                background:
                    radial-gradient(circle at 16% 12%, rgba(212,175,55,0.16), transparent 28%),
                    radial-gradient(circle at 86% 2%, rgba(242,209,107,0.10), transparent 18%),
                    linear-gradient(180deg, {COR_FUNDO} 0%, #090D14 100%);
            }}

            header {{
                display: none !important;
            }}

           .block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    max-width: 100% !important;
}

            .main .block-container {{
                padding-top: 0 !important;
            }}

            .login-shell {
    min-height: 100vh;
    display: flex;
    align-items: center; /* 🔥 CENTRALIZA VERTICAL */
    justify-content: center;
    padding: 0;
    }
            }}

            .login-shell::before {{
                content: "";
                position: absolute;
                inset: 0;
                pointer-events: none;
                background:
                    linear-gradient(130deg, rgba(212,175,55,0.16), transparent 22%),
                    linear-gradient(320deg, rgba(212,175,55,0.16), transparent 22%);
                opacity: .30;
            }}

           .login-grid {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 1200px;
    margin: 0 auto; /* 🔥 CENTRALIZA */
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    align-items: center;
}

            .login-left {{
                display: flex;
                flex-direction: column;
                justify-content: center;
                padding: 0 18px 0 10px;
            }}

            .brand-icon {{
                width: 168px;
                height: 168px;
                border-radius: 26px;
                display: grid;
                place-items: center;
                margin-bottom: 10px;
                border: 1px solid rgba(212,175,55,0.10);
                background: linear-gradient(180deg, rgba(212,175,55,0.08), rgba(255,255,255,0.02));
                box-shadow: 0 20px 50px rgba(0,0,0,0.20);
            }}

            .brand-icon .emoji {{
                font-size: 4.7rem;
                line-height: 1;
                filter: drop-shadow(0 0 18px rgba(212,175,55,0.18));
            }}

            .login-kicker {{
                color: #D8C98A !important;
                letter-spacing: .24em;
                text-transform: uppercase;
                font-size: .74rem;
                font-weight: 800;
                margin-top: 10px;
            }}

            .login-title {{
                font-size: clamp(2.2rem, 3vw, 3.15rem);
                line-height: 1.02;
                font-weight: 900;
                margin: 12px 0 10px 0;
                letter-spacing: -0.02em;
            }}

            .login-title .gold {{
                color: {COR_DOURADO_2} !important;
            }}

            .login-sub {{
                color: {COR_MUTED} !important;
                margin-top: .35rem;
                line-height: 1.85;
                max-width: 640px;
                font-size: 1rem;
            }}

            .badge-row {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 18px;
            }}

            .badge {{
                background: rgba(212,175,55,0.10);
                border: 1px solid rgba(212,175,55,0.38);
                color: #F5E7B2 !important;
                border-radius: 999px;
                padding: 8px 14px;
                font-size: .82rem;
                font-weight: 800;
                box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            }}

            .login-note {{
                margin-top: 18px;
                color: {COR_MUTED} !important;
                line-height: 1.8;
                max-width: 640px;
            }}

            .login-card {
    width: 100%;
    max-width: 480px;
    margin: 0 auto; /* 🔥 CENTRALIZA */
}
            }}

            .login-card-top {{
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 18px;
            }}

            .shield {{
                width: 60px;
                height: 60px;
                border-radius: 18px;
                display: grid;
                place-items: center;
                background: linear-gradient(135deg, rgba(212,175,55,0.18), rgba(255,255,255,0.03));
                border: 1px solid rgba(212,175,55,0.45);
                color: #F2D16B !important;
                font-size: 1.55rem;
                box-shadow: 0 10px 24px rgba(0,0,0,0.16);
            }}

            .login-card-title {{
                font-size: 1.9rem;
                font-weight: 900;
                text-align: center;
                margin: 6px 0 4px 0;
                letter-spacing: -0.01em;
            }}

            .login-card-sub {{
                color: {COR_MUTED} !important;
                text-align: center;
                line-height: 1.7;
                margin-bottom: 18px;
            }}

            .stTextInput>div>div>input, .stTextInput input {{
                border-radius: 14px !important;
                border: 1px solid {COR_BORDA} !important;
                background-color: #0F172A !important;
                color: {COR_TEXTO} !important;
                height: 48px;
            }}

            .stButton>button {{
                width: 100%;
                border-radius: 14px;
                border: 1px solid rgba(212,175,55,0.25);
                padding: 0.92rem 1rem;
                font-weight: 900;
                background: linear-gradient(90deg, #D4AF37, #F2D16B);
                color: #111827;
                box-shadow: 0 12px 28px rgba(212,175,55,0.18);
            }}

            .stButton>button:hover {{
                filter: brightness(1.03);
            }}

            .login-footer {{
                margin-top: 12px;
                text-align: center;
                color: {COR_MUTED} !important;
                font-size: .86rem;
            }}

            @media (max-width: 900px) {{
                .login-shell {{
                    min-height: auto;
                    padding: 14px 10px 20px 10px;
                }}

                .login-grid {{
                    grid-template-columns: 1fr;
                    gap: 18px;
                    margin-top: 0;
                }}

                .login-left {{
                    padding: 0 4px;
                    text-align: center;
                    align-items: center;
                }}

                .login-card {{
                    max-width: 100%;
                    padding: 22px 18px;
                }}

                .brand-icon {{
                    width: 124px;
                    height: 124px;
                    margin-bottom: 4px;
                }}

                .brand-icon .emoji {{
                    font-size: 3.7rem;
                }}

                .login-title {{
                    font-size: 2rem;
                }}

                .login-sub, .login-note {{
                    max-width: 100%;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )
def tela_login() -> None:
    aplicar_estilo_login()

    st.markdown("<div class='login-shell'>", unsafe_allow_html=True)
    st.markdown("<div class='login-grid'>", unsafe_allow_html=True)

    st.markdown("<div class='login-left'>", unsafe_allow_html=True)
    st.markdown("<div class='brand-icon'><div class='emoji'>💼</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='login-kicker'>ACESSO RESTRITO</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-title'>Orçamento <span class='gold'>Premium</span></div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='login-sub'>Sistema completo para criar orçamentos profissionais, organizar múltiplos serviços e gerar propostas elegantes para fechar mais negócios.</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='badge-row'>"
        "<span class='badge'>Profissional</span>"
        "<span class='badge'>Seguro</span>"
        "<span class='badge'>Elegante</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='login-note'>Logo e identidade visual carregados automaticamente quando o arquivo <b>logo.png</b> estiver na pasta do app.</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='login-right'>", unsafe_allow_html=True)
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)
    st.markdown("<div class='login-card-top'><div class='shield'>🔒</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='login-card-title'>Acesso ao Sistema</div>", unsafe_allow_html=True)
    st.markdown("<div class='login-card-sub'>Entre com suas credenciais para continuar.</div>", unsafe_allow_html=True)

    with st.form("form_login"):
        usuario = st.text_input("Usuário", placeholder="Digite seu usuário")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
        entrar = st.form_submit_button("Entrar no Sistema")

    if entrar:
        if usuario in USUARIOS and USUARIOS[usuario] == senha:
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.markdown("<div class='login-footer'>Sistema protegido • Interface premium • Acesso restrito</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# =========================
# APP
# =========================
def aplicar_estilo_app() -> None:
    st.markdown(
        f"""
        <style>
            .stApp {{ background: linear-gradient(180deg, {COR_FUNDO} 0%, #0C1420 100%); }}
            h1, h2, h3, p, label, span, div {{ color: {COR_TEXTO} !important; }}
            .block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1250px; }}
            .hero {{
                background: radial-gradient(circle at top left, rgba(212,175,55,0.16), transparent 35%), linear-gradient(135deg, rgba(17,24,39,0.98), rgba(10,14,22,0.98));
                border: 1px solid {COR_BORDA};
                border-radius: 24px;
                padding: 22px;
                margin-bottom: 18px;
                box-shadow: 0 18px 60px rgba(0,0,0,0.25);
            }}
            .hero-title {{ font-size: 2rem; font-weight: 800; margin: 0; }}
            .hero-sub {{ color: {COR_MUTED} !important; font-size: 0.95rem; margin-top: 4px; }}
            .card-box {{
                background: linear-gradient(180deg, {COR_CARD}, #0B1320);
                border: 1px solid {COR_BORDA};
                border-radius: 16px;
                padding: 14px 16px;
                margin-bottom: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.18);
            }}
            .metric-box {{
                background: linear-gradient(180deg, #111827, #0F172A);
                border: 1px solid {COR_BORDA};
                border-radius: 18px;
                padding: 16px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.18);
            }}
            .metric-title {{ color: {COR_MUTED} !important; font-size: 0.78rem; text-transform: uppercase; letter-spacing: .12em; }}
            .metric-value {{ color: {COR_TEXTO} !important; font-size: 1.45rem; font-weight: 800; margin-top: 4px; }}
            .total-box {{
                background: linear-gradient(90deg, rgba(212,175,55,0.18), rgba(52,211,153,0.12));
                border: 1px solid rgba(212,175,55,0.45);
                border-radius: 18px;
                padding: 16px 18px;
                font-size: 1.15rem;
                font-weight: 800;
                color: {COR_DOURADO_2} !important;
                margin: 10px 0 18px 0;
            }}
            .stButton>button {{
                width: 100%;
                border-radius: 12px;
                border: 1px solid transparent;
                padding: 0.78rem 1rem;
                font-weight: 800;
                background: linear-gradient(90deg, {COR_PRIMARIA}, {COR_PRIMARIA_2});
                color: white;
                box-shadow: 0 10px 24px rgba(109,94,247,0.22);
            }}
            .stButton>button:hover {{ filter: brightness(1.05); }}
            .stTextInput>div>div>input, .stNumberInput>div>div>input {{
                border-radius: 12px !important;
                border: 1px solid {COR_BORDA} !important;
                background-color: #0F172A !important;
                color: {COR_TEXTO} !important;
            }}
            .stTextArea textarea {{
                border-radius: 12px !important;
                border: 1px solid {COR_BORDA} !important;
                background-color: #0F172A !important;
                color: {COR_TEXTO} !important;
            }}
            .stTabs [data-baseweb="tab-list"] {{ gap: 8px; }}
            .stTabs [data-baseweb="tab"] {{
                background: #0F172A;
                border: 1px solid {COR_BORDA};
                border-radius: 12px;
                padding: 10px 16px;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    left, right = st.columns([1.1, 5])
    with left:
        if os.path.exists(LOGO_PADRAO):
            st.image(LOGO_PADRAO, width=88)
        else:
            st.markdown("<div style='font-size:58px; line-height:1;'>💼</div>", unsafe_allow_html=True)
    with right:
        st.markdown(
            f"""
            <div class='hero'>
                <div class='hero-title'>Orçamento Premium</div>
                <div class='hero-sub'>Painel elegante para múltiplos serviços, histórico, PDF profissional e envio pelo WhatsApp.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_metric(title: str, value: str) -> str:
    return f"<div class='metric-box'><div class='metric-title'>{title}</div><div class='metric-value'>{value}</div></div>"


def logout() -> None:
    st.session_state.logado = False
    st.session_state.usuario = ""
    st.rerun()


def app_principal() -> None:
    aplicar_estilo_app()
    render_hero()

    header_left, header_right = st.columns([5, 1.5])
    with header_right:
        st.markdown(f"**Usuário:** {st.session_state.usuario}")
        if st.button("Sair"):
            logout()

    tab_orc, tab_hist, tab_info = st.tabs(["📄 Orçamento", "📂 Histórico", "✨ Premium"])

    with tab_orc:
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
                            "id": str(uuid4()),
                            "servico": servico.strip(),
                            "quantidade": int(qtd),
                            "preco_unitario": float(preco),
                        }
                    )
                    st.success("Serviço adicionado.")
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

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("🧹 Limpar itens"):
                        st.session_state.itens = []
                        st.rerun()
                with col_b:
                    st.write(f"**Itens no orçamento:** {len(st.session_state.itens)}")
            else:
                st.caption("Adicione um ou mais serviços para montar o orçamento.")

        with right:
            desconto = st.number_input("Desconto", min_value=0.0, step=1.0, value=0.0)
            taxa_extra = st.number_input("Taxa extra", min_value=0.0, step=1.0, value=0.0)

            if st.session_state.itens:
                subtotal, total = calcular_total(st.session_state.itens, desconto, taxa_extra)
                st.markdown(f"<div class='total-box'>TOTAL FINAL: {format_brl(total)}</div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(render_metric("Subtotal", format_brl(subtotal)), unsafe_allow_html=True)
                with c2:
                    st.markdown(render_metric("Serviços", str(len(st.session_state.itens))), unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='total-box'>Adicione serviços para visualizar o total</div>", unsafe_allow_html=True)
                subtotal, total = 0.0, 0.0

            st.markdown("---")
            if st.button("🚀 Gerar orçamento"):
                erro = validar_campos_basicos(negocio, cliente, whatsapp, st.session_state.itens)
                if erro:
                    st.error(erro)
                    return

                subtotal, total = calcular_total(st.session_state.itens, desconto, taxa_extra)
                mensagem = gerar_mensagem(cliente, negocio, st.session_state.itens, subtotal, desconto, taxa_extra, total)
                link = gerar_link_whatsapp(whatsapp, mensagem)

                st.success("Orçamento gerado com sucesso.")
                st.text_area("Mensagem pronta", mensagem, height=260)
                st.markdown(f"### 📲 [Abrir WhatsApp]({link})")

                registro = {
                    "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "negocio": negocio,
                    "cliente": cliente,
                    "whatsapp": whatsapp,
                    "itens": st.session_state.itens,
                    "subtotal": subtotal,
                    "desconto": desconto,
                    "taxa_extra": taxa_extra,
                    "total": total,
                }

                try:
                    pdf_path = gerar_pdf_profissional(
                        negocio=negocio,
                        cliente=cliente,
                        whatsapp=whatsapp,
                        itens=st.session_state.itens,
                        subtotal=subtotal,
                        desconto=desconto,
                        taxa_extra=taxa_extra,
                        total=total,
                        logo_path=LOGO_PADRAO,
                    )
                    st.success(f"PDF gerado: {pdf_path}")
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            "⬇️ Baixar PDF",
                            data=f.read(),
                            file_name=Path(pdf_path).name,
                            mime="application/pdf",
                        )
                except Exception as exc:
                    st.warning(f"PDF não gerado: {exc}")

                try:
                    salvar_historico(registro)
                    st.session_state.historico = carregar_historico()
                except Exception:
                    pass

    with tab_hist:
        st.subheader("Histórico recente")
        historico = st.session_state.historico[-10:]
        if not historico:
            st.caption("Nenhum orçamento salvo ainda.")
        else:
            for item in reversed(historico):
                with st.expander(f"{item.get('data', '')} - {item.get('cliente', '')} - {format_brl(float(item.get('total', 0)))}"):
                    st.write(f"**Negócio:** {item.get('negocio', '')}")
                    st.write(f"**WhatsApp:** {item.get('whatsapp', '')}")
                    st.write(f"**Subtotal:** {format_brl(float(item.get('subtotal', 0)))}")
                    st.write(f"**Desconto:** {format_brl(float(item.get('desconto', 0)))}")
                    st.write(f"**Taxa extra:** {format_brl(float(item.get('taxa_extra', 0)))}")
                    st.write(f"**Total:** {format_brl(float(item.get('total', 0)))}")
                    st.write("**Serviços:**")
                    for s in item.get("itens", []):
                        st.write(f"- {s.get('servico', '')} | {s.get('quantidade', '')} x {format_brl(float(s.get('preco_unitario', 0)))}")

    with tab_info:
        st.subheader("Como deixar com cara de sistema pago")
        st.write("- Adicione um logo consistente em `logo.png`.")
        st.write("- Padronize cores e nomes dos serviços.")
        st.write("- Use os PDFs como propostas oficiais.")
        st.write("- Publique o app e adicione à tela inicial no celular.")
        st.write("- Depois, conecte pagamento e libere acesso por assinatura.")

    st.caption("Visual premium, fluxo limpo e base pronta para monetização.")


# =========================
# EXECUÇÃO
# =========================
if not st.session_state.logado:
    tela_login()
else:
    app_principal()
