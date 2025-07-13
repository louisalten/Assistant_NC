// src/services/chatHistoryService.js
// DEPRECATED: Ce service est remplacé par apiService.js
// Utilisez apiService.saveChatMessage(), apiService.getChatHistory(), etc.

import apiService from './apiService';

/**
 * @deprecated Utilisez apiService à la place
 */
class ChatHistoryService {
  /**
   * @deprecated Utilisez apiService.saveChatMessage()
   */
  async saveMessage(ncId, messageData) {
    console.warn('ChatHistoryService.saveMessage() is deprecated. Use apiService.saveChatMessage() instead.');
    return apiService.saveChatMessage(ncId, messageData);
  }

  /**
   * @deprecated Utilisez apiService.getChatHistory()
   */
  async getHistory(ncId) {
    console.warn('ChatHistoryService.getHistory() is deprecated. Use apiService.getChatHistory() instead.');
    return apiService.getChatHistory(ncId);
  }

  /**
   * @deprecated Utilisez apiService.deleteChatMessage()
   */
  async deleteMessage(ncId, messageId) {
    console.warn('ChatHistoryService.deleteMessage() is deprecated. Use apiService.deleteChatMessage() instead.');
    return apiService.deleteChatMessage(ncId, messageId);
  }

  /**
   * @deprecated Utilisez apiService.clearChatHistory()
   */
  async clearHistory(ncId) {
    console.warn('ChatHistoryService.clearHistory() is deprecated. Use apiService.clearChatHistory() instead.');
    return apiService.clearChatHistory(ncId);
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
