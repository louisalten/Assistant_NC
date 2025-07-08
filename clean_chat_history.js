// Script pour nettoyer l'historique de chat dans la base de données
async function cleanChatHistory() {
  console.log('🧹 Nettoyage de l\'historique de chat...');
  
  try {
    // Supprimer tous les messages de chat pour la NC 2
    const response = await fetch('http://127.0.0.1:8000/api/nonconformites/2/chat-history', {
      method: 'DELETE'
    });
    
    if (response.ok) {
      console.log('✅ Historique supprimé avec succès');
      
      // Vérifier que c'est bien vide
      const checkResponse = await fetch('http://127.0.0.1:8000/api/nonconformites/2/chat-history');
      if (checkResponse.ok) {
        const data = await checkResponse.json();
        console.log(`📊 Messages restants: ${data.messages.length}`);
      }
    } else {
      console.error('❌ Erreur lors de la suppression:', response.status);
    }
  } catch (error) {
    console.error('❌ Erreur:', error);
  }
}

cleanChatHistory();
