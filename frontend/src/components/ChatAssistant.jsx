// src/components/ChatAssistant.jsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useForm8D } from '../contexts/Form8DContext';
import { COLORS } from '../colors';
import apiService from '../services/apiService';
import { Box, Paper, Avatar, Typography, TextField, IconButton, CircularProgress, Snackbar, MenuItem, Select, FormControl, InputLabel, Accordion, AccordionSummary, AccordionDetails, Dialog, DialogTitle, DialogContent, DialogActions, Button } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import StopIcon from '@mui/icons-material/Stop';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import CloseIcon from '@mui/icons-material/Close';
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
  const [historyLoaded, setHistoryLoaded] = useState(false); // Pour tracker si l'historique a été chargé
  const [autoScroll, setAutoScroll] = useState(true); // Pour contrôler le scroll automatique
  const [ncPreviewOpen, setNcPreviewOpen] = useState(false); // Modal d'aperçu NC
  const [previewNCData, setPreviewNCData] = useState(null); // Données de la NC en aperçu
  const [previewLoading, setPreviewLoading] = useState(false); // Chargement de l'aperçu
  const messagesEndRef = useRef(null);
  const chatMessagesRef = useRef(null);
  const streamReaderRef = useRef(null); // Pour garder le reader courant
  const bubblesCreatedRef = useRef({ think: false, response: false, sources: false }); // Pour tracker les bulles créées

  const { getAllFormData, currentStepKey, form8DData, updateFormField, currentNCId } = useForm8D();

  console.log('[CHAT ASSISTANT] Rendu avec currentNCId:', currentNCId);

  const scrollToBottom = () => {
    if (autoScroll && chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  };

  // Détecter quand l'utilisateur scroll manuellement
  const handleScroll = () => {
    if (!chatMessagesRef.current) return;
    
    const { scrollTop, scrollHeight, clientHeight } = chatMessagesRef.current;
    const isAtBottom = scrollHeight - scrollTop <= clientHeight + 10; // 10px de tolérance
    
    // Réactiver l'auto-scroll si l'utilisateur est revenu en bas
    if (isAtBottom && !autoScroll) {
      setAutoScroll(true);
    }
    // Désactiver l'auto-scroll si l'utilisateur scroll vers le haut
    else if (!isAtBottom && autoScroll) {
      setAutoScroll(false);
    }
  };

  useEffect(scrollToBottom, [messages]);

  // Fonction pour nettoyer les doublons de bulles par conversationId et type
  const cleanDuplicateBubbles = useCallback((messages) => {
    const seenBubbles = new Set();
    const cleanedMessages = [];
    
    for (const msg of messages) {
      if (msg.conversationId && (msg.type || msg.isSourceBubble)) {
        const bubbleType = msg.type || (msg.isSourceBubble ? 'source' : 'unknown');
        const bubbleKey = `${msg.conversationId}-${bubbleType}`;
        if (seenBubbles.has(bubbleKey)) {
          console.log('[CHAT CLEANUP] Removing duplicate bubble:', bubbleKey, msg.id);
          continue; // Ignorer ce doublon
        }
        seenBubbles.add(bubbleKey);
      }
      cleanedMessages.push(msg);
    }
    
    if (cleanedMessages.length !== messages.length) {
      console.log(`[CHAT CLEANUP] Cleaned ${messages.length - cleanedMessages.length} duplicate bubbles`);
    }
    
    return cleanedMessages;
  }, []);

  // Charger l'historique de chat depuis la base de données
  const loadChatHistory = useCallback(async () => {
    if (!currentNCId) {
      console.log('[CHAT HISTORY] Pas de currentNCId, arrêt du chargement');
      return;
    }
    
    try {
      console.log(`[CHAT HISTORY] Chargement de l'historique pour NC ${currentNCId}`);
      const data = await apiService.getChatHistory(currentNCId);
      
      console.log(`[CHAT HISTORY] Historique chargé:`, data);
      
      if (data.messages && data.messages.length > 0) {
          // Convertir les messages de la DB au format attendu par le frontend
          const loadedMessages = data.messages.map(msg => ({
            id: `db-${msg.id}`, // Utiliser l'ID auto-increment de la DB avec un préfixe
            messageId: msg.message_id, // Garder le message_id original comme propriété séparée
            text: msg.content,
            htmlText: msg.html_content,
            sender: msg.sender,
            type: msg.message_type,
            isLoading: false,
            timestamp: new Date(msg.timestamp).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
            conversationId: msg.conversation_id,
            isSourceBubble: msg.message_type === 'source',
            isSuggestion: msg.is_suggestion === 'true',
            stepContext: msg.step_context
          }));
          
          // Ajouter le message de bienvenue si pas déjà présent
          const welcomeMessage = { 
            id: uuidv4(), 
            text: 'Bonjour ! Comment puis-je vous aider avec votre 8D ?', 
            sender: 'bot', 
            isLoading: false 
          };
          
          console.log(`[CHAT HISTORY] Mise à jour des messages avec ${loadedMessages.length} messages chargés`);
          
          // Filtrer les doublons basés sur l'ID de la base de données
          const existingDbIds = new Set();
          const uniqueLoadedMessages = loadedMessages.filter(msg => {
            const dbId = msg.id.replace('db-', '');
            if (existingDbIds.has(dbId)) {
              console.log('[CHAT HISTORY] Message dupliqué ignoré:', msg.id);
              return false;
            }
            existingDbIds.add(dbId);
            return true;
          });
          
          console.log(`[CHAT HISTORY] Messages uniques après filtrage: ${uniqueLoadedMessages.length}`);
          
          // Nettoyer les doublons de bulles par conversationId
          const cleanedMessages = cleanDuplicateBubbles([welcomeMessage, ...uniqueLoadedMessages]);
          
          setMessages(cleanedMessages);
          setHistoryLoaded(true);
          console.log(`[CHAT HISTORY] ${cleanedMessages.length} messages chargés et affichés après nettoyage`);
        } else {
          console.log('[CHAT HISTORY] Aucun message trouvé');
          setHistoryLoaded(true);
        }
    } catch (error) {
      console.error('[CHAT HISTORY] Erreur lors du chargement de l\'historique:', error);
      setHistoryLoaded(true);
    }
  }, [currentNCId]);

  // Charger l'historique quand l'ID de la NC change
  useEffect(() => {
    if (currentNCId) {
      console.log(`[CHAT HISTORY] NC ID changé: ${currentNCId}, chargement de l'historique...`);
      // Reset d'abord
      setMessages([
        { id: uuidv4(), text: 'Bonjour ! Comment puis-je vous aider avec votre 8D ?', sender: 'bot', isLoading: false }
      ]);
      setHistoryLoaded(false);
      setUserInput('');
      // Puis charger l'historique
      loadChatHistory();
    }
  }, [currentNCId, loadChatHistory]);

  // Vide le chat à chaque changement de mode (chatMode)
  useEffect(() => {
    console.log(`[CHAT MODE] Changement de mode: ${chatMode}`);
    if (chatMode === 'REQ') {
      // En mode REQ, afficher seulement le message de bienvenue REQ
      console.log('[CHAT MODE] Passage en mode REQ, nettoyage interface...');
      setMessages([
        { id: uuidv4(), text: 'Bonjour ! Utilisez le bouton "Rechercher des NC similaires" pour trouver des sources pertinentes.', sender: 'bot', isLoading: false }
      ]);
      setUserInput('');
      setAutoScroll(true); // Réactiver l'auto-scroll en mode REQ
    } else if (chatMode === 'CHAT') {
      // En mode CHAT, toujours nettoyer d'abord puis recharger l'historique
      console.log('[CHAT MODE] Passage en mode CHAT, nettoyage et rechargement...');
      // D'abord nettoyer l'interface
      setMessages([
        { id: uuidv4(), text: 'Bonjour ! Comment puis-je vous aider avec votre 8D ?', sender: 'bot', isLoading: false }
      ]);
      setUserInput('');
      setAutoScroll(true); // Réactiver l'auto-scroll en mode CHAT
      
      // Puis recharger l'historique si on a une NC
      if (currentNCId) {
        console.log('[CHAT MODE] Rechargement de l\'historique pour NC:', currentNCId);
        // Forcer le rechargement de l'historique
        setHistoryLoaded(false);
        loadChatHistory();
      }
    }
  }, [chatMode, currentNCId, loadChatHistory]);

  const handleInputChange = (e) => setUserInput(e.target.value);

  // Sauvegarder un message dans la base de données
  const saveChatMessage = async (message, stepContext = null) => {
    if (!currentNCId) return;
    
    // Ne pas sauvegarder les messages en mode REQ (ils sont temporaires)
    if (chatMode === 'REQ') {
      console.log('[CHAT HISTORY] Mode REQ: message non sauvegardé', message.id);
      return;
    }
    
    try {
      // Déterminer le message_type correct
      let messageType = message.type;
      if (message.isSourceBubble || (message.sender === 'system' && message.htmlText)) {
        messageType = 'source';
      }
      
      const messageToSave = {
        message_id: message.id,
        conversation_id: message.conversationId || null,
        sender: message.sender,
        message_type: messageType || null,
        content: message.text || message.partialText || '',
        html_content: message.htmlText || null,
        step_context: stepContext || currentStepKey,
        is_suggestion: message.isSuggestion ? 'true' : 'false'
      };

      await apiService.saveChatMessage(currentNCId, messageToSave);
      
      console.log('[CHAT HISTORY] Message sauvegardé:', messageToSave.message_type, messageToSave.sender, messageToSave.conversation_id);
    } catch (error) {
      console.error('[CHAT HISTORY] Erreur lors de la sauvegarde:', error);
    }
  };

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

    // Réactiver l'auto-scroll lors de l'envoi d'un nouveau message
    setAutoScroll(true);

    const conversationId = uuidv4(); // ID pour grouper les bulles de cette conversation
    console.log('[CHAT] Nouvelle conversation:', conversationId);
    
    // Reset le tracker des bulles pour cette nouvelle conversation
    bubblesCreatedRef.current = { think: false, response: false, sources: false };
    
    if (chatMode === 'CHAT') {
      // Mode CHAT : créer d'abord la bulle utilisateur
      const userMsg = { 
        id: uuidv4(), 
        text: text, 
        sender: 'user', 
        isLoading: false,
        timestamp: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' }),
        conversationId // Ajouter l'ID de conversation
      };
      console.log('[CHAT] Ajout message utilisateur:', userMsg);
      setMessages(prev => {
        console.log('[CHAT] Messages avant ajout user:', prev.length);
        const newMessages = [...prev, userMsg];
        console.log('[CHAT] Messages après ajout user:', newMessages.length);
        return newMessages;
      });
      // Sauvegarder le message utilisateur
      saveChatMessage(userMsg, currentStepKey);
    } else {
      // Mode REQ : créer seulement la bulle de sources
      const sourcesMsg = { id: uuidv4(), htmlText: '', sender: 'system', type: 'source', isSourceBubble: true, conversationId, isLoading: true };
      console.log('[CHAT] Ajout sources (REQ mode):', sourcesMsg);
      setMessages(prev => [...prev, sourcesMsg]);
    }
    
    setUserInput('');
    setIsOverallLoading(true);
    setError(null);

    const all8DData = getAllFormData();
    const currentSectionData = form8DData[currentStepKey] || {};

    try {
      const payload = {
        query: chatMode === 'CHAT' ? text : '', // Envoie la question seulement en mode CHAT
        form_data: all8DData,
        current_section_data: currentSectionData,
        current_section_name: currentStepKey,
        mode: chatMode,
        model_key : "qwen_base",
        context_only: chatMode === 'REQ' // Indique au serveur de ne se baser que sur le contexte
      };

      const response = await apiService.queryWithStreamingResponse(payload);

      if (chatMode === 'REQ') {
        // Mode REQ : réponse JSON directe
        const data = await response.json();
        console.log('[CHAT ASSISTANT] Données reçues en mode REQ:', data);
        console.log('[CHAT ASSISTANT] Sources reçues:', data.sources);
        if (data.sources && data.sources.length > 0) {
          data.sources.forEach((source, i) => {
            console.log(`[CHAT ASSISTANT] Source ${i+1}:`, source);
            console.log(`[CHAT ASSISTANT] Score de la source ${i+1}:`, source.similarity_score);
          });
        }
        setMessages(prev => {
          const updatedMessages = prev.map(m => {
            if (m.conversationId === conversationId && m.isSourceBubble) {
              if (data.sources && Array.isArray(data.sources) && data.sources.length > 0) {
                const sourceHtmlContent = "<div style='background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #007bff;'>" +
                  "<strong style='color: #007bff; font-size: 1.1em;'>📋 Sources Pertinentes :</strong>" +
                  "<div style='margin-top: 8px;'>" +
                  data.sources.map((s, index) =>
                    `<div style='background: white; margin: 8px 0; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>` +
                    `  <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;'>` +
                    `    <span style='background: #007bff; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold;'>${s.nc_id || 'N/A'}</span>` +
                    (s.similarity_score !== undefined ? 
                      `    <span style='background: #17a2b8; color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.7em; font-weight: bold; margin-left: 8px;'>📊 ${(s.similarity_score * 100).toFixed(1)}%</span>` : '') +
                    `    <a href='${apiService.getPdfUrl(s.nc_id, m.conversationId)}' target='_blank' style='background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 0.75em; font-weight: bold; transition: background 0.2s; display: inline-flex; align-items: center; gap: 4px;' onmouseover='this.style.background="#218838"' onmouseout='this.style.background="#28a745"'>📄 PDF</a>` +
                    `  </div>` +
                    `  <div style='color: #666; line-height: 1.4; font-size: 0.9em; margin-bottom: 8px;'>${s.content || 'Aucun aperçu disponible'}</div>` +
                    `  <div style='border-top: 1px solid #eee; padding-top: 8px; margin-top: 8px;'>` +
                    `    <button onclick='showNCPreview("${s.nc_id}", "${m.conversationId}")' style='background: #17a2b8; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.75em; cursor: pointer; transition: background 0.2s;' onmouseover='this.style.background="#138496"' onmouseout='this.style.background="#17a2b8"'>👁️ Aperçu rapide</button>` +
                    `  </div>` +
                    `</div>`
                  ).join('') + 
                  "</div></div>";              const updatedMsg = { ...m, htmlText: sourceHtmlContent, isLoading: false, type: 'source' };
              // Sauvegarder le message sources
              console.log('[CHAT ASSISTANT] Sauvegarde sources REQ mode:', updatedMsg.id, updatedMsg.conversationId);
              saveChatMessage(updatedMsg, currentStepKey);
              return updatedMsg;
            } else {
              const updatedMsg = { ...m, htmlText: '<em>Aucune source similaire trouvée.</em>', isLoading: false, type: 'source' };
              console.log('[CHAT ASSISTANT] Sauvegarde sources vides REQ mode:', updatedMsg.id, updatedMsg.conversationId);
              saveChatMessage(updatedMsg, currentStepKey);
              return updatedMsg;
              }
            }
            return m;
          });
          // Nettoyer les doublons
          return cleanDuplicateBubbles(updatedMessages);
        });
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
            continue; 
          }
          console.log('[CHAT ASSISTANT] Donnée parsée reçue:', dataChunk);

          // Mettre à jour les bulles de réflexion et réponse (UNIQUEMENT en mode CHAT)
          if (dataChunk.response !== undefined && chatMode === 'CHAT') {
            const { think, response } = parseBotResponse(dataChunk.response);
            console.log('[CHAT ASSISTANT] Parsed content (CHAT mode):', { 
              think: think ? `${think.substring(0, 50)}...` : 'null', 
              response: response ? `${response.substring(0, 50)}...` : 'null',
              bubblesCreated: bubblesCreatedRef.current
            });
            
            // Créer la bulle de réflexion si elle n'existe pas et qu'on a du contenu think
            if (think !== null && think !== '' && !bubblesCreatedRef.current.think) {
              setMessages(prev => {
                // Vérifier si une bulle think existe déjà pour cette conversation
                const existingThinkBubble = prev.find(m => m.conversationId === conversationId && m.type === 'think');
                if (existingThinkBubble) {
                  console.log('[CHAT ASSISTANT] Think bubble already exists for conv:', conversationId);
                  bubblesCreatedRef.current.think = true;
                  return prev; // Ne pas créer de nouvelle bulle
                }
                
                console.log('[CHAT ASSISTANT] Creating think bubble for conv:', conversationId);
                const thinkMsg = { id: uuidv4(), text: '', sender: 'bot', type: 'think', conversationId, isLoading: true, partialText: '' };
                console.log('[CHAT] Adding think bubble, messages before:', prev.length);
                const newMessages = [...prev, thinkMsg];
                console.log('[CHAT] Adding think bubble, messages after:', newMessages.length);
                bubblesCreatedRef.current.think = true;
                return newMessages;
              });
            }
            
            // Créer la bulle de réponse si elle n'existe pas et qu'on a du contenu response
            if (response !== null && response !== '' && !bubblesCreatedRef.current.response) {
              setMessages(prev => {
                // Vérifier si une bulle response existe déjà pour cette conversation
                const existingResponseBubble = prev.find(m => m.conversationId === conversationId && m.type === 'response');
                if (existingResponseBubble) {
                  console.log('[CHAT ASSISTANT] Response bubble already exists for conv:', conversationId);
                  bubblesCreatedRef.current.response = true;
                  return prev; // Ne pas créer de nouvelle bulle
                }
                
                console.log('[CHAT ASSISTANT] Creating response bubble for conv:', conversationId);
                const responseMsg = { id: uuidv4(), text: '', sender: 'bot', type: 'response', conversationId, isLoading: true, partialText: '' };
                console.log('[CHAT] Adding response bubble, messages before:', prev.length);
                const newMessages = [...prev, responseMsg];
                console.log('[CHAT] Adding response bubble, messages after:', newMessages.length);
                bubblesCreatedRef.current.response = true;
                return newMessages;
              });
            }
            
            // Mettre à jour les bulles existantes avec le contenu streamé (CHAT mode uniquement)
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
            
            if (chatMode === 'CHAT') {
              // Mode CHAT : créer la bulle de sources si elle n'existe pas encore
              if (!bubblesCreatedRef.current.sources) {
                setMessages(prev => {
                  // Vérifier si une bulle sources existe déjà pour cette conversation
                  const existingSourcesBubble = prev.find(m => m.conversationId === conversationId && m.isSourceBubble);
                  if (existingSourcesBubble) {
                    console.log('[CHAT ASSISTANT] Sources bubble already exists for conv:', conversationId);
                    bubblesCreatedRef.current.sources = true;
                    return prev; // Ne pas créer de nouvelle bulle
                  }
                  
                  console.log('[CHAT ASSISTANT] Creating sources bubble for conv:', conversationId);
                  const sourcesMsg = { id: uuidv4(), htmlText: '', sender: 'system', type: 'source', isSourceBubble: true, conversationId, isLoading: true };
                  bubblesCreatedRef.current.sources = true;
                  return [...prev, sourcesMsg];
                });
              }
              
              // Finaliser toutes les bulles de cette conversation (CHAT mode)
              setMessages(prev => prev.map(m => {
                if (m.conversationId === conversationId) {
                  if (m.type === 'think' && m.partialText) {
                    const finalThinkMsg = { ...m, text: m.partialText, partialText: undefined, isLoading: false };
                    // Sauvegarder la bulle de réflexion finale
                    saveChatMessage(finalThinkMsg, currentStepKey);
                    return finalThinkMsg;
                  }
                  if (m.type === 'response' && m.partialText) {
                    const finalResponseMsg = { ...m, text: m.partialText, partialText: undefined, isLoading: false };
                    // Sauvegarder la bulle de réponse finale
                    saveChatMessage(finalResponseMsg, currentStepKey);
                    return finalResponseMsg;
                  }
                  if (m.isSourceBubble) {
                    // Mettre à jour la bulle des sources
                    if (dataChunk.sources && Array.isArray(dataChunk.sources) && dataChunk.sources.length > 0) {                        const sourceHtmlContent = "<div style='background: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #007bff;'>" +
                        "<strong style='color: #007bff; font-size: 1.1em;'>📋 Sources Pertinentes :</strong>" +
                        "<div style='margin-top: 8px;'>" +
                        dataChunk.sources.map((s, index) => 
                          `<div style='background: white; margin: 8px 0; padding: 12px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>` +
                          `  <div style='display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;'>` +
                          `    <span style='background: #007bff; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8em; font-weight: bold;'>${s.nc_id || 'N/A'}</span>` +
                          (s.similarity_score !== undefined ? 
                            `    <span style='background: #17a2b8; color: white; padding: 2px 6px; border-radius: 8px; font-size: 0.7em; font-weight: bold; margin-left: 8px;'>📊 ${(s.similarity_score * 100).toFixed(1)}%</span>` : '') +
                          `    <a href='${apiService.getPdfUrl(s.nc_id, m.conversationId)}' target='_blank' style='background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 0.75em; font-weight: bold; transition: background 0.2s; display: inline-flex; align-items: center; gap: 4px;' onmouseover='this.style.background="#218838"' onmouseout='this.style.background="#28a745"'>📄 PDF</a>` +
                          `  </div>` +
                          `  <div style='color: #666; line-height: 1.4; font-size: 0.9em; margin-bottom: 8px;'>${s.content || 'Aucun aperçu disponible'}</div>` +
                          `  <div style='border-top: 1px solid #eee; padding-top: 8px; margin-top: 8px;'>` +
                          `    <button onclick='showNCPreview("${s.nc_id}", "${m.conversationId}")' style='background: #17a2b8; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 0.75em; cursor: pointer; transition: background 0.2s;' onmouseover='this.style.background="#138496"' onmouseout='this.style.background="#17a2b8"'>👁️ Aperçu rapide</button>` +
                          `  </div>` +
                          `</div>`
                        ).join('') + 
                        "</div></div>";
                      const finalSourceMsg = { ...m, htmlText: sourceHtmlContent, isLoading: false, type: 'source' };
                      // Sauvegarder la bulle des sources
                      console.log('[CHAT ASSISTANT] Sauvegarde de la bulle sources CHAT:', finalSourceMsg.id, finalSourceMsg.conversationId);
                      saveChatMessage(finalSourceMsg, currentStepKey);
                      return finalSourceMsg;
                    } else {
                      const finalSourceMsg = { ...m, htmlText: '<em>Aucune source trouvée.</em>', isLoading: false, type: 'source' };
                      console.log('[CHAT ASSISTANT] Sauvegarde de la bulle sources vide CHAT:', finalSourceMsg.id, finalSourceMsg.conversationId);
                      saveChatMessage(finalSourceMsg, currentStepKey);
                      return finalSourceMsg;
                    }
                  }
                  return { ...m, isLoading: false };
                }
                return m;
              }));
            }
            // Pour le mode REQ, les sources sont déjà finalisées plus haut

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
              // Sauvegarder la suggestion
              saveChatMessage(suggestionMessageObject, currentStepKey);
            }
          } 
        } 
      } 
    } catch (error) {
      console.error("Erreur dans handleSendMessage:", error);
      // Mettre à jour les bulles avec le message d'erreur
      setMessages(prev => {
        const updatedMessages = prev.map(m => {
          if (m.conversationId === conversationId) {
            const errorMsgText = `Erreur: ${error.message || 'Une erreur inconnue est survenue.'}`;
            if (m.type === 'think') {
              const errorThinkMsg = { ...m, text: errorMsgText, isLoading: false };
              saveChatMessage(errorThinkMsg, currentStepKey);
              return errorThinkMsg;
            }
            if (m.type === 'response') {
              const errorResponseMsg = { ...m, text: errorMsgText, isLoading: false, sender: 'error' };
              saveChatMessage(errorResponseMsg, currentStepKey);
              return errorResponseMsg;
            }
            if (m.isSourceBubble) {
              const errorSourceMsg = { ...m, htmlText: '<em>Erreur lors de la récupération des sources.</em>', isLoading: false };
              saveChatMessage(errorSourceMsg, currentStepKey);
              return errorSourceMsg;
            }
          }
          return m;
        });
        // Nettoyer les doublons après la gestion d'erreur
        return cleanDuplicateBubbles(updatedMessages);
      });
      setError(error.message || 'Une erreur inconnue est survenue.');
    } finally {
      setIsOverallLoading(false);
      streamReaderRef.current = null; // Nettoie le reader
      // Assurer qu'aucun message individuel ne reste en mode chargement si le flux s'est terminé (même par erreur)
      setMessages(prev => {
        const updatedMessages = prev.map(m => m.isLoading ? { ...m, isLoading: false } : m);
        // Nettoyer les doublons après la finalisation
        return cleanDuplicateBubbles(updatedMessages);
      });
    }
  };

  const applyFieldSuggestion = (section, field, value) => {
     updateFormField(section, field, value);
     const confirmationText = `Champ '${field}' de la section '${section}' mis à jour.`;
     const confirmationMsg = {id: uuidv4(), text: confirmationText, sender: 'system', isLoading: false };
     setMessages(prev => [...prev, confirmationMsg]);
     saveChatMessage(confirmationMsg, currentStepKey);
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

  // Fonction pour afficher l'aperçu rapide d'une NC
  const showNCPreview = async (ncId, conversationId) => {
    setPreviewLoading(true);
    setNcPreviewOpen(true);
    
    try {
      const htmlContent = await apiService.getSummary(ncId, conversationId);
      setPreviewNCData({
        id: ncId,
        conversationId: conversationId, // Stocke l'ID de conversation pour les actions ultérieures
        htmlContent: htmlContent
      });
    } catch (error) {
      console.error('Erreur lors du chargement de l\'aperçu NC:', error);
      setPreviewNCData({
        id: ncId,
        conversationId: conversationId,
        htmlContent: '<p style="color: red;">Erreur lors du chargement de l\'aperçu.</p>'
      });
    } finally {
      setPreviewLoading(false);
    }
  };
  
  // Exposer la fonction showNCPreview au niveau global pour les onclick inline
  useEffect(() => {
    window.showNCPreview = (ncId, conversationId) => {
      showNCPreview(ncId, conversationId);
    };
    
    return () => {
      // Nettoyer la fonction globale lors du démontage
      delete window.showNCPreview;
    };
  }, []);

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
        {/* ...existing chat content... */}
        
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

        <Box 
          sx={{ flex: 1, overflowY: 'auto', mb: 2, p:1, background: '#f7fafd', borderRadius: 2 }} 
          ref={chatMessagesRef}
          onScroll={handleScroll}
        >
          {messages
            .filter(msg => {
              // En mode REQ, afficher seulement les messages du bot de bienvenue et les sources
              if (chatMode === 'REQ') {
                return (msg.sender === 'bot' && !msg.type && !msg.isSourceBubble) || 
                       (msg.sender === 'system' && msg.isSourceBubble);
              }
              // En mode CHAT, afficher tous les messages
              return true;
            })
            .map((msg, idx) => {
            // Ne pas afficher les messages invalides
            if (!msg.id) return null;
            
            // Grouper les messages par conversation pour un affichage ordonné
            // Chaque message s'affiche dans l'ordre chronologique
            
            // Message utilisateur
            if (msg.sender === 'user') {
              return (
                <Accordion key={msg.id} defaultExpanded={true} sx={{ mb: 1.5, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: COLORS.primaryDark, color: COLORS.white }}>
                    <Avatar sx={{ bgcolor: COLORS.primaryDark, color: COLORS.white, ml: 1, mr: 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>U</Avatar>
                    <Typography variant="body2" sx={{ color: 'inherit', fontWeight: 500, ml: 1, flex: 1 }}>Utilisateur</Typography>
                    {msg.timestamp && (
                      <Typography variant="caption" sx={{ color: 'inherit', opacity: 0.7, fontSize: '0.75rem' }}>
                        {msg.timestamp}
                      </Typography>
                    )}
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: 'inherit' }}>{msg.text}</Typography>
                  </AccordionDetails>
                </Accordion>
              );
            }
            
            // Réflexion de l'assistant
            if (msg.type === 'think') {
              const displayText = msg.partialText || msg.text || '';
              const isEmpty = !displayText.trim();
              
              return (
                <Accordion key={msg.id} defaultExpanded={false} sx={{ mb: 1.5, ml: 2, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#eaf1fb', color: COLORS.primaryDark }}>
                    <Avatar sx={{ bgcolor: COLORS.accentBlue, color: COLORS.white, mr: 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>🤔</Avatar>
                    <Typography variant="body2" sx={{ color: COLORS.primaryDark, fontWeight: 500, ml: 1 }}>Réflexion de l'assistant</Typography>
                    {msg.isLoading && (
                      <CircularProgress size={16} sx={{ ml: 2, color: COLORS.primaryDark }} />
                    )}
                  </AccordionSummary>
                  <AccordionDetails>
                    {isEmpty && !msg.isLoading ? (
                      <Typography variant="body2" sx={{ fontStyle: 'italic', color: '#999' }}>
                        Réflexion en cours...
                      </Typography>
                    ) : (
                      <ReactMarkdown>{displayText}</ReactMarkdown>
                    )}
                  </AccordionDetails>
                </Accordion>
              );
            }
            
            // Réponse de l'assistant
            if (msg.type === 'response') {
              const displayText = msg.partialText || msg.text || '';
              const isEmpty = !displayText.trim();
              
              return (
                <Accordion key={msg.id} defaultExpanded={true} sx={{ mb: 1.5, ml: 2, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#e6f7ef', color: COLORS.primaryDark }}>
                    <Avatar sx={{ bgcolor: COLORS.accentGreen, color: COLORS.white, mr: 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>A</Avatar>
                    <Typography variant="body2" sx={{ color: COLORS.primaryDark, fontWeight: 500, ml: 1 }}>Réponse de l'assistant</Typography>
                    {msg.isLoading && (
                      <CircularProgress size={16} sx={{ ml: 2, color: COLORS.primaryDark }} />
                    )}
                  </AccordionSummary>
                  <AccordionDetails>
                    {isEmpty && !msg.isLoading ? (
                      <Typography variant="body2" sx={{ fontStyle: 'italic', color: '#999' }}>
                        En attente de réponse...
                      </Typography>
                    ) : (
                      <ReactMarkdown>{displayText}</ReactMarkdown>
                    )}
                  </AccordionDetails>
                </Accordion>
              );
            }
            
            // Sources (système)
            if (msg.isSourceBubble || (msg.sender === 'system' && msg.type === 'source')) {
              const isEmpty = !msg.htmlText || msg.htmlText.trim() === '';
              
              return (
                <Accordion key={msg.id} defaultExpanded={false} sx={{ mb: 1.5, ml: 2, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#e6f7ef', color: COLORS.primaryDark }}>
                    <Avatar sx={{ bgcolor: COLORS.accentGreen, color: COLORS.white, mr: 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>S</Avatar>
                    <Typography variant="body2" sx={{ color: COLORS.primaryDark, fontWeight: 500, ml: 1 }}>Non-conformités sources</Typography>
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
            
            // Messages du bot générique (bienvenue, etc.)
            if (msg.sender === 'bot' && !msg.type && !msg.isSourceBubble) {
              return (
                <Accordion key={msg.id} defaultExpanded={true} sx={{ mb: 1.5, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#eaf1fb', color: COLORS.primaryDark }}>
                    <Avatar sx={{ bgcolor: COLORS.accentBlue, color: COLORS.white, mr: 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>A</Avatar>
                    <Typography variant="body2" sx={{ color: COLORS.primaryDark, fontWeight: 500, ml: 1 }}>Assistant</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: 'inherit' }}>{msg.text}</Typography>
                  </AccordionDetails>
                </Accordion>
              );
            }
            
            // Messages d'erreur
            if (msg.sender === 'error') {
              return (
                <Accordion key={msg.id} defaultExpanded={true} sx={{ mb: 1.5, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#ffeaea', color: COLORS.error }}>
                    <Avatar sx={{ bgcolor: COLORS.error, color: COLORS.white, mr: 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>E</Avatar>
                    <Typography variant="body2" sx={{ color: 'inherit', fontWeight: 500, ml: 1 }}>Erreur</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: 'inherit' }}>{msg.text}</Typography>
                  </AccordionDetails>
                </Accordion>
              );
            }
            
            // Messages système avec suggestions
            if (msg.sender === 'system' && msg.isSuggestion) {
              return (
                <Accordion key={msg.id} defaultExpanded={true} sx={{ mb: 1.5, ml: 2, boxShadow: '0 1px 4px #e3eafc', borderRadius: 2 }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#e6f7ef', color: '#218c5a' }}>
                    <Avatar sx={{ bgcolor: COLORS.accentGreen, color: COLORS.white, mr: 1, width: 32, height: 32, fontSize: '0.8rem', boxShadow: '0 1px 4px #e3eafc' }}>💡</Avatar>
                    <Typography variant="body2" sx={{ color: 'inherit', fontWeight: 500, ml: 1 }}>Suggestion</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', color: 'inherit' }}>{msg.text}</Typography>
                    {msg.suggestionDetails && (
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
            }
            
            // Par défaut, ne pas afficher (pour éviter les messages non reconnus)
            return null;
          })}
          <div ref={messagesEndRef} />
        </Box>
        
        {/* Bouton "Aller au bas" qui apparaît quand l'utilisateur a scrollé vers le haut */}
        {!autoScroll && (
          <Box sx={{ 
            position: 'relative', 
            display: 'flex', 
            justifyContent: 'center', 
            mb: 1 
          }}>
            <IconButton
              onClick={() => {
                setAutoScroll(true);
                scrollToBottom();
              }}
              sx={{
                position: 'absolute',
                bottom: 0,
                bgcolor: COLORS.accentBlue,
                color: COLORS.white,
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                '&:hover': { 
                  bgcolor: COLORS.primaryDark,
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.2s ease',
                zIndex: 10
              }}
              size="small"
            >
              <ArrowDownwardIcon />
            </IconButton>
          </Box>
        )}
        
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

      {/* Modal d'aperçu NC */}
      <Dialog 
        open={ncPreviewOpen} 
        onClose={() => setNcPreviewOpen(false)} 
        maxWidth="md" 
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            boxShadow: '0 8px 32px rgba(35,57,93,0.15)'
          }
        }}
      >
        <DialogTitle sx={{ 
          background: COLORS.gradientGreen, 
          color: COLORS.white, 
          fontWeight: 700,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            👁️ Aperçu Rapide - NC #{previewNCData?.id}
          </Box>
          <IconButton 
            onClick={() => setNcPreviewOpen(false)}
            sx={{ color: COLORS.white }}
            size="small"
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        
        <DialogContent sx={{ p: 3 }}>
          {previewLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}>
              <CircularProgress />
            </Box>
          ) : previewNCData ? (
            <div dangerouslySetInnerHTML={{ __html: previewNCData.htmlContent }} />
          ) : (
            <Typography>Aucune donnée disponible.</Typography>
          )}
        </DialogContent>
        
        <DialogActions sx={{ p: 2, background: COLORS.background }}>
          <Button 
            onClick={() => {
              if (previewNCData?.id) {
                window.open(apiService.getPdfUrl(previewNCData.id, previewNCData.conversationId || '', true), '_blank');
              }
            }}
            sx={{ 
              background: COLORS.accentGreen, 
              color: COLORS.white,
              '&:hover': { background: COLORS.primaryDark },
              mr: 1
            }}
          >
            📄 Télécharger PDF
          </Button>
          <Button 
            onClick={() => setNcPreviewOpen(false)} 
            sx={{ 
              background: COLORS.textGrey, 
              color: COLORS.white,
              '&:hover': { background: COLORS.primaryDark }
            }}
          >
            Fermer
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
export default ChatAssistant;
