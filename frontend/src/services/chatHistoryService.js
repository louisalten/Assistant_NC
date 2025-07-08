// src/services/chatHistoryService.js

const API_BASE_URL = 'http://localhost:8000/api';

class ChatHistoryService {
  /**
   * Sauvegarder un message de chat dans la base de données
   * @param {number} ncId - ID de la non-conformité
   * @param {Object} messageData - Données du message
   */
  async saveMessage(ncId, messageData) {
    try {
      const response = await fetch(`${API_BASE_URL}/nonconformites/${ncId}/chat/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(messageData),
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la sauvegarde du message:', error);
      throw error;
    }
  }

  /**
   * Récupérer l'historique complet des messages pour une NC
   * @param {number} ncId - ID de la non-conformité
   */
  async getHistory(ncId) {
    try {
      const response = await fetch(`${API_BASE_URL}/nonconformites/${ncId}/chat/messages`);
      
      if (!response.ok) {
        throw new Error(`Erreur HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'historique:', error);
      throw error;
    }
  }

  /**
   * Supprimer un message spécifique
   * @param {number} ncId - ID de la non-conformité
   * @param {number} messageId - ID du message à supprimer
   */
  async deleteMessage(ncId, messageId) {
    try {
      const response = await fetch(`${API_BASE_URL}/nonconformites/${ncId}/chat/messages/${messageId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur lors de la suppression du message:', error);
      throw error;
    }
  }

  /**
   * Effacer tout l'historique de chat pour une NC
   * @param {number} ncId - ID de la non-conformité
   */
  async clearHistory(ncId) {
    try {
      const response = await fetch(`${API_BASE_URL}/nonconformites/${ncId}/chat/clear`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Erreur HTTP ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Erreur lors de l\'effacement de l\'historique:', error);
      throw error;
    }
  }

  /**
   * Formater un message du frontend pour la sauvegarde
   * @param {Object} message - Message du ChatAssistant
   * @param {string} stepContext - Contexte de l'étape 8D
   * @param {string} conversationId - ID de la conversation
   */
  formatMessageForSave(message, stepContext = null, conversationId = null) {
    return {
      message_id: message.id,
      conversation_id: conversationId,
      sender: message.sender,
      message_type: message.type || null,
      content: message.text || '',
      html_content: message.htmlText || null,
      step_context: stepContext,
      is_suggestion: message.isSuggestion ? 'true' : 'false',
      suggestion_data: message.suggestionDetails ? JSON.stringify(message.suggestionDetails) : null,
    };
  }

  /**
   * Formater un message de la base de données pour l'affichage
   * @param {Object} dbMessage - Message de la base de données
   */
  formatMessageForDisplay(dbMessage) {
    return {
      id: dbMessage.message_id,
      text: dbMessage.content,
      htmlText: dbMessage.html_content,
      sender: dbMessage.sender,
      type: dbMessage.message_type,
      timestamp: new Date(dbMessage.timestamp).toLocaleTimeString('fr-FR', { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      isLoading: false,
      isSuggestion: dbMessage.is_suggestion === 'true',
      suggestionDetails: dbMessage.suggestion_data ? JSON.parse(dbMessage.suggestion_data) : null,
      conversationId: dbMessage.conversation_id,
      isSourceBubble: dbMessage.message_type === 'source' || dbMessage.html_content !== null,
    };
  }
}

export const chatHistoryService = new ChatHistoryService();
