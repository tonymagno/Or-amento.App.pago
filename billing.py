# billing.py

import streamlit as st
from db import init_db

# Inicializa o DB (caso ainda não exista tabela de assinaturas)
# Por simplicidade, trata 'billing' no próprio DB de usuários
def verificar_acesso(username):
    """
    Retorna True se o usuário tiver assinatura ativa.
    Por exemplo, podemos usar uma tabela ou flag; aqui assumimos True para o admin.
    """
    # Usuário administrador sempre tem acesso completo
    if username == st.secrets["ADMIN_USERNAME"]:
        return True
    # (Aqui você poderia verificar outra tabela de assinaturas no DB)
    # Simulação: usuários comuns não têm acesso
    return False
