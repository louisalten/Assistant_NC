// Exemple d'utilisation dans D0Form.jsx

import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useNonConformite } from '../hooks/useApi';
import { useForm8D } from '../contexts/Form8DContext';

function D0Form({ tabKeyLabel }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const { form8DData, updateFormField, currentStepKey, setCurrentStepKey } = useForm8D();
  const { nonConformite, updateNonConformite, createNonConformite } = useNonConformite(id);
  
  const [localErrors, setLocalErrors] = useState({});
  const [apiStatus, setApiStatus] = useState(null);

  const handleSubmitToAPI = async () => {
    if (!validatePage()) return;
    
    setApiStatus('loading');
    
    try {
      const payload = {
        d0_initialisation: {
          referenceNC: sectionData.referenceNC,
          dateDetection: sectionData.dateDetection,
          dateCreation: sectionData.dateCreation,
          produitRef: sectionData.produitRef,
          LieuDetection: sectionData.LieuDetection,
          detectePar: sectionData.detectePar,
          descriptionInitiale: sectionData.descriptionInitiale,
          Criticite: sectionData.Criticite,
          FonctionCrea: sectionData.FonctionCrea
        },
        statut: 'En cours',
      };

      let result;
      if (id) {
        result = await updateNonConformite(payload);
      } else {
        result = await createNonConformite(payload);
        if (result && result.id) {
          navigate(`/d0/${result.id}`);
        }
      }
      
      setApiStatus('success');
    } catch (error) {
      setApiStatus('error');
      console.error('Erreur API:', error);
    }
  };

  // ... reste du composant
}

export default D0Form;
