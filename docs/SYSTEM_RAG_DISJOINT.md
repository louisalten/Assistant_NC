# Système de Disjonction RAG par Étape 8D

## Vue d'ensemble

Ce système implémente une approche intelligente de récupération d'informations (RAG) qui s'adapte automatiquement selon l'étape 8D en cours. Au lieu d'utiliser toujours les mêmes critères de recherche et d'extraction, le système personnalise sa stratégie pour chaque étape.

## Architecture

### Composants principaux

1. **`step_retrieval_config.py`** : Configuration des stratégies par étape
2. **`field_mapping.py`** : Mapping entre noms logiques et colonnes CSV
3. **`retrieval.py`** : Logique de récupération adaptative
4. **`query.py`** : Construction du contexte pour le LLM

## Fonctionnement par étape

### D0 - Initialisation

**Objectif :** Aider à la saisie initiale en montrant des exemples similaires

**Recherche basée sur :**
- `produitRef` : Article impacté
- `descriptionInitiale` : Description du problème  
- `detectePar` : Créateur NC
- `LieuDetection` : Lieu de détection

**Extraction des NCs similaires :**
- `detectePar` : Nom du créateur
- `FonctionCrea` : Fonction du créateur
- `Criticite` : Niveau de criticité
- `descriptionInitiale` : Description pour comparaison
- `produitRef` : Article pour vérifier la pertinence

**Contexte pour le LLM :**
- **ID de la NC actuelle** (toujours inclus pour référence)
- Description et contexte du problème actuel
- Exemples de NCs similaires avec créateurs et criticités

### D1 - Constitution d'équipe

**Objectif :** Suggérer une composition d'équipe adaptée au problème

**Recherche basée sur :**
- `produitRef` : Type de produit (influence le type d'expertise)
- `descriptionInitiale` : Nature du problème (détermine les compétences)
- `LieuDetection` : Site (disponibilité des ressources)
- `Criticite` : Urgence (taille et niveau de l'équipe)

**Extraction des NCs similaires :**
- `chefEquipe` : Chef d'équipe et ses informations
- `membresEquipe` : Composition de l'équipe
- `Sponsor` : Sponsor du projet
- `descriptionInitiale` : Contexte du problème
- `Criticite` : Niveau pour comparaison

**Contexte pour le LLM :**
- **ID de la NC actuelle** (toujours inclus pour référence)
- Problème actuel avec ses caractéristiques
- Créateur initial et sa fonction
- Exemples d'équipes constituées pour des problèmes similaires

## Exemple concret

### Scénario : Problème de peinture sur porte avant

**Étape D0 :**
```
Recherche : "Porte avant droite | Mauvaise teinte de peinture | Claude BEGUIN | Site A"
↓
Extraction : Créateurs, fonctions, criticités de NCs similaires  
↓
LLM : "Voici des exemples de NCs similaires avec leurs créateurs et niveaux de criticité"
```

**Étape D1 :**
```
Recherche : "Porte avant droite | Mauvaise teinte de peinture | Site A | Criticité 4.0"
↓
Extraction : Équipes constituées pour des problèmes de peinture similaires
↓
LLM : "Pour ce type de problème, voici des exemples d'équipes efficaces : 
       - Chef : Manager Qualité
       - Membres : Technicien Peinture, Contrôleur, Production"
```

## Avantages

1. **Pertinence maximale** : Chaque étape reçoit exactement les informations dont elle a besoin
2. **Contextualisation** : Le LLM dispose du bon contexte pour chaque étape
3. **Efficacité** : Évite la surcharge d'informations non pertinentes
4. **Évolutivité** : Facile d'ajouter de nouvelles étapes ou modifier les stratégies

## Principes de conception

### ID NC toujours inclus
L'**Identification NC** (référence de la NC) est automatiquement incluse dans le contexte envoyé au LLM pour **toutes les étapes**, mais n'est **jamais utilisée** pour la recherche de similarités car elle n'est pas pertinente pour trouver des NCs similaires.

### Séparation recherche/contexte
- **Champs de recherche** : Utilisés pour trouver des NCs similaires (article, description, lieu, etc.)
- **Champs d'extraction** : Récupérés depuis les NCs similaires trouvées
- **Champs de contexte** : Envoyés au LLM (incluent toujours l'ID + informations pertinentes)

## Configuration

### Ajouter une nouvelle étape

1. Modifier `step_retrieval_config.py` :
```python
"dx_nouvelle_etape": {
    "search_fields": {
        "from_current_nc": ["champ1", "champ2"]
    },
    "retrieve_fields": {
        "from_similar_ncs": ["champ3", "champ4"] 
    },
    "context_fields": {
        "keep_for_llm": ["champ1", "champ3"]
    }
}
```

2. Ajouter le mapping dans `field_mapping.py` si nécessaire :
```python
"champ1": "Colonne CSV correspondante"
```

### Modifier une stratégie existante

Éditer simplement la configuration dans `step_retrieval_config.py` pour l'étape concernée.

## Tests

- `test_step_rag.py` : Test de base de la configuration
- `test_complete_rag.py` : Test complet avec simulation de données

## Intégration

Le système s'intègre automatiquement dans le flux RAG existant via :
- `get_relevant_documents()` : Récupération adaptative
- `query_documents_with_context()` : Construction du contexte intelligent
