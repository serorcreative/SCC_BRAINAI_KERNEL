# Orchestration cognitive

Comment BrainAI transforme une demande en réponse, en mobilisant les Agents et le
Runtime — sans exécuter lui-même la moindre logique métier.

## 1. Intention → agents

Un classificateur déterministe (mots-clés) déduit l'intention, qui sélectionne des
**rôles d'agents réels** du catalogue. BrainAI **incarne toujours** le Superviseur
(`SCC-AGENT-0020`).

| Intention | Agents mobilisés (outre le Superviseur) |
|-----------|------------------------------------------|
| `cognition` | Ingestion, Extraction, Mémoire, Connaissance, Raisonnement, Architecte |
| `governance` | Gouvernance, Gardien de la Fondation, Architecte |
| `graph` | Architecte, Connaissance |
| `inspect` | Qualité, Sécurité, Architecte |
| `general` | Architecte, Gouvernance |

Chaque agent est enrichi de ses attributs réels (autonomie A0–A4, confiance T1–T3)
lus via l'API.

## 2. Plan → actions

Une étape de plan par agent, avec une **action** dérivée de son rôle et les
**doctrines** qui la gouvernent (relation `governs`, lue dans le graphe) :

| Action | Agent type | Effet |
|--------|-----------|-------|
| `map_architecture` | Architecte | structure du graphe + ADR pertinents |
| `consult_governance` | Gouvernance | doctrines + ADR gouvernant la demande |
| `check_foundation` | Gardien Fondation | doctrines de Fondation |
| `cognitive_stage` | moteurs (Ingestion…Raisonnement) | supervise un étage de la chaîne |
| `inspect_health` | Qualité / Sécurité | santé via Control Plane |
| `observe_supervision` | Superviseur | consolide + supervise l'exécution |

## 3. Exécution gouvernée (Runtime)

BrainAI orchestre **un job Runtime**, sous le `KernelSupervisor` (branché sur le
`SupervisorPort`) :

- **mode standard** : job `echo` (diagnostic hermétique, T1) — prouve l'orchestration
  gouvernée et la boucle de supervision ;
- **mode `--deep`** (intention *cognition*) : job `brain_pass` — la **chaîne réelle
  des cinq moteurs** (ingestion → extraction → mémoire → connaissance →
  raisonnement), sous gouvernance.

Chaque agent cognitif reçoit alors sa **part** du résultat (le résumé de son étage).
Une éventuelle action T3 serait **bloquée puis validée humainement** — BrainAI
n'échappe pas au garde-fou.

## 4. Consolidation & synthèse

Les contributions des agents sont agrégées ; la gouvernance (doctrines + ADR) est
consolidée ; une **synthèse déterministe** est produite par le fournisseur par
défaut. Une IA optionnelle (si disponible) peut *augmenter* cette synthèse — sans
jamais être requise.

## 5. Réponse structurée

```json
{
  "ok": true, "intent": "...", "as_of": "...",
  "context": { "system": {...}, "readiness": "...", "health": "..." },
  "agents": [ { "id": "SCC-AGENT-0002", "autonomy": "A3", "reason": "..." } ],
  "plan": { "intent": "...", "steps": [ { "agent": "...", "action": "...", "doctrines": [...] } ] },
  "governance": { "doctrines": [...], "adrs": [...] },
  "runtime": { "kind": "echo|brain_pass", "status": "succeeded", "events_by_type": {...} },
  "supervisor": { "name": "brainai", "plans": 1, "reviews": 1, "decisions": 1 },
  "contributions": [ { "agent": "...", "findings": {...} } ],
  "synthesis": "…",
  "provider": { "selected": "deterministic", "available": ["deterministic"] }
}
```

## 6. Mode dégradé

Si une source est indisponible, le noyau la **note** et continue : il produit une
réponse partielle plutôt que d'échouer. BrainAI reste utile même incomplet.
