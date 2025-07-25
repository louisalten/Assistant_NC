import os
from pathlib import Path

# ========================================
# CONFIGURATION DES CHEMINS - À ADAPTER PAR L'UTILISATEUR
# ========================================
# 🔧 MODIFIEZ UNIQUEMENT CETTE LIGNE SELON VOTRE INSTALLATION :
# Par défaut, utilise le dossier du projet. Pour changer, remplacez par votre chemin :
# Exemples :
# PROJECT_ROOT = Path("C:/MonProjet/Assistant_NC")  # Windows
# PROJECT_ROOT = Path("/home/user/Assistant_NC")    # Linux/Mac
PROJECT_ROOT = Path(__file__).parent.absolute()  # Chemin automatique vers le dossier du projet

# ========================================
# CHEMINS DÉRIVÉS (NE PAS MODIFIER)
# ========================================
# Ces chemins sont calculés automatiquement à partir de PROJECT_ROOT
CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"
DOCUMENTS_DIR = PROJECT_ROOT / "documents"
DATABASE_PATH = PROJECT_ROOT / "backend" / "nonconformites.db"

# Conversion en string pour compatibilité avec l'ancien code
DB_DIR = str(CHROMA_DB_DIR)
DOCUMENTS_DIR_STR = str(DOCUMENTS_DIR)
DATABASE_PATH_STR = str(DATABASE_PATH)

# ========================================
# CONFIGURATION DES MODÈLES IA
# ========================================
AVAILABLE_EMBEDDING_MODELS = {
    "qwen_base": "dengcao/Qwen3-Embedding-0.6B:f16",
    "dengcao_qwen3_4b": "dengcao/Qwen3-Embedding-4B:q5_K_M",
    "snowflake2": "snowflake-arctic-embed2:latest"
    # Ajoutez d'autres modèles que vous voulez tester ici
}

# Modèle par défaut à utiliser si aucun n'est spécifié
DEFAULT_EMBEDDING_MODEL_KEY = "qwen_base"

# Fonction utilitaire pour obtenir l'identifiant technique à partir de la clé
def get_model_id(model_key: str | None) -> str:
    """Retourne l'ID du modèle à partir de sa clé. Utilise le défaut si invalide."""
    if not model_key or model_key not in AVAILABLE_EMBEDDING_MODELS:
        model_key = DEFAULT_EMBEDDING_MODEL_KEY
    return AVAILABLE_EMBEDDING_MODELS[model_key]

# ========================================
# CONFIGURATION OLLAMA
# ========================================
OLLAMA_ENDPOINT = "http://localhost:11434"

# ========================================
# AFFICHAGE DE LA CONFIGURATION
# ========================================
def show_config():
    """Affiche la configuration actuelle pour diagnostic"""
    print("=== CONFIGURATION ACTUELLE ===")
    print(f"Racine du projet: {PROJECT_ROOT}")
    print(f"Base ChromaDB: {DB_DIR}")
    print(f"Dossier documents: {DOCUMENTS_DIR_STR}")
    print(f"Base de données: {DATABASE_PATH_STR}")
    print(f"Endpoint Ollama: {OLLAMA_ENDPOINT}")
    print("==============================")

def validate_paths():
    """Vérifie que tous les chemins existent et les crée si nécessaire"""
    try:
        # Créer les dossiers s'ils n'existent pas
        CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        (PROJECT_ROOT / "backend").mkdir(parents=True, exist_ok=True)
        
        print("✅ Tous les dossiers requis existent ou ont été créés.")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création des dossiers: {e}")
        return False

if __name__ == "__main__":
    show_config()
    validate_paths()
