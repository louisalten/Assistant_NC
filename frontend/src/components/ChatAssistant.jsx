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
    // Cherche <think>...</think>
    const thinkRegex = /<think>([\s\S]*?)<\/think>/i;
    const thinkMatch = rawText.match(thinkRegex);
    let think = thinkMatch ? thinkMatch[1].trim() : null;
    let response = rawText.replace(thinkRegex, '').trim();
    return { think, response };
  }

  const handleSendMessage = async (event) => {
    if (event) event.preventDefault();
    let text = userInput.trim();
    if (chatMode === 'REQ') text = '';
    if (text === '' && event && chatMode !== 'REQ') return; // Si appelé par un événement et que l'input est vide

    const userMsg = { id: uuidv4(), text, sender: 'user', isLoading: false };
    setMessages(prev => [...prev, userMsg]);
    setUserInput('');
    setIsOverallLoading(true);
    setError(null);

    const all8DData = getAllFormData();
    const currentSectionData = form8DData[currentStepKey] || {};
    
    let botMessageId = uuidv4(); // ID pour la bulle de réponse du bot
///////Modif du moèdle d'embedding dans model_key , allez voir dans config.py pour les modèles disponibles
    try {
      const payload = {
        query: text,
        form_data: all8DData,
        current_section_data: currentSectionData,
        current_section_name: currentStepKey,
        mode: chatMode,
        model_key : "dengcao_qwen3_4b"
      };

      // Ajoute une bulle de bot en attente
      setMessages(prev => [...prev, { id: botMessageId, text: '', sender: 'bot', isLoading: true }]);

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
        setMessages(prev => prev.map(m => m.id === botMessageId ? { ...m, isLoading: false } : m));
        if (data.sources && Array.isArray(data.sources) && data.sources.length > 0) {
          const sourceHtmlContent = "<strong>Sources Pertinentes :</strong><ul>" +
            data.sources.map(s =>
              `<li>` +
              `  <strong>NC ID:</strong> ${s.nc_id || 'N/A'}<br/>` +
              `  <strong>Aperçu:</strong> <small>${ s.content || 'Aucun aperçu disponible'}</small>` +
              `</li>`
            ).join('') + "</ul>";
          const sourcesMessageObject = {
            id: uuidv4(),
            htmlText: sourceHtmlContent,
            sender: 'system',
            isSourceBubble: true
          };
          setMessages(prev => [...prev, sourcesMessageObject]);
        } else {
          setMessages(prev => prev.map(m => m.id === botMessageId ? { ...m, text: 'Aucune source similaire trouvée.', isLoading: false } : m));
        }
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

          // Mettre à jour la bulle de réponse du bot existante
          if (dataChunk.response !== undefined) {
            const { think, response } = parseBotResponse(dataChunk.response);
            setMessages(prev => {
              let newMsgs = [...prev];
              // Stream la réflexion (concatène si déjà partielle)
              if (think !== null) {
                const thinkIdx = newMsgs.findIndex(m => m.parentId === botMessageId && m.type === 'think');
                if (thinkIdx !== -1) {
                  const prevText = newMsgs[thinkIdx].partialText || '';
                  newMsgs[thinkIdx] = { ...newMsgs[thinkIdx], partialText: prevText + think, isLoading: !dataChunk.done };
                } else {
                  newMsgs.push({ id: uuidv4(), partialText: think, sender: 'bot', type: 'think', parentId: botMessageId, isLoading: !dataChunk.done });
                }
              }
              // Stream la réponse principale (concatène si déjà partielle)
              if (response !== null) {
                const respIdx = newMsgs.findIndex(m => m.parentId === botMessageId && m.type === 'response');
                if (respIdx !== -1) {
                  const prevText = newMsgs[respIdx].partialText || '';
                  newMsgs[respIdx] = { ...newMsgs[respIdx], partialText: prevText + response, isLoading: !dataChunk.done };
                } else if (response !== '') {
                  newMsgs.push({ id: uuidv4(), partialText: response, sender: 'bot', type: 'response', parentId: botMessageId, isLoading: !dataChunk.done });
                }
              }
              // Met à jour la bulle de chargement
              return newMsgs.map(m => m.id === botMessageId ? { ...m, isLoading: !dataChunk.done } : m);
            });
          }

          // Gérer le chunk final avec "done"
          if (dataChunk.done) {
            console.log('[CHAT ASSISTANT] Chunk final "done" reçu:', dataChunk);
            // S'assurer que la bulle de réponse principale est finalisée
            setMessages(prev => prev.map(m => m.id === botMessageId ? { ...m, isLoading: false } : m));

            // Quand done, on remplace partialText par text définitif
            setMessages(prev => prev.map(m => {
              if (m.parentId === botMessageId && m.type === 'think' && m.partialText) {
                return { ...m, text: m.partialText, partialText: undefined, isLoading: false };
              }
              if (m.parentId === botMessageId && m.type === 'response' && m.partialText) {
                return { ...m, text: m.partialText, partialText: undefined, isLoading: false };
              }
              if (m.id === botMessageId) {
                return { ...m, isLoading: false };
              }
              return m;
            }));

            // Ajouter la bulle des sources si des sources existent
            if (dataChunk.sources && Array.isArray(dataChunk.sources) && dataChunk.sources.length > 0) {
              console.log('[CHAT ASSISTANT] Préparation de la bulle des sources avec:', dataChunk.sources);
              const sourceHtmlContent = "<strong>Sources Pertinentes :</strong><ul>" +
                dataChunk.sources.map(s => 
                  `<li>` +
                  `  <strong>NC ID:</strong> ${s.nc_id || 'N/A'}<br/>` +
                  `  <strong>Aperçu:</strong> <small>${ s.content || 'Aucun aperçu disponible'}</small>` +
                  `</li>`
                ).join('') + "</ul>";

              const sourcesMessageObject = {
                id: uuidv4(),
                htmlText: sourceHtmlContent,
                sender: 'system', // Style différent pour les infos système/sources
                isSourceBubble: true 
              };
              setMessages(prev => [...prev, sourcesMessageObject]); 
            } else {
              console.log('[CHAT ASSISTANT] Aucune source à afficher (data.sources vide, absente, ou non-tableau dans le chunk "done")');
            }

            // Ajouter la bulle de suggestion de champ si elle existe
            if (dataChunk.suggested_field_update) {
              const { section, field, value } = dataChunk.suggested_field_update;
              const suggestionText = `Je suggère pour la section '${section}', champ '${field}' : \"${value}\".`;
              const suggestionMessageObject = {
                id: uuidv4(),
                text: suggestionText,
                sender: 'bot', // Ou 'system'
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
      // Mettre à jour la bulle de chargement avec le message d'erreur ou ajouter une nouvelle
      setMessages(prev => {
        const errorMsgText = `Erreur: ${error.message || 'Une erreur inconnue est survenue.'}`;
        const existingBotMsgIndex = prev.findIndex(m => m.id === botMessageId && m.isLoading);
        if (existingBotMsgIndex !== -1) {
          const updatedMessages = [...prev];
          updatedMessages[existingBotMsgIndex] = { ...updatedMessages[existingBotMsgIndex], text: errorMsgText, isLoading: false, sender: 'error' };
          return updatedMessages;
        } else {
          return [...prev, { id: uuidv4(), text: errorMsgText, sender: 'error', isLoading: false }];
        }
      });
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
              return (
                <Accordion key={msg.id} defaultExpanded={true} sx={{ mb: 1.5, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: msg.type === 'think' ? '#eaf1fb' : '#e6f7ef', color: COLORS.primaryDark }}>
                    <Avatar sx={{ bgcolor: msg.type === 'think' ? COLORS.accentBlue : COLORS.accentGreen, color: COLORS.white, mr: 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>{msg.type === 'think' ? '🤔' : 'A'}</Avatar>
                    <Typography variant="body2" sx={{ color: COLORS.primaryDark, fontWeight: 500, ml: 1 }}>{msg.type === 'think' ? "Réflexion de l'assistant" : "Réponse de l'assistant"}</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <ReactMarkdown>{msg.partialText || msg.text}</ReactMarkdown>
                    {msg.isLoading && (
                      <CircularProgress size={16} sx={{ position: 'absolute', top: '10px', left: '10px', color: COLORS.primaryDark }} />
                    )}
                  </AccordionDetails>
                </Accordion>
              );
            }
            if (msg.isSourceBubble) {
              return (
                <Accordion key={msg.id} defaultExpanded={true} sx={{ mb: 1.5, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#eaf1fb', color: COLORS.primaryDark }}>
                    <Avatar sx={{ bgcolor: COLORS.accentBlue, color: COLORS.white, mr: 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>S</Avatar>
                    <Typography variant="body2" sx={{ color: COLORS.primaryDark, fontWeight: 500, ml: 1 }}>Sources</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <div dangerouslySetInnerHTML={{ __html: msg.htmlText }} />
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
                  <Typography variant="body2" sx={{ color: 'inherit', fontWeight: 500, ml: 1 }}>
                    {msg.sender === 'user' ? 'Utilisateur' : (msg.sender === 'error' ? 'Erreur' : (msg.sender === 'system' ? 'Système' : 'Assistant'))}
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {msg.isLoading && msg.sender === 'bot' && (
                    <CircularProgress size={16} sx={{ position: 'absolute', top: '10px', left: '10px', color: COLORS.primaryDark }} />
                  )}
                  {msg.htmlText ? <div dangerouslySetInnerHTML={{ __html: msg.htmlText }} /> : <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: 'inherit' }}>{msg.text}</Typography>}
                  {msg.isSuggestion && msg.suggestionDetails && (
                    <button onClick={() => applyFieldSuggestion(msg.suggestionDetails.section, msg.suggestionDetails.field, msg.suggestionDetails.value)} style={{ display: 'block', marginTop: '10px', padding: '6px 12px', fontSize: '0.875rem', cursor: 'pointer', backgroundColor: COLORS.accentGreen, color: COLORS.white, border: 'none', borderRadius: '4px', boxShadow: '0 2px 2px 0 rgba(0,0,0,0.10)' }}>
                      Appliquer la Suggestion
                    </button>
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