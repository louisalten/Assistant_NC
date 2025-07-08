#!/usr/bin/env python3
# Test simple et direct du système de chat persistant

import requests
import json

def test_complete_chat_system():
    """Test complet : création NC, ajout messages, récupération historique"""
    
    print("🧪 TEST COMPLET DU SYSTÈME DE CHAT PERSISTANT")
    print("=" * 60)
    
    # 1. Vérifier que l'API est accessible
    print("\n1️⃣ Vérification de l'API...")
    try:
        response = requests.get('http://localhost:8000/api/nonconformites')
        if response.status_code == 200:
            ncs = response.json()
            print(f"✅ API accessible - {len(ncs)} NC trouvées")
            if ncs:
                nc_id = ncs[0]['id']
                print(f"   Utilisation de la NC #{nc_id}")
            else:
                print("❌ Aucune NC trouvée - test impossible")
                return
        else:
            print(f"❌ API non accessible (Status: {response.status_code})")
            return
    except Exception as e:
        print(f"❌ Erreur connexion API: {e}")
        return
    
    # 2. Test de création de message
    print(f"\n2️⃣ Test création de message pour NC #{nc_id}...")
    message_data = {
        'message_id': 'test-msg-001',
        'sender': 'user',
        'content': 'Message de test - système fonctionne !',
        'step_context': 'd1'
    }
    
    try:
        response = requests.post(
            f'http://localhost:8000/api/nonconformites/{nc_id}/chat-history',
            json=message_data
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Message créé (ID: {result['id']})")
        else:
            print(f"❌ Échec création message (Status: {response.status_code})")
            print(f"   Erreur: {response.text}")
    except Exception as e:
        print(f"❌ Exception création: {e}")
    
    # 3. Test de récupération d'historique
    print(f"\n3️⃣ Test récupération historique pour NC #{nc_id}...")
    try:
        response = requests.get(f'http://localhost:8000/api/nonconformites/{nc_id}/chat-history')
        if response.status_code == 200:
            data = response.json()
            messages = data['messages']
            print(f"✅ Historique récupéré - {len(messages)} messages")
            
            for i, msg in enumerate(messages[-3:], 1):  # Afficher les 3 derniers
                print(f"   Message {i}: [{msg['sender']}] {msg['content'][:50]}...")
        else:
            print(f"❌ Échec récupération (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Exception récupération: {e}")
    
    # 4. Test de l'endpoint de sauvegarde de conversation
    print(f"\n4️⃣ Test sauvegarde conversation...")
    conversation_data = [
        {
            'id': 'msg-conv-001',
            'sender': 'user',
            'text': 'Question de test',
            'stepContext': 'd2'
        },
        {
            'id': 'msg-conv-002', 
            'sender': 'bot',
            'text': 'Réponse de test',
            'stepContext': 'd2'
        }
    ]
    
    try:
        response = requests.post(
            f'http://localhost:8000/api/nonconformites/{nc_id}/chat-history/bulk',
            json=conversation_data
        )
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Conversation sauvegardée ({result.get('saved_messages', 0)} messages)")
        else:
            print(f"❌ Échec sauvegarde conversation (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Exception sauvegarde: {e}")
    
    # 5. Vérification finale
    print(f"\n5️⃣ Vérification finale...")
    try:
        response = requests.get(f'http://localhost:8000/api/nonconformites/{nc_id}/chat-history')
        if response.status_code == 200:
            data = response.json()
            total_messages = len(data['messages'])
            print(f"✅ Total final: {total_messages} messages dans l'historique")
            
            # Afficher les types de messages
            senders = {}
            for msg in data['messages']:
                sender = msg['sender']
                senders[sender] = senders.get(sender, 0) + 1
            
            print("   Répartition:")
            for sender, count in senders.items():
                print(f"     {sender}: {count} messages")
                
        else:
            print(f"❌ Échec vérification finale")
    except Exception as e:
        print(f"❌ Exception vérification: {e}")
    
    print(f"\n🎯 TEST TERMINÉ")
    print("=" * 60)
    
    # 6. Instructions pour le frontend
    print(f"\n📋 INSTRUCTIONS POUR TESTER LE FRONTEND:")
    print(f"1. Ouvrir http://localhost:5174")
    print(f"2. Aller sur la NC #{nc_id} (/resolution/{nc_id})")
    print(f"3. Utiliser le chat assistant")
    print(f"4. Vérifier que l'historique se charge automatiquement")
    print(f"5. Utiliser le bouton 'Historique Chat' pour voir tous les messages")

if __name__ == "__main__":
    test_complete_chat_system()
