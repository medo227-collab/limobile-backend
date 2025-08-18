from flask import Blueprint, request, jsonify
from kkiapay import Kkiapay
import os

transfer_bp = Blueprint("transfer_bp", __name__)

# Configuration Kkiapay
KKIAPAY_PUBLIC_KEY = os.getenv('KKIAPAY_PUBLIC_KEY', 'test_public_key')
KKIAPAY_PRIVATE_KEY = os.getenv('KKIAPAY_PRIVATE_KEY', 'test_private_key')
KKIAPAY_SECRET = os.getenv('KKIAPAY_SECRET', 'test_secret')
SANDBOX_MODE = os.getenv('KKIAPAY_SANDBOX', 'true').lower() == 'true'

k = Kkiapay(
    public_key=KKIAPAY_PUBLIC_KEY,
    private_key=KKIAPAY_PRIVATE_KEY,
    secret=KKIAPAY_SECRET,
    sandbox=SANDBOX_MODE
)

@transfer_bp.route("/credit", methods=["POST"])
def transfer_credit():
    data = request.get_json()
    source_operator = data.get("source_operator")
    destination_number = data.get("destination_number")
    amount = data.get("amount")

    if not all([source_operator, destination_number, amount]):
        return jsonify({"status": "error", "message": "Données manquantes"}), 400

    # En mode simulation, on retourne directement un succès
    if SANDBOX_MODE:
        print(f"Simulation de transfert de {amount} F de {source_operator} vers {destination_number}")
        return jsonify({
            "status": "success", 
            "message": f"Transfert de {amount} F vers {destination_number} simulé avec succès !",
            "transaction_id": "SIMUL_" + str(hash(f"{amount}{destination_number}"))[:8]
        }), 200
    
    # En mode production, ici on intégrerait la logique réelle avec l'API des opérateurs
    # via Kkiapay ou d'autres agrégateurs
    try:
        # Logique de transfert réel à implémenter
        return jsonify({
            "status": "success", 
            "message": f"Transfert de {amount} F vers {destination_number} effectué avec succès !"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Erreur lors du transfert : {str(e)}"
        }), 500


