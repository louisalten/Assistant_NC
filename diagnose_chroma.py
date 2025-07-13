import chromadb
import os
from pathlib import Path
import sqlite3

DB_DIR = "C:/Users/lrodembourg/Documents/Test_Langchain/chroma_db"

def diagnose_chroma_db():
    """Diagnostic complet de la base de données ChromaDB"""
    
    print("=== DIAGNOSTIC ChromaDB ===")
    print(f"Répertoire de base: {DB_DIR}")
    print(f"Répertoire existe: {Path(DB_DIR).exists()}")
    
    if Path(DB_DIR).exists():
        print(f"Contenu du répertoire:")
        for item in Path(DB_DIR).iterdir():
            if item.is_file():
                print(f"  📄 {item.name} ({item.stat().st_size} bytes)")
            else:
                print(f"  📁 {item.name}/")
    
    print("\n=== Test avec différents clients ===")
    
    # Test 1: Client par défaut
    print("\n1. Test avec client par défaut:")
    try:
        client_default = chromadb.PersistentClient()
        collections = client_default.list_collections()
        print(f"   Collections trouvées: {len(collections)}")
        for c in collections:
            print(f"   - {c.name}")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Test 2: Client avec path
    print("\n2. Test avec client path:")
    try:
        client_path = chromadb.PersistentClient(path=DB_DIR)
        collections = client_path.list_collections()
        print(f"   Collections trouvées: {len(collections)}")
        for c in collections:
            print(f"   - {c.name}")
    except Exception as e:
        print(f"   Erreur: {e}")
    
    # Test 3: Inspection de la base SQLite
    print("\n3. Inspection de la base SQLite:")
    sqlite_path = Path(DB_DIR) / "chroma.sqlite3"
    if sqlite_path.exists():
        try:
            conn = sqlite3.connect(str(sqlite_path))
            cursor = conn.cursor()
            
            # Lister les tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"   Tables trouvées: {[t[0] for t in tables]}")
            
            # Vérifier la table collections
            if ('collections',) in tables:
                cursor.execute("SELECT name, id FROM collections;")
                collections_db = cursor.fetchall()
                print(f"   Collections dans la DB: {collections_db}")
            
            conn.close()
        except Exception as e:
            print(f"   Erreur SQLite: {e}")
    else:
        print(f"   Fichier SQLite non trouvé: {sqlite_path}")

if __name__ == "__main__":
    diagnose_chroma_db()
