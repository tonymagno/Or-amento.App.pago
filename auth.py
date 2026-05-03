from __future__ import annotations

from datetime import datetime, timedelta, timezone

import streamlit as st

from db import create_user, get_user, init_db, user_count, verify_password


def _secret(key: str, default: str) -> str:
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def bootstrap_admin() -> None:
    init_db()
    if user_count() == 0:
        admin_user = _secret("ADMIN_USERNAME", "admin")
        admin_pass = _secret("ADMIN_PASSWORD", "1234")
        create_user(
            admin_user,
            admin_pass,
            role="admin",
            subscription_status="active",
            plan_expires_at=(datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
        )


def usuario_logado() -> bool:
    return bool(st.session_state.get("logado", False))


def usuario_atual() -> str:
    return st.session_state.get("usuario", "")


def fazer_logout() -> None:
    st.session_state.logado = False
    st.session_state.usuario = ""
    st.rerun()


def tela_login() -> None:
    bootstrap_admin()

    st.markdown(
        """
        <style>
            .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
            header, footer { visibility: hidden; }
            .stApp {
                background: radial-gradient(circle at top left, #0f172a, #020617);
            }
            .login-wrap {
    min-height: 100vh;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: 8px 18px 12px;
    position: relative;
    overflow: hidden;
}
            .login-box {
    width: min(1100px, 100%);
    display: grid;
    grid-template-columns: 1.15fr 0.85fr;
    gap: 18px;
    align-items: center;
}
            .hero {
                color: white;
                padding: 12px 0;
            }
            .kicker {
                color: #f5d46b;
                text-transform: uppercase;
                letter-spacing: .22em;
                font-size: .74rem;
                font-weight: 800;
            }
            .title {
                font-size: clamp(2.3rem, 3vw, 3.4rem);
                font-weight: 900;
                line-height: 1.02;
                margin: 12px 0 12px 0;
            }
            .gold { color: #f2d16b; }
            .sub {
                color: #94a3b8;
                line-height: 1.8;
                max-width: 620px;
                font-size: 1rem;
            }
            .badges { display:flex; gap:10px; flex-wrap:wrap; margin-top:18px; }
            .badge {
                color:#f5e7b2;
                border:1px solid rgba(212,175,55,.35);
                background: rgba(212,175,55,.08);
                padding:7px 14px;
                border-radius:999px;
                font-size:.82rem;
                font-weight:800;
            }
.card {
    background: linear-gradient(180deg, rgba(16,24,39,.98), rgba(11,18,32,.98));
    border: 1px solid rgba(255,255,255,.10);
    border-radius: 24px;
    padding: 24px 28px 22px;
    box-shadow: 0 18px 48px rgba(0,0,0,.28);
    backdrop-filter: blur(12px);
    max-width: 520px;
    margin-left: auto;
}
            .shield {
                width: 60px; height: 60px; border-radius: 18px;
                display:grid; place-items:center;
                margin: 0 auto 14px auto;
                background: linear-gradient(135deg, rgba(212,175,55,.18), rgba(255,255,255,.03));
                border: 1px solid rgba(212,175,55,.45);
                color:#f2d16b; font-size:1.55rem;
            }
            .card-title { margin: 2px 0 2px 0; }
.card-sub { margin-bottom: 12px; }
            .stTextInput>div>div>input {
                border-radius: 14px !important;
                border: 1px solid #253244 !important;
                background-color: #0f172a !important;
                color: #f8fafc !important;
                height: 48px;
            }
            .stButton>button {
                width: 100%;
                border-radius: 14px;
                border: 1px solid rgba(212,175,55,.25);
                padding: .92rem 1rem;
                font-weight: 900;
                background: linear-gradient(90deg, #D4AF37, #F2D16B);
                color: #111827;
                box-shadow: 0 12px 28px rgba(212,175,55,.18);
            }
            @media (max-width: 900px) {
                .login-box { grid-template-columns: 1fr; }
                .card { max-width: 100%; margin-left: 0; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.15, 0.85], gap="large")

    with col1:
        st.markdown(
            """
            <div class='hero'>
                <div class='kicker'>ACESSO RESTRITO</div>
                <div class='title'>Orçamento <span class='gold'>Premium</span></div>
                <div class='sub'>
                    Sistema profissional para criar orçamentos, organizar múltiplos serviços
                    e gerar propostas elegantes para fechar mais negócios.
                </div>
                <div class='badges'>
                    <span class='badge'>Profissional</span>
                    <span class='badge'>Seguro</span>
                    <span class='badge'>Elegante</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class='card'>
                <div class='shield'>🔒</div>
                <div class='card-title'>Acesso ao Sistema</div>
                <div class='card-sub'>Entre com suas credenciais para continuar.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("form_login"):
    usuario = st.text_input(
        "Usuário",
        placeholder="Digite seu usuário",
        label_visibility="collapsed",
    )
    senha = st.text_input(
        "Senha",
        type="password",
        placeholder="Digite sua senha",
        label_visibility="collapsed",
    )
    entrar = st.form_submit_button("Entrar no Sistema")

        if entrar:
            user = get_user(usuario)
            if user and verify_password(senha, user["password_salt"], user["password_hash"]):
                st.session_state.logado = True
                st.session_state.usuario = usuario
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()
