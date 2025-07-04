// src/components/ChatAssistant.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useForm8D } from '../contexts/Form8DContext';
import { COLORS } from '../colors';
import { Box, Paper, Avatar, Typography, TextField, IconButton, CircularProgress, Snackbar, MenuItem, Select, FormControl, InputLabel, Accordion, AccordionSummary, AccordionDetails } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import StopIcon from '@mui/icons-material/Stop';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { v4 as uuidv4 } from 'uuid'; // Pour des IDs uniques
import ReactMarkdown from 'react-markdown';

function ChatAssistant() {
  const [messages, setMessages] = useState([
    { id: uuidv4(), text: 'Bonjour ! Comment puis-je vous aider avec votre 8D ?', sender: 'bot', isLoading: false }
  ]);
  const [userInput, setUserInput] = useState('');
  const [isOverallLoading, setIsOverallLoading] = useState(false); // Pour le spinner global de l'input
  const [error, setError] = useState(null);
  const [chatMode, setChatMode] = useState('CHAT'); // 'CHAT' ou 'REQ'
  const messagesEndRef = useRef(null);
  const chatMessagesRef = useRef(null);
  const streamReaderRef = useRef(null); // Pour garder le reader courant
  const bubblesCreatedRef = useRef({ think: false, response: false, sources: false }); // Pour tracker les bulles créées

  const { getAllFormData, currentStepKey, form8DData, updateFormField } = useForm8D();

  const scrollToBottom = () => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  };

  useEffect(scrollToBottom, [messages]);

  // Vide le chat à chaque changement de mode (chatMode)
  useEffect(() => {
    setMessages([
      { id: uuidv4(), text: 'Bonjour ! Comment puis-je vous aider avec votre 8D ?', sender: 'bot', isLoading: false }
    ]);
    setUserInput('');
  }, [chatMode]);

  const handleInputChange = (e) => setUserInput(e.target.value);

  // Helper pour parser la réponse du bot en sections (think/réponse)
  function parseBotResponse(rawText) {
    // Nettoie d'abord les balises <think> multiples ou malformées qui se répètent à cause du streaming
    let cleanedText = rawText;
    
    // Supprime les répétitions de balises <think> qui s'accumulent
    cleanedText = cleanedText.replace(/(<think>)+/g, '<think>');
    
    let think = null;
    let response = cleanedText;
    
    // Trouve le contenu entre <think> et </think> (balises fermées)
    const fullThinkMatch = cleanedText.match(/<think>([\s\S]*?)<\/think>/);
    if (fullThinkMatch) {
      // Balises <think> fermées - extraction de la réflexion
      let thinkContent = fullThinkMatch[1];
      thinkContent = thinkContent.replace(/<think>/g, '').trim();
      think = thinkContent;
      
      // Supprime toute la section <think>...</think> de la réponse
      response = cleanedText.replace(/<think>[\s\S]*?<\/think>\s*/, '').trim();
    } else {
      // Vérifie si on a une balise <think> ouverte mais pas fermée (streaming en cours)
      const openThinkMatch = cleanedText.match(/<think>([\s\S]*)$/);
      if (openThinkMatch) {
        // Balise <think> ouverte - streaming de la réflexion en cours
        let thinkContent = openThinkMatch[1];
        thinkContent = thinkContent.replace(/<think>/g, '').trim();
        think = thinkContent;
        
        // Supprime la section <think> ouverte de la réponse (pas de réponse encore)
        response = cleanedText.replace(/<think>[\s\S]*$/, '').trim();
      } else if (cleanedText.includes('<think>')) {
        // Cas où il y a des balises <think> malformées - on nettoie
        response = cleanedText.replace(/<\/?think>/g, '').trim();
      }
    }
    
    // Nettoie les balises <think> restantes dans la réponse
    response = response.replace(/<\/?think>/g, '').trim();
    
    // Si on n'a pas trouvé de balises think, tout le contenu est considéré comme réponse
    if (think === null && !cleanedText.includes('<think>')) {
      response = cleanedText.trim();
    }
    
    return { think, response };
  }

  const handleSendMessage = async (event) => {
    if (event) event.preventDefault();
    let text = userInput.trim();
    if (chatMode === 'REQ') text = '';
    if (text === '' && event && chatMode !== 'REQ') return; // Si appelé par un événement et que l'input est vide

    const conversationId = uuidv4(); // ID pour grouper les bulles de cette conversation
    
    // Reset le tracker des bulles pour cette nouvelle conversation
    bubblesCreatedRef.current = { think: false, response: false, sources: false };
    
    if (chatMode === 'CHAT') {
      // Mode CHAT : créer d'abord la bulle utilisateur
      const userMsg = { 
        id: uuidv4(), 
        text: text, 
        sender: 'user', 
        isLoading: false,
        timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, userMsg]);
    } else {
      // Mode REQ : créer seulement la bulle de sources
      const sourcesMsg = { id: uuidv4(), htmlText: '', sender: 'system', isSourceBubble: true, conversationId, isLoading: true };
      setMessages(prev => [...prev, sourcesMsg]);
    }
    
    setUserInput('');
    setIsOverallLoading(true);
    setError(null);

    const all8DData = getAllFormData();
    const currentSectionData = form8DData[currentStepKey] || {};
///////Modif du moèdle d'embedding dans model_key , allez voir dans config.py pour les modèles disponibles
    try {
      const payload = {
        query: chatMode === 'CHAT' ? text : '', // Envoie la question seulement en mode CHAT
        form_data: all8DData,
        current_section_data: currentSectionData,
        current_section_name: currentStepKey,
        mode: chatMode,
        model_key : "dengcao_qwen3_4b",
        context_only: chatMode === 'REQ' // Indique au serveur de ne se baser que sur le contexte
      };

      // Ajoute une bulle de bot en attente - SUPPRIMÉ car on a déjà créé les 4 bulles
      // setMessages(prev => [...prev, { id: botMessageId, text: '', sender: 'bot', isLoading: true }]);

      const response = await fetch('http://localhost:8000/query_with_context', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: `Erreur HTTP ${response.status}` }));
        throw new Error(errorData.detail || `Erreur serveur ${response.status}`);
      }

      if (chatMode === 'REQ') {
        // Mode REQ : réponse JSON directe
        const data = await response.json();
        setMessages(prev => prev.map(m => {
          if (m.conversationId === conversationId && m.isSourceBubble) {
            if (data.sources && Array.isArray(data.sources) && data.sources.length > 0) {
              const sourceHtmlContent = "<div style='background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #007bff;'>" +
                "<strong style='color: #007bff; font-size: 1.1em;'>📋 Sources Pertinentes :</strong>" +
                "<div style='margin-top: 8px;'>" +
                data.sources.map((s, index) =>
                  `<div style='background: white; margin: 8px 0; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>` +
                  `  <div style='display: flex; align-items: center; margin-bottom: 8px;'>` +
                  `    <span style='background: #007bff; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold;'>${s.nc_id || 'N/A'}</span>` +
                  `  </div>` +
                  `  <div style='color: #666; line-height: 1.4; font-size: 0.9em;'>${s.content || 'Aucun aperçu disponible'}</div>` +
                  `</div>`
                ).join('') + 
                "</div></div>";
              return { ...m, htmlText: sourceHtmlContent, isLoading: false };
            } else {
              return { ...m, htmlText: '<em>Aucune source similaire trouvée.</em>', isLoading: false };
            }
          }
          return m;
        }));
        setIsOverallLoading(false);
        streamReaderRef.current = null;
        return;
      }
      
      if (!response.body) throw new Error('Pas de flux de réponse du serveur.');
      
      const reader = response.body.getReader();
      streamReaderRef.current = reader; // <-- Stocke le reader pour pouvoir l'annuler
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let doneReadingStream = false;

      while (!doneReadingStream) {
        const { value, done } = await reader.read();
        doneReadingStream = done;

        if (value) {
          buffer += decoder.decode(value, { stream: true });
        }
        
        // Traiter les lignes complètes dans le buffer
        // La dernière ligne est gardée dans le buffer sauf si le stream est fini
        let lastNewlineIndex = buffer.lastIndexOf('\n');
        let processBufferUpTo = buffer.length;
        if (!doneReadingStream && lastNewlineIndex !== -1) {
            processBufferUpTo = lastNewlineIndex + 1;
        }

        const linesToProcess = buffer.substring(0, processBufferUpTo);
        buffer = buffer.substring(processBufferUpTo);
        
        const lines = linesToProcess.split('\n').filter(line => line.trim() !== '');

        for (const line of lines) {
          console.log('[CHAT ASSISTANT] Ligne brute à parser:', line);
          let dataChunk;
          try { 
            dataChunk = JSON.parse(line); 
          } catch (e) {
            console.error('ERREUR PARSING JSON sur la ligne:', line, 'Erreur:', e);
            // Si une ligne est invalide, on peut l'ignorer ou afficher une erreur spécifique
            // setMessages(prev => [...prev, { id: uuidv4(), text: `Erreur de format de données reçues: ${line}`, sender: 'error' }]);
            continue; 
          }
          console.log('[CHAT ASSISTANT] Donnée parsée reçue:', dataChunk);

          // Mettre à jour les bulles de réflexion et réponse
          if (dataChunk.response !== undefined) {
            const { think, response } = parseBotResponse(dataChunk.response);
            console.log('[CHAT ASSISTANT] Parsed content:', { 
              think: think ? `${think.substring(0, 50)}...` : 'null', 
              response: response ? `${response.substring(0, 50)}...` : 'null',
              bubblesCreated: bubblesCreatedRef.current
            });
            
            // Créer la bulle de réflexion si elle n'existe pas et qu'on a du contenu think
            if (think !== null && think !== '' && !bubblesCreatedRef.current.think) {
              console.log('[CHAT ASSISTANT] Creating think bubble');
              const thinkMsg = { id: uuidv4(), text: '', sender: 'bot', type: 'think', conversationId, isLoading: true, partialText: '' };
              setMessages(prev => [...prev, thinkMsg]);
              bubblesCreatedRef.current.think = true;
            }
            
            // Créer la bulle de réponse si elle n'existe pas et qu'on a du contenu response
            if (response !== null && response !== '' && !bubblesCreatedRef.current.response) {
              console.log('[CHAT ASSISTANT] Creating response bubble');
              // Délai pour créer la bulle de réponse après la bulle de réflexion si elle existe
              const delay = bubblesCreatedRef.current.think ? 300 : 0;
              setTimeout(() => {
                if (!bubblesCreatedRef.current.response) {
                  const responseMsg = { id: uuidv4(), text: '', sender: 'bot', type: 'response', conversationId, isLoading: true, partialText: '' };
                  setMessages(prev => [...prev, responseMsg]);
                  bubblesCreatedRef.current.response = true;
                  console.log('[CHAT ASSISTANT] Response bubble created');
                }
              }, delay);
            }
            
            // Mettre à jour les bulles existantes avec le contenu streamé
            setMessages(prev => {
              return prev.map(m => {
                // Stream la réflexion - on remplace au lieu de concaténer pour éviter les doublons
                if (m.conversationId === conversationId && m.type === 'think') {
                  if (think !== null && think !== '') {
                    return { ...m, partialText: think, isLoading: !dataChunk.done };
                  }
                  return m;
                }
                // Stream la réponse principale - on remplace au lieu de concaténer
                if (m.conversationId === conversationId && m.type === 'response') {
                  if (response !== null && response !== '') {
                    return { ...m, partialText: response, isLoading: !dataChunk.done };
                  }
                  return m;
                }
                return m;
              });
            });
          }

          // Gérer le chunk final avec "done"
          if (dataChunk.done) {
            console.log('[CHAT ASSISTANT] Chunk final "done" reçu:', dataChunk);
            
            // Créer la bulle de sources si elle n'existe pas encore
            if (!bubblesCreatedRef.current.sources) {
              const sourcesMsg = { id: uuidv4(), htmlText: '', sender: 'system', isSourceBubble: true, conversationId, isLoading: true };
              setMessages(prev => [...prev, sourcesMsg]);
              bubblesCreatedRef.current.sources = true;
            }
            
            // Finaliser toutes les bulles de cette conversation
            setMessages(prev => prev.map(m => {
              if (m.conversationId === conversationId) {
                if (m.type === 'think' && m.partialText) {
                  return { ...m, text: m.partialText, partialText: undefined, isLoading: false };
                }
                if (m.type === 'response' && m.partialText) {
                  return { ...m, text: m.partialText, partialText: undefined, isLoading: false };
                }
                if (m.isSourceBubble) {
                  // Mettre à jour la bulle des sources
                  if (dataChunk.sources && Array.isArray(dataChunk.sources) && dataChunk.sources.length > 0) {
                    const sourceHtmlContent = "<div style='background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #007bff;'>" +
                      "<strong style='color: #007bff; font-size: 1.1em;'>📋 Sources Pertinentes :</strong>" +
                      "<div style='margin-top: 8px;'>" +
                      dataChunk.sources.map((s, index) => 
                        `<div style='background: white; margin: 8px 0; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>` +
                        `  <div style='display: flex; align-items: center; margin-bottom: 8px;'>` +
                        `    <span style='background: #007bff; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold;'>${s.nc_id || 'N/A'}</span>` +
                        `  </div>` +
                        `  <div style='color: #666; line-height: 1.4; font-size: 0.9em;'>${s.content || 'Aucun aperçu disponible'}</div>` +
                        `</div>`
                      ).join('') + 
                      "</div></div>";
                    return { ...m, htmlText: sourceHtmlContent, isLoading: false };
                  } else {
                    return { ...m, htmlText: '<em>Aucune source trouvée.</em>', isLoading: false };
                  }
                }
                return { ...m, isLoading: false };
              }
              return m;
            }));

            // Ajouter la bulle de suggestion de champ si elle existe
            if (dataChunk.suggested_field_update) {
              const { section, field, value } = dataChunk.suggested_field_update;
              const suggestionText = `Je suggère pour la section '${section}', champ '${field}' : \"${value}\".`;
              const suggestionMessageObject = {
                id: uuidv4(),
                text: suggestionText,
                sender: 'bot',
                isSuggestion: true,
                suggestionDetails: dataChunk.suggested_field_update
              };
              setMessages(prev => [...prev, suggestionMessageObject]);
            }
          } 
        } 
      } 
    } catch (error) {
      console.error("Erreur dans handleSendMessage:", error);
      // Mettre à jour les bulles avec le message d'erreur
      setMessages(prev => prev.map(m => {
        if (m.conversationId === conversationId) {
          const errorMsgText = `Erreur: ${error.message || 'Une erreur inconnue est survenue.'}`;
          if (m.type === 'think') {
            return { ...m, text: errorMsgText, isLoading: false };
          }
          if (m.type === 'response') {
            return { ...m, text: errorMsgText, isLoading: false, sender: 'error' };
          }
          if (m.isSourceBubble) {
            return { ...m, htmlText: '<em>Erreur lors de la récupération des sources.</em>', isLoading: false };
          }
        }
        return m;
      }));
      setError(error.message || 'Une erreur inconnue est survenue.');
    } finally {
      setIsOverallLoading(false);
      streamReaderRef.current = null; // Nettoie le reader
      // Assurer qu'aucun message individuel ne reste en mode chargement si le flux s'est terminé (même par erreur)
      setMessages(prev => prev.map(m => m.isLoading ? { ...m, isLoading: false } : m));
    }
  };

  const applyFieldSuggestion = (section, field, value) => {
     updateFormField(section, field, value);
     const confirmationText = `Champ '${field}' de la section '${section}' mis à jour.`;
     setMessages(prev => [...prev, {id: uuidv4(), text: confirmationText, sender: 'system', isLoading: false }]);
  };

  // Bouton STOP : annule le stream
  const handleStopGeneration = () => {
    if (streamReaderRef.current) {
      try { streamReaderRef.current.cancel(); } catch (e) { /* ignore */ }
      streamReaderRef.current = null;
    }
    setIsOverallLoading(false);
    setMessages(prev => prev.map(m => m.isLoading ? { ...m, isLoading: false } : m));
  };

  return (
    <>
      <Paper elevation={3} sx={{
        p: { xs: 1, sm: 2 },
        bgcolor: COLORS.background,
        borderRadius: 4,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: '0 4px 24px 0 rgba(35,57,93,0.10)',
        border: `1.5px solid ${COLORS.primaryDark}20`
      }}>
        {/* Menu déroulant pour choisir le mode */}
        <FormControl size="small" sx={{ mb: 1, minWidth: 120, bgcolor: COLORS.white, borderRadius: 2, boxShadow: '0 1px 4px #e3eafc' }}>
          <InputLabel id="chat-mode-label" sx={{ color: COLORS.primaryDark, fontWeight: 600 }}>Mode</InputLabel>
          <Select
            labelId="chat-mode-label"
            id="chat-mode-select"
            value={chatMode}
            label="Mode"
            onChange={e => setChatMode(e.target.value)}
            sx={{ color: COLORS.primaryDark, bgcolor: COLORS.white, '& .MuiSelect-icon': { color: COLORS.primaryDark } }}
          >
            <MenuItem value="CHAT" sx={{ color: COLORS.primaryDark }}>Chat</MenuItem>
            <MenuItem value="REQ" sx={{ color: COLORS.accentGreen }}>Requête (sources)</MenuItem>
          </Select>
        </FormControl>
        <Box sx={{ flex: 1, overflowY: 'auto', mb: 2, p:1, background: '#f7fafd', borderRadius: 2 }} ref={chatMessagesRef}>
          {messages.map((msg, idx) => {
            // Accordéon pour chaque bulle
            if (msg.type === 'think' || msg.type === 'response') {
              // On stream le contenu dans la même bulle
              const displayText = msg.partialText || msg.text || '';
              const isEmpty = !displayText.trim();
              
              return (
                <Accordion key={msg.id} defaultExpanded={true} sx={{ mb: 1.5, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: msg.type === 'think' ? '#eaf1fb' : '#e6f7ef', color: COLORS.primaryDark }}>
                    <Avatar sx={{ bgcolor: msg.type === 'think' ? COLORS.accentBlue : COLORS.accentGreen, color: COLORS.white, mr: 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>{msg.type === 'think' ? '🤔' : 'A'}</Avatar>
                    <Typography variant="body2" sx={{ color: COLORS.primaryDark, fontWeight: 500, ml: 1 }}>{msg.type === 'think' ? "Réflexion de l'assistant" : "Réponse de l'assistant"}</Typography>
                    {msg.isLoading && (
                      <CircularProgress size={16} sx={{ ml: 2, color: COLORS.primaryDark }} />
                    )}
                  </AccordionSummary>
                  <AccordionDetails>
                    {isEmpty && !msg.isLoading ? (
                      <Typography variant="body2" sx={{ fontStyle: 'italic', color: '#999' }}>
                        {msg.type === 'think' ? 'Aucune réflexion disponible...' : 'En attente de réponse...'}
                      </Typography>
                    ) : (
                      <ReactMarkdown>{displayText}</ReactMarkdown>
                    )}
                  </AccordionDetails>
                </Accordion>
              );
            }
            if (msg.isSourceBubble) {
              const isEmpty = !msg.htmlText || msg.htmlText.trim() === '';
              
              return (
                <Accordion key={msg.id} defaultExpanded={true} sx={{ mb: 1.5, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#eaf1fb', color: COLORS.primaryDark }}>
                    <Avatar sx={{ bgcolor: COLORS.accentBlue, color: COLORS.white, mr: 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>S</Avatar>
                    <Typography variant="body2" sx={{ color: COLORS.primaryDark, fontWeight: 500, ml: 1 }}>Sources</Typography>
                    {msg.isLoading && (
                      <CircularProgress size={16} sx={{ ml: 2, color: COLORS.primaryDark }} />
                    )}
                  </AccordionSummary>
                  <AccordionDetails>
                    {isEmpty && !msg.isLoading ? (
                      <Typography variant="body2" sx={{ fontStyle: 'italic', color: '#999' }}>
                        Recherche de sources en cours...
                      </Typography>
                    ) : (
                      <div dangerouslySetInnerHTML={{ __html: msg.htmlText }} />
                    )}
                  </AccordionDetails>
                </Accordion>
              );
            }
            // Accordéon pour utilisateur, erreur, suggestion, etc.
            return (
              <Accordion key={msg.id} defaultExpanded={true} sx={{ mb: 1.5, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: msg.sender === 'user' ? COLORS.primaryDark : (msg.sender === 'error' ? '#ffeaea' : (msg.sender === 'system' ? '#e6f7ef' : '#eaf1fb')), color: msg.sender === 'user' ? COLORS.white : (msg.sender === 'error' ? COLORS.error : (msg.sender === 'system' ? '#218c5a' : COLORS.primaryDark)) }}>
                  <Avatar sx={{ bgcolor: msg.sender === 'user' ? COLORS.primaryDark : (msg.sender === 'error' ? COLORS.error : (msg.sender === 'system' ? COLORS.accentGreen : COLORS.accentBlue)), color: COLORS.white, ml: msg.sender === 'user' ? 1 : 0, mr: msg.sender === 'user' ? 0 : 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>
                    {msg.sender === 'user' ? 'U' : (msg.sender === 'error' ? 'E' : (msg.sender === 'system' ? 'S' : 'A'))}
                  </Avatar>
                  <Typography variant="body2" sx={{ color: 'inherit', fontWeight: 500, ml: 1, flex: 1 }}>
                    {msg.sender === 'user' ? 'Utilisateur' : (msg.sender === 'error' ? 'Erreur' : (msg.sender === 'system' ? 'Système' : 'Assistant'))}
                  </Typography>
                  {msg.timestamp && (
                    <Typography variant="caption" sx={{ color: 'inherit', opacity: 0.7, fontSize: '0.75rem' }}>
                      {msg.timestamp}
                    </Typography>
                  )}
                  {msg.isLoading && msg.sender === 'bot' && (
                    <CircularProgress size={16} sx={{ ml: 2, color: COLORS.primaryDark }} />
                  )}
                </AccordionSummary>
                <AccordionDetails>
                  {msg.htmlText ? <div dangerouslySetInnerHTML={{ __html: msg.htmlText }} /> : <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: 'inherit' }}>{msg.text}</Typography>}
                  {msg.isSuggestion && msg.suggestionDetails && (
                    <div style={{ 
                      marginTop: '12px', 
                      padding: '12px', 
                      background: 'linear-gradient(135deg, #e8f5e8 0%, #f0f8f0 100%)', 
                      borderRadius: '8px', 
                      border: '1px solid #28a745' 
                    }}>
                      <div style={{ 
                        color: '#155724', 
                        fontWeight: '600', 
                        marginBottom: '8px',
                        fontSize: '0.9em'
                      }}>
                        💡 Suggestion de completion automatique
                      </div>
                      <button 
                        onClick={() => applyFieldSuggestion(msg.suggestionDetails.section, msg.suggestionDetails.field, msg.suggestionDetails.value)} 
                        style={{ 
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                          padding: '8px 16px', 
                          fontSize: '0.875rem', 
                          cursor: 'pointer', 
                          background: 'linear-gradient(135deg, #28a745 0%, #20c997 100%)', 
                          color: 'white', 
                          border: 'none', 
                          borderRadius: '6px', 
                          fontWeight: '500',
                          boxShadow: '0 2px 4px rgba(40, 167, 69, 0.3)',
                          transition: 'all 0.2s ease'
                        }}
                        onMouseOver={(e) => e.target.style.transform = 'translateY(-1px)'}
                        onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
                      >
                        ✓ Appliquer la Suggestion
                      </button>
                    </div>
                  )}
                </AccordionDetails>
              </Accordion>
            );
          })}
          <div ref={messagesEndRef} />
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, pt:1, borderTop: '1px solid', borderColor: '#e3eafc', background: COLORS.white, borderRadius: 2, boxShadow: '0 1px 4px #e3eafc' }}>
          {chatMode === 'CHAT' ? (
            <>
              <TextField
                fullWidth
                placeholder="Posez votre question..."
                value={userInput}
                onChange={handleInputChange}
                onKeyDown={e => {if (e.key === 'Enter' && !e.shiftKey) { handleSendMessage(e); e.preventDefault();}}}
                disabled={isOverallLoading}
                size="small"
                variant="outlined"
                sx={{ bgcolor: COLORS.white, borderRadius: 2 }}
              />
              <IconButton sx={{ bgcolor: COLORS.primaryDark, color: COLORS.white, '&:hover': { bgcolor: COLORS.accentBlue }, boxShadow: '0 1px 4px #e3eafc' }} onClick={handleSendMessage} disabled={isOverallLoading || !userInput.trim()}>
                {isOverallLoading ? <CircularProgress size={24} /> : <SendIcon />}
              </IconButton>
            </>
          ) : (
            <>
              <button
                style={{
                  background: COLORS.accentBlue, color: COLORS.white, border: 'none', borderRadius: 8, padding: '0.7rem 1.5rem', fontWeight: 600, fontSize: '1rem', cursor: 'pointer', boxShadow: '0 2px 8px #e3eafc'
                }}
                disabled={isOverallLoading}
                onClick={() => handleSendMessage({ preventDefault: () => {} })}
              >
                {isOverallLoading ? 'Recherche...' : 'Rechercher des NC similaires'}
              </button>
            </>
          )}
          {isOverallLoading && (
            <IconButton sx={{ bgcolor: COLORS.white, color: COLORS.error, border: '1px solid', borderColor: COLORS.error, ml: 1, boxShadow: '0 1px 4px #e3eafc' }} onClick={handleStopGeneration} title="Arrêter la génération">
              <StopIcon />
            </IconButton>
          )}
        </Box>
        <Snackbar 
          open={!!error} 
          message={error} 
          autoHideDuration={6000} 
          onClose={() => setError(null)} 
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        />
      </Paper>
    </>
  );
}
export default ChatAssistant;