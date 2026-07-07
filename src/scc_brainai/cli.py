"""CLI du noyau BrainAI (``scc-brainai``).

Expose la demande principale (``ask``) et l'introspection (status, self-check,
providers, intent). Sortie JSON déterministe.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, List, Optional

from scc_brainai import __version__
from scc_brainai.core.config import load_config
from scc_brainai.kernel import BrainAIKernel, classify_intent


def _out(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _kernel(args) -> BrainAIKernel:
    return BrainAIKernel(config=load_config(args.config))


def cmd_ask(args) -> int:
    kernel = _kernel(args)
    options = {"deep": bool(args.deep)}
    order = args.provider_order.split(",") if args.provider_order else None
    resp = kernel.handle(args.query, intent=args.intent, options=options, provider_order=order)
    _out(resp)
    return 0 if resp.get("ok") else 1


def cmd_status(args) -> int:
    _out(_kernel(args).status()); return 0


def cmd_self_check(args) -> int:
    sc = _kernel(args).self_check()
    _out(sc)
    return 0 if sc["ok"] else 1


def cmd_providers(args) -> int:
    _out(_kernel(args).providers.to_dict()); return 0


def cmd_intent(args) -> int:
    _out({"query": args.query, "intent": classify_intent(args.query)}); return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scc-brainai",
                                     description="Noyau BrainAI — chef d'orchestre cognitif de SCC.")
    parser.add_argument("--version", action="version", version=f"scc-brainai {__version__}")
    parser.add_argument("--config", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    p_ask = sub.add_parser("ask", help="Adresser une demande au noyau.")
    p_ask.add_argument("query")
    p_ask.add_argument("--deep", action="store_true", help="Passe cognitive complète (5 moteurs).")
    p_ask.add_argument("--intent", default=None, help="Forcer l'intention.")
    p_ask.add_argument("--provider-order", default=None, help="Ordre de préférence des IA (a,b,c).")
    p_ask.set_defaults(func=cmd_ask)

    sub.add_parser("status", help="État du noyau et des sources.").set_defaults(func=cmd_status)
    sub.add_parser("self-check", help="Auto-vérification du noyau.").set_defaults(func=cmd_self_check)
    sub.add_parser("providers", help="Fournisseurs d'intelligence enregistrés.").set_defaults(func=cmd_providers)

    p_intent = sub.add_parser("intent", help="Classer l'intention d'une demande.")
    p_intent.add_argument("query")
    p_intent.set_defaults(func=cmd_intent)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


__all__ = ["main", "build_parser"]
