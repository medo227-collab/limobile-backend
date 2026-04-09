from flask import Blueprint, request, jsonify
import os

kkiapay_bp = Blueprint("kkiapay_bp", __name__)

# Configuration Kkiapay (en mode sandbox pour les tests)
# En production, ces clés doivent être stockées dans des variables d'environnement
KKIAPAY_PUBLIC_KEY = os.getenv('KKIAPAY_PUBLIC_KEY', 'test_public_key')
KKIAPAY_PRIVATE_KEY = os.getenv('KKIAPAY_PRIVATE_KEY', 'test_private_key')
KKIAPAY_SECRET = os.getenv('KKIAPAY_SECRET', 'test_secret')
SANDBOX_MODE = os.getenv('KKIAPAY_SANDBOX', 'true').lower() == 'true'

# Initialisation du client Kkiapay (optionnel)
k = None
try:
    from kkiapay import Kkiapay
    k = Kkiapay(
        public_key=KKIAPAY_PUBLIC_KEY,
        private_key=KKIAPAY_PRIVATE_KEY,
        secret=KKIAPAY_SECRET,
        sandbox=SANDBOX_MODE
    )
except ImportError:
    print("⚠️  Kkiapay not installed - payment verification disabled")

@kkiapay_bp.route("/verify-transaction", methods=["POST"])
def verify_transaction():
    """Vérifie le statut d'une transaction Kkiapay"""
    if not k:
        return jsonify({
            "status": "error",
            "message": "Kkiapay not configured"
        }), 503
    
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
            "message": f"Erreur lors de la vérification: {str(e)}"
        }), 500

@kkiapay_bp.route("/health", methods=["GET"])
def health():
    """Vérifier la santé de l'intégration Kkiapay"""
    return jsonify({
        "status": "ok" if k else "not_configured",
        "kkiapay_available": k is not None
    }), 200
