// src/hooks/useApi.js

import { useState, useEffect, useCallback } from 'react';
import apiService from '../services/apiService';

/**
 * Hook personnalisé pour la gestion des appels API avec état
 * @param {Function} apiCall - Fonction d'appel API
 * @param {Array} dependencies - Dépendances pour déclencher l'appel
 * @param {Object} options - Options du hook
 * @returns {Object} - État et méthodes de l'API
 */
export const useApi = (apiCall, dependencies = [], options = {}) => {
  const [data, setData] = useState(options.initialData || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await apiCall(...args);
      setData(result);
      
      return result;
    } catch (err) {
      setError(err.message || 'Erreur API');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiCall]);

  useEffect(() => {
    if (options.executeOnMount !== false) {
      execute();
    }
  }, dependencies);

  return {
    data,
    loading,
    error,
    execute,
    setData,
    setError,
  };
};

/**
 * Hook spécialisé pour les non-conformités
 */
export const useNonConformites = () => {
  const [nonConformites, setNonConformites] = useState([]);
  const [fetchError, setFetchError] = useState(null);

  const loadNonConformites = useCallback(async () => {
    try {
      setFetchError(null);
      const data = await apiService.getNonConformites();
      
      if (Array.isArray(data)) {
        setNonConformites(data);
      } else {
        setNonConformites([]);
        setFetchError('Format inattendu de la réponse API');
      }
    } catch (error) {
      setNonConformites([]);
      setFetchError('Impossible de charger les non-conformités (API non disponible)');
    }
  }, []);

  useEffect(() => {
    loadNonConformites();
  }, [loadNonConformites]);

  return {
    nonConformites,
    fetchError,
    refetch: loadNonConformites, // Alias pour la cohérence
    loadNonConformites,
    setNonConformites,
    setFetchError,
  };
};

/**
 * Hook spécialisé pour une non-conformité spécifique
 */
export const useNonConformite = (id) => {
  const {
    data: nonConformite,
    loading,
    error,
    execute: loadNonConformite,
  } = useApi(
    () => apiService.getNonConformite(id),
    [id],
    { executeOnMount: !!id }
  );

  const updateNonConformite = useCallback(async (data) => {
    try {
      const result = await apiService.updateNonConformite(id, data);
      return result;
    } catch (error) {
      throw error;
    }
  }, [id]);

  const createNonConformite = useCallback(async (data) => {
    try {
      const result = await apiService.createNonConformite(data);
      return result;
    } catch (error) {
      throw error;
    }
  }, []);

  return {
    nonConformite,
    loading,
    error,
    loadNonConformite,
    updateNonConformite,
    createNonConformite,
  };
};

/**
 * Hook spécialisé pour le chat
 */
export const useChatHistory = (ncId) => {
  const {
    data: chatHistory,
    loading,
    error,
    execute: loadChatHistory,
  } = useApi(
    () => apiService.getChatHistory(ncId),
    [ncId],
    { executeOnMount: !!ncId }
  );

  const saveChatMessage = useCallback(async (messageData) => {
    try {
      const result = await apiService.saveChatMessage(ncId, messageData);
      return result;
    } catch (error) {
      throw error;
    }
  }, [ncId]);

  const deleteChatHistory = useCallback(async () => {
    try {
      await apiService.deleteChatHistory(ncId);
      loadChatHistory(); // Recharger après suppression
    } catch (error) {
      throw error;
    }
  }, [ncId, loadChatHistory]);

  return {
    chatHistory,
    loading,
    error,
    loadChatHistory,
    saveChatMessage,
    deleteChatHistory,
  };
};

export default useApi;
