// src/config/api.js

/**
 * Configuration centralisée pour les URLs et paramètres API
 */
const API_CONFIG = {
  // URL de base selon l'environnement
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
  
  // URL alternative (pour les cas où vous avez 127.0.0.1 vs localhost)
  FALLBACK_URL: 'http://127.0.0.1:8000/api',
  
  // Timeout par défaut pour les requêtes
  DEFAULT_TIMEOUT: 10000,
  
  // Headers par défaut
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  
  // Endpoints spécifiques
  ENDPOINTS: {
    // Non-conformités
    NONCONFORMITES: '/nonconformites',
    NONCONFORMITE_BY_ID: (id) => `/nonconformites/${id}`,
    
    // Chat
    CHAT_HISTORY: (ncId) => `/nonconformites/${ncId}/chat-history`,
    CHAT_MESSAGES: (ncId) => `/nonconformites/${ncId}/chat/messages`,
    CHAT_MESSAGE_BY_ID: (ncId, messageId) => `/nonconformites/${ncId}/chat/messages/${messageId}`,
    CHAT_BULK_SAVE: (ncId) => `/nonconformites/${ncId}/chat-history/bulk`,
    
    // Assistant IA
    QUERY_WITH_CONTEXT: '/query_with_context',
    
    // Santé de l'API
    HEALTH: '/health',
  },
  
  // Codes de statut HTTP
  STATUS_CODES: {
    SUCCESS: 200,
    CREATED: 201,
    BAD_REQUEST: 400,
    UNAUTHORIZED: 401,
    FORBIDDEN: 403,
    NOT_FOUND: 404,
    INTERNAL_SERVER_ERROR: 500,
  },
  
  // Messages d'erreur standardisés
  ERROR_MESSAGES: {
    NETWORK_ERROR: 'Erreur de réseau. Vérifiez votre connexion.',
    API_NOT_AVAILABLE: 'API non disponible. Réessayez plus tard.',
    UNAUTHORIZED: 'Accès non autorisé.',
    NOT_FOUND: 'Ressource non trouvée.',
    VALIDATION_ERROR: 'Erreur de validation des données.',
    INTERNAL_SERVER_ERROR: 'Erreur interne du serveur.',
    TIMEOUT: 'Délai d\'attente dépassé.',
    UNEXPECTED_FORMAT: 'Format inattendu de la réponse API.',
  },
  
  // Configuration retry
  RETRY_CONFIG: {
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000, // ms
    RETRY_MULTIPLIER: 2,
  },
};

export default API_CONFIG;
