// src/hooks/useFormApi.js

import { useState, useCallback } from 'react';
import apiService from '../services/apiService';

/**
 * Hook spécialisé pour les formulaires 8D
 * Gère automatiquement la création/mise à jour des NC
 */
export const useFormApi = (id = null) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState(null);

  const submitForm = useCallback(async (formData) => {
    setApiStatus(null);
    setError(null);
    setLoading(true);

    try {
      let result;
      if (id) {
        // Mise à jour d'une NC existante
        result = await apiService.updateNonConformite(id, formData);
        setApiStatus('success');
      } else {
        // Création d'une nouvelle NC
        result = await apiService.createNonConformite(formData);
        setApiStatus('success');
      }
      
      return result;
    } catch (err) {
      setApiStatus('error');
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [id]);

  const resetStatus = useCallback(() => {
    setApiStatus(null);
    setError(null);
  }, []);

  return {
    loading,
    error,
    apiStatus,
    submitForm,
    resetStatus,
  };
};
