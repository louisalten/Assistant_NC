// Test pour simuler le comportement du frontend
async function testChatHistoryFrontend() {
  const ncId = 2;
  
  console.log(`🔍 Test de chargement de l'historique pour NC ${ncId}`);
  
  try {
    console.log('📞 Appel de l\'endpoint...');
    const response = await fetch(`http://127.0.0.1:8000/api/nonconformites/${ncId}/chat-history`);
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Réponse reçue:', data);
      
      if (data.messages && data.messages.length > 0) {
        console.log('📝 Messages trouvés:');
        data.messages.forEach((msg, index) => {
          console.log(`   ${index + 1}. [${msg.sender}] ${msg.content.substring(0, 60)}...`);
          console.log(`      ID: ${msg.message_id}, Type: ${msg.message_type}, Timestamp: ${msg.timestamp}`);
        });
        
        // Simuler la conversion des messages comme dans le frontend
        console.log('\n🔄 Conversion des messages comme dans le frontend:');
        const loadedMessages = data.messages.map(msg => ({
          id: msg.message_id,
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
        
        console.log('✅ Messages convertis:');
        loadedMessages.forEach((msg, index) => {
          console.log(`   ${index + 1}. [${msg.sender}] ${msg.text.substring(0, 60)}... (${msg.timestamp})`);
        });
        
      } else {
        console.log('ℹ️ Aucun message trouvé');
      }
    } else {
      console.error('❌ Erreur HTTP:', response.status);
      const error = await response.text();
      console.error('❌ Détails:', error);
    }
  } catch (error) {
    console.error('❌ Erreur réseau:', error);
  }
}

testChatHistoryFrontend();
