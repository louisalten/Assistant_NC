// src/components/ChatHistoryViewer.jsx
import React, { useState, useEffect } from 'react';
import { COLORS } from '../colors';
import { Box, Paper, Avatar, Typography, Dialog, DialogTitle, DialogContent, DialogActions, Button, CircularProgress } from '@mui/material';
import ChatIcon from '@mui/icons-material/Chat';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ReactMarkdown from 'react-markdown';

function ChatHistoryViewer({ ncId, onClose, open }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [ncInfo, setNcInfo] = useState(null);

  useEffect(() => {
    if (open && ncId) {
      loadChatHistory();
      loadNCInfo();
    }
  }, [open, ncId]);

  const loadChatHistory = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/nonconformites/${ncId}/chat-history`);
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
      } else {
        console.warn('Aucun historique de chat trouvé pour cette NC');
        setMessages([]);
      }
    } catch (error) {
      console.error('Erreur lors du chargement de l\'historique de chat:', error);
      setMessages([]);
    } finally {
      setLoading(false);
    }
  };

  const loadNCInfo = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/nonconformites/${ncId}`);
      if (response.ok) {
        const data = await response.json();
        setNcInfo(data);
      }
    } catch (error) {
      console.error('Erreur lors du chargement des infos NC:', error);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getMessageIcon = (sender) => {
    switch (sender) {
      case 'user':
        return <PersonIcon sx={{ color: COLORS.white }} />;
      case 'bot':
        return <SmartToyIcon sx={{ color: COLORS.white }} />;
      default:
        return <ChatIcon sx={{ color: COLORS.white }} />;
    }
  };

  const getMessageColor = (sender) => {
    switch (sender) {
      case 'user':
        return COLORS.primaryBlue;
      case 'bot':
        return COLORS.accentGreen;
      default:
        return COLORS.textGrey;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ 
        background: COLORS.gradientGreen, 
        color: COLORS.white, 
        fontWeight: 700 
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ChatIcon />
          Historique de Chat - NC #{ncId}
        </Box>
        {ncInfo && (
          <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.8)', mt: 1 }}>
            {ncInfo.d0_initialisation?.referenceNC} - {ncInfo.d0_initialisation?.descriptionInitiale?.substring(0, 100)}...
          </Typography>
        )}
      </DialogTitle>
      
      <DialogContent sx={{ p: 0 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}>
            <CircularProgress />
          </Box>
        ) : messages.length === 0 ? (
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center', 
            height: 200,
            color: COLORS.textGrey 
          }}>
            <ChatIcon sx={{ fontSize: 48, mb: 2, opacity: 0.5 }} />
            <Typography variant="h6">Aucun historique de chat</Typography>
            <Typography variant="body2">Cette non-conformité n'a pas encore d'historique de chat.</Typography>
          </Box>
        ) : (
          <Box sx={{ 
            maxHeight: 500, 
            overflowY: 'auto', 
            p: 2,
            background: COLORS.background 
          }}>
            {messages.map((message, index) => (
              <Paper
                key={message.id}
                sx={{
                  mb: 2,
                  p: 2,
                  backgroundColor: COLORS.white,
                  borderRadius: 2,
                  boxShadow: '0 2px 8px rgba(35,57,93,0.08)'
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                  <Avatar sx={{ 
                    bgcolor: getMessageColor(message.sender),
                    width: 36,
                    height: 36
                  }}>
                    {getMessageIcon(message.sender)}
                  </Avatar>
                  
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography 
                        variant="subtitle2" 
                        sx={{ 
                          fontWeight: 600,
                          color: getMessageColor(message.sender),
                          textTransform: 'capitalize'
                        }}
                      >
                        {message.sender === 'user' ? 'Utilisateur' : 
                         message.sender === 'bot' ? 'Assistant' : message.sender}
                        {message.message_type && (
                          <Typography component="span" variant="caption" sx={{ 
                            ml: 1, 
                            px: 1, 
                            py: 0.25, 
                            backgroundColor: 'rgba(0,0,0,0.1)', 
                            borderRadius: 1,
                            fontSize: '0.7rem'
                          }}>
                            {message.message_type}
                          </Typography>
                        )}
                      </Typography>
                      <Typography variant="caption" sx={{ color: COLORS.textGrey }}>
                        {formatTimestamp(message.timestamp)}
                      </Typography>
                    </Box>
                    
                    <Box sx={{ 
                      backgroundColor: message.sender === 'user' ? 'rgba(35,57,93,0.05)' : 'rgba(46,204,113,0.05)',
                      borderRadius: 1,
                      p: 1.5
                    }}>
                      {message.html_content ? (
                        <div dangerouslySetInnerHTML={{ __html: message.html_content }} />
                      ) : (
                        <ReactMarkdown
                          components={{
                            p: ({ children }) => <Typography variant="body2" sx={{ mb: 1, '&:last-child': { mb: 0 } }}>{children}</Typography>,
                            strong: ({ children }) => <Typography component="span" sx={{ fontWeight: 700 }}>{children}</Typography>,
                            em: ({ children }) => <Typography component="span" sx={{ fontStyle: 'italic' }}>{children}</Typography>
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      )}
                    </Box>
                    
                    {message.step_context && (
                      <Typography variant="caption" sx={{ 
                        display: 'block', 
                        mt: 1, 
                        color: COLORS.textGrey,
                        fontStyle: 'italic'
                      }}>
                        Contexte : Étape {message.step_context.toUpperCase()}
                      </Typography>
                    )}
                  </Box>
                </Box>
              </Paper>
            ))}
          </Box>
        )}
      </DialogContent>
      
      <DialogActions sx={{ p: 2, background: COLORS.background }}>
        <Button 
          onClick={onClose} 
          sx={{ 
            background: COLORS.textGreen, 
            color: COLORS.white,
            '&:hover': { background: COLORS.primaryDark }
          }}
        >
          Fermer
        </Button>
      </DialogActions>
    </Dialog>
  );
}

export default ChatHistoryViewer;
