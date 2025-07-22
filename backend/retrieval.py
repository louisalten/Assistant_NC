from .get_vector_db import get_vectorstore
from .step_retrieval_config import step_retrieval_config
from .field_mapping import get_csv_field_name, get_qqoqccp_fields, get_ishikawa_fields, get_five_whys_fields

def extract_relevant_fields_from_docs(docs, current_section_name: str):
    """
    Extrait les champs pertinents des documents selon la configuration de l'étape 8D
    """
    retrieve_fields = step_retrieval_config.get_retrieve_fields(current_section_name)
    print(f"[RETRIEVAL] Champs à extraire pour {current_section_name}: {retrieve_fields}")
    
    extracted_docs = []
    
    for doc in docs:
        # Créer un nouveau contenu focalisé sur les champs pertinents
        relevant_content_parts = []
        metadata = doc.metadata
        
        # Ajouter l'ID de la NC pour référence
        nc_id = metadata.get("id_non_conformite", metadata.get("Identification NC 0D", "Inconnu"))
        relevant_content_parts.append(f"=== NC {nc_id} ===")
        
        # Extraire les champs selon la configuration
        for field in retrieve_fields:
            field_value = None
            
            # Utiliser le mapping pour trouver le bon nom de colonne
            csv_field_name = get_csv_field_name(field)
            
            # Gestion des champs complexes (QQOQCCP, Ishikawa, etc.)
            if field == "descriptionDetaillee":
                qqoqccp_fields = get_qqoqccp_fields()
                qqoqccp_parts = []
                for sub_field, csv_col in qqoqccp_fields.items():
                    value = metadata.get(csv_col)
                    if value:
                        qqoqccp_parts.append(f"  {sub_field}: {value}")
                if qqoqccp_parts:
                    relevant_content_parts.append("QQOQCCP:")
                    relevant_content_parts.extend(qqoqccp_parts)
            
            elif field == "ishikawaData":
                ishikawa_fields = get_ishikawa_fields()
                ishikawa_parts = []
                for sub_field, csv_col in ishikawa_fields.items():
                    value = metadata.get(csv_col)
                    if value:
                        ishikawa_parts.append(f"  {sub_field}: {value}")
                if ishikawa_parts:
                    relevant_content_parts.append("Analyse Ishikawa (5M):")
                    relevant_content_parts.extend(ishikawa_parts)
            
            elif field == "fiveWhysData":
                five_whys_fields = get_five_whys_fields()
                five_whys_parts = []
                for sub_field, csv_col in five_whys_fields.items():
                    value = metadata.get(csv_col)
                    if value:
                        five_whys_parts.append(f"  {sub_field}: {value}")
                if five_whys_parts:
                    relevant_content_parts.append("5 Pourquoi:")
                    relevant_content_parts.extend(five_whys_parts)
            
            else:
                # Champ simple
                field_value = metadata.get(csv_field_name)
                if field_value:
                    relevant_content_parts.append(f"{field}: {field_value}")
        
        # Si aucun champ pertinent trouvé, garder un extrait du contenu original
        if len(relevant_content_parts) == 1:  # Seulement l'ID
            relevant_content_parts.append(f"Contenu: {doc.page_content[:200]}...")
        
        # Créer le nouveau document avec contenu focalisé
        new_content = "\n".join(relevant_content_parts)
        new_doc = type(doc)(
            page_content=new_content,
            metadata=metadata
        )
        extracted_docs.append(new_doc)
    
    return extracted_docs

def get_relevant_documents(
    query_text: str,
    current_section_data: dict,
    current_section_name: str,
    form_data: dict | None = None, # Rend form_data optionnel
    k: int = 3,
    model_key : int | None = None, # Ajout de model_key pour la flexibilité
    return_scores: bool = False,  # Nouveau paramètre pour retourner les scores
):
    # <<< AJOUTEZ CE BLOC DE DEBUG >>>
    print("\n" + "="*50)
    print("DEBUG DANS get_relevant_documents")
    print(f"  - query_text (reçu): '{query_text}'")
    print(f"  - current_section_name (reçu): '{current_section_name}'")
    print(f"  - current_section_data (reçu): {current_section_data}")
    print(f"  - form_data (reçu): {'OUI' if form_data else 'NON'}") # Juste pour voir s'il est là
    if form_data:
        print(f"    - d0_initialisation dans form_data: {form_data.get('d0_initialisation', 'NON TROUVÉ')}")
    print("="*50 + "\n")
    # <<< FIN DU BLOC DE DEBUG >>>
    
    # 1. Configuration spécifique à l'étape 8D
    search_fields = step_retrieval_config.get_search_fields(current_section_name)
    
    print(f"[RETRIEVAL] Configuration pour l'étape {current_section_name}:")
    print(f"  - Champs de recherche: {search_fields}")
    
    # 2. Construction de la requête enrichie selon l'étape
    collected_field_values = {}  # Dictionnaire pour éviter les doublons par champ
    
    # Récupérer les données pertinentes selon la configuration de l'étape
    if form_data:
        for field in search_fields:
            # Chercher dans D0
            if form_data.get('d0_initialisation'):
                value = form_data['d0_initialisation'].get(field)
                if value and value.strip() and field not in collected_field_values:
                    collected_field_values[field] = value.strip()
            
            # Chercher dans les autres sections selon l'étape
            for section_key, section_data in form_data.items():
                if section_data and isinstance(section_data, dict):
                    if field in section_data and section_data[field]:
                        value = section_data[field]
                        if value and value.strip() and field not in collected_field_values:
                            collected_field_values[field] = value.strip()
    
    # Ajouter les données de la section actuelle (priorité aux données actuelles)
    if current_section_data:
        for field in search_fields:
            if field in current_section_data and current_section_data[field]:
                value = current_section_data[field]
                if value and value.strip():
                    collected_field_values[field] = value.strip()  # Écrase les valeurs précédentes
    
    # Construire la requête finale au format "clé: valeur" pour matcher le format des documents
    if collected_field_values:
        enriched_query_parts = []
        for field, value in collected_field_values.items():
            csv_field_name = get_csv_field_name(field)
            enriched_query_parts.append(f"{csv_field_name}: {value}")
        
        enriched_query = ". ".join(enriched_query_parts) + "."
        print(f"[RETRIEVAL] Champs collectés: {list(collected_field_values.keys())}")
        print(f"[RETRIEVAL] Valeurs uniques par champ: {collected_field_values}")
    else:
        # Fallback si pas de données spécifiques
        enriched_query = f"Analyse du formulaire 8D, section {current_section_name}"
    
    print(f"[RETRIEVAL] Requête enrichie (étape {current_section_name}): '{enriched_query}'")

    # 3. Récupération des documents
    vectorstore = get_vectorstore(model_key=model_key)
    
    if return_scores:
        # Utilise similarity_search_with_score pour obtenir les scores
        docs_with_scores = vectorstore.similarity_search_with_score(enriched_query, k=k)
        print(f"[RETRIEVAL] {len(docs_with_scores)} documents récupérés avec scores.")
        
        # Extraire et traiter les documents selon l'étape
        docs = [doc for doc, score in docs_with_scores]
        scores = [score for doc, score in docs_with_scores]
        
        # Appliquer l'extraction des champs pertinents
        filtered_docs = extract_relevant_fields_from_docs(docs, current_section_name)
        
        # Recombiner avec les scores
        filtered_docs_with_scores = list(zip(filtered_docs, scores))
        return filtered_docs_with_scores
    else:
        # Comportement original sans scores
        retriever = vectorstore.as_retriever(search_kwargs={"k": k})
        docs = retriever.invoke(enriched_query)
        print(f"[RETRIEVAL] {len(docs)} documents récupérés.")
        
        # Appliquer l'extraction des champs pertinents
        filtered_docs = extract_relevant_fields_from_docs(docs, current_section_name)
        return filtered_docs