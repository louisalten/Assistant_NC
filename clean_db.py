# Script pour nettoyer la base de données de chat
from backend.database import SessionLocal
from backend.models import ChatMessage

def clean_chat_messages():
    db = SessionLocal()
    try:
        # Supprimer tous les messages de chat pour la NC 2
        deleted_count = db.query(ChatMessage).filter(ChatMessage.nonconformite_id == 2).delete()
        db.commit()
        print(f"✅ {deleted_count} messages supprimés pour la NC 2")
        
        # Vérifier
        remaining = db.query(ChatMessage).filter(ChatMessage.nonconformite_id == 2).count()
        print(f"📊 Messages restants pour NC 2: {remaining}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_chat_messages()
