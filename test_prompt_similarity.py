"""
Test de recherche de similarité vectorielle entre requête utilisateur et prompts 8D
Utilise OllamaEmbeddings avec le modèle dengcao/Qwen3-Embedding-0.6B:f16
"""

import os
import sys
from typing import List, Dict, Tuple, Any
import numpy as np
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import chromadb
from sklearn.metrics.pairwise import cosine_similarity

# Ajouter le backend au path pour importer les prompts
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import des prompts depuis le fichier backend/prompts.py
from backend.prompts import (
    rag_8D_prompt_template_llama,
    prompt_8D_1_template,
    prompt_8D_2_template,
    prompt_8D_3_template,
    prompt_8D_4_main_oeuvre_template,
    prompt_8D_4_materiel_template,
    prompt_8D_4_matiere_template,
    prompt_8D_4_methode_template,
    prompt_8D_4_milieu_template,
    prompt_8D_4_5why_template,
    prompt_8D_5_corrective_template,
    prompt_8D_5_preventive_template,
    prompt_8D_6_template,
    prompt_8D_7_template,
    prompt_8D_8_template
)

class PromptSimilarityFinder:
    def __init__(self, model_name: str = "dengcao/Qwen3-Embedding-0.6B:f16", ollama_endpoint: str = "http://localhost:11434"):
        """
        Initialise le système de recherche de similarité des prompts
        
        Args:
            model_name: Nom du modèle d'embedding Ollama
            ollama_endpoint: URL de l'API Ollama
        """
        self.model_name = model_name
        self.ollama_endpoint = ollama_endpoint
        self.embeddings = None
        self.prompt_documents = []
        self.prompt_vectors = []
        self.vectorstore = None
        
        # Mapping des templates vers leurs métadonnées
        self.prompt_mapping = {
            "general_8d": {
                "template": rag_8D_prompt_template_llama,
                "step": "général",
                "description": "Prompt général pour la résolution 8D"
            },
            "8d_step_1": {
                "template": prompt_8D_1_template,
                "step": "1D",
                "description": "Formation de l'équipe"
            },
            "8d_step_2": {
                "template": prompt_8D_2_template,
                "step": "2D", 
                "description": "Description du problème (QQOQCCP)"
            },
            "8d_step_3": {
                "template": prompt_8D_3_template,
                "step": "3D",
                "description": "Actions curatives immédiates"
            },
            "8d_step_4_main_oeuvre": {
                "template": prompt_8D_4_main_oeuvre_template,
                "step": "4D",
                "description": "Analyse des causes - Main d'œuvre (Ishikawa)"
            },
            "8d_step_4_materiel": {
                "template": prompt_8D_4_materiel_template,
                "step": "4D",
                "description": "Analyse des causes - Matériel (Ishikawa)"
            },
            "8d_step_4_matiere": {
                "template": prompt_8D_4_matiere_template,
                "step": "4D",
                "description": "Analyse des causes - Matière (Ishikawa)"
            },
            "8d_step_4_methode": {
                "template": prompt_8D_4_methode_template,
                "step": "4D",
                "description": "Analyse des causes - Méthode (Ishikawa)"
            },
            "8d_step_4_milieu": {
                "template": prompt_8D_4_milieu_template,
                "step": "4D",
                "description": "Analyse des causes - Milieu (Ishikawa)"
            },
            "8d_step_4_5why": {
                "template": prompt_8D_4_5why_template,
                "step": "4D",
                "description": "Analyse des causes - 5 Pourquoi"
            },
            "8d_step_5_corrective": {
                "template": prompt_8D_5_corrective_template,
                "step": "5D",
                "description": "Actions correctives permanentes"
            },
            "8d_step_5_preventive": {
                "template": prompt_8D_5_preventive_template,
                "step": "5D",
                "description": "Actions préventives permanentes"
            },
            "8d_step_6": {
                "template": prompt_8D_6_template,
                "step": "6D",
                "description": "Mise en œuvre et validation des actions correctives"
            },
            "8d_step_7": {
                "template": prompt_8D_7_template,
                "step": "7D",
                "description": "Mise en œuvre et validation des actions préventives"
            },
            "8d_step_8": {
                "template": prompt_8D_8_template,
                "step": "8D",
                "description": "Capitalisation et félicitations de l'équipe"
            }
        }
    
    def initialize_embeddings(self):
        """Initialise le modèle d'embeddings Ollama"""
        try:
            print(f"Initialisation des embeddings avec le modèle: {self.model_name}")
            self.embeddings = OllamaEmbeddings(
                model=self.model_name,
                base_url=self.ollama_endpoint
            )
            
            # Test avec un embedding simple
            test_embedding = self.embeddings.embed_query("test")
            print(f"✅ Embeddings initialisés avec succès. Dimension: {len(test_embedding)}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation des embeddings: {e}")
            print("Vérifiez que:")
            print("1. Ollama est démarré")
            print(f"2. Le modèle {self.model_name} est installé")
            print("3. L'API Ollama est accessible")
            return False
    
    def extract_prompt_content(self, template: str) -> str:
        """
        Extrait le contenu textuel principal d'un template de prompt
        en supprimant les balises de format Llama
        """
        # Supprimer les balises de format Llama
        content = template.replace("<|begin_of_text|>", "")
        content = content.replace("<|start_header_id|>system<|end_header_id|>", "")
        content = content.replace("<|start_header_id|>user<|end_header_id|>", "")
        content = content.replace("<|start_header_id|>assistant<|end_header_id|>", "")
        content = content.replace("<|start_header_id|>end_header_id|>", "")
        content = content.replace("<|eot_id|>", "")
        
        # Supprimer les variables de template
        content = content.replace("{input}", "")
        content = content.replace("{context}", "")
        content = content.replace("{query}", "")
        
        # Nettoyer les espaces multiples et les retours à la ligne
        content = " ".join(content.split())
        
        return content.strip()
    
    def create_prompt_documents(self) -> List[Document]:
        """Crée des documents à partir des templates de prompts"""
        documents = []
        
        for prompt_id, prompt_info in self.prompt_mapping.items():
            # Extraire le contenu textuel principal
            content = self.extract_prompt_content(prompt_info["template"])
            
            # Créer un document avec métadonnées
            doc = Document(
                page_content=content,
                metadata={
                    "prompt_id": prompt_id,
                    "step": prompt_info["step"],
                    "description": prompt_info["description"],
                    "source": "8d_prompts"
                }
            )
            documents.append(doc)
            
        print(f"✅ {len(documents)} documents créés à partir des prompts")
        return documents
    
    def build_vectorstore(self, persist_directory: str = "./chroma_prompts_db"):
        """Construit la base vectorielle avec les prompts"""
        if not self.embeddings:
            print("❌ Embeddings non initialisés")
            return False
        
        try:
            # Créer les documents
            self.prompt_documents = self.create_prompt_documents()
            
            # Supprimer l'ancienne base si elle existe
            if os.path.exists(persist_directory):
                import shutil
                shutil.rmtree(persist_directory)
                print(f"🗑️ Ancienne base vectorielle supprimée: {persist_directory}")
            
            # Créer la nouvelle base vectorielle
            print("🔨 Création de la base vectorielle...")
            self.vectorstore = Chroma.from_documents(
                documents=self.prompt_documents,
                embedding=self.embeddings,
                persist_directory=persist_directory,
                collection_name="prompts_8d"
            )
            
            print(f"✅ Base vectorielle créée avec {len(self.prompt_documents)} prompts")
            return True
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de la base vectorielle: {e}")
            return False
    
    def find_most_similar_prompt(self, user_query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Trouve les prompts les plus similaires à la requête utilisateur
        
        Args:
            user_query: Requête de l'utilisateur
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste des prompts les plus similaires avec scores
        """
        if not self.vectorstore:
            print("❌ Base vectorielle non initialisée")
            return []
        
        try:
            print(f"🔍 Recherche de similarité pour: '{user_query}'")
            
            # Recherche de similarité
            results = self.vectorstore.similarity_search_with_score(
                query=user_query,
                k=top_k
            )
            
            # Formater les résultats
            formatted_results = []
            for doc, score in results:
                result = {
                    "prompt_id": doc.metadata["prompt_id"],
                    "step": doc.metadata["step"],
                    "description": doc.metadata["description"],
                    "similarity_score": float(1 - score),  # Convertir distance en similarité
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "full_template": self.prompt_mapping[doc.metadata["prompt_id"]]["template"]
                }
                formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Erreur lors de la recherche: {e}")
            return []
    
    def display_results(self, results: List[Dict[str, Any]]):
        """Affiche les résultats de recherche de manière formatée"""
        if not results:
            print("❌ Aucun résultat trouvé")
            return
        
        print("\n" + "="*80)
        print("🎯 RÉSULTATS DE LA RECHERCHE DE SIMILARITÉ")
        print("="*80)
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. 📋 PROMPT: {result['prompt_id'].upper()}")
            print(f"   📝 Étape: {result['step']}")
            print(f"   📖 Description: {result['description']}")
            print(f"   📊 Score de similarité: {result['similarity_score']:.4f}")
            print(f"   📄 Aperçu: {result['content_preview']}")
            print("-" * 60)

def test_prompt_similarity():
    """Fonction de test principale"""
    print("🚀 DÉMARRAGE DU TEST DE SIMILARITÉ DES PROMPTS 8D")
    print("="*60)
    
    # Initialiser le système
    finder = PromptSimilarityFinder()
    
    # Étape 1: Initialiser les embeddings
    if not finder.initialize_embeddings():
        return False
    
    # Étape 2: Construire la base vectorielle
    if not finder.build_vectorstore():
        return False
    
    # Étape 3: Tests avec différentes requêtes utilisateur
    test_queries = [
        "Je veux former une équipe pour résoudre un problème qualité",
        "Comment décrire précisément mon problème de non-conformité ?",
        "Quelles actions immédiates dois-je prendre ?",
        "Je cherche les causes liées au personnel dans mon problème",
        "Comment analyser les causes liées aux machines ?",
        "Je veux comprendre pourquoi ce problème est arrivé",
        "Quelles solutions permanentes proposer ?",
        "Comment éviter que ce problème se reproduise ?",
        "Comment valider que mes actions fonctionnent ?",
        "Je veux capitaliser sur cette résolution",
        "Problème de qualité sur une pièce défectueuse",
        "Ma machine ne fonctionne plus correctement"
    ]
    
    print(f"\n🧪 TEST AVEC {len(test_queries)} REQUÊTES DIFFÉRENTES")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 TEST {i}: {query}")
        print("-" * 40)
        
        results = finder.find_most_similar_prompt(query, top_k=3)
        
        if results:
            print(f"✅ Meilleur match: {results[0]['step']} - {results[0]['description']}")
            print(f"   Score: {results[0]['similarity_score']:.4f}")
            
            # Afficher les 3 meilleurs résultats pour le premier test
            if i == 1:
                finder.display_results(results)
        else:
            print("❌ Aucun résultat")
    
    return True

def interactive_test():
    """Test interactif permettant à l'utilisateur de saisir ses propres requêtes"""
    print("\n🎮 MODE INTERACTIF")
    print("="*40)
    
    finder = PromptSimilarityFinder()
    
    if not finder.initialize_embeddings():
        return
    
    if not finder.build_vectorstore():
        return
    
    print("\n✅ Système prêt ! Saisissez vos requêtes (tapez 'quit' pour sortir)")
    
    while True:
        user_query = input("\n🔍 Votre requête: ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("👋 Au revoir !")
            break
        
        if not user_query:
            continue
        
        results = finder.find_most_similar_prompt(user_query, top_k=3)
        finder.display_results(results)

if __name__ == "__main__":
    # Test automatique
    success = test_prompt_similarity()
    
    if success:
        # Proposer le mode interactif
        print("\n" + "="*60)
        user_input = input("Voulez-vous tester le mode interactif ? (y/n): ").strip().lower()
        if user_input in ['y', 'yes', 'o', 'oui']:
            interactive_test()
    
    print("\n🎉 Tests terminés !")
