#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification de la c            else:
                print("❌ Dossier ChromaDB existe mais est vide")
                print("   🔥 OBLIGATOIRE: Exécutez: cd backend && python embed.py \"nom_du_modèle\"")
                print("   📝 Pour PC performant: python embed.py \"dengcao/Qwen3-Embedding-0.6B:f16\"")
                print("   📝 Pour PC classique: python embed.py \"toshk0/nomic-embed-text-v2-moe\"")
                print("   ⏱️ Cette opération prend 5-15 minutes")
                all_good = False
        else:
            print("❌ ChromaDB non initialisé")
            print("   🔥 OBLIGATOIRE: Exécutez: cd backend && python embed.py \"nom_du_modèle\"")
            print("   📝 Pour PC performant: python embed.py \"dengcao/Qwen3-Embedding-0.6B:f16\"")
            print("   📝 Pour PC classique: python embed.py \"toshk0/nomic-embed-text-v2-moe\"")
            print("   ⏱️ Cette opération prend 5-15 minutes")
            all_good = Falseon du projet RAG 8D
Utilise ce script pour diagnostiquer les chemins et la configuration.
"""

import os
import sys
from pathlib import Path

def check_configuration():
    """
    Vérifie la configuration complète du projet
    """
    print("🔍 DIAGNOSTIC DE CONFIGURATION - Système RAG 8D")
    print("=" * 60)
    
    try:
        # Importer la configuration
        from config import (
            PROJECT_ROOT, DB_DIR, DOCUMENTS_DIR_STR, DATABASE_PATH_STR, 
            OLLAMA_ENDPOINT, show_config, validate_paths
        )
        
        # 1. Afficher la configuration
        show_config()
        print()
        
        # 2. Vérifier l'existence des chemins
        print("📁 VÉRIFICATION DES CHEMINS :")
        print("-" * 30)
        
        paths_to_check = {
            "Dossier racine du projet": PROJECT_ROOT,
            "Base de données vectorielle": Path(DB_DIR),
            "Dossier documents": Path(DOCUMENTS_DIR_STR),
            "Dossier backend": PROJECT_ROOT / "backend",
            "Dossier frontend": PROJECT_ROOT / "frontend"
        }
        
        all_good = True
        for name, path in paths_to_check.items():
            exists = path.exists()
            status = "✅" if exists else "❌"
            print(f"{status} {name}: {path}")
            if not exists:
                all_good = False
        
        print()
        
        # 3. Vérifier les fichiers critiques
        print("📄 FICHIERS CRITIQUES :")
        print("-" * 20)
        
        critical_files = {
            "app.py": PROJECT_ROOT / "app.py",
            "config.py": PROJECT_ROOT / "config.py",
            "requirements.txt": PROJECT_ROOT / "requirements.txt",
            "Base données SQLite": Path(DATABASE_PATH_STR),
            "Frontend package.json": PROJECT_ROOT / "frontend" / "package.json"
        }
        
        for name, file_path in critical_files.items():
            exists = file_path.exists()
            status = "✅" if exists else "❌"
            print(f"{status} {name}: {file_path}")
            if not exists:
                all_good = False
        
        print()
        
        # 4. Vérifier la base vectorielle
        print("🗃️ BASE DE DONNÉES VECTORIELLE :")
        print("-" * 30)
        
        chroma_path = Path(DB_DIR)
        if chroma_path.exists():
            subfolders = [d for d in chroma_path.iterdir() if d.is_dir()]
            if subfolders:
                print(f"✅ ChromaDB initialisée avec {len(subfolders)} collection(s)")
                for folder in subfolders:
                    print(f"   📂 {folder.name}")
                print("   💡 ChromaDB est généré localement et non versionné")
            else:
                print("❌ Dossier ChromaDB existe mais est vide")
                print("   � OBLIGATOIRE: Exécutez: cd backend && python embed.py")
                print("   ⏱️ Cette opération prend 5-15 minutes")
                all_good = False
        else:
            print("❌ ChromaDB non initialisé")
            print("   � OBLIGATOIRE: Exécutez: cd backend && python embed.py")
            print("   ⏱️ Cette opération prend 5-15 minutes")
            all_good = False
        
        print()
        
        # 5. Vérifier les documents
        print("📑 DOCUMENTS SOURCE :")
        print("-" * 18)
        
        docs_path = Path(DOCUMENTS_DIR_STR)
        if docs_path.exists():
            csv_files = list(docs_path.glob("*.csv"))
            pdf_files = list(docs_path.glob("*.pdf"))
            txt_files = list(docs_path.glob("*.txt"))
            
            print(f"✅ Dossier documents existe")
            print(f"   📊 CSV: {len(csv_files)} fichier(s)")
            print(f"   📄 PDF: {len(pdf_files)} fichier(s)")
            print(f"   📝 TXT: {len(txt_files)} fichier(s)")
            
            if csv_files:
                print("   📋 Fichiers CSV trouvés:")
                for csv_file in csv_files:
                    print(f"      • {csv_file.name}")
        else:
            print("❌ Dossier documents introuvable")
            
        print()
        
        # 6. Test de connexion Ollama
        print("🤖 CONNEXION OLLAMA :")
        print("-" * 18)
        
        try:
            import requests
            response = requests.get(f"{OLLAMA_ENDPOINT}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"✅ Ollama accessible sur {OLLAMA_ENDPOINT}")
                print(f"   🧠 {len(models)} modèle(s) installé(s):")
                for model in models:
                    print(f"      • {model['name']}")
            else:
                print(f"⚠️ Ollama répond mais erreur: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Ollama non accessible sur {OLLAMA_ENDPOINT}")
            print("   💡 Vérifiez qu'Ollama est démarré")
        except Exception as e:
            print(f"❌ Erreur test Ollama: {e}")
        
        print()
        
        # 7. Résumé final
        print("📋 RÉSUMÉ :")
        print("-" * 10)
        
        if all_good:
            print("🎉 Configuration OK ! Le projet devrait fonctionner.")
        else:
            print("⚠️ Problèmes détectés. Consultez les détails ci-dessus.")
            print("💡 Conseil: Exécutez 'python -c \"from config import validate_paths; validate_paths()\"'")
        
        print()
        print("🔧 Pour modifier la configuration:")
        print(f"   Éditez le fichier: {PROJECT_ROOT}/config.py")
        print("   Modifiez uniquement la ligne PROJECT_ROOT")
        
    except ImportError as e:
        print(f"❌ Erreur d'import de la configuration: {e}")
        print("💡 Vérifiez que vous êtes dans le bon dossier et que config.py existe")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")

if __name__ == "__main__":
    check_configuration()
