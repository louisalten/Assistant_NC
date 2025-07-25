# backend/utils/doc_processing.py

from typing import List, Dict
from langchain_core.documents import Document

def build_sources(docs: List[Document], mode: str = "RAG", scores: List[float] = None) -> List[Dict]:
    sources = []
    for i, doc in enumerate(docs):
        meta = getattr(doc, "metadata", {})
        content = getattr(doc, "page_content", "")
        nc_id = meta.get("id_non_conformite") or meta.get("Identification NC 0D", "Inconnu")
        source_file = meta.get("nom_fichier_source", "Source Manquante")
        preview = (content or "")[:150] + "..."
        
        # Préparer la source avec le score de similarité si disponible
        source = {
            "nc_id": nc_id,
            "content": meta.get("Description du problème 0D") or preview,
            "preview": preview,
            "source_file": source_file,
        }
        
        # Ajouter le score de similarité si disponible
        if scores and i < len(scores):
            # Convertir la distance en score de similarité (plus c'est proche de 1, plus c'est similaire)
            similarity_score = 1 - scores[i]
            source["similarity_score"] = round(similarity_score, 3)
        
        sources.append(source)
    return sources

def get_source_by_id(nc_id: str, db_dir: str = None) -> Dict:
    """
    Récupère directement les données d'une source par son ID (format 'NC-XXX')
    """
    from langchain_community.vectorstores import Chroma
    from backend.embed import get_embedding_model
    from config import get_model_id, DEFAULT_EMBEDDING_MODEL_KEY, DB_DIR
    
    # Utiliser la configuration centralisée si aucun db_dir n'est fourni
    if db_dir is None:
        db_dir = DB_DIR
    
    # Extraire le numéro si l'ID est au format 'NC-XXX'
    search_id = nc_id
    if "-" in nc_id:
        search_id = nc_id.split("-")[-1]  # Prend juste le nombre après le tiret
    
    print(f"[DEBUG] Recherche de source avec NC ID: {search_id}")
    
    # Initialiser l'embedding et Chroma avec le modèle par défaut
    model_id = get_model_id(DEFAULT_EMBEDDING_MODEL_KEY)
    embeddings = get_embedding_model(model_id)
    db = Chroma(persist_directory=db_dir, embedding_function=embeddings)
    
    # Recherche par metadata
    results = db.get(
        where={"id_non_conformite": {"$eq": search_id}},
        include=["metadatas", "documents"]
    )
    
    # Si aucun résultat, essayer d'autres champs de métadonnées
    if not results["ids"]:
        results = db.get(
            where={"Identification NC 0D": {"$eq": search_id}},
            include=["metadatas", "documents"]
        )
    
    # Si toujours aucun résultat, faire une recherche par similarité sémantique
    if not results["ids"]:
        results = db.similarity_search(f"NC {search_id}", k=1)
        if results:
            # Convertir le résultat en format compatible
            return {
                "nc_id": search_id,
                "content": results[0].page_content,
                "metadata": results[0].metadata
            }
        return None
    
    # Formater la réponse
    if results["ids"] and len(results["ids"]) > 0:
        idx = 0
        return {
            "nc_id": search_id,
            "content": results["documents"][idx],
            "metadata": results["metadatas"][idx]
        }
    
    return None

def get_source_by_id(nc_id: str) -> Dict:
    """
    Récupère les données d'une source par son ID (format 'NC-XXX')
    Utilise une approche simplifiée sans embedding
    """
    # Extraire le numéro si l'ID est au format 'NC-XXX'
    original_id = nc_id  # Conserver l'ID original pour les logs et le retour
    search_id = nc_id
    
    if isinstance(nc_id, str):
        if "-" in nc_id:
            search_id = nc_id.split("-")[-1]  # Prend juste le nombre après le tiret
            print(f"[DEBUG] ID transformé de '{nc_id}' à '{search_id}'")
    
    print(f"[DEBUG] Recherche de source directe pour NC ID: {search_id} (original: {original_id})")
    
    # Lire les données depuis le fichier CSV source
    import pandas as pd
    import os
    from pathlib import Path
    
    # Essayer différents chemins pour le fichier CSV
    possible_paths = [
        os.path.join("documents", "NC5_clean.csv"),
        os.path.join("documents", "NC5.csv"),
        os.path.join("C:", "Users", "lrodembourg", "Documents", "Test_Langchain", "documents", "NC5_clean.csv"),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "documents", "NC5_clean.csv")),
        "./documents/NC5_clean.csv"
    ]
    
    csv_path = None
    for path in possible_paths:
        if os.path.exists(path):
            csv_path = path
            print(f"[DEBUG] Fichier CSV trouvé: {path}")
            break
    
    if not csv_path:
        print(f"[ERREUR] Fichier CSV non trouvé. Chemins essayés: {possible_paths}")
        # Lister le contenu du répertoire documents
        try:
            docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "documents"))
            print(f"[DEBUG] Contenu du répertoire documents ({docs_dir}):")
            for item in os.listdir(docs_dir):
                print(f"  - {item}")
        except Exception as e:
            print(f"[DEBUG] Impossible de lister le contenu du répertoire: {e}")
        return None
    
    try:
        # Lire le CSV
        print(f"[DEBUG] Tentative de lecture du CSV: {csv_path}")
        df = pd.read_csv(csv_path, sep=';')
        
        print(f"[DEBUG] CSV chargé avec succès: {len(df)} lignes")
        print(f"[DEBUG] Colonnes du CSV: {df.columns.tolist()}")
        print(f"[DEBUG] Échantillon des valeurs d'ID disponibles: {df['Identification NC 0D'].astype(str).tolist()[:5]}...")
        
        # Convertir l'ID recherché en chaîne pour assurer la correspondance
        str_search_id = str(search_id).strip()
        print(f"[DEBUG] Recherche d'ID: '{str_search_id}'")
        
        # Afficher quelques lignes pour déboguer
        print(f"[DEBUG] Échantillon des premières lignes:")
        for idx, row in df.head(3).iterrows():
            print(f"  - Ligne {idx}, ID: '{row.get('Identification NC 0D')}', Type: {type(row.get('Identification NC 0D'))}")
        
        # Recherche par ID dans la colonne 'Identification NC 0D' avec plusieurs approches
        matching_rows = pd.DataFrame()
        
        # 1. Recherche exacte
        exact_matches = df[df["Identification NC 0D"].astype(str).str.strip() == str_search_id]
        if len(exact_matches) > 0:
            print(f"[DEBUG] Trouvé correspondance exacte pour '{str_search_id}'")
            matching_rows = exact_matches
        
        # 2. Recherche avec le format "NC-XXX"
        elif not matching_rows.empty and "NC-" not in str_search_id.upper():
            nc_format_id = f"NC-{str_search_id}"
            nc_matches = df[df["Identification NC 0D"].astype(str).str.strip() == nc_format_id]
            if len(nc_matches) > 0:
                print(f"[DEBUG] Trouvé correspondance avec format NC- pour '{nc_format_id}'")
                matching_rows = nc_matches
        
        # 3. Recherche flexible (contient le numéro)
        if matching_rows.empty:
            print(f"[DEBUG] Essai de recherche flexible...")
            flexible_matches = []
            for idx, row in df.iterrows():
                row_id = str(row.get("Identification NC 0D", "")).strip()
                if row_id == str_search_id or row_id.endswith(str_search_id) or str_search_id in row_id:
                    print(f"[DEBUG] Trouvé une correspondance flexible à l'index {idx}: '{row_id}'")
                    flexible_matches.append(idx)
                    break
            
            if flexible_matches:
                matching_rows = df.iloc[flexible_matches]
        
        if matching_rows.empty:
            print(f"[AVERTISSEMENT] Aucune NC trouvée avec ID '{str_search_id}' ni format similaire")
            return None
        
        # Prendre la première correspondance
        row = matching_rows.iloc[0]
        print(f"[DEBUG] NC trouvée avec ID '{row.get('Identification NC 0D')}'")
        
        # Créer le contenu textuel
        content_columns = [
            "Identification NC 0D", "Description du problème 0D", "Article impacté (pas de marque et/ou modèle) 0D", 
            "Date de Détection 0D(jj/mm/aaaa)", "Criticité 0D", "Quoi/Quelle pièce est impactée ? 2D",
            "Combien de pièces impactée ? (0000) 2D", "Pourquoi est ce un problème ? 2D",
            "Cause Racine 4D", "Résumé 8D"
        ]
        
        content_parts = []
        for col in content_columns:
            if col in row.index and not pd.isna(row[col]) and str(row[col]).strip():
                content_parts.append(f"{col}: {row[col]}")
        
        content = "\n\n".join(content_parts)
        
        # Créer les métadonnées
        metadata = {}
        for col in row.index:
            if not pd.isna(row[col]):
                metadata[col] = str(row[col])
        
        # Utiliser l'ID original pour la cohérence avec la requête
        return {
            "nc_id": original_id,
            "content": content,
            "metadata": metadata,
            "source_file": os.path.basename(csv_path)
        }
        
    except Exception as e:
        print(f"[ERREUR] Problème lors de la lecture du CSV: {str(e)}")
        import traceback
        traceback.print_exc()
        return None