// Test simple du streaming avec un message court
async function testStreaming() {
  console.log('🧪 Test de streaming...');
  
  const payload = {
    query: "Bonjour",
    form_data: {},
    current_section_data: {},
    current_section_name: "d0_initialisation",
    mode: "CHAT",
    model_key: "dengcao_qwen3_4b",
    context_only: false
  };

  try {
    const response = await fetch('http://127.0.0.1:8000/query_with_context', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    console.log('📡 Réponse reçue:', response.status, response.ok);
    console.log('📡 Headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ Erreur:', errorText);
      return;
    }

    if (!response.body) {
      console.error('❌ Pas de body dans la réponse');
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let chunkCount = 0;

    while (true) {
      const { value, done } = await reader.read();
      
      if (done) {
        console.log('✅ Stream terminé');
        break;
      }

      chunkCount++;
      buffer += decoder.decode(value, { stream: true });
      console.log(`📦 Chunk ${chunkCount}:`, buffer.substring(Math.max(0, buffer.length - 100)));

      // Traiter les lignes complètes
      const lines = buffer.split('\n');
      buffer = lines.pop() || ''; // Garder la dernière ligne incomplète

      for (const line of lines) {
        if (line.trim()) {
          try {
            const data = JSON.parse(line);
            console.log('📝 Données parsées:', {
              hasResponse: !!data.response,
              responseLength: data.response ? data.response.length : 0,
              done: data.done,
              hasSources: !!data.sources
            });
          } catch (e) {
            console.log('⚠️ Ligne non-JSON:', line.substring(0, 50));
          }
        }
      }
    }

  } catch (error) {
    console.error('❌ Erreur de test:', error);
  }
}

testStreaming();
