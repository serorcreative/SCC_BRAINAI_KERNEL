# Déterminisme du noyau BrainAI

Le chantier exige un **déterminisme complet**. Le noyau le garantit : à demande
égale, réponse **strictement identique** — vérifié byte-for-byte, y compris pour la
passe cognitive réelle traversant les cinq moteurs.

## 1. Sources de déterminisme

| Mécanisme | Effet |
|-----------|-------|
| `config.as_of` figé | horodatage unique ; aucune horloge murale lue |
| Runtime piloté avec `FixedClock(as_of)` + `SequentialFactory` | jobs/événements rejouables (ids et timestamps stables) |
| Classification d'intention par règles | même demande → même intention |
| Sélection d'agents & plan par tables | aucune part d'aléatoire |
| Synthèse déterministe (fournisseur par défaut) | texte reproductible |
| Itérations triées, agrégats ordonnés | sérialisation stable |

## 2. La passe cognitive `--deep`

La passe complète (`brain_pass`) traverse les moteurs réels. Pour rester
déterministe, **chaque passe part d'un répertoire de travail vierge** : le noyau
nettoie le workdir avant exécution, de sorte qu'aucune réingestion cumulée ne
fausse la consolidation (mémoire/connaissance). Le `run_id` est fixe (`brainai_pass`)
et les identifiants de connaissance sont dérivés du **contenu** (empreintes), donc
stables.

## 3. Preuves

- **Test unitaire** `test_default_pipeline_deterministic` : deux exécutions du
  pipeline standard produisent une réponse identique.
- **Test unitaire** `test_deep_pipeline_deterministic` : idem pour la passe cognitive
  complète (5 moteurs).
- **Vérifié cross-process** : deux invocations CLI indépendantes (`ask` standard et
  `ask --deep`) produisent des sorties **byte-for-byte identiques**.

## 4. Ce qui n'entre jamais dans la réponse

- Aucune donnée RAW, aucun export utilisateur/OpenAI.
- Aucun chemin volatil ni identifiant aléatoire (le workdir de la passe n'apparaît
  pas dans la réponse ; seuls les résumés d'étapes et le `run_id` fixe y figurent).
- Aucune sortie d'IA externe (aucune n'est branchée dans le socle).

## 5. Limite documentée

Le déterminisme du noyau couvre **sa propre logique** et l'orchestration qu'il
pilote avec horloge injectée et workdir propre. Une IA externe, une fois branchée
(hors socle, sous ADR), pourra introduire sa propre variabilité : elle
n'*augmentera* que la synthèse, laissant intacts le plan, les agents, la gouvernance
et le résultat Runtime — le **squelette déterministe** de la réponse demeure.
