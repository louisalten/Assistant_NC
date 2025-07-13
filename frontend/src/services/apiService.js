// src/services/apiService.js

import API_CONFIG from '../config/api';

/**
 * Service API centralisé pour toutes les communications avec le backend FastAPI
 */
class ApiService {
  constructor() {
    this.baseURL = API_CONFIG.BASE_URL;
    this.defaultHeaders = { ...API_CONFIG.DEFAULT_HEADERS };
    this.timeout = API_CONFIG.DEFAULT_TIMEOUT;
  }

  /**
   * Méthode générique pour les requêtes HTTP
   * @param {string} endpoint - Point de terminaison de l'API
   * @param {Object} options - Options de la requête (method, body, headers, etc.)
   * @returns {Promise<Object>} - Réponse de l'API
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      headers: { ...this.defaultHeaders, ...options.headers },
      ...options,
    };

    try {
      console.log(`[API] ${config.method || 'GET'} ${url}`);
      
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP ${response.status}: ${errorText}`);
      }

      // Vérifier si la réponse contient du JSON
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return await response.text();
    } catch (error) {
      console.error(`[API ERROR] ${config.method || 'GET'} ${url}:`, error);
      throw error;
    }
  }

  // === MÉTHODES GÉNÉRIQUES ===

  /**
   * Requête GET
   */
  async get(endpoint, options = {}) {
    return this.request(endpoint, { method: 'GET', ...options });
  }

  /**
   * Requête POST
   */
  async post(endpoint, data = null, options = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
  }

  /**
   * Requête PUT
   */
  async put(endpoint, data = null, options = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
      ...options,
    });
  }

  /**
   * Requête DELETE
   */
  async delete(endpoint, options = {}) {
    return this.request(endpoint, { method: 'DELETE', ...options });
  }

  // === MÉTHODES SPÉCIFIQUES - NON-CONFORMITÉS ===

  /**
   * Récupérer toutes les non-conformités
   */
  async getNonConformites() {
    return this.get(API_CONFIG.ENDPOINTS.NONCONFORMITES);
  }

  /**
   * Récupérer une non-conformité par ID
   */
  async getNonConformite(id) {
    return this.get(API_CONFIG.ENDPOINTS.NONCONFORMITE_BY_ID(id));
  }

  /**
   * Créer une nouvelle non-conformité
   */
  async createNonConformite(data) {
    return this.post(API_CONFIG.ENDPOINTS.NONCONFORMITES, data);
  }

  /**
   * Mettre à jour une non-conformité existante
   */
  async updateNonConformite(id, data) {
    return this.put(API_CONFIG.ENDPOINTS.NONCONFORMITE_BY_ID(id), data);
  }

  /**
   * Supprimer une non-conformité
   */
  async deleteNonConformite(id) {
    return this.delete(API_CONFIG.ENDPOINTS.NONCONFORMITE_BY_ID(id));
  }

  // === MÉTHODES SPÉCIFIQUES - CHAT ===

  /**
   * Récupérer l'historique de chat pour une NC
   */
  async getChatHistory(ncId) {
    return this.get(`/nonconformites/${ncId}/chat-history`);
  }

  /**
   * Sauvegarder un message de chat
   */
  async saveChatMessage(ncId, messageData) {
    return this.post(`/nonconformites/${ncId}/chat/messages`, messageData);
  }

  /**
   * Supprimer l'historique de chat
   */
  async deleteChatHistory(ncId) {
    return this.delete(`/nonconformites/${ncId}/chat-history`);
  }

  /**
   * Sauvegarder une conversation complète
   */
  async saveBulkChatHistory(ncId, conversationData) {
    return this.post(`/nonconformites/${ncId}/chat-history/bulk`, conversationData);
  }

  // === MÉTHODES SPÉCIFIQUES - ASSISTANT IA ===

  /**
   * Requête contextuelle avec streaming
   */
  async queryWithContext(queryData) {
    return this.post('/query_with_context', queryData);
  }

  /**
   * Requête avec streaming (pour les réponses en temps réel)
   */
  async queryWithStreaming(queryData, onChunk) {
    const url = `${this.baseURL}/query_with_context`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: this.defaultHeaders,
      body: JSON.stringify(queryData),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value, { stream: true });
        onChunk(chunk);
      }
    } finally {
      reader.releaseLock();
    }
  }

  // === MÉTHODES UTILITAIRES ===

  /**
   * Vérifier la disponibilité de l'API
   */
  async healthCheck() {
    try {
      await this.get('/health');
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Définir un token d'authentification (pour usage futur)
   */
  setAuthToken(token) {
    if (token) {
      this.defaultHeaders['Authorization'] = `Bearer ${token}`;
    } else {
      delete this.defaultHeaders['Authorization'];
    }
  }

  /**
   * Changer l'URL de base (utile pour dev/prod)
   */
  setBaseURL(url) {
    this.baseURL = url;
  }
}

// Export d'une instance singleton
export const apiService = new ApiService();
export default apiService;
