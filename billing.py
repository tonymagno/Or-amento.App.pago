from __future__ import annotations

from datetime import datetime, timezone

from db import get_user, set_subscription


def verificar_acesso(username: str) -> bool:
    user = get_user(username)
    if not user:
        return False

    if int(user["is_active"]) != 1:
        return False

    if user["subscription_status"] != "active":
        return False

    expires_at = user["plan_expires_at"]
    if expires_at:
        try:
            exp = datetime.fromisoformat(expires_at)
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < datetime.now(timezone.utc):
                return False
        except ValueError:
            return False

    return True


def ativar_plano(username: str, expires_at_iso: str | None = None) -> None:
    set_subscription(username, "active", expires_at_iso)


def bloquear_plano(username: str) -> None:
    set_subscription(username, "inactive", None)
