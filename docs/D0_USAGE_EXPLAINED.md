# LOGIQUE DE SÉLECTION DES CONFIGURATIONS PAR ÉTAPE

## 🎯 RÉPONSE À TA QUESTION

La logique qui permet de choisir la partie du dictionnaire se trouve dans **plusieurs endroits** qui travaillent ensemble :

## 1. 🗂️ **STOCKAGE DES CONFIGURATIONS** (`step_retrieval_config.py`)

Le dictionnaire `self.config` contient TOUTES les configurations :

```python
class StepRetrievalConfig:
    def __init__(self):
        self.config = {
            "d0_initialisation": {
                "search_fields": {...},
                "retrieve_fields": {...}, 
                "context_fields": {...}
            },
            "d1_team": {
                "search_fields": {...},
                "retrieve_fields": {...},
                "context_fields": {...}
            },
            # ... toutes les autres étapes
        }
```

## 2. � **MÉCANISME DE SÉLECTION** (Méthodes de `StepRetrievalConfig`)

### Méthode principale de sélection :
```python
def get_config_for_step(self, step_name: str) -> Dict:
    """Récupère la configuration pour une étape donnée"""
    return self.config.get(step_name, self.config["d0_initialisation"])
    #                    ↑           ↑
    #               CLÉ D'ÉTAPE    FALLBACK
```

### Méthodes spécialisées :
```python
def get_search_fields(self, step_name: str) -> List[str]:
    config = self.get_config_for_step(step_name)  # ← SÉLECTION ICI
    return config["search_fields"]["from_current_nc"]

def get_retrieve_fields(self, step_name: str) -> List[str]:
    config = self.get_config_for_step(step_name)  # ← SÉLECTION ICI
    return config["retrieve_fields"]["from_similar_ncs"]

def get_context_fields(self, step_name: str) -> List[str]:
    config = self.get_config_for_step(step_name)  # ← SÉLECTION ICI
    return config["context_fields"]["keep_for_llm"]
```

## 3. 🎯 **UTILISATION DANS LE CODE PRINCIPAL** (`retrieval.py`)

```python
def get_relevant_documents(
    query_text: str,
    current_section_data: dict,
    current_section_name: str,  # ← CLÉ IMPORTANTE !
    form_data: dict | None = None,
    k: int = 5,
    model_key : int | None = None,
    return_scores: bool = False,
):
    # 1. Configuration spécifique à l'étape 8D
    step_config = step_retrieval_config.get_config_for_step(current_section_name)
    #                                                      ↑
    #                                           VOICI LA CLÉ DE SÉLECTION !
    
    search_fields = step_retrieval_config.get_search_fields(current_section_name)
    #                                                      ↑
    #                                           ENCORE LA CLÉ DE SÉLECTION !
```

## 4. � **FLUX COMPLET DE SÉLECTION**

```
┌─────────────────────────────────────┐
│ 1. Frontend envoie la requête      │
│    avec current_section_name        │
│    (ex: "d1_team")                  │
└─────┬───────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ 2. Backend reçoit                   │
│    current_section_name = "d1_team" │
└─────┬───────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ 3. retrieval.py appelle             │
│    step_retrieval_config            │
│    .get_config_for_step("d1_team")  │
└─────┬───────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ 4. get_config_for_step fait :       │
│    return self.config["d1_team"]    │
└─────┬───────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ 5. RÉSULTAT: Configuration D1       │
│    search_fields: [produitRef, ...]  │
│    retrieve_fields: [chefEquipe, ...] │
│    context_fields: [referenceNC, ...] │
└─────────────────────────────────────┘
```

## 5. 💡 **EXEMPLES CONCRETS**

### Exemple 1: Utilisateur à l'étape D0
```python
current_section_name = "d0_initialisation"
↓
config = self.config.get("d0_initialisation")
↓
search_fields = ["produitRef", "descriptionInitiale", "detectePar", "LieuDetection"]
```

### Exemple 2: Utilisateur à l'étape D1
```python
current_section_name = "d1_team"
↓
config = self.config.get("d1_team")
↓
search_fields = ["produitRef", "descriptionInitiale", "LieuDetection", "Criticite"]
```

### Exemple 3: Étape inexistante (sécurité)
```python
current_section_name = "d99_inexistant"
↓
config = self.config.get("d99_inexistant", self.config["d0_initialisation"])
↓
config = self.config["d0_initialisation"]  # Fallback
```

## 6. � **OÙ TROUVE-T-ON LA CLÉ `current_section_name` ?**

### Dans le Frontend (`ChatAssistant.jsx`) :
```javascript
const payload = {
    query: text,
    form_data: all8DData,
    current_section_data: currentSectionData,
    current_section_name: currentStepKey,  // ← VOICI LA CLÉ !
    mode: chatMode,
    model_key : "qwen_base"
};
```

### Dans le Backend (`query.py`) :
```python
async def query_documents_with_context(
    query_text: str, 
    form_data: dict, 
    current_section_data: dict, 
    current_section_name: str,  # ← REÇUE DU FRONTEND
    stream: bool, 
    model_key:int
):
    # Cette variable est passée à get_relevant_documents()
    retrieved_docs_with_scores = get_relevant_documents(
        query_text=query_text,
        current_section_data=current_section_data,
        current_section_name=current_section_name,  # ← TRANSMISE ICI
        form_data=form_data,
        model_key=model_key,
        return_scores=True,
    )
```

## 🎯 **RÉSUMÉ : LA MAGIE EN 3 ÉTAPES**

1. **Frontend** → `current_section_name = "d1_team"` (exemple)
2. **Backend** → `self.config.get("d1_team")` 
3. **Résultat** → Configuration spécifique D1 sélectionnée !

**La logique de sélection est donc un simple `dict.get(clé)` dans la méthode `get_config_for_step()` !**
│ 3. Système lit config[étape_X]      │
│                                     │
│ search_fields: [champ1, champ2]     │
│ retrieve_fields: [champA, champB]   │
│ context_fields: [champX, champY]    │
└─────┬───────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ 4. RECHERCHE de NCs similaires      │
│                                     │
│ Requête = D0.champ1 + D0.champ2     │
│ (selon search_fields)               │
└─────┬───────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ 5. EXTRACTION des NCs trouvées      │
│                                     │
│ Récupère champA + champB            │
│ (selon retrieve_fields)             │
└─────┬───────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────┐
│ 6. CONTEXTE pour LLM                │
│                                     │
│ NC actuelle: D0.champX + D0.champY  │
│ + Exemples: champA + champB         │
│ (selon context_fields)              │
└─────┬───────────────────────────────┘
      │
      ▼
┌─────────────────┐
│ 7. LLM répond   │
│ avec contexte   │
│ optimal         │
└─────────────────┘
```

## 📊 PATTERNS OBSERVÉS

### 🔍 **Recherche** (search_fields)
- **Début** (D0, D1, D2, D3) : Beaucoup de champs D0 (produit, description, lieu, criticité)
- **Milieu** (D4, D5, D6) : Moins de champs D0, plus de données des étapes précédentes
- **Fin** (D7, D8) : Principalement description + quelques champs spécifiques

### 💭 **Contexte LLM** (context_fields)
- **referenceNC** : TOUJOURS présent (identification)
- **descriptionInitiale** : Presque toujours (contexte du problème)
- **Autres champs D0** : Diminuent progressivement au profit des données des étapes

### 🎯 **Principe de conception**
Plus on avance dans les étapes 8D, moins on a besoin du contexte D0 détaillé, mais on garde toujours :
1. L'ID de référence (`referenceNC`)
2. La description du problème (`descriptionInitiale`)

## 🔧 DANS LE CODE

Les données D0 sont utilisées dans `retrieval.py` :

```python
# 1. Pour construire la requête de recherche
for field in search_fields:
    if form_data.get('d0_initialisation'):
        value = form_data['d0_initialisation'].get(field)
        if value:
            enriched_query_parts.append(f"{field}: {value}")

# 2. Pour construire le contexte LLM  
for field in context_fields:
    if field in form_data['d0_initialisation']:
        current_nc_context_parts.append(f"{field}: {value}")
```

**Résultat :** Le système s'adapte intelligemment selon l'étape pour utiliser juste les bonnes données D0 ! 🚀
