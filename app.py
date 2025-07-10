from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict
import json
import asyncio

from backend.database import SessionLocal, engine
from backend import models, schemas, crud
from backend.query import query_documents_with_context
from backend.utils import build_sources
from backend.retrieval import get_relevant_documents
from backend.document_generator import generate_nc_pdf, generate_nc_summary_html
from backend.rag_cache import rag_sources_cache  # Import du cache RAG



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CONFIGURATION CORS ---
origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- FIN CONFIG CORS ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES NON-CONFORMITES ---
@app.get("/api/nonconformites", response_model=List[schemas.NonConformite])
def list_nonconformites(db: Session = Depends(get_db)):
    return crud.get_ncs(db)

@app.get("/api/nonconformites/{nc_id}", response_model=schemas.NonConformite)
def get_nonconformite(nc_id: int, db: Session = Depends(get_db)):
    nc = crud.get_nc(db, nc_id)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    return nc

@app.post("/api/nonconformites", response_model=schemas.NonConformite)
def create_nonconformite(nc: schemas.NonConformiteCreate, db: Session = Depends(get_db)):
    print("[DEBUG] Reçu POST /api/nonconformites avec:", nc)
    print("[DEBUG] Détail du dict envoyé:", nc.dict())
    result = crud.create_nc(db, nc)
    print("[DEBUG] NonConformite créée:", result)
    return result

@app.put("/api/nonconformites/{nc_id}", response_model=schemas.NonConformite)
def update_nonconformite(nc_id: int, nc: schemas.NonConformiteUpdate, db: Session = Depends(get_db)):
    updated = crud.update_nc(db, nc_id, nc)
    if not updated:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    return updated

@app.delete("/api/nonconformites/{nc_id}")
def delete_nonconformite(nc_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_nc(db, nc_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    return {"ok": True}

# --- ROUTES MEMBRES EQUIPE (optionnel) ---
@app.get("/api/membres", response_model=List[schemas.MembreEquipe])
def list_membres(db: Session = Depends(get_db)):
    return crud.get_membres(db)

@app.post("/api/membres", response_model=schemas.MembreEquipe)
def create_membre(membre: schemas.MembreEquipeCreate, db: Session = Depends(get_db)):
    return crud.create_membre(db, membre)

# --- CHAT ASSISTANT ---
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class QueryContextPayload(BaseModel):
    query: str
    form_data: Dict[str, Any] = Field(default_factory=dict)
    current_section_data: Dict[str, Any] = Field(default_factory=dict)
    current_section_name: Optional[str] = None
    mode: Optional[str] = 'CHAT'  # Ajout du mode
    model_key: Optional[str] = Field(None, description="La clé du modèle d'embedding à utiliser (ex: 'qwen_base', 'mxbai_large').")


@app.post("/query_with_context")
async def process_contextual_query(payload: QueryContextPayload):
    query_text = payload.query
    form_data_8d = payload.form_data
    current_section_data_8d = payload.current_section_data
    current_section_name_8d = payload.current_section_name
    mode = payload.mode or 'CHAT'
    model_key = payload.model_key
    print(f"DEBUG API: Clé de modèle reçue dans le payload = {model_key}")

    if mode == 'REQ':
        
        docs = get_relevant_documents(
            query_text=query_text,
            current_section_data=current_section_data_8d,
            current_section_name=current_section_name_8d,
            form_data=form_data_8d,
            model_key=model_key # <-- Assurez-vous que cet argument est bien passé !
        )
        # Formate les sources comme dans le RAG
        sources = build_sources(docs, mode="REQ")
        print("[DEBUG SOURCES RETRIEVAL] Nombre de sources récupérées:", len(sources))
        
        def simple_stream():
            yield json.dumps({"sources": sources, "done": True}, ensure_ascii=False) + "\n"
        return StreamingResponse(simple_stream(), media_type="application/jsonlines")
    ####CHAT####
    async def stream_response():
        async for chunk in query_documents_with_context(
            query_text=query_text,
            form_data=form_data_8d,
            current_section_data=current_section_data_8d,
            current_section_name=current_section_name_8d,
            stream=True,
            model_key=model_key, # <-- Passer le paramètre

        ):
            if 'sources' in chunk:
                print("[DEBUG SOURCES STREAM] Nombre de sources dans chunk:", len(chunk['sources']))
                for idx, src in enumerate(chunk['sources']):
                    print(f"  Source {idx+1}: NC ID: {src.get('nc_id', 'N/A')} | Fichier: {src.get('source_file', src.get('source', 'N/A'))} | Aperçu: {src.get('preview', src.get('content', 'N/A'))[:60]}")
                    # Log complet des métadonnées du document source si possible
                    if 'retrieved_docs' in chunk and idx < len(chunk['retrieved_docs']):
                        print(f"    [META] Métadonnées complètes: {getattr(chunk['retrieved_docs'][idx], 'metadata', {})}")
            
            yield json.dumps(chunk, ensure_ascii=False) + "\n"
    return StreamingResponse(stream_response(), media_type="application/jsonlines")

# === ENDPOINTS POUR CHAT HISTORY ===

@app.post("/api/nonconformites/{nc_id}/chat/messages", response_model=schemas.ChatMessage)
def create_chat_message(nc_id: int, message: schemas.ChatMessageCreateRequest, db: Session = Depends(get_db)):
    """Créer un nouveau message de chat pour une NC"""
    # Vérifier que la NC existe
    nc = crud.get_nc(db, nc_id)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    
    # Créer le message avec nonconformite_id
    message_data = schemas.ChatMessageCreate(
        nonconformite_id=nc_id,
        **message.dict()
    )
    return crud.create_chat_message(db, message_data)

@app.get("/api/nonconformites/{nc_id}/chat/messages", response_model=List[schemas.ChatMessage])
def get_chat_history(nc_id: int, db: Session = Depends(get_db)):
    """Récupérer l'historique complet des messages de chat pour une NC"""
    # Vérifier que la NC existe
    nc = crud.get_nc(db, nc_id)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    
    return crud.get_chat_messages_by_nc(db, nc_id)

@app.delete("/api/nonconformites/{nc_id}/chat/messages/{message_id}")
def delete_chat_message(nc_id: int, message_id: int, db: Session = Depends(get_db)):
    """Supprimer un message de chat spécifique"""
    # Vérifier que la NC existe
    nc = crud.get_nc(db, nc_id)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    
    success = crud.delete_chat_message(db, message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message non trouvé")
    
    return {"message": "Message supprimé avec succès"}

@app.delete("/api/nonconformites/{nc_id}/chat/clear")
def clear_chat_history(nc_id: int, db: Session = Depends(get_db)):
    """Effacer tout l'historique de chat pour une NC"""
    # Vérifier que la NC existe
    nc = crud.get_nc(db, nc_id)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    
    success = crud.clear_chat_history_for_nc(db, nc_id)
    return {"message": f"Historique de chat effacé", "deleted": success}

# --- ROUTES CHAT HISTORY ---
@app.get("/api/nonconformites/{nc_id}/chat-history", response_model=schemas.ChatHistoryResponse)
def get_chat_history(nc_id: int, db: Session = Depends(get_db)):
    """Récupérer l'historique de chat pour une NC"""
    nc = crud.get_nc(db, nc_id)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    
    messages = crud.get_chat_history(db, nc_id)
    return schemas.ChatHistoryResponse(
        nonconformite_id=nc_id,
        messages=messages
    )

@app.post("/api/nonconformites/{nc_id}/chat-history")
def save_chat_message(nc_id: int, message: schemas.ChatMessageCreateRequest, db: Session = Depends(get_db)):
    """Sauvegarder un message de chat"""
    try:
        print(f"🔍 Tentative de sauvegarde pour NC {nc_id}")
        print(f"🔍 Message reçu: {message.dict()}")
        
        # Vérifier que la NC existe (sans la charger complètement pour éviter les problèmes de dict)
        nc_exists = db.query(models.NonConformite).filter(models.NonConformite.id == nc_id).first()
        if not nc_exists:
            raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
        
        # Créer le message avec nonconformite_id
        message_data = schemas.ChatMessageCreate(
            nonconformite_id=nc_id,
            **message.dict()
        )
        print(f"🔍 Message_data créé: {message_data.dict()}")
        
        result = crud.create_chat_message(db, message_data)
        print(f"✅ Message sauvegardé avec ID: {result.id}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {str(e)}")
        print(f"❌ Type d'erreur: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la sauvegarde: {str(e)}")

@app.post("/api/nonconformites/{nc_id}/chat-history/bulk")
def save_chat_conversation(nc_id: int, messages: List[dict] = Body(...), db: Session = Depends(get_db)):
    """Sauvegarder une conversation complète"""
    nc = crud.get_nc(db, nc_id)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    
    result = crud.save_chat_conversation(db, nc_id, messages)
    return {"success": result, "saved_messages": len(messages)}

@app.delete("/api/nonconformites/{nc_id}/chat-history")
def clear_chat_history(nc_id: int, db: Session = Depends(get_db)):
    """Supprimer l'historique de chat pour une NC"""
    nc = crud.get_nc(db, nc_id)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    
    result = crud.delete_chat_history(db, nc_id)
    return {"success": result}

# --- PDF GENERATION ROUTES ---
@app.post("/api/nonconformites/{nc_id}/generate-pdf")
def generate_pdf(nc_id: int, db: Session = Depends(get_db)):
    """Générer un PDF pour une non-conformité"""
    nc = crud.get_nc(db, nc_id)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    
    # Générer le PDF
    pdf_path = generate_nc_pdf(nc_id)
    if not pdf_path:
        raise HTTPException(status_code=500, detail="Erreur lors de la génération du PDF")
    
    return FileResponse(pdf_path, media_type='application/pdf', filename=f"non_conformite_{nc_id}.pdf")

@app.post("/api/nonconformites/{nc_id}/generate-summary")
def generate_summary(nc_id: int, db: Session = Depends(get_db)):
    """Générer un résumé HTML pour une non-conformité"""
    nc = crud.get_nc(db, nc_id)
    if not nc:
        raise HTTPException(status_code=404, detail="Non-conformité non trouvée")
    
    # Générer le résumé HTML
    html_content = generate_nc_summary_html(nc_id)
    if not html_content:
        raise HTTPException(status_code=500, detail="Erreur lors de la génération du résumé")
    
    return {"nc_id": nc_id, "summary": html_content}

# --- ROUTE GÉNÉRATION DE DOCUMENTS ---
@app.get("/api/nonconformites/{nc_id}/document.pdf")
def generate_nc_document(nc_id: str, conversation_id: str = None, download: bool = False, db: Session = Depends(get_db)):
    """Générer un document PDF pour une non-conformité basé sur sa source depuis le cache RAG"""
    from backend.utils import get_source_by_id
    from backend.document_generator import generate_source_pdf
    
    print(f"[DEBUG] Génération de PDF pour NC ID: {nc_id}, Conversation ID: {conversation_id}")
    
    try:
        # Normaliser l'ID pour accepter différents formats (avec ou sans préfixe "NC-")
        normalized_id = nc_id
        if not nc_id.upper().startswith("NC-") and nc_id.isdigit():
            normalized_id = f"NC-{nc_id}"
            print(f"[DEBUG] ID normalisé: '{nc_id}' -> '{normalized_id}'")
        
        source_data = None
        
        # Si un conversation_id est fourni, essayer d'abord de récupérer depuis le cache RAG
        if conversation_id:
            print(f"[DEBUG] Tentative de récupération depuis le cache RAG avec conversation_id: {conversation_id}")
            source_data = rag_sources_cache.get_source_by_id(conversation_id, normalized_id)
            
            if source_data:
                print(f"[DEBUG] Source trouvée dans le cache RAG pour conversation_id: {conversation_id}, NC ID: {normalized_id}")
            else:
                print(f"[DEBUG] Source non trouvée dans le cache RAG, essai avec conversation_id: {conversation_id}, NC ID sans préfixe")
                # Essayer sans préfixe NC-
                if normalized_id.upper().startswith("NC-"):
                    numeric_id = normalized_id.split("-", 1)[1]
                    source_data = rag_sources_cache.get_source_by_id(conversation_id, numeric_id)
                    if source_data:
                        print(f"[DEBUG] Source trouvée dans le cache RAG avec NC ID sans préfixe: {numeric_id}")
        
        # Si pas trouvé dans le cache RAG, utiliser la méthode traditionnelle
        if not source_data:
            print(f"[DEBUG] Pas de source dans le cache RAG, utilisation de la méthode traditionnelle")
            source_data = get_source_by_id(normalized_id)
        
        if source_data:
            print(f"[DEBUG] Source trouvée, génération du PDF...")
            pdf_content = generate_source_pdf(source_data)
            if pdf_content:
                print(f"[DEBUG] PDF généré avec succès pour NC ID {normalized_id}")
                # Utiliser un nom de fichier cohérent avec le format de l'ID
                filename = f"{normalized_id}.pdf" if normalized_id.upper().startswith("NC-") else f"NC-{normalized_id}.pdf"
                
                # BytesIO est retourné par generate_source_pdf, donc on utilise StreamingResponse
                pdf_content.seek(0)  # S'assurer que le pointeur est au début
                
                # Choisir entre affichage dans le navigateur (inline) et téléchargement (attachment)
                disposition = "attachment" if download else "inline"
                
                return StreamingResponse(
                    pdf_content,
                    media_type="application/pdf",
                    headers={"Content-Disposition": f"{disposition}; filename={filename}"}
                )
            else:
                print(f"[ERREUR] Échec de la génération du PDF pour NC ID {normalized_id}")
        else:
            print(f"[AVERTISSEMENT] Aucune source trouvée pour NC ID {normalized_id}")
            # Essayer avec l'ID sans préfixe via méthode traditionnelle si ce n'est pas déjà fait
            if normalized_id.upper().startswith("NC-") and not conversation_id:
                numeric_id = normalized_id.split("-", 1)[1]
                print(f"[DEBUG] Tentative avec ID numérique uniquement: {numeric_id}")
                source_data = get_source_by_id(numeric_id)
                
                if source_data:
                    print(f"[DEBUG] Source trouvée avec ID numérique {numeric_id}, génération du PDF...")
                    pdf_content = generate_source_pdf(source_data)
                    if pdf_content:
                        print(f"[DEBUG] PDF généré avec succès pour ID numérique {numeric_id}")
                        # BytesIO est retourné par generate_source_pdf, donc on utilise StreamingResponse
                        pdf_content.seek(0)  # S'assurer que le pointeur est au début
                        
                        # Choisir entre affichage dans le navigateur (inline) et téléchargement (attachment)
                        disposition = "attachment" if download else "inline"
                        
                        return StreamingResponse(
                            pdf_content,
                            media_type="application/pdf",
                            headers={"Content-Disposition": f"{disposition}; filename=NC-{numeric_id}.pdf"}
                        )
        
        # Si on arrive ici, c'est qu'on n'a pas pu générer le PDF
        # Retourner un PDF générique indiquant que la NC n'a pas été trouvée
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Un message plus descriptif
        story = [
            Paragraph(f"Non-conformité non trouvée: {normalized_id}", styles["Title"]),
            Spacer(1, 12),
            Paragraph("La non-conformité demandée n'a pas été trouvée dans la base de données.", styles["Normal"]),
            Spacer(1, 12),
            Paragraph(f"Identifiant recherché: {normalized_id}", styles["Normal"]),
            Spacer(1, 6),
            Paragraph(f"Format attendu: NC-XXX où XXX est le numéro de la non-conformité.", styles["Normal"]),
            Spacer(1, 12),
            Paragraph("Veuillez vérifier l'identifiant et réessayer.", styles["Normal"])
        ]
        doc.build(story)
        buffer.seek(0)
        
        print(f"[INFO] Retour d'un PDF générique pour NC ID {normalized_id} non trouvée")
        buffer.seek(0)  # S'assurer que le pointeur est au début
        
        # Choisir entre affichage dans le navigateur (inline) et téléchargement (attachment)
        disposition = "attachment" if download else "inline"
        
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"{disposition}; filename={normalized_id}-not-found.pdf"}
        )
        
    except Exception as e:
        print(f"[ERREUR] Exception lors de la génération du PDF pour NC ID {nc_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du PDF: {str(e)}")

@app.get("/api/nonconformites/{nc_id}/summary")  
def get_nc_summary(nc_id: str, conversation_id: str = None, db: Session = Depends(get_db)):
    """Générer un résumé HTML pour une non-conformité basé sur sa source depuis le cache RAG"""
    from backend.utils import get_source_by_id
    from backend.document_generator import generate_source_html_summary
    
    print(f"[DEBUG] Génération d'aperçu HTML pour NC ID: {nc_id}, Conversation ID: {conversation_id}")
    
    try:
        # Normaliser l'ID pour accepter différents formats (avec ou sans préfixe "NC-")
        normalized_id = nc_id
        if not nc_id.upper().startswith("NC-") and nc_id.isdigit():
            normalized_id = f"NC-{nc_id}"
            print(f"[DEBUG] ID normalisé: '{nc_id}' -> '{normalized_id}'")
        
        source_data = None
        
        # Si un conversation_id est fourni, essayer d'abord de récupérer depuis le cache RAG
        if conversation_id:
            print(f"[DEBUG] Tentative de récupération depuis le cache RAG avec conversation_id: {conversation_id}")
            source_data = rag_sources_cache.get_source_by_id(conversation_id, normalized_id)
            
            if source_data:
                print(f"[DEBUG] Source trouvée dans le cache RAG pour conversation_id: {conversation_id}, NC ID: {normalized_id}")
            else:
                print(f"[DEBUG] Source non trouvée dans le cache RAG, essai avec conversation_id: {conversation_id}, NC ID sans préfixe")
                # Essayer sans préfixe NC-
                if normalized_id.upper().startswith("NC-"):
                    numeric_id = normalized_id.split("-", 1)[1]
                    source_data = rag_sources_cache.get_source_by_id(conversation_id, numeric_id)
                    if source_data:
                        print(f"[DEBUG] Source trouvée dans le cache RAG avec NC ID sans préfixe: {numeric_id}")
        
        # Si pas trouvé dans le cache RAG, utiliser la méthode traditionnelle
        if not source_data:
            print(f"[DEBUG] Pas de source dans le cache RAG, utilisation de la méthode traditionnelle")
            source_data = get_source_by_id(normalized_id)
        
        if source_data:
            print(f"[DEBUG] Source trouvée pour NC ID {normalized_id}, génération de l'aperçu HTML...")
            html_content = generate_source_html_summary(source_data)
            if html_content:
                print(f"[DEBUG] Aperçu HTML généré avec succès pour NC ID {normalized_id}")
                return {"id": normalized_id, "html": html_content}
            else:
                print(f"[ERREUR] Échec de la génération de l'aperçu HTML pour NC ID {normalized_id}")
        else:
            print(f"[AVERTISSEMENT] Aucune source trouvée pour NC ID {normalized_id}")
            # Essayer avec l'ID sans préfixe via méthode traditionnelle si ce n'est pas déjà fait
            if normalized_id.upper().startswith("NC-") and not conversation_id:
                numeric_id = normalized_id.split("-", 1)[1]
                print(f"[DEBUG] Tentative avec ID numérique uniquement: {numeric_id}")
                source_data = get_source_by_id(numeric_id)
                
                if source_data:
                    print(f"[DEBUG] Source trouvée avec ID numérique {numeric_id}, génération de l'aperçu HTML...")
                    html_content = generate_source_html_summary(source_data)
                    if html_content:
                        print(f"[DEBUG] Aperçu HTML généré avec succès pour ID numérique {numeric_id}")
                        return {"id": normalized_id, "html": html_content}
        
        # Générer un HTML générique plus informatif
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; text-align: center; border: 1px solid #ff6b6b; border-radius: 5px;">
            <h1 style="color: #ff6b6b;">Non-conformité non trouvée</h1>
            <p>La non-conformité avec l'identifiant <strong>{normalized_id}</strong> n'a pas été trouvée dans la base de données.</p>
            <p>Format attendu: <code>NC-XXX</code> où XXX est le numéro de la non-conformité.</p>
            <p>Veuillez vérifier l'identifiant et réessayer.</p>
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 20px; text-align: left;">
                <p style="font-size: 0.9em; color: #6c757d;"><strong>Note technique:</strong> Les identifiants sont recherchés dans la colonne "Identification NC 0D" du fichier CSV source.</p>
            </div>
        </div>
        """
        print(f"[INFO] Retour d'un aperçu HTML générique pour NC ID {normalized_id} non trouvée")
        return {"id": normalized_id, "html": html_content}
        
    except Exception as e:
        print(f"[ERREUR] Exception lors de la génération de l'aperçu HTML pour NC ID {nc_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Générer un HTML d'erreur avec plus de détails
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; text-align: center; border: 1px solid #ff6b6b; border-radius: 5px; background-color: #fff5f5;">
            <h1 style="color: #ff6b6b;">Erreur</h1>
            <p>Une erreur s'est produite lors de la génération de l'aperçu pour la non-conformité <strong>{nc_id}</strong>.</p>
            <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 15px 0; text-align: left;">
                <p style="font-family: monospace; color: #e74c3c; margin: 0; white-space: pre-wrap;"><strong>Détails:</strong> {str(e)}</p>
            </div>
            <p>Veuillez contacter l'administrateur du système si l'erreur persiste.</p>
        </div>
        """
        return {"id": nc_id, "html": html_content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)