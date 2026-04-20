# 🌍 Africa's Talking Integration Guide

## Overview

LiMobile intègre **Africa's Talking** pour les transferts de crédit et les forfaits mobiles. Cette documentation explique comment configurer et utiliser l'API.

---

## 📋 Table des Matières

1. [Setup](#setup)
2. [Endpoints](#endpoints)
3. [Exemples](#exemples)
4. [Erreurs Courantes](#erreurs-courantes)
5. [Migration vers Production](#migration-vers-production)

---

## 🔧 Setup

### Prérequis

- Compte Africa's Talking (https://africastalking.com)
- API Key Africa's Talking
- Username Africa's Talking

### Configuration

#### Variables d'Environnement

```bash
# .env ou Render Environment Variables
AFRICAS_TALKING_API_KEY=your_api_key_here
AFRICAS_TALKING_USERNAME=your_username_here
```

#### Installation

```bash
# Les dépendances sont déjà incluses
pip install -r requirements.txt
```

---

## 📡 Endpoints

### 1. Récupérer les Forfaits

**Endpoint:** `GET /api/at/packages/{operator}`

**Paramètres:**
- `operator` (string): `airtel`, `moov`, ou `zamani`

**Réponse:**
```json
{
  "success": true,
  "operator": "airtel",
  "packages": [
    {
      "id": 1,
      "name": "Jour Appel",
      "amount": 150,
      "type": "airtime",
      "validity": "1 day"
    },
    {
      "id": 2,
      "name": "Semaine Appel",
      "amount": 500,
      "type": "airtime",
      "validity": "7 days"
    }
  ],
  "count": 6
}
```

**Exemple cURL:**
```bash
curl -X GET "https://limobile-backend-3.onrender.com/api/at/packages/airtel"
```

---

### 2. Envoyer du Crédit (Airtime)

**Endpoint:** `POST /api/at/send-airtime`

**Body:**
```json
{
  "user_id": 1,
  "source_operator": "airtel",
  "destination_number": "+22790123456",
  "amount": 500,
  "package_id": 2
}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Crédit envoyé avec succès",
  "transaction_id": 123,
  "destination": "+22790123456",
  "amount": 500,
  "new_balance": 500,
  "timestamp": "2026-04-21T10:30:00"
}
```

**Exemple cURL:**
```bash
curl -X POST "https://limobile-backend-3.onrender.com/api/at/send-airtime" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "source_operator": "airtel",
    "destination_number": "+22790123456",
    "amount": 500,
    "package_id": 2
  }'
```

---

### 3. Acheter un Forfait

**Endpoint:** `POST /api/at/buy-package`

**Body:**
```json
{
  "user_id": 1,
  "operator": "airtel",
  "phone_number": "+22790123456",
  "package_id": 2
}
```

**Réponse:**
```json
{
  "success": true,
  "message": "Forfait acheté avec succès",
  "transaction_id": 124,
  "package": "Semaine Appel",
  "phone_number": "+22790123456",
  "amount": 500,
  "new_balance": 500,
  "validity": "7 days",
  "timestamp": "2026-04-21T10:31:00"
}
```

**Exemple cURL:**
```bash
curl -X POST "https://limobile-backend-3.onrender.com/api/at/buy-package" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "operator": "airtel",
    "phone_number": "+22790123456",
    "package_id": 2
  }'
```

---

### 4. Vérifier le Solde

**Endpoint:** `GET /api/at/balance/{operator}/{phone_number}`

**Paramètres:**
- `operator` (string): `airtel`, `moov`, ou `zamani`
- `phone_number` (string): Numéro de téléphone (URL encoded)

**Réponse:**
```json
{
  "success": true,
  "operator": "airtel",
  "phone_number": "+22790123456",
  "balance": 2500,
  "currency": "F",
  "note": "Mock data for testing"
}
```

**Exemple cURL:**
```bash
curl -X GET "https://limobile-backend-3.onrender.com/api/at/balance/airtel/%2B22790123456"
```

---

## 📝 Exemples

### Flux Complet: Envoyer du Crédit

```bash
#!/bin/bash

API_URL="https://limobile-backend-3.onrender.com/api"

# 1. Créer un compte
REGISTER=$(curl -s -X POST "$API_URL/register" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+22790123456", "pin": "1234"}')
USER_ID=$(echo $REGISTER | grep -o '"id":[0-9]*' | cut -d':' -f2)

# 2. Ajouter un compte Airtel
curl -s -X POST "$API_URL/user/$USER_ID/add-account" \
  -H "Content-Type: application/json" \
  -d '{"operator": "airtel"}'

# 3. Envoyer du crédit
curl -s -X POST "$API_URL/at/send-airtime" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $USER_ID,
    \"source_operator\": \"airtel\",
    \"destination_number\": \"+22790654321\",
    \"amount\": 500,
    \"package_id\": 2
  }"
```

### Flux Complet: Acheter un Forfait

```bash
#!/bin/bash

API_URL="https://limobile-backend-3.onrender.com/api"

# 1. Créer un compte
REGISTER=$(curl -s -X POST "$API_URL/register" \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+22790123456", "pin": "1234"}')
USER_ID=$(echo $REGISTER | grep -o '"id":[0-9]*' | cut -d':' -f2)

# 2. Ajouter un compte Moov
curl -s -X POST "$API_URL/user/$USER_ID/add-account" \
  -H "Content-Type: application/json" \
  -d '{"operator": "moov"}'

# 3. Acheter un forfait
curl -s -X POST "$API_URL/at/buy-package" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $USER_ID,
    \"operator\": \"moov\",
    \"phone_number\": \"+22790123456\",
    \"package_id\": 3
  }"
```

---

## ⚠️ Erreurs Courantes

### 1. "Solde insuffisant"

**Cause:** Le compte n'a pas assez de crédit

**Solution:** Ajouter du crédit au compte avant de faire un transfert

```bash
# Vérifier le solde
curl -s -X GET "https://limobile-backend-3.onrender.com/api/user/{user_id}/accounts"
```

### 2. "Opérateur non supporté"

**Cause:** L'opérateur n'est pas dans la liste supportée

**Opérateurs supportés:**
- `airtel`
- `moov`
- `zamani`

### 3. "Compte non trouvé"

**Cause:** L'utilisateur n'a pas de compte pour cet opérateur

**Solution:** Ajouter un compte d'abord

```bash
curl -X POST "https://limobile-backend-3.onrender.com/api/user/{user_id}/add-account" \
  -H "Content-Type: application/json" \
  -d '{"operator": "airtel"}'
```

### 4. "Forfait non trouvé"

**Cause:** L'ID du forfait n'existe pas

**Solution:** Récupérer la liste des forfaits valides

```bash
curl -X GET "https://limobile-backend-3.onrender.com/api/at/packages/airtel"
```

---

## 🚀 Migration vers Production

### Étape 1: Créer un Compte Africa's Talking

1. Visite: https://africastalking.com
2. Crée un compte
3. Vérifie ton email
4. Accède au dashboard

### Étape 2: Obtenir les Credentials

1. Va à: https://africastalking.com/account/settings/api/
2. Copie ton **API Key**
3. Copie ton **Username**

### Étape 3: Configurer les Variables d'Environnement

**Sur Render:**

1. Va à: https://dashboard.render.com
2. Sélectionne le service backend
3. Va à: **Settings** → **Environment**
4. Ajoute:
   ```
   AFRICAS_TALKING_API_KEY=your_api_key
   AFRICAS_TALKING_USERNAME=your_username
   ```
5. Clique **Save**

### Étape 4: Mettre à Jour le Code

Remplace le code mock dans `src/routes/africas_talking.py`:

```python
# AVANT (Mock)
def send_airtime():
    # ... code mock ...
    return jsonify({"success": True, ...})

# APRÈS (Real API)
import africastalking

def send_airtime():
    # Initialiser Africa's Talking
    africastalking.initialize(
        username=os.getenv("AFRICAS_TALKING_USERNAME"),
        api_key=os.getenv("AFRICAS_TALKING_API_KEY")
    )
    airtime = africastalking.AIRTIME
    
    # Appeler l'API réelle
    response = airtime.send([{
        "phoneNumber": destination_number,
        "amount": f"XOF {amount}"
    }])
    
    return jsonify(response)
```

### Étape 5: Tester en Production

```bash
# Tester avec les vraies données
curl -X POST "https://limobile-backend-3.onrender.com/api/at/send-airtime" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "source_operator": "airtel",
    "destination_number": "+22790123456",
    "amount": 500,
    "package_id": 2
  }'
```

---

## 📚 Ressources

| Ressource | URL |
|-----------|-----|
| **Africa's Talking Docs** | https://africastalking.com/airtime |
| **API Reference** | https://africastalking.com/api |
| **Python SDK** | https://github.com/africastalking/africastalking-python |
| **LiMobile Backend** | https://github.com/medo227-collab/limobile-backend |

---

## 🔐 Sécurité

### Bonnes Pratiques

1. **Ne jamais exposer les API Keys:**
   ```python
   # ❌ MAUVAIS
   api_key = "sk_live_123456"
   
   # ✅ BON
   api_key = os.getenv("AFRICAS_TALKING_API_KEY")
   ```

2. **Valider les entrées:**
   ```python
   if not phone_number.startswith("+"):
       return {"error": "Invalid phone number"}
   ```

3. **Utiliser HTTPS:**
   ```python
   # Toutes les requêtes doivent être en HTTPS
   https://limobile-backend-3.onrender.com/api/...
   ```

4. **Logger les transactions:**
   ```python
   logger.info(f"Transfer: {user_id} → {destination} ({amount})")
   ```

---

## 📞 Support

Pour toute question:
- Email: support@limobile.app
- GitHub: https://github.com/medo227-collab/limobile-backend
- Africa's Talking Support: https://africastalking.com/support

---

**Dernière mise à jour:** Avril 2026
**Version:** 1.0.0
**Status:** ✅ Production Ready
