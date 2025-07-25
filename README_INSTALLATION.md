# 🚀 Guide d'Installation Complet - Système RAG 8D Non-Conformités

Ce guide vous accompagne pas à pas pour installer et configurer le système d'assistance IA pour la gestion des non-conformités 8D, depuis le téléchargement du code jusqu'à l'utilisation complète.

## 📋 Vue d'ensemble du système

Le système se compose de :
- **Backend Python** : API avec intelligence artificielle (FastAPI + LangChain)
- **Frontend React** : Interface utilisateur moderne et intuitive
- **Base de données vectorielle** : ChromaDB pour la recherche sémantique
- **Ollama** : Serveur local d'IA pour les modèles de langage

---

## 🛠️ Prérequis - Logiciels à installer

### 1. Python 3.11 ou plus récent
**Deux choix**
1. Télécharger : [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. OU télécharger python avec le protail d'entreprise 
- **IMPORTANT** : Cocher "Add Python to PATH" pendant l'installation
- Vérifier l'installation : ouvrir PowerShell (terminal Windows) et taper `python --version`

### 2. Node.js (pour le frontend)
- Télécharger : [https://nodejs.org/](https://nodejs.org/) (version LTS recommandée)
- Installer avec les options par défaut
- Vérifier l'installation : ouvrir PowerShell (terminal Windows) et taper `node --version` et `npm --version`

### 3. Ollama (serveur IA local)
- Télécharger : [https://ollama.ai/download](https://ollama.ai/download)
- Installer l'application
- L'application se lancera automatiquement dans la barre système

---

## 📥 Étape 1 : Télécharger le projet depuis Azure DevOps

### Option A : Via Visual Studio Code (Recommandé)
1. Installer [Visual Studio Code](https://code.visualstudio.com/)
2. Aller sur votre projet Azure DevOps dans le navigateur
3. **S'assurer d'être sur la branche `master`** (vérifier en haut de la page)
4. Cliquer sur le bouton **"Clone"** en haut à droite
5. Cliquer sur **"Generate Git Credentials"** 
   - 📝 **IMPORTANT** : Noter les identifiants générés quelque part (nom d'utilisateur et mot de passe)
6. Cliquer sur **"Clone in VS Code"**
7. VS Code va s'ouvrir automatiquement
8. Choisir un dossier de destination :
   - Vous pouvez créer un nouveau dossier (ex: `C:\Assistant_NC\`)
   - Sélectionner ce dossier
9. Se connecter avec les Git Credentials générés à l'étape 5 si demandé
10. Cliquer sur **"Open in this window"** quand VS Code vous le propose

---

## ⚙️ Étape 2 : Configuration du Backend Python

### 1. Ouvrir un terminal dans VS Code
1. Dans VS Code, aller dans le menu : **Terminal** → **New Terminal** (ou `Ctrl+Shift+ù`)
2. Un terminal PowerShell va s'ouvrir en bas de l'écran
3. **Vérifier le chemin actuel** : le terminal doit afficher un chemin qui finit par :
   ```
   ...DIN-SMQ et Assistant NC Illustrateurs>
   ```
4. Si le chemin n'est pas correct, naviguer vers le bon dossier :
   ```powershell
   cd "chemin\vers\DIN-SMQ et Assistant NC Illustrateurs"
   ```

### 2. Créer un environnement virtuel Python (dans le terminal)
```powershell
python -m venv venv
```

### 3. Activer l'environnement virtuel (dans le terminal)
```powershell
./venv/Scripts/activate
```
*Note : Si erreur de sécurité, exécuter dans le terminal : `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`*

### 4. Installer les dépendances Python (dans le terminal)
```powershell
pip install -r requirements.txt
```

### 5. Vérifier la configuration (dans le terminal)
```powershell
python -c "import fastapi; print('FastAPI installé avec succès')"
```

---

## 🌐 Étape 3 : Configuration du Frontend

**⚠️ IMPORTANT** : Toutes ces commandes doivent être exécutées dans l'environnement virtuel Python activé.

### 1. S'assurer que l'environnement virtuel est activé
```powershell
# Si pas déjà fait, activer l'environnement virtuel :
./venv/Scripts/activate
```
Vous devriez voir `(venv)` au début de votre ligne de commande.

### 2. Naviguer vers le dossier frontend (dans le terminal)
```powershell
cd frontend
```

### 3. Installer les dépendances Node.js (dans l'environnement virtuel)
```powershell
npm install
```

### 4. Corriger les vulnérabilités de sécurité (dans l'environnement virtuel)
```powershell
npm audit fix
```

### 5. Retourner au dossier racine (dans le terminal)
```powershell
cd ..
```

---

## 🤖 Étape 4 : Configuration d'Ollama (IA)

### 1. Vérifier qu'Ollama fonctionne (dans le terminal)
```powershell
ollama --version
```

### 2. Télécharger les modèles IA nécessaires (dans le terminal)

**⚠️ IMPORTANT : Choisir selon votre configuration PC**

#### Pour PC classique/bureautique (8-16 GB RAM) :
```powershell
# Modèle léger et rapide (recommandé pour PC standard)
ollama pull qwen3:4b
```

#### Pour PC performant (16-32 GB RAM) - Option rapide :
```powershell
# Modèle plus puissant mais rapide (meilleur raisonnement, quelques hallucinations)
ollama pull qwen3:14b
```

#### Pour PC performant (16-32 GB RAM) - Option qualité maximale :
```powershell
# Modèle avec raisonnement avancé (plus lent mais très précis)
ollama pull phi4-reasoning:plus
```

#### Modèles d'embedding (obligatoires pour tous) :

**⚠️ CHOISIR SELON VOTRE CONFIGURATION PC :**

##### Pour PC performant (16-32 GB RAM) - Modèle haute qualité :
```powershell
# Modèle d'embedding haute performance (meilleure précision de recherche)
ollama pull dengcao/Qwen3-Embedding-0.6B:f16
```

##### Pour PC classique/bureautique (8-16 GB RAM) - Modèle optimisé :
```powershell
# Modèle d'embedding léger et rapide (bon équilibre performance/qualité)
ollama pull toshk0/nomic-embed-text-v2-moe
```

**💡 Important :** Notez le nom exact du modèle affiché par `ollama list`, vous en aurez besoin pour `python embed.py`.

**💡 Conseil :** Vous pouvez télécharger plusieurs modèles LLM, mais **un seul modèle d'embedding** à la fois.

## 🧠 Guide de choix des modèles d'embedding

| Configuration PC | Modèle d'embedding | Vitesse | Qualité | Utilisation RAM |
|------------------|-------------------|---------|---------|-----------------|
| **PC classique (8-16 GB)** | `toshk0/nomic-embed-text-v2-moe` | ⚡⚡ Rapide | ⭐⭐⭐ Bonne | 💾 Faible |
| **PC performant (16+ GB)** | `dengcao/Qwen3-Embedding-0.6B:f16` | ⚡ Correct | ⭐⭐⭐⭐ Très bonne | 💾💾 Moyenne |

**Recommandation :** Commencez par le modèle adapté à votre PC. Vous pourrez changer plus tard en recréant la base vectorielle.

## 🔍 Comparaison des modèles d'embedding

## 🧠 Guide de choix des modèles IA (LLM)

| Modèle | Configuration PC | Vitesse | Qualité | Caractéristiques |
|--------|------------------|---------|---------|------------------|
| **qwen3:4b** | PC classique (8-16 GB) | ⚡ Très rapide | ⭐⭐⭐ Bonne | Léger, réponses concises |
| **qwen3:14b** | PC performant (16+ GB) | ⚡⚡ Rapide | ⭐⭐⭐⭐ Très bonne | Plus intelligent, parfois créatif |
| **phi4-reasoning:plus** | PC performant (16+ GB) | 🐌 Plus lent | ⭐⭐⭐⭐⭐ Excellente | Raisonnement détaillé, très précis |

**Recommandation :** Commencez par le modèle adapté à votre PC, vous pourrez changer plus tard.

### 3. Tester les modèles (dans le terminal)
```powershell
ollama list
```
Vous devriez voir tous les modèles téléchargés.

**📝 Important :** Notez le nom exact du modèle d'embedding selon votre choix :
- **PC performant** : `dengcao/Qwen3-Embedding-0.6B:f16` 
- **PC classique** : `toshk0/nomic-embed-text-v2-moe`

Vous en aurez besoin pour la commande `python embed.py`.

### 4. Configurer le modèle dans le code
**⚠️ IMPORTANT** : Selon le modèle choisi, il faut modifier le code pour utiliser le bon modèle.

1. Dans VS Code, ouvrir le fichier `backend/query.py`
2. Chercher la ligne qui contient `model="phi4-reasoning"` (vers la ligne 140)
3. Remplacer par le modèle que vous avez téléchargé :

```python
# Pour PC classique :
llm = ChatOllamaWithThinking(
    model="qwen3:4b",  # ← Changer ici
    num_ctx=16384,
    temperature=0.7,
    base_url=ollama_endpoint,
    thinking_mode=True
)

# Pour PC performant (option rapide) :
llm = ChatOllamaWithThinking(
    model="qwen3:14b",  # ← Changer ici
    num_ctx=16384,
    temperature=0.7,
    base_url=ollama_endpoint,
    thinking_mode=True
)

# Pour PC performant (option qualité) :
llm = ChatOllamaWithThinking(
    model="phi4-reasoning:plus",  # ← Changer ici
    num_ctx=16384,
    temperature=0.7,
    base_url=ollama_endpoint,
    thinking_mode=True
)
```

4. Sauvegarder le fichier (`Ctrl+S`)

### 5. Configurer le modèle d'embedding

**⚠️ ÉTAPE IMPORTANTE** : Selon le modèle d'embedding choisi, vous devez modifier la configuration.

#### Option A : PC performant (avec dengcao/Qwen3-Embedding-0.6B:f16)

1. **Ouvrir le fichier `config.py`** dans VS Code
2. **Vérifier que cette ligne est activée** :
   ```python
   AVAILABLE_EMBEDDING_MODELS = {
       "qwen_base": "dengcao/Qwen3-Embedding-0.6B:f16",  # ← Modèle haute performance
       "nomic_moe": "toshk0/nomic-embed-text-v2-moe",
       # autres modèles...
   }
   
   # Modèle par défaut pour PC performant
   DEFAULT_EMBEDDING_MODEL_KEY = "qwen_base"
   ```

#### Option B : PC classique (avec toshk0/nomic-embed-text-v2-moe)

1. **Ouvrir le fichier `config.py`** dans VS Code
2. **Modifier cette ligne** :
   ```python
   AVAILABLE_EMBEDDING_MODELS = {
       "qwen_base": "dengcao/Qwen3-Embedding-0.6B:f16",
       "nomic_moe": "toshk0/nomic-embed-text-v2-moe",  # ← Modèle optimisé
       # autres modèles...
   }
   
   # Modèle par défaut pour PC classique
   DEFAULT_EMBEDDING_MODEL_KEY = "nomic_moe"  # ← Changer ici
   ```

3. **Sauvegarder le fichier** (`Ctrl+S`)

**💡 Rappel important :** Le modèle configuré ici doit correspondre exactement à celui que vous utiliserez dans `python embed.py "nom_du_modèle"`.

---

## 📊 Étape 5 : Configuration des bases de données

**ℹ️ Le système utilise 2 types de bases de données :**
- **Base relationnelle** (SQLite) : stockage des non-conformités
- **Base vectorielle** (ChromaDB) : recherche sémantique IA (**doit être créée localement**)

### 1. Créer la base de données relationnelle (dans le terminal)
```powershell
python -c "from backend.database import engine; from backend import models; models.Base.metadata.create_all(bind=engine); print('Base de données relationnelle créée')"
```

### 2. Créer la base de données vectorielle (OBLIGATOIRE)

**⚠️ ÉTAPE OBLIGATOIRE** : La base vectorielle doit toujours être créée localement sur chaque poste.

```powershell
# 1. Placer votre fichier CSV de non-conformités dans le dossier 'documents/'
# 2. Créer les embeddings pour la recherche IA (dans le terminal) :
cd backend

# CHOISIR LA COMMANDE SELON VOTRE CONFIGURATION :

# Option A : PC performant (modèle haute performance)
python embed.py "dengcao/Qwen3-Embedding-0.6B:f16"

# Option B : PC classique (modèle optimisé)
python embed.py "toshk0/nomic-embed-text-v2-moe"
```

**💡 Syntaxe importante :**
- Le nom du modèle doit être exactement celui affiché par `ollama list`
- **Utilisez le modèle correspondant à votre choix** dans l'étape 5 ci-dessus
- Exemple pour PC performant : `python embed.py "dengcao/Qwen3-Embedding-0.6B:f16"`
- Exemple pour PC classique : `python embed.py "toshk0/nomic-embed-text-v2-moe"`

**⚠️ Cohérence obligatoire :**
- Le modèle utilisé ici doit correspondre au `DEFAULT_EMBEDDING_MODEL_KEY` dans `config.py`
- Si vous changez de modèle plus tard, vous devrez recréer toute la base vectorielle

**💡 Pourquoi cette étape est obligatoire :**
- La base vectorielle n'est pas incluse dans le code source (trop volumineuse)
- Elle doit être générée avec vos données spécifiques
- Cette opération peut prendre 5-15 minutes selon la taille de votre fichier CSV

### 3. Vérification finale
Après `python embed.py`, vous devriez voir apparaître un dossier avec un nom aléatoire dans `chroma_db/`

---

## ⚙️ Étape 5.5 : Configuration Centralisée des Chemins (OPTIONNEL)

**🎯 Pour les utilisateurs avancés** : Si vous souhaitez installer le projet dans un autre dossier ou modifier l'emplacement des bases de données, toute la configuration est centralisée dans un seul fichier.

### Modifier les chemins du projet

1. **Ouvrir le fichier de configuration** dans VS Code :
   ```
   config.py
   ```

2. **Modifier uniquement cette ligne** selon vos besoins :
   ```python
   # 🔧 MODIFIEZ UNIQUEMENT CETTE LIGNE SELON VOTRE INSTALLATION :
   PROJECT_ROOT = Path(__file__).parent.absolute()  # Configuration par défaut
   
   # Exemples de personnalisation :
   # PROJECT_ROOT = Path("C:/MonProjet/Assistant_NC")      # Windows
   # PROJECT_ROOT = Path("D:/Projets/RAG_NonConformites")  # Windows autre disque
   # PROJECT_ROOT = Path("/home/user/Assistant_NC")        # Linux/Mac
   ```

3. **Tous les autres chemins** sont calculés automatiquement :
   - Base de données vectorielle : `[VOTRE_CHEMIN]/chroma_db/`
   - Documents CSV : `[VOTRE_CHEMIN]/documents/`
   - Base de données relationnelle : `[VOTRE_CHEMIN]/backend/nonconformites.db`

4. **Vérifier la configuration** (dans le terminal) :
   ```powershell
   python config.py
   ```
   Cette commande affiche tous les chemins configurés.

5. **Diagnostic complet** (dans le terminal) :
   ```powershell
   python check_config.py
   ```
   Ce script vérifie tous les chemins, fichiers et connexions.

6. **Créer les dossiers automatiquement** :
   ```powershell
   python -c "from config import validate_paths; validate_paths()"
   ```

**💡 Conseil** : La configuration par défaut fonctionne parfaitement. Ne modifiez que si vous avez des besoins spécifiques (espace disque, organisation, etc.).

---

## 🚀 Étape 6 : Premier lancement

### 1. Démarrer le backend (dans un terminal)
```powershell
# S'assurer que l'environnement virtuel est activé
./venv/Scripts/activate
# Lancer l'API backend, dans le dossier racine de votre projet toujours
python app.py
```

### 2. Démarrer le frontend (dans un nouveau terminal)
```powershell
# 1. Ouvrir un nouveau terminal dans VS Code (Terminal → New Terminal)
# 2. Activer l'environnement virtuel dans ce nouveau terminal :
./venv/Scripts/activate

# 3. Naviguer vers le frontend
cd frontend

# 4. Lancer le serveur de développement (dans l'environnement virtuel)
npm run dev
```

### 3. Accéder à l'application
- Ouvrir votre navigateur
- Aller à : `http://localhost:5173`
- L'interface utilisateur devrait s'afficher

---

## 🔧 Vérification de l'installation

### Tests de fonctionnement

1. **API Backend** : `http://localhost:8000/docs`
   - Vous devriez voir la documentation automatique de l'API

2. **Frontend** : `http://localhost:5173`
   - L'interface utilisateur devrait se charger

3. **Test IA** : Dans l'interface
   - Créer une nouvelle non-conformité
   - Poser une question à l'assistant IA
   - Vérifier que la réponse s'affiche

### Diagnostic en cas de problème

```powershell
# 🔍 DIAGNOSTIC COMPLET - Recommandé en premier
python check_config.py

# Vérifier les services (dans le terminal)
python diagnose_chroma.py

# Tester la connexion Ollama (dans le terminal)
python -c "import requests; print(requests.get('http://localhost:11434/api/tags').json())"
```

---

## 📂 Structure des dossiers

```
votre-projet/
├── config.py             # ⚙️ CONFIGURATION CENTRALISÉE (chemins, modèles)
├── backend/              # Code Python API
├── frontend/             # Interface React
├── documents/            # Fichiers CSV à importer (configurable)
├── chroma_db/           # Base de données vectorielle (configurable)
├── app.py               # Serveur principal
├── requirements.txt     # Dépendances Python
└── README_INSTALLATION.md
```

**🔧 Configuration centralisée** : Tous les chemins importants sont configurables dans le fichier `config.py`. Modifiez une seule ligne pour adapter le projet à votre environnement.

**⚠️ Important** : Le dossier `chroma_db/` n'est pas versionné. Si vous clonez le projet sur un nouveau poste, vous devez **toujours** recréer la base vectorielle avec `python embed.py`.

---

## 🔄 Utilisation quotidienne

### Démarrage rapide
1. Ouvrir PowerShell (terminal) dans le dossier du projet
2. Activer l'environnement dans le terminal : `./venv/Scripts/activate`
3. Lancer le backend dans le terminal : `python app.py`
4. Ouvrir un nouveau terminal PowerShell : 
   - Activer l'environnement : `./venv/Scripts/activate`
   - Aller au frontend : `cd frontend`
   - Lancer le frontend : `npm run dev`
5. Aller sur `http://localhost:5173`

### Arrêt
- `Ctrl+C` dans chaque terminal pour arrêter les serveurs front et back

---

## 🆘 Résolution des problèmes courants

### Erreur "Port already in use"
Dans le terminal PowerShell :
```powershell
# Tuer les processus sur le port 8000
netstat -ano | findstr :8000
taskkill /PID [numéro_processus] /F
```

### Erreur d'environnement virtuel
Dans le terminal PowerShell :
```powershell
# Supprimer et recréer l'environnement
rmdir /s venv
python -m venv venv
./venv/Scripts/activate
pip install -r requirements.txt
```

### Ollama ne répond pas
1. Redémarrer l'application Ollama
2. Vérifier dans la barre système (icône de la caméléon)
3. Si nécessaire, dans le terminal : `ollama serve`

### Problèmes de modèles IA
Dans le terminal PowerShell :
```powershell
# Re-télécharger un modèle
ollama pull phi4-reasoning --insecure
```

### Base vectorielle (ChromaDB) corrompue ou manquante
```powershell
# Supprimer l'ancienne base vectorielle
rmdir /s chroma_db

# Recréer la base vectorielle (CHOISIR selon votre configuration)
cd backend

# Pour PC performant :
python embed.py "dengcao/Qwen3-Embedding-0.6B:f16"

# Pour PC classique :
python embed.py "toshk0/nomic-embed-text-v2-moe"

cd ..
```

**💡 Note** : Cette opération prend 5-15 minutes et doit être refaite à chaque nouveau clone du projet.

---

## 📞 Support

### Logs de diagnostic
- Backend : Consulter la console où `uvicorn` est lancé
- Frontend : Console du navigateur (F12)
- Ollama : `ollama logs`

### Fichiers de configuration importants
- **`config.py`** : 🎯 **FICHIER PRINCIPAL** - Configuration centralisée des chemins et modèles IA
- `backend/database.py` : Configuration base de données
- `frontend/src/config/api.js` : URLs de l'API

---

## 🔄 Mise à jour du projet

Dans le terminal PowerShell :
```powershell
# Récupérer les dernières modifications
git pull origin main

# Mettre à jour les dépendances Python
pip install -r requirements.txt --upgrade

# Mettre à jour les dépendances frontend
cd frontend
npm update
cd ..

# ⚠️ IMPORTANT: Régénérer la base vectorielle si de nouvelles données sont disponibles
cd backend

# CHOISIR selon votre configuration :
# Pour PC performant :
python embed.py "dengcao/Qwen3-Embedding-0.6B:f16"
# Pour PC classique :
python embed.py "toshk0/nomic-embed-text-v2-moe"

cd ..
```
```

**💡 Note** : La base vectorielle (ChromaDB) n'est pas versionnée. Après chaque `git pull`, vérifiez s'il y a de nouveaux fichiers dans `documents/` et relancez `python embed.py "nom_du_modèle"` si nécessaire.

---

## ✅ Check-list de validation

- [ ] Python 3.11+ installé avec PATH configuré
- [ ] Node.js et npm installés
- [ ] Ollama installé et modèles téléchargés
- [ ] Projet cloné depuis Azure DevOps
- [ ] Environnement virtuel Python créé et activé
- [ ] Dépendances Python installées (`pip install -r requirements.txt`)
- [ ] Dépendances frontend installées (`npm install`)
- [ ] **Configuration vérifiée** (`python check_config.py` ✅)
- [ ] Base de données relationnelle créée
- [ ] **Base vectorielle créée** (`python embed.py "nom_du_modèle"` dans backend/ ✅)
- [ ] Backend démarre sans erreur (port 8000)
- [ ] Frontend démarre sans erreur (port 5173)
- [ ] Interface accessible dans le navigateur
- [ ] Test IA fonctionnel

---


Pour toute question ou problème, consultez les logs d'erreur et n'hésitez pas à demander de l'aide à l'équipe technique.
