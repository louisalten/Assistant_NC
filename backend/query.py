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
import uuid  # Pour générer des identifiants uniques de conversation

# Configuration
DB_DIR = "C:/Users/lrodembourg/Documents/Test_Langchain/chroma_db"
ollama_endpoint = "http://localhost:11434"

def query_documents(query_text, ):
    vectorstore = get_vectorstore()
    llm = ChatOllama(
        model="qwen3:14b",
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
        retrieved_docs = get_relevant_documents(
            query_text=query_text,
            current_section_data=current_section_data,
            current_section_name=current_section_name,
            form_data=form_data, # On passe le form_data complet
            model_key=model_key, # On passe le model_key pour flexibilité
        )
    except Exception as e_ret:
        print(f"ERREUR RAG: Échec de la récupération des documents: {e_ret}")
        error_message_for_client = f"Désolé, une erreur est survenue lors de la recherche d'informations : {e_ret}"
        yield {"response": error_message_for_client, "error": str(e_ret)}
        yield {"done": True, "sources": [], "conversation_id": conversation_id, "suggested_field_update": None}
        return

    # 3. Construction des sources pour le client
    sources_for_client = build_sources(retrieved_docs, mode="RAG")
    
    # Stocker les sources complètes dans le cache
    sources_for_cache = []
    for doc in retrieved_docs:
        source = {
            "content": doc.page_content[:200] + "...",  # Aperçu pour l'UI
            "nc_id": doc.metadata.get("id_non_conformite", "Inconnu"),
            "source": doc.metadata.get("nom_fichier_source", "Unknown"),
            "full_content": doc.page_content,  # Contenu complet pour le PDF/HTML
            "metadata": doc.metadata  # Métadonnées complètes
        }
        sources_for_cache.append(source)
    
    rag_sources_cache.add_sources(conversation_id, sources_for_cache)
    print(f"[RAG] {len(sources_for_cache)} sources stockées dans le cache avec conversation_id: {conversation_id}")
    
    print(f"RAG: Sources construites pour le client: {sources_for_client}")

    # 4. Formatage du contexte pour le LLM (contexte NC actuelle + retrieved_docs)
    context_to_pass_to_llm = [] # Initialisation
    
    # 4.1. Ajout du contexte de la NC actuelle en premier (TOUJOURS INCLUS)
    current_nc_context_parts = ["=== CONTEXTE DE LA NON-CONFORMITÉ ACTUELLE ==="]
    
    # Ajouter la description initiale si disponible
    if form_data and form_data.get('d0_initialisation', {}).get('descriptionInitiale'):
        desc_initiale = form_data['d0_initialisation']['descriptionInitiale']
        current_nc_context_parts.append(f"Description du problème (D0): {desc_initiale}")
    
    # Ajouter le contexte de la section actuelle
    if current_section_data:
        current_nc_context_parts.append(f"Données de la section actuelle ({current_section_name}):")
        for key, value in current_section_data.items():
            if value and key != 'id':
                current_nc_context_parts.append(f"  - {key}: {value}")
    
    # Ajouter d'autres sections pertinentes du formulaire 8D si disponibles
    if form_data:
        # Équipe D1
        if form_data.get('d1_team') and any(form_data['d1_team'].values()):
            current_nc_context_parts.append("Équipe constituée (D1):")
            for key, value in form_data['d1_team'].items():
                if value:
                    current_nc_context_parts.append(f"  - {key}: {value}")
        
        # QQOQCCP D2
        if form_data.get('d2_qqoqccp') and any(form_data['d2_qqoqccp'].values()):
            current_nc_context_parts.append("Analyse QQOQCCP (D2):")
            for key, value in form_data['d2_qqoqccp'].items():
                if value and key != 'id':
                    current_nc_context_parts.append(f"  - {key}: {value}")
        
        # Actions curatives D3
        if form_data.get('d3_actions') and any(form_data['d3_actions'].values()):
            current_nc_context_parts.append("Actions curatives (D3):")
            for key, value in form_data['d3_actions'].items():
                if value and key != 'id':
                    current_nc_context_parts.append(f"  - {key}: {value}")
    
    current_nc_context_parts.append("=== FIN CONTEXTE NC ACTUELLE ===\n")
    
    # Créer le document de contexte NC actuelle
    current_nc_context_doc = Document(
        page_content="\n".join(current_nc_context_parts),
        metadata={"source": "current_nc", "type": "context"}
    )
    context_to_pass_to_llm.append(current_nc_context_doc)
    
    # 4.2. Ajout des documents similaires récupérés
    if retrieved_docs:
        print(f"RAG: Formatage du contexte pour le LLM à partir de {len(retrieved_docs)} documents similaires.")
        context_to_pass_to_llm.append(Document(
            page_content="=== EXEMPLES DE NON-CONFORMITÉS SIMILAIRES ===",
            metadata={"source": "separator", "type": "separator"}
        ))
        
        for i, doc_to_format in enumerate(retrieved_docs):
            if not hasattr(doc_to_format, 'metadata'):
                if hasattr(doc_to_format, 'page_content') and doc_to_format.page_content:
                    context_to_pass_to_llm.append(Document(page_content=doc_to_format.page_content, metadata={}))
                continue
#Quelle partie spécifique du document doit on envoyé en fonction de l'étape actuelle  
            nc_id_ctx = doc_to_format.metadata.get("id_non_conformite", "Non spécifié")
            desc_probleme_ctx = doc_to_format.metadata.get("Description du problème 0D", "")
            cause_racine_ctx = doc_to_format.metadata.get("Cause Racine 4D", "")
            actions_5d_ctx = doc_to_format.metadata.get("Action(s) systémique(s) 5D", "")
            
            single_doc_context_parts = [f"--- Document Pertinent Réf. NC: {nc_id_ctx} ---"]
            if desc_probleme_ctx: single_doc_context_parts.append(f"Description du Problème: {desc_probleme_ctx}")
            if cause_racine_ctx: single_doc_context_parts.append(f"Cause Racine Identifiée: {cause_racine_ctx}")
            if actions_5d_ctx: single_doc_context_parts.append(f"Actions Correctives (5D): {actions_5d_ctx}")
            if hasattr(doc_to_format, 'page_content') and doc_to_format.page_content:
                 single_doc_context_parts.append(f"Informations textuelles complémentaires du document:\n{doc_to_format.page_content}")
            
            formatted_page_content_for_llm = "\n".join(single_doc_context_parts) + "\n--- Fin Document Pertinent ---\n"
            
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
        model="qwen3:14b",
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