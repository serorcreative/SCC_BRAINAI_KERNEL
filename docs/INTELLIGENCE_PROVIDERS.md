# Fournisseurs d'intelligence — brancher plusieurs IA sans toucher au noyau

> **Le noyau fonctionne sans aucune IA.** Les IA (Claude, ChatGPT, Gemini…) sont des
> **capacités optionnelles** qui *augmentent* BrainAI, jamais des prérequis.

## 1. Principe : augmentation, pas dépendance

La cognition par défaut de BrainAI est **déterministe** (règles). Un fournisseur
d'intelligence ne *décide* rien : il *enrichit* (indices de plan, prose de
synthèse). Le noyau reste maître de la planification, de la sélection d'agents et
de l'orchestration. Ainsi, retirer toutes les IA ne casse rien.

## 2. Le contrat (`IntelligenceProvider`)

```python
class IntelligenceProvider(Protocol):
    name: str
    def available(self) -> bool: ...
    def assist_plan(self, intent, query, context) -> Optional[list[str]]: ...
    def assist_synthesis(self, query, contributions, context) -> Optional[str]: ...
```

Minimal et *augmentatif*. Un fournisseur indisponible renvoie `None` partout et est
ignoré par le noyau.

## 3. Fournisseurs fournis

| Fournisseur | Disponible ? | Rôle |
|-------------|--------------|------|
| `DeterministicProvider` | **toujours** | cognition par règles (défaut, repli garanti) |
| `ClaudeProvider` | non (sans client) | emplacement d'extension |
| `ChatGPTProvider` | non (sans client) | emplacement d'extension |
| `GeminiProvider` | non (sans client) | emplacement d'extension |

Les adaptateurs externes **ne réalisent aucun appel réseau** dans ce socle : sans
`client` injecté, ils se déclarent indisponibles. Le noyau retombe alors sur le
déterministe.

## 4. Sélection avec repli garanti

```python
registry = ProviderRegistry()
provider = registry.select(["claude", "chatgpt", "deterministic"])
# → premier disponible dans l'ordre ; ici "deterministic" (les IA ne sont pas configurées)
```

`select()` **retombe toujours** sur `deterministic`. Le noyau ne peut donc jamais
se retrouver sans cognition.

## 5. Brancher une IA (le jour venu, sous ADR)

```python
class MyClaude(ClaudeProvider):
    def __init__(self, client): super().__init__(client=client)   # transport injecté hors socle
    def assist_synthesis(self, query, contributions, context):
        return self._client.complete(...)                          # appel réel (couche réseau future)

registry.register(MyClaude(client=my_transport))
kernel.handle("...", provider_order=["claude", "deterministic"])
```

L'**architecture du noyau ne change pas** : on enregistre un fournisseur, on ajuste
l'ordre de préférence. L'exposition réseau d'une IA relèvera d'un chantier et d'un
ADR dédiés (comme l'HTTP de l'API et le tableau de bord du Control Plane).

## 6. Plusieurs IA en parallèle

Le registre accepte autant de fournisseurs que voulu. La stratégie de sélection
(ordre de préférence) est une donnée de configuration (`provider_order`), pas du
code : on peut préférer Claude, puis ChatGPT, puis Gemini, puis le déterministe —
sans recompiler quoi que ce soit.
