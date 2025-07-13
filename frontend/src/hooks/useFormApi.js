// src/hooks/useFormApi.js

import { useState, useCallback } from 'react';
import { useNonConformiteApi } from './useApi';

/**
 * Hook spécialisé pour les formulaires 8D
 * Gère automatiquement la création/mise à jour des NC
 */
export const useFormApi = (id = null) => {
  const { loading, error, createNonConformite, updateNonConformite, clearError } = useNonConformiteApi();
  const [apiStatus, setApiStatus] = useState(null);

  const submitForm = useCallback(async (formData) => {
    setApiStatus(null);
    clearError();

    try {
      let result;
      if (id) {
        // Mise à jour d'une NC existante
        result = await updateNonConformite(id, formData);
        setApiStatus('success');
      } else {
        // Création d'une nouvelle NC
        result = await createNonConformite(formData);
        setApiStatus('success');
      }
      
      return result;
    } catch (err) {
      setApiStatus('error');
      throw err;
    }
  }, [id, createNonConformite, updateNonConformite, clearError]);

  const resetStatus = useCallback(() => {
    setApiStatus(null);
    clearError();
  }, [clearError]);

  return {
    loading,
    error,
    apiStatus,
    submitForm,
    resetStatus,
  };
};
