// Test script pour ajouter des messages de test pour la NC 2
const messages = [
  {
    message_id: "test-user-001",
    conversation_id: "conv-001",
    sender: "user",
    message_type: null,
    content: "Pouvez-vous m'aider avec l'analyse de cette non-conformité ?",
    html_content: null,
    step_context: "d0_initialisation",
    is_suggestion: "false"
  },
  {
    message_id: "test-bot-001",
    conversation_id: "conv-001",
    sender: "bot",
    message_type: "response",
    content: "Bien sûr ! Je peux vous aider à analyser cette non-conformité. Pouvez-vous me donner plus de détails sur le problème rencontré ?",
    html_content: null,
    step_context: "d0_initialisation",
    is_suggestion: "false"
  },
  {
    message_id: "test-user-002",
    conversation_id: "conv-002",
    sender: "user",
    message_type: null,
    content: "Le produit présente des défauts de surface après le processus de vernissage.",
    html_content: null,
    step_context: "d2_problem",
    is_suggestion: "false"
  },
  {
    message_id: "test-bot-002",
    conversation_id: "conv-002",
    sender: "bot",
    message_type: "response",
    content: "Les défauts de surface après vernissage peuvent avoir plusieurs causes. Avez-vous vérifié la température et l'humidité lors du processus ?",
    html_content: null,
    step_context: "d2_problem",
    is_suggestion: "false"
  }
];

async function addTestMessages() {
  const ncId = 2;
  
  for (const message of messages) {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/nonconformites/${ncId}/chat-history`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log(`✅ Message ajouté: ${message.message_id} - ${result.message_id}`);
      } else {
        console.error(`❌ Erreur pour ${message.message_id}:`, response.status);
      }
    } catch (error) {
      console.error(`❌ Erreur réseau pour ${message.message_id}:`, error);
    }
  }
  
  console.log('\n📖 Vérification de l\'historique:');
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/nonconformites/${ncId}/chat-history`);
    if (response.ok) {
      const data = await response.json();
      console.log(`✅ Historique récupéré: ${data.messages.length} messages`);
      data.messages.forEach((msg, index) => {
        console.log(`   ${index + 1}. [${msg.sender}] ${msg.content.substring(0, 50)}...`);
      });
    }
  } catch (error) {
    console.error('❌ Erreur lors de la récupération:', error);
  }
}

addTestMessages();
