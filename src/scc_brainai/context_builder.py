"""Construction du contexte d'exécution.

Rassemble, via la passerelle, l'état nécessaire à une décision éclairée :
interrogation de l'**API** (système, readiness, graphe), consultation du
**Control Plane** (santé). Tolérant : une source indisponible est notée, jamais
fatale (le noyau doit fonctionner en mode dégradé).
"""

from __future__ import annotations

from typing import Any, Dict

from scc_brainai.core.model import Request
from scc_brainai.sources.scc_gateway import SccGateway


def build_context(request: Request, gateway: SccGateway, as_of: str) -> Dict[str, Any]:
    context: Dict[str, Any] = {
        "as_of": as_of,
        "request": request.to_dict(),
        "sources": gateway.available(),
        "notes": [],
    }

    context["system"] = _safe(gateway.system_status, context, "system.status")
    context["readiness"] = _safe(gateway.readiness, context, "system.readiness")
    context["graph"] = _safe(gateway.graph_summary, context, "graph.summary")
    context["health"] = _safe(gateway.health, context, "control_plane.health")
    return context


def _safe(fn, context: Dict[str, Any], label: str) -> Dict[str, Any]:
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 - source dégradée notée, non fatale
        context["notes"].append(f"{label} indisponible : {exc}")
        return {}


__all__ = ["build_context"]
