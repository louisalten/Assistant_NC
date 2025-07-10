# backend/rag_cache.py

import time
from typing import Dict, Any, Optional, List

class RAGCache:
    """Cache pour stocker temporairement les sources utilisées dans le RAG par conversation/utilisateur"""
    
    def __init__(self, expiration_seconds: int = 3600):
        """
        Initialiser le cache RAG
        
        Args:
            expiration_seconds: Durée en secondes avant qu'une entrée expire (défaut: 1 heure)
        """
        self.cache = {}  # { conversation_id: { 'timestamp': int, 'sources': List[Dict] } }
        self.expiration_seconds = expiration_seconds
    
    def add_sources(self, conversation_id: str, sources: List[Dict[str, Any]]) -> None:
        """
        Ajouter des sources au cache pour une conversation donnée
        
        Args:
            conversation_id: Identifiant unique de la conversation
            sources: Liste des sources récupérées lors du RAG
        """
        self.cache[conversation_id] = {
            'timestamp': int(time.time()),
            'sources': sources
        }
        print(f"[RAG CACHE] Sources ajoutées pour conversation {conversation_id}: {len(sources)} sources")
    
    def get_source_by_id(self, conversation_id: str, nc_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupérer une source spécifique par ID de NC pour une conversation donnée
        
        Args:
            conversation_id: Identifiant unique de la conversation
            nc_id: ID de la non-conformité recherchée
            
        Returns:
            Source trouvée ou None si non trouvée
        """
        # Normaliser l'ID de NC pour la recherche
        normalized_nc_id = nc_id.upper()
        if not normalized_nc_id.startswith("NC-") and nc_id.isdigit():
            normalized_nc_id = f"NC-{nc_id}"
        
        if conversation_id not in self.cache:
            print(f"[RAG CACHE] Conversation {conversation_id} non trouvée dans le cache")
            return None
            
        entry = self.cache[conversation_id]
        
        # Vérifier l'expiration
        current_time = int(time.time())
        if current_time - entry['timestamp'] > self.expiration_seconds:
            print(f"[RAG CACHE] Entrée expirée pour conversation {conversation_id}")
            del self.cache[conversation_id]
            return None
            
        # Recherche dans les sources
        for source in entry['sources']:
            source_nc_id = source.get('nc_id', '')
            # Normaliser l'ID de source pour la comparaison
            if source_nc_id.upper() == normalized_nc_id:
                print(f"[RAG CACHE] Source trouvée pour NC ID {nc_id} dans conversation {conversation_id}")
                return source
                
            # Essayer sans le préfixe NC-
            if normalized_nc_id.startswith("NC-") and source_nc_id.upper() == normalized_nc_id.split("-", 1)[1]:
                print(f"[RAG CACHE] Source trouvée avec ID sans préfixe pour NC ID {nc_id}")
                return source
        
        print(f"[RAG CACHE] Aucune source trouvée pour NC ID {nc_id} dans conversation {conversation_id}")
        return None
        
    def cleanup(self) -> int:
        """
        Nettoyer les entrées expirées du cache
        
        Returns:
            Nombre d'entrées supprimées
        """
        current_time = int(time.time())
        keys_to_delete = []
        
        for conversation_id, entry in self.cache.items():
            if current_time - entry['timestamp'] > self.expiration_seconds:
                keys_to_delete.append(conversation_id)
                
        for key in keys_to_delete:
            del self.cache[key]
            
        return len(keys_to_delete)
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Récupérer des statistiques sur le cache
        
        Returns:
            Informations sur le cache
        """
        return {
            'total_entries': len(self.cache),
            'total_sources': sum(len(entry['sources']) for entry in self.cache.values()),
            'oldest_entry_age': max([int(time.time()) - entry['timestamp'] for entry in self.cache.values()]) if self.cache else 0
        }

# Initialisation du cache global
rag_sources_cache = RAGCache()
