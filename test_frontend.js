// Test rapide frontend - à exécuter dans la console du navigateur
// Aller sur http://localhost:5174/resolution/2 et exécuter dans la console :

console.log('🧪 TEST FRONTEND - Système de Chat Persistant');

// Test 1: Vérifier le contexte Form8D
if (window.React && window.React.version) {
    console.log('✅ React détecté:', window.React.version);
} else {
    console.log('⚠️ React non détecté directement');
}

// Test 2: Vérifier l'API depuis le frontend
async function testAPIFromFrontend() {
    try {
        console.log('\n📡 Test API depuis le frontend...');
        
        // Test récupération historique
        const response = await fetch('http://localhost:8000/api/nonconformites/2/chat-history');
        const data = await response.json();
        console.log(`✅ Historique récupéré: ${data.messages.length} messages`);
        
        data.messages.forEach((msg, i) => {
            console.log(`   ${i+1}. [${msg.sender}] ${msg.content.substring(0, 50)}...`);
        });
        
        // Test création message simple
        console.log('\n💾 Test création message...');
        const newMessage = {
            message_id: 'frontend-test-' + Date.now(),
            sender: 'user',
            content: 'Test depuis le frontend - ' + new Date().toLocaleTimeString()
        };
        
        const createResponse = await fetch('http://localhost:8000/api/nonconformites/2/chat-history', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(newMessage)
        });
        
        if (createResponse.ok) {
            const result = await createResponse.json();
            console.log('✅ Message créé avec succès, ID:', result.id);
            
            // Revérifier l'historique
            const updatedResponse = await fetch('http://localhost:8000/api/nonconformites/2/chat-history');
            const updatedData = await updatedResponse.json();
            console.log(`✅ Historique mis à jour: ${updatedData.messages.length} messages`);
        } else {
            console.log('❌ Échec création:', createResponse.status);
            console.log('   Erreur:', await createResponse.text());
        }
        
    } catch (error) {
        console.log('❌ Erreur:', error.message);
    }
}

// Test 3: Vérifier les composants React dans la page
function checkReactComponents() {
    console.log('\n🔍 Vérification des composants React...');
    
    // Chercher le composant ChatAssistant
    const chatElements = document.querySelectorAll('[class*="chat"], [class*="Chat"]');
    console.log(`🗨️ Éléments chat trouvés: ${chatElements.length}`);
    
    // Chercher les boutons d'historique
    const historyButtons = document.querySelectorAll('button');
    const historyRelated = Array.from(historyButtons).filter(btn => 
        btn.textContent.toLowerCase().includes('historique') || 
        btn.textContent.toLowerCase().includes('chat')
    );
    console.log(`📊 Boutons historique trouvés: ${historyRelated.length}`);
    historyRelated.forEach((btn, i) => {
        console.log(`   ${i+1}. "${btn.textContent.trim()}"`);
    });
    
    // Chercher les input de chat
    const inputs = document.querySelectorAll('input[type="text"], textarea');
    const chatInputs = Array.from(inputs).filter(input => 
        input.placeholder && (
            input.placeholder.toLowerCase().includes('message') ||
            input.placeholder.toLowerCase().includes('chat') ||
            input.placeholder.toLowerCase().includes('question')
        )
    );
    console.log(`💬 Inputs de chat trouvés: ${chatInputs.length}`);
}

// Lancer tous les tests
console.log('🚀 Lancement des tests...');
testAPIFromFrontend();
checkReactComponents();

console.log('\n📋 INSTRUCTIONS:');
console.log('1. Ouvrir http://localhost:5174/resolution/2');
console.log('2. Copier-coller ce script dans la console');
console.log('3. Tester manuellement le chat assistant');
console.log('4. Vérifier que les boutons "Historique Chat" fonctionnent');
