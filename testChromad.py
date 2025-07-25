# new_script_debug_chroma.py
import chromadb
from config import DB_DIR  # Import de la configuration centralisée

# Configurez avec les mêmes paramètres que votre application
COLLECTION_NAME = "dengcao_Qwen3-Embedding-0.6B_f16"

# def inspect_collection():
#     # client = chromadb.PersistentClient(path=DB_DIR) # Si vous persistez sur disque
#     client = chromadb.PersistentClient() # Si vous utilisez le client par défaut

#     print(f"Tentative de connexion à la collection : '{COLLECTION_NAME}'")
    
#     try:
#         collection = client.get_collection(name=COLLECTION_NAME)
        
#         # Obtenir le nombre total d'éléments
#         count = collection.count()
#         print(f"✅ Connexion réussie ! La collection contient {count} documents.")
        
#         if count > 0:
#             # Récupérer un échantillon de documents pour les inspecter
#             print("\n--- Échantillon de 5 documents ---")
#             sample = collection.get(
#                 limit=5,
#                 include=["metadatas", "documents"] # 'documents' est le contenu textuel
#             )
            
#             for i in range(len(sample['ids'])):
#                 print(f"\nDocument ID: {sample['ids'][i]}")
#                 print(f"  Metadata: {sample['metadatas'][i]}")
#                 print(f"  Content: {sample['documents'][i][:200]}...") # Aperçu du contenu
                
#     except Exception as e:
#         print(f"❌ ERREUR: Impossible d'accéder à la collection. Erreur : {e}")
#         print("\nPistes possibles :")
#         print(" - La collection n'existe pas ou le nom est incorrect.")
#         print(" - Problème de connexion au client ChromaDB.")
#         print(" - Vérifiez que le `PersistentClient` pointe au bon endroit.")

# if __name__ == "__main__":
#     # inspect_collection()

# # script_list_collections.py
# # import chromadb

import chromadb

def list_all_collections_with_counts():
    """
    Se connecte au client ChromaDB persistant et liste toutes les collections disponibles
    avec le nombre de documents dans chacune.
    :param path: Chemin vers la base de données Chroma persistante.
    """
    print("Tentative de connexion au client ChromaDB persistant...")
    
    try:
        client = chromadb.PersistentClient(path=DB_DIR)
        print("✅ Connexion au client réussie.")
        
        collections = client.list_collections()
        
        if not collections:
            print("\n-> Aucune collection trouvée dans cette instance de ChromaDB.")
            print("   Vérifiez que vous utilisez le même chemin de persistence qu’à l’indexation.")
        else:
            print(f"\n-> {len(collections)} collection(s) trouvée(s) :")
            for i, col_meta in enumerate(collections):
                # Important : on doit recharger la collection pour avoir accès à ses méthodes
                collection = client.get_collection(name=col_meta.name)
                count = collection.count()
                print(f"  {i+1}. Nom : {col_meta.name} | 📄 {count} document(s)")
                
    except Exception as e:
        print(f"❌ ERREUR lors de la tentative de lister les collections : {e}")



# if __name__ == "__main__":
#     # list_all_collections_with_counts(path="chemin/vers/ta/db")
#     list_all_collections_with_counts()
# import chromadb

def clean_empty_collections():
    """
    Se connecte au client ChromaDB persistant, liste les collections,
    affiche leur taille et supprime celles qui sont vides (0 documents).
    :param path: Chemin vers la base de données Chroma persistante.
    """
    print("Connexion au client ChromaDB persistant...")

    try:
        client = chromadb.PersistentClient(path=DB_DIR)
        print("✅ Connexion réussie.")

        collections = client.list_collections()
        removed = []

        if not collections:
            print("\n-> Aucune collection trouvée.")
        else:
            print(f"\n-> {len(collections)} collection(s) détectée(s) :\n")
            for i, col_meta in enumerate(collections):
                collection = client.get_collection(name=col_meta.name)
                count = collection.count()
                print(f"  {i+1}. {col_meta.name} | 📄 {count} document(s)")

                if count == 0:
                    print(f"     🗑️ Suppression de la collection vide : {col_meta.name}")
                    client.delete_collection(name=col_meta.name)
                    removed.append(col_meta.name)

            print("\n✅ Nettoyage terminé.")
            if removed:
                print(f"➡️ Collections supprimées ({len(removed)}) : {', '.join(removed)}")
            else:
                print("➡️ Aucune collection vide à supprimer.")

    except Exception as e:
        print(f"❌ ERREUR : {e}")

if __name__ == "__main__":
    # clean_empty_collections(path="chemin/vers/ta/db")
    # clean_empty_collections()
    list_all_collections_with_counts()


def delete_collection_by_name(name: str):
    """
    Supprime une collection spécifique dans ChromaDB.
    :param name: Nom exact de la collection à supprimer.
    :param path: Chemin de la base persistante, si utilisé.
    """
    try:
        client = chromadb.PersistentClient(path=DB_DIR)
        print(f"🔍 Recherche de la collection '{name}'...")

        # Vérifie d'abord si la collection existe
        collections = [c.name for c in client.list_collections()]
        if name not in collections:
            print(f"⚠️ La collection '{name}' n'existe pas.")
            return
        
        client.delete_collection(name=name)
        print(f"✅ Collection '{name}' supprimée avec succès.")
    
    except Exception as e:
        print(f"❌ ERREUR : {e}")

# if __name__ == "__main__":
#     delete_collection_by_name("snowflake-arctic-embed2_latest")