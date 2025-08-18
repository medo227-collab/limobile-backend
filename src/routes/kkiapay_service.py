from flask import Blueprint, request, jsonify
from kkiapay import Kkiapay
import os

kkiapay_bp = Blueprint("kkiapay_bp", __name__)

# Configuration Kkiapay (en mode sandbox pour les tests)
# En production, ces clés doivent être stockées dans des variables d'environnement
KKIAPAY_PUBLIC_KEY = os.getenv('KKIAPAY_PUBLIC_KEY', 'test_public_key')
KKIAPAY_PRIVATE_KEY = os.getenv('KKIAPAY_PRIVATE_KEY', 'test_private_key')
KKIAPAY_SECRET = os.getenv('KKIAPAY_SECRET', 'test_secret')
SANDBOX_MODE = os.getenv('KKIAPAY_SANDBOX', 'true').lower() == 'true'

# Initialisation du client Kkiapay
k = Kkiapay(
    public_key=KKIAPAY_PUBLIC_KEY,
    private_key=KKIAPAY_PRIVATE_KEY,
    secret=KKIAPAY_SECRET,
    sandbox=SANDBOX_MODE
)

@kkiapay_bp.route("/verify-transaction", methods=["POST"])
def verify_transaction():
    """Vérifie le statut d'une transaction Kkiapay"""
    data = request.get_json()
    transaction_id = data.get("transaction_id")
    
    if not transaction_id:
        return jsonify({"status": "error", "message": "ID de transaction manquant"}), 400
    
    try:
        # Vérification de la transaction via l'API Kkiapay
        transaction = k.verify_transaction(transaction_id)
        
        return jsonify({
            "status": "success",
            "transaction": {
                "id": transaction.transactionId,
                "status": transaction.status,
                "amount": transaction.amount,
                "type": transaction.type,
                "performed_at": transaction.performed_at,
                "source": transaction.source,
                "fees": transaction.fees,
                "country": transaction.country
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Erreur lors de la vérification : {str(e)}"
        }), 500

@kkiapay_bp.route("/initiate-payment", methods=["POST"])
def initiate_payment():
    """Initie un paiement via Kkiapay (retourne les paramètres pour le frontend)"""
    data = request.get_json()
    amount = data.get("amount")
    phone = data.get("phone")
    description = data.get("description", "Paiement LiMobile")
    
    if not amount:
        return jsonify({"status": "error", "message": "Montant manquant"}), 400
    
    try:
        # Retourne les paramètres nécessaires pour le widget Kkiapay côté frontend
        payment_params = {
            "public_key": KKIAPAY_PUBLIC_KEY,
            "amount": str(amount),
            "phone": phone,
            "sandbox": SANDBOX_MODE,
            "description": description
        }
        
        return jsonify({
            "status": "success",
            "payment_params": payment_params
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Erreur lors de l'initialisation : {str(e)}"
        }), 500

@kkiapay_bp.route("/webhook", methods=["POST"])
def webhook():
    """Endpoint pour recevoir les notifications webhook de Kkiapay"""
    data = request.get_json()
    
    # Log de la notification webhook
    print(f"Webhook reçu : {data}")
    
    # Ici, vous pouvez traiter les notifications de Kkiapay
    # Par exemple, mettre à jour le statut des transactions dans votre base de données
    
    transaction_id = data.get("transactionId")
    status = data.get("status")
    
    if transaction_id and status:
        # Traitement selon le statut
        if status == "SUCCESS":
            # Transaction réussie
            print(f"Transaction {transaction_id} réussie")
        elif status == "FAILED":
            # Transaction échouée
            print(f"Transaction {transaction_id} échouée")
    
    return jsonify({"status": "received"}), 200

@kkiapay_bp.route("/config", methods=["GET"])
def get_config():
    """Retourne la configuration publique pour le frontend"""
    return jsonify({
        "public_key": KKIAPAY_PUBLIC_KEY,
        "sandbox": SANDBOX_MODE
    }), 200

