# Assistant 8D – Application de résolution de problèmes

Ce projet est une application web complète pour accompagner la démarche 8D (résolution de problèmes en 8 étapes) avec un assistant conversationnel intelligent basé sur l'IA.

## 🎯 Vue d'ensemble

L'Assistant 8D est un outil complet d'aide à la résolution de non-conformités industrielles suivant la méthodologie 8D (8 Disciplines). Il combine une interface utilisateur moderne avec un assistant IA contextuel pour guider les utilisateurs à travers chaque étape du processus de résolution de problèmes.

### 🌟 Fonctionnalités principales

- **Interface 8D complète** : Formulaires guidés pour chaque étape (D0 à D8)
- **Assistant IA conversationnel** : Chat intelligent avec suggestions contextuelles
- **Recherche vectorielle** : Analyse de similarité avec des cas précédents
- **Gestion des non-conformités** : Suivi complet du cycle de vie
- **Scores de similarité** : Affichage des pourcentages de correspondance
- **Suggestions automatiques** : Complétion intelligente des champs
- **Export PDF** : Génération de rapports complets
- **Historique des conversations** : Persistance des échanges

## 🏗️ Architecture du système

### Frontend (React + Vite)
- **Technologies** : React 18, Material-UI, Vite, React Router
- **Composants principaux** :
  - `Form8DAndChatInterface` : Interface principale combinant formulaires et chat
  - `ChatAssistant` : Assistant conversationnel avec deux modes (CHAT/REQ)
  - `ListeNonConformites` : Gestion et visualisation des NC
  - `Dashboard` : Tableau de bord avec statistiques

### Backend (FastAPI + Python)
- **Technologies** : FastAPI, LangChain, ChromaDB, Ollama
- **Modules principaux** :
  - `app.py` : Point d'entrée FastAPI avec API REST
  - `backend/query.py` : Moteur de requêtes contextuelles
  - `backend/retrieval.py` : Recherche vectorielle avec scores
  - `backend/prompts.py` : Gestion des prompts spécialisés par étape
  - `backend/get_vector_db.py` : Interface avec ChromaDB

### Base de données vectorielle
- **ChromaDB** : Stockage des embeddings des non-conformités
- **Modèles d'embedding** : Support de plusieurs modèles (Qwen, Snowflake Arctic)
- **Recherche sémantique** : Calcul de similarité avec scores

## 🔧 Prérequis

### Système
- **Python** 3.10+ 
- **Node.js** 18+
- **Ollama** (serveur LLM local)
- **Git** pour le clonage du projet

### Ressources matérielles recommandées
- **RAM** : 8GB minimum, 16GB recommandé
- **CPU** : Multi-core pour les embeddings
- **Stockage** : 5GB pour les modèles et données

## 📦 Installation complète

### 1. Clonage du projet
```bash
git clone <repository-url>
cd Test_Langchain
```

### 2. Configuration du Backend

#### 2.1 Environnement virtuel Python
```powershell
# Création de l'environnement virtuel
python -m venv venv

# Activation (Windows)
.\venv\Scripts\activate

# Activation (Linux/Mac)
source venv/bin/activate
```

#### 2.2 Installation des dépendances Python
```bash
pip install -r requirements.txt
```

#### 2.3 Configuration Ollama
```bash
# Installation d'Ollama
# Télécharger depuis https://ollama.com/download

# Téléchargement des modèles nécessaires
ollama pull qwen3:14b
ollama pull dengcao/Qwen3-Embedding-0.6B:f16
ollama pull dengcao/Qwen3-Embedding-4B:q5_K_M

# Démarrage du serveur Ollama
ollama serve
```

### 3. Configuration du Frontend

#### 3.1 Installation des dépendances Node.js
```bash
cd frontend
npm install
```

### 4. Génération de la base de données vectorielle

#### 4.1 Préparation des données
```bash
# Vérifier la présence du fichier source
ls documents/NC5_clean.csv
```

#### 4.2 Génération des embeddings
```bash
# Retour au répertoire racine
cd ..

# Génération de la base ChromaDB
python embed.py
```

Cette étape peut prendre plusieurs minutes selon la taille des données.

### 5. Configuration des modèles

#### 5.1 Modèles d'embedding disponibles
Le système supporte plusieurs modèles configurés dans `config.py` :

```python
AVAILABLE_EMBEDDING_MODELS = {
    "qwen_base": "dengcao/Qwen3-Embedding-0.6B:f16",
    "dengcao_qwen3_4b": "dengcao/Qwen3-Embedding-4B:q5_K_M",
    "snowflake2": "snowflake-arctic-embed2:latest"
}
```

#### 5.2 Modèle par défaut
Le modèle `qwen_base` est utilisé par défaut. Pour changer :
```python
DEFAULT_EMBEDDING_MODEL_KEY = "dengcao_qwen3_4b"
```

## 🚀 Lancement de l'application

### 1. Démarrage du backend
```bash
# Dans le répertoire racine
python app.py
```
Le backend sera accessible sur `http://localhost:8000`

### 2. Démarrage du frontend
```bash
# Dans le répertoire frontend
cd frontend
npm run dev
```
Le frontend sera accessible sur `http://localhost:5174`

### 3. Vérification des services
- **Backend API** : `http://localhost:8000/docs` (documentation Swagger)
- **Frontend** : `http://localhost:5174`
- **Ollama** : `http://localhost:11434` (API LLM)

## 📋 Utilisation de l'application

### 1. Interface principale

#### Création d'une nouvelle non-conformité
1. Accéder à l'interface principale
2. Remplir l'étape D0 (Initialisation)
3. Naviguer entre les étapes D1 à D8
4. Utiliser l'assistant chat pour obtenir de l'aide

#### Gestion des non-conformités existantes
1. Accéder à "Liste des Non-Conformités"
2. Sélectionner une NC existante
3. Reprendre le processus 8D

### 2. Assistant conversationnel

#### Mode CHAT
- Conversation libre avec l'assistant
- Suggestions contextuelles selon l'étape
- Historique des échanges persistant

#### Mode REQ (Requête)
- Recherche directe de NC similaires
- Affichage des sources avec scores de similarité
- Pas de conversation, uniquement recherche

### 3. Fonctionnalités avancées

#### Scores de similarité
- Pourcentage de correspondance affiché pour chaque source
- Calcul basé sur la similarité cosinus des embeddings
- Aide à identifier les cas les plus pertinents

#### Suggestions automatiques
- Complétion intelligente des champs
- Basée sur l'analyse des cas similaires
- Application en un clic

## 🔧 Configuration avancée

### 1. Personnalisation des prompts
Les prompts sont définis dans `backend/prompts.py` et peuvent être personnalisés par étape :

```python
# Exemple de prompt pour l'étape D2
prompt_8D_2_template = """
Tu es à la deuxième étape de la méthode 8D.
Ta mission est de remplir un QQOQCCP...
"""
```

### 2. Ajout de nouveaux modèles d'embedding
1. Ajouter le modèle dans `config.py`
2. Télécharger le modèle avec Ollama
3. Régénérer les embeddings si nécessaire

### 3. Personnalisation de l'interface
- Couleurs définies dans `frontend/src/colors.js`
- Composants Material-UI personnalisables
- Thèmes adaptables

## 🗂️ Structure détaillée du projet

```
Test_Langchain/
├── README.md                 # Documentation principale
├── requirements.txt          # Dépendances Python
├── config.py                # Configuration des modèles
├── app.py                   # Point d'entrée FastAPI
├── embed.py                 # Génération des embeddings
├── package.json             # Dépendances Node.js globales
├── TODO.md                  # Tâches à réaliser
│
├── backend/                 # Code Python backend
│   ├── __init__.py
│   ├── query.py            # Moteur de requêtes
│   ├── retrieval.py        # Recherche vectorielle
│   ├── prompts.py          # Gestion des prompts
│   ├── get_vector_db.py    # Interface ChromaDB
│   ├── models.py           # Modèles de données
│   ├── schemas.py          # Schémas Pydantic
│   ├── crud.py             # Opérations CRUD
│   ├── database.py         # Configuration BDD
│   └── utils.py            # Utilitaires
│
├── frontend/               # Application React
│   ├── package.json        # Dépendances Node.js
│   ├── vite.config.js      # Configuration Vite
│   ├── index.html          # Template HTML
│   └── src/
│       ├── main.jsx        # Point d'entrée React
│       ├── App.jsx         # Composant principal
│       ├── colors.js       # Définition des couleurs
│       ├── components/     # Composants réutilisables
│       │   ├── ChatAssistant.jsx
│       │   ├── Dashboard.jsx
│       │   └── ListeNonConformites.jsx
│       ├── contexts/       # Contextes React
│       │   └── Form8DContext.jsx
│       └── pages/          # Pages/étapes 8D
│           ├── D0Form.jsx
│           ├── D1Form.jsx
│           └── ... (D2 à D8)
│
├── documents/              # Données source
│   └── NC5_clean.csv      # Non-conformités d'exemple
│
├── chroma_db/             # Base de données vectorielle
│   ├── chroma.sqlite3     # Index SQLite
│   └── collections/       # Collections d'embeddings
│
└── templates/             # Templates HTML (legacy)
    └── index.html
```

## 🧪 Tests et débogage

### Scripts de test inclus
- `test_api_scores.py` : Test des scores de similarité
- `test_vectorstore_access.py` : Test d'accès à ChromaDB
- `test_similarity_scores.py` : Test des calculs de similarité

### Débogage
```bash
# Test de l'API
python test_api_scores.py

# Test de la base vectorielle
python test_vectorstore_access.py

# Vérification des logs
tail -f logs/app.log
```

## 📊 Métriques et monitoring

### Logs disponibles
- Requêtes API dans les logs FastAPI
- Accès ChromaDB dans les logs backend
- Erreurs frontend dans la console navigateur

### Métriques surveillées
- Temps de réponse des requêtes
- Scores de similarité moyens
- Utilisation des modèles d'embedding

## 🔒 Sécurité et bonnes pratiques

### Recommandations
- Variables d'environnement pour les configurations sensibles
- Validation des entrées utilisateur
- Limitation du taux de requêtes
- Authentification pour la production

### Fichiers à protéger
- `config.py` : Configuration des modèles
- `chroma_db/` : Base de données vectorielle
- `documents/` : Données source sensibles

## 🚨 Dépannage

### Problèmes courants

#### Ollama non accessible
```bash
# Vérifier le statut
curl http://localhost:11434/api/tags

# Redémarrer Ollama
ollama serve
```

#### ChromaDB corrompue
```bash
# Supprimer et régénérer
rm -rf chroma_db/
python embed.py
```

#### Erreurs de dépendances
```bash
# Réinstaller les dépendances
pip install --force-reinstall -r requirements.txt
```

### Support et logs
- Logs détaillés dans la console
- Documentation API : `http://localhost:8000/docs`
- Logs ChromaDB dans les sorties console

## 🔄 Mise à jour des données

### Ajout de nouvelles non-conformités
1. Modifier `documents/NC5_clean.csv`
2. Exécuter `python embed.py`
3. Redémarrer l'application

### Changement de modèle d'embedding
1. Modifier `config.py`
2. Télécharger le nouveau modèle avec Ollama
3. Régénérer les embeddings

## 📈 Performance et optimisation

### Recommandations
- Utiliser un SSD pour ChromaDB
- Optimiser la taille des embeddings
- Mettre en cache les requêtes fréquentes
- Surveiller l'utilisation mémoire

### Monitoring
- Temps de réponse API
- Utilisation CPU/RAM
- Taille de la base vectorielle

## 📝 Contribution

### Développement
1. Fork du projet
2. Création d'une branche feature
3. Tests des modifications
4. Pull request avec description

### Standards de code
- Python : PEP 8
- JavaScript : ESLint + Prettier
- Documentation : Markdown

## 📞 Support

### Ressources
- Documentation technique dans le code
- Exemples dans `TODO.md`
- Tests dans les fichiers `test_*.py`

### Contact
- **Auteur** : lrodembourg
- **Projet** : Assistant 8D
- **Version** : 1.0.0

---

*Ce README couvre l'ensemble du projet Assistant 8D. Pour des questions spécifiques, consulter la documentation technique dans le code ou les fichiers de test.*
