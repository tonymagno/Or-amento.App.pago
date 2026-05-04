# billing.py

import streamlit as st
from db import init_db

init_db()  # Garante que o DB esteja pronto (apesar de já haver em outros pontos)

def verificar_acesso(username):
    """
    Verifica se o usuário tem acesso premium.
    Por padrão, apenas o admin definido em secrets tem acesso.
    """
    # Se não há usuário logado, bloqueia
    if not username:
        return False
    # O admin (definido nos secrets) sempre tem acesso
    if username == st.secrets["ADMIN_USERNAME"]:
        return True
    # (Aqui seria implementada checagem real de assinatura)
    return False
