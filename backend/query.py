from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate # Pour le prompt par défaut
from backend.utils import  build_sources
from backend.routeur import detect_prompt
from backend.get_vector_db import get_vectorstore
from backend.retrieval import get_relevant_documents
from backend.ollama_thinking import ChatOllamaWithThinking
from backend.rag_cache import rag_sources_cache  # Import du cache RAG
from backend.step_retrieval_config import step_retrieval_config  # Import de la config étapes
import uuid  # Pour générer des identifiants uniques de conversation

# Configuration
DB_DIR = "C:/Users/lrodembourg/Documents/Test_Langchain/chroma_db"
ollama_endpoint = "http://localhost:11434"

def query_documents(query_text, ):
    vectorstore = get_vectorstore()
    llm = ChatOllama(
        model="phi4-reasoning",
        num_ctx=4096,
        temperature=0.5,
        base_url=ollama_endpoint,
    )
    selected_prompt = detect_prompt(query_text)
    # Création des composants RAG
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    retrieved_docs = retriever.invoke(query_text)
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain
    question_answer_chain = create_stuff_documents_chain(llm, selected_prompt)
    rag_chain = create_retrieval_chain(lambda q: retrieved_docs, question_answer_chain)
    result = rag_chain.invoke({"input": query_text})
    sources = []
    for doc in result.get("context", []):
        source = {
            "content": doc.page_content[:200] + "...",
            "nc_id": doc.metadata.get("id_non_conformite", "Inconnu"),
            "source": doc.metadata.get("nom_fichier_source", "Unknown"),
            "full_content": doc.page_content,  # Stocker le contenu complet
            "metadata": doc.metadata  # Stocker les métadonnées complètes
        }
        sources.append(source)
    
    # Générer un ID de conversation et stocker les sources dans le cache
    conversation_id = str(uuid.uuid4())
    rag_sources_cache.add_sources(conversation_id, sources)
    print(f"[QUERY] Sources stockées dans le cache avec conversation_id: {conversation_id}")
    
    # Retourner l'ID de conversation avec la réponse et les sources
    return result["answer"], sources, conversation_id

async def query_documents_with_context(query_text: str, form_data: dict, current_section_data: dict, current_section_name: str, stream: bool, model_key:int):
    print(f"RAG: Requête: '{query_text}' pour section '{current_section_name}' ")
    # Générer un ID de conversation unique
    conversation_id = str(uuid.uuid4())
    print(f"[RAG] Nouvel ID de conversation généré: {conversation_id}")
    
    # 2. Initialisation et récupération des documents
    try:
        retrieved_docs_with_scores = get_relevant_documents(
            query_text=query_text,
            current_section_data=current_section_data,
            current_section_name=current_section_name,
            form_data=form_data, # On passe le form_data complet
            model_key=model_key, # On passe le model_key pour flexibilité
            return_scores=True,  # Demander les scores
        )
        
        # Séparer les documents et les scores
        retrieved_docs = [doc for doc, score in retrieved_docs_with_scores]
        similarity_scores = [score for doc, score in retrieved_docs_with_scores]
        
    except Exception as e_ret:
        print(f"ERREUR RAG: Échec de la récupération des documents: {e_ret}")
        error_message_for_client = f"Désolé, une erreur est survenue lors de la recherche d'informations : {e_ret}"
        yield {"response": error_message_for_client, "error": str(e_ret)}
        yield {"done": True, "sources": [], "conversation_id": conversation_id, "suggested_field_update": None}
        return

    # 3. Construction des sources pour le client
    sources_for_client = build_sources(retrieved_docs, mode="RAG", scores=similarity_scores)
    
    # Stocker les sources complètes dans le cache
    sources_for_cache = []
    for i, doc in enumerate(retrieved_docs):
        source = {
            "content": doc.page_content[:200] + "...",  # Aperçu pour l'UI
            "nc_id": doc.metadata.get("id_non_conformite", "Inconnu"),
            "source": doc.metadata.get("nom_fichier_source", "Unknown"),
            "full_content": doc.page_content,  # Contenu complet pour le PDF/HTML
            "metadata": doc.metadata,  # Métadonnées complètes
            "similarity_score": similarity_scores[i] if i < len(similarity_scores) else None  # Ajouter le score
        }
        sources_for_cache.append(source)
    
    rag_sources_cache.add_sources(conversation_id, sources_for_cache)
    print(f"[RAG] {len(sources_for_cache)} sources stockées dans le cache avec conversation_id: {conversation_id}")
    
    print(f"RAG: Sources construites pour le client: {sources_for_client}")

    # 4. Formatage du contexte pour le LLM (contexte NC actuelle + retrieved_docs)
    context_to_pass_to_llm = [] # Initialisation
    
    # 4.1. Construction du contexte de la NC actuelle selon la configuration de l'étape
    context_fields = step_retrieval_config.get_context_fields(current_section_name)
    print(f"[RAG] Champs de contexte pour la NC actuelle ({current_section_name}): {context_fields}")
    
    current_nc_context_parts = [f"=== CONTEXTE DE LA NON-CONFORMITÉ ACTUELLE ({current_section_name}) ==="]
    
    # Ajouter les champs configurés pour cette étape depuis form_data
    if form_data:
        for section_key, section_data in form_data.items():
            if section_data and isinstance(section_data, dict):
                for field in context_fields:
                    if field in section_data and section_data[field]:
                        current_nc_context_parts.append(f"{field}: {section_data[field]}")
    
    # Ajouter les données de la section actuelle (tous les champs)
    if current_section_data:
        for field, value in current_section_data.items():
            if value:
                current_nc_context_parts.append(f"{field} (section actuelle): {value}")
    
    current_nc_context_parts.append("=== FIN CONTEXTE NC ACTUELLE ===\n")
    
    # Créer le document de contexte NC actuelle
    current_nc_context_doc = Document(
        page_content="\n".join(current_nc_context_parts),
        metadata={"source": "current_nc", "type": "context"}
    )
    context_to_pass_to_llm.append(current_nc_context_doc)
    
    # 4.3. Ajout des documents similaires récupérés (déjà enrichis avec retrieve_fields + context_fields)
    if retrieved_docs:
        print(f"RAG: Formatage du contexte pour le LLM à partir de {len(retrieved_docs)} documents similaires (enrichis avec retrieve_fields + context_fields pour {current_section_name}).")
        context_to_pass_to_llm.append(Document(
            page_content=f"=== EXEMPLES DE NON-CONFORMITÉS SIMILAIRES (PERTINENTS POUR {current_section_name.upper()}) ===",
            metadata={"source": "separator", "type": "separator"}
        ))
        
        for i, doc_to_format in enumerate(retrieved_docs):
            if not hasattr(doc_to_format, 'metadata'):
                if hasattr(doc_to_format, 'page_content') and doc_to_format.page_content:
                    context_to_pass_to_llm.append(Document(page_content=doc_to_format.page_content, metadata={}))
                continue
            
            # Les documents sont déjà filtrés avec les champs pertinents par extract_relevant_fields_from_docs
            # On utilise directement le contenu formaté
            nc_id_ctx = doc_to_format.metadata.get("id_non_conformite", "Non spécifié")
            
            single_doc_context_parts = [f"--- NC Similaire {nc_id_ctx} (pertinente pour {current_section_name}) ---"]
            
            # Le contenu est déjà structuré avec les champs pertinents à l'étape
            if hasattr(doc_to_format, 'page_content') and doc_to_format.page_content:
                single_doc_context_parts.append(doc_to_format.page_content)
            
            single_doc_context_parts.append("--- Fin NC Similaire ---\n")
            
            formatted_page_content_for_llm = "\n".join(single_doc_context_parts)
            
            context_to_pass_to_llm.append(
                Document(page_content=formatted_page_content_for_llm, metadata=doc_to_format.metadata)
            )
    else:
        print("RAG: Aucun document similaire récupéré.")
        context_to_pass_to_llm.append(Document(
            page_content="=== AUCUN EXEMPLE SIMILAIRE TROUVÉ ===\nAucune non-conformité similaire n'a été trouvée dans la base de données.",
            metadata={"source": "no_similar", "type": "info"}
        ))

    # 5. Préparation chaîne LLM avec mode thinking réactivé
    llm = ChatOllamaWithThinking(
        model="phi4-reasoning",
        num_ctx=16384,
        temperature=0.7,
        base_url=ollama_endpoint,
        top_k=20,
        top_p=0.95,
        thinking_mode=True
    )

    selected_prompt = detect_prompt(query_text, step=current_section_name if 'step' in detect_prompt.__code__.co_varnames else None)

    # LOG PROMPT COMPLET
    # Récupère le template string du prompt
    if hasattr(selected_prompt, 'format') and hasattr(selected_prompt, 'template'):
        prompt_template_str = selected_prompt.template
    elif isinstance(selected_prompt, str):
        prompt_template_str = selected_prompt
    else:
        prompt_template_str = str(selected_prompt)
    # Construit le contexte texte (concatène tous les docs)
    context_text = "\n\n".join([doc.page_content for doc in context_to_pass_to_llm]) if context_to_pass_to_llm else ""
    prompt_complet = prompt_template_str.replace('{context}', context_text).replace('{input}', query_text)
    print("\n========== PROMPT LLM COMPLET ==========")
    print(prompt_complet)
    print("========== FIN PROMPT LLM COMPLET ==========")

    if not selected_prompt or not (isinstance(selected_prompt, str) and "{context}" in selected_prompt and "{input}" in selected_prompt) and \
       not (hasattr(selected_prompt, 'input_variables') and "context" in selected_prompt.input_variables and "input" in selected_prompt.input_variables):
        print("AVERTISSEMENT RAG: 'selected_prompt' invalide. Utilisation d'un prompt par défaut.")
        default_prompt_str = "Contexte:\n{context}\n\nQuestion: {input}\n\nRéponse:"
        selected_prompt = ChatPromptTemplate.from_template(default_prompt_str)

    from langchain.chains.combine_documents import create_stuff_documents_chain
    question_answer_chain = create_stuff_documents_chain(llm, selected_prompt)

    # 6. Logique de Streaming ou Non-Streaming
    if stream:
        chain_input = {"input": query_text, "context": context_to_pass_to_llm}
        full_answer = ""
        try:
            async for chunk_content_obj in question_answer_chain.astream(chain_input):
                delta = getattr(chunk_content_obj, 'content', str(chunk_content_obj) if isinstance(chunk_content_obj, str) else "")
                if delta:
                    full_answer += delta
                    yield {"response": full_answer}
        except Exception as e_llm_stream:
            print(f"ERREUR RAG STREAM: Échec du stream LLM: {e_llm_stream}")
            yield {"response": f"Erreur durant la génération de la réponse: {e_llm_stream}", "error": str(e_llm_stream)}

        suggested_field_update = None
        if (not query_text.strip() or "sponsor" in query_text.lower()) and current_section_name == "d1_team" and not form_data.get('d1_team', {}).get('Sponsor'):
            suggested_field_update = {"section": "d1_team", "field": "Sponsor", "value": "Nom du Sponsor à définir"}
        
        print(f"RAG STREAM: Yield final: sources: {sources_for_client}, suggestion: {suggested_field_update}")
        yield {"done": True, "sources": sources_for_client, "suggested_field_update": suggested_field_update}
    return # Fin du générateur asynchrone