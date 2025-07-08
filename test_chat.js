// Test script pour vérifier le système de chat persistant
const fetch = require('node-fetch');

async function testChatPersistence() {
    console.log('🧪 Test du système de chat persistant\n');
    
    // Test 1: Vérifier que nous pouvons créer un message
    console.log('📝 Test 1: Création d\'un message de chat...');
    try {
        const messageData = {
            message_id: 'test-frontend-001',
            conversation_id: 'test-conv-frontend',
            sender: 'user',
            content: 'Message de test depuis le frontend',
            step_context: 'd1'
        };
        
        const response = await fetch('http://127.0.0.1:8000/api/nonconformites/2/chat-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(messageData)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('✅ Message créé avec succès:', result.id);
        } else {
            console.log('❌ Erreur lors de la création:', response.status);
            const errorText = await response.text();
            console.log('   Détails:', errorText);
        }
    } catch (error) {
        console.log('❌ Exception:', error.message);
    }
    
    // Test 2: Vérifier que nous pouvons récupérer l'historique
    console.log('\n📖 Test 2: Récupération de l\'historique...');
    try {
        const response = await fetch('http://127.0.0.1:8000/api/nonconformites/2/chat-history');
        const data = await response.json();
        console.log(`✅ Historique récupéré: ${data.messages.length} messages`);
        
        data.messages.forEach((msg, index) => {
            console.log(`   ${index + 1}. [${msg.sender}] ${msg.content.substring(0, 50)}...`);
        });
    } catch (error) {
        console.log('❌ Erreur récupération:', error.message);
    }
    
    console.log('\n🎯 Tests terminés !');
}

testChatPersistence();
