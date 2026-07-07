# Architecture du noyau BrainAI

## 1. Position dans SCC

BrainAI est la couche la plus haute (`10`) : le **chef d'orchestre cognitif**. Il se
place au-dessus de tout et **coordonne** l'existant via des interfaces publiques.

```
▶ BrainAI (10) ── kernel : intention · contexte · plan · agents · orchestration · synthèse
        │
   ┌────┼───────────────┬───────────────────────┐
   │ SccGateway (réutilisation stricte)          │
   ▼                     ▼                        ▼
 API (08)          Runtime (07)             Control Plane (09)
 dispatch()        RuntimeEngine +          ControlPlane.health()
 graphe/catalogues SupervisorPort           observabilité
        │                     (BrainAI incarne SCC-AGENT-0020)
   Graphe · Doctrines · ADR (via relation `governs` du méta-modèle)
```

BrainAI **ne remplace aucun composant**. Il n'ajoute qu'une chose : la
**coordination cognitive** — décider quoi interroger, quels agents mobiliser, dans
quel ordre, et comment consolider.

## 2. Réutilisation, jamais duplication

| Besoin du Kernel | Fourni par | Interface |
|------------------|-----------|-----------|
| état, readiness, graphe, catalogues | API (08) | `SccApi.dispatch` |
| doctrines/ADR pertinents | Graphe (via API) | `graph.neighbors` relation `governs`/`references` |
| exécution gouvernée d'un job | Runtime (07) | `RuntimeEngine` + `SupervisorPort` |
| santé consolidée / alertes | Control Plane (09) | `ControlPlane.health()` |

Rien de ceci n'est réécrit : la passerelle `SccGateway` localise les trois `src/`
et les invoque. Aucun composant n'est modifié.

## 3. Pipeline du noyau

`BrainAIKernel.handle(query)` déroule douze responsabilités, dans l'ordre :

1. **recevoir la demande** → `Request` normalisée ;
2. **classer l'intention** (déterministe, mots-clés) : cognition / gouvernance /
   graphe / inspection / général ;
3. **construire le contexte** : interroge l'API (système, readiness, graphe) et le
   Control Plane (santé) ;
4. **consulter le graphe** : compteurs, nœuds pertinents ;
5. **consulter doctrines & ADR** : via la relation `governs` (par agent) ;
6. **interroger le Runtime** : capacités, puis exécution gouvernée ;
7. **consulter le Control Plane** : santé globale ;
8. **construire un plan** : une étape par agent, avec action et doctrines ;
9. **sélectionner les agents** : rôles réels du catalogue selon l'intention ;
10. **orchestrer leur exécution** : job Runtime gouverné + contributions ;
11. **consolider les résultats** : gouvernance, contributions ;
12. **produire une réponse structurée** : contexte, plan, agents, gouvernance,
    runtime, contributions, synthèse.

## 4. BrainAI incarne le Superviseur

Le méta-modèle pose : « BrainAI *incarne* l'Agent Superviseur et *orchestre* via le
Runtime ». Le noyau le réalise : `KernelSupervisor` implémente le `SupervisorPort`
du Runtime (`on_plan` / `on_review` / `on_decision`). BrainAI supervise chaque job,
mais **la gouvernance reste souveraine** : la règle dure T3 et les vetos ne sont
jamais court-circuités (`on_decision` est consultatif).

## 5. Composants internes

```
core/         config (as_of figé) · errors · model (Request, Plan, Contribution…)
providers/    base (contrat) · deterministic (défaut) · external (Claude/ChatGPT/Gemini) · registry
sources/      scc_gateway (API + Runtime + Control Plane)
supervisor    KernelSupervisor (SupervisorPort du Runtime)
context_builder · agent_selector · planner · orchestrator
kernel        BrainAIKernel (façade + classificateur d'intention)
cli           scc-brainai
```

## 6. Invariants tenus

| Invariant | Comment |
|-----------|---------|
| Aucun moteur modifié | coordination via interfaces publiques |
| Ni Runtime, ni API, ni Control Plane modifiés | `dispatch`, `SupervisorPort`, `ControlPlane` |
| Aucune IA obligatoire | cognition déterministe par défaut ; IA optionnelles |
| Aucun réseau / dépendance externe | stdlib pur ; adaptateurs IA non branchés |
| Déterminisme complet | `as_of` figé + horloge Runtime injectée + règles pures |
