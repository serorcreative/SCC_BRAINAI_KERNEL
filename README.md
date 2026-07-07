# SCC BrainAI Kernel

**Noyau officiel de BrainAI — le chef d'orchestre cognitif de Seror Créative Core.**

BrainAI **coordonne** les composants SCC déjà construits ; il n'en remplace ni n'en
modifie aucun. Il reçoit une demande, construit un contexte, planifie, sélectionne
et **orchestre des Agents sous gouvernance**, consolide et produit une réponse
structurée — **de façon entièrement déterministe**.

> **Aucune IA obligatoire.** La cognition par défaut est déterministe (règles). Les
> IA externes (Claude, ChatGPT, Gemini…) sont des **capacités optionnelles**
> branchables sans modifier l'architecture du noyau. **Aucun réseau. Stdlib pur.**

## Réutilisation stricte (aucune duplication)

| Composant | Interface publique réutilisée |
|-----------|-------------------------------|
| **API (08)** | `SccApi.dispatch` — graphe, catalogues, système, readiness |
| **Runtime (07)** | `RuntimeEngine` + `SupervisorPort` — exécution **gouvernée** |
| **Control Plane (09)** | `ControlPlane` — santé, observabilité |
| **Graphe / Doctrines / ADR** | via `graph.*` (relation `governs` du méta-modèle) |

BrainAI **incarne** l'Agent Superviseur (`SCC-AGENT-0020`, méta-modèle) : il se
branche sur le Runtime via `SupervisorPort` sans jamais court-circuiter la
gouvernance (règle dure T3, vetos restent souverains).

## Installation

```bash
cd 10_BRAINAI
python -m pip install -e .        # expose la commande `scc-brainai`
```

Aucune dépendance externe.

## Utilisation (CLI)

```bash
scc-brainai ask "Quelles doctrines gouvernent la gouvernance ?"
scc-brainai ask "état de santé du système"
scc-brainai ask "analyse l'architecture" --deep      # passe cognitive complète (5 moteurs)
scc-brainai ask "..." --provider-order claude,deterministic   # préférence IA (repli garanti)
scc-brainai intent "montre le graphe"                # classification d'intention
scc-brainai status | providers | self-check
```

## Utilisation (Python)

```python
from scc_brainai import BrainAIKernel

kernel = BrainAIKernel()
response = kernel.handle("Explique l'architecture de raisonnement", options={"deep": True})
print(response["synthesis"])
```

## Pipeline (déterministe)

```
demande → intention → contexte (API + graphe + Control Plane)
        → sélection d'agents → doctrines/ADR (governs) → plan
        → orchestration (job Runtime gouverné) → consolidation → réponse
```

Détails : [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) ·
[`docs/ORCHESTRATION.md`](docs/ORCHESTRATION.md) ·
[`docs/INTELLIGENCE_PROVIDERS.md`](docs/INTELLIGENCE_PROVIDERS.md) ·
[`docs/DETERMINISM.md`](docs/DETERMINISM.md).

## Tests

```bash
python -m pytest -q      # 21 tests (intégration déterministe sur composants réels)
```
