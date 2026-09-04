from app.auth import Principal
from app.persist import append_audit, list_audit


def log(
    principal: Principal | None,
    action: str,
    product_id: str = "",
    detail: str = "",
) -> None:
    actor = "anonymous"
    role = ""
    if principal is not None:
        actor = principal.email or principal.name
        role = principal.role
    append_audit(
        actor=actor,
        role=role,
        action=action,
        product_id=product_id,
        detail=detail,
    )


def for_product(product_id: str) -> list[dict]:
    return list_audit(product_id)
