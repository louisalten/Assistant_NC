from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from datetime import datetime
import json

def get_nc(db: Session, nc_id: int):
    nc = db.query(models.NonConformite).filter(models.NonConformite.id == nc_id).first()
    if nc:
        for key in [
            'd0_initialisation', 'd1_team', 'd2_problem', 'd3_containment',
            'd4_rootcause', 'd5_correctiveactions', 'd6_implementvalidate',
            'd7_preventrecurrence', 'd8_congratulate']:
            val = getattr(nc, key)
            if isinstance(val, str):
                try:
                    setattr(nc, key, json.loads(val))
                except Exception:
                    setattr(nc, key, None)
    return nc

def get_ncs(db: Session, skip: int = 0, limit: int = 100):
    ncs = db.query(models.NonConformite).offset(skip).limit(limit).all()
    for nc in ncs:
        for key in [
            'd0_initialisation', 'd1_team', 'd2_problem', 'd3_containment',
            'd4_rootcause', 'd5_correctiveactions', 'd6_implementvalidate',
            'd7_preventrecurrence', 'd8_congratulate']:
            val = getattr(nc, key)
            if isinstance(val, str):
                try:
                    setattr(nc, key, json.loads(val))
                except Exception:
                    setattr(nc, key, None)
    return ncs

def create_nc(db: Session, nc: schemas.NonConformiteCreate):
    data = nc.dict()
    # Sérialiser tous les champs D0 à D8 si ce sont des dicts
    for key in [
        'd0_initialisation', 'd1_team', 'd2_problem', 'd3_containment',
        'd4_rootcause', 'd5_correctiveactions', 'd6_implementvalidate',
        'd7_preventrecurrence', 'd8_congratulate']:
        if data.get(key) is not None and not isinstance(data[key], str):
            data[key] = json.dumps(data[key])
    db_nc = models.NonConformite(**data)
    db.add(db_nc)
    db.commit()
    db.refresh(db_nc)
    # Désérialisation pour la réponse
    for key in [
        'd0_initialisation', 'd1_team', 'd2_problem', 'd3_containment',
        'd4_rootcause', 'd5_correctiveactions', 'd6_implementvalidate',
        'd7_preventrecurrence', 'd8_congratulate']:
        val = getattr(db_nc, key)
        if isinstance(val, str):
            try:
                setattr(db_nc, key, json.loads(val))
            except Exception:
                setattr(db_nc, key, None)
    return db_nc

def update_nc(db: Session, nc_id: int, nc: schemas.NonConformiteUpdate):
    db_nc = db.query(models.NonConformite).filter(models.NonConformite.id == nc_id).first()
    if db_nc:
        for key, value in nc.dict(exclude_unset=True).items():
            # Sérialiser les champs D0 à D8 si besoin
            if key in [
                'd0_initialisation', 'd1_team', 'd2_problem', 'd3_containment',
                'd4_rootcause', 'd5_correctiveactions', 'd6_implementvalidate',
                'd7_preventrecurrence', 'd8_congratulate'] and value is not None and not isinstance(value, str):
                value = json.dumps(value)
            setattr(db_nc, key, value)
        db.commit()
        db.refresh(db_nc)
        # Désérialisation pour la réponse
        for key in [
            'd0_initialisation', 'd1_team', 'd2_problem', 'd3_containment',
            'd4_rootcause', 'd5_correctiveactions', 'd6_implementvalidate',
            'd7_preventrecurrence', 'd8_congratulate']:
            val = getattr(db_nc, key)
            if isinstance(val, str):
                try:
                    setattr(db_nc, key, json.loads(val))
                except Exception:
                    setattr(db_nc, key, None)
    return db_nc

def delete_nc(db: Session, nc_id: int):
    db_nc = db.query(models.NonConformite).filter(models.NonConformite.id == nc_id).first()
    if db_nc:
        db.delete(db_nc)
        db.commit()
    return db_nc

def get_membres(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.MembreEquipe).offset(skip).limit(limit).all()

def create_membre(db: Session, membre: schemas.MembreEquipeCreate):
    db_membre = models.MembreEquipe(**membre.dict())
    db.add(db_membre)
    db.commit()
    db.refresh(db_membre)
    return db_membre

# === Fonctions CRUD pour ChatMessage ===

def create_chat_message(db: Session, message: schemas.ChatMessageCreate) -> models.ChatMessage:
    """Créer un nouveau message de chat"""
    try:
        # Créer le message directement avec les données
        db_message = models.ChatMessage(
            nonconformite_id=message.nonconformite_id,
            message_id=message.message_id,
            conversation_id=message.conversation_id,
            sender=message.sender,
            message_type=message.message_type,
            content=message.content,
            html_content=message.html_content,
            step_context=message.step_context,
            is_suggestion=message.is_suggestion
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except Exception as e:
        print(f"❌ Erreur CRUD create_chat_message: {str(e)}")
        db.rollback()
        raise

def get_chat_messages_by_nc(db: Session, nc_id: int) -> List[models.ChatMessage]:
    """Récupérer tous les messages de chat pour une non-conformité"""
    return db.query(models.ChatMessage).filter(
        models.ChatMessage.nonconformite_id == nc_id
    ).order_by(models.ChatMessage.timestamp.asc()).all()

def get_chat_message(db: Session, message_id: int) -> Optional[models.ChatMessage]:
    """Récupérer un message de chat par son ID"""
    return db.query(models.ChatMessage).filter(models.ChatMessage.id == message_id).first()

def delete_chat_message(db: Session, message_id: int) -> bool:
    """Supprimer un message de chat"""
    db_message = db.query(models.ChatMessage).filter(models.ChatMessage.id == message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
        return True
    return False

def clear_chat_history_for_nc(db: Session, nc_id: int) -> bool:
    """Effacer tout l'historique de chat pour une non-conformité"""
    deleted_count = db.query(models.ChatMessage).filter(
        models.ChatMessage.nonconformite_id == nc_id
    ).delete()
    db.commit()
    return deleted_count > 0

def get_chat_history(db: Session, nc_id: int):
    """Récupérer l'historique des messages pour une NC"""
    return db.query(models.ChatMessage).filter(
        models.ChatMessage.nonconformite_id == nc_id
    ).order_by(models.ChatMessage.timestamp.asc()).all()

def delete_chat_history(db: Session, nc_id: int):
    """Supprimer l'historique des messages pour une NC"""
    db.query(models.ChatMessage).filter(
        models.ChatMessage.nonconformite_id == nc_id
    ).delete()
    db.commit()
    return True

def save_chat_conversation(db: Session, nc_id: int, messages: List[dict]):
    """Sauvegarder une conversation complète pour une NC"""
    # Optionnel : supprimer les anciens messages de cette conversation
    # pour éviter les doublons si on sauvegarde plusieurs fois
    
    for msg_data in messages:
        if msg_data.get('sender') == 'bot' and not msg_data.get('text', '').strip():
            continue  # Skip les messages vides
            
        chat_message = schemas.ChatMessageCreate(
            nonconformite_id=nc_id,
            message_id=msg_data.get('id', ''),
            conversation_id=msg_data.get('conversationId', None),
            sender=msg_data.get('sender', 'unknown'),
            message_type=msg_data.get('type', None),
            content=msg_data.get('text', '') or msg_data.get('partialText', ''),
            html_content=msg_data.get('htmlText', None),
            step_context=msg_data.get('stepContext', None),
            is_suggestion='true' if msg_data.get('isSuggestion', False) else 'false'
        )
        create_chat_message(db, chat_message)
    
    return True