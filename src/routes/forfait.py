from flask import Blueprint, request, jsonify
from kkiapay import Kkiapay
import os

forfait_bp = Blueprint("forfait_bp", __name__)

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

@forfait_bp.route("/forfait", methods=["POST"])
def buy_forfait():
    data = request.get_json()
    operator = data.get("operator")
    beneficiary_number = data.get("beneficiary_number")
    forfait_type = data.get("forfait_type")

    if not all([operator, beneficiary_number, forfait_type]):
        return jsonify({"status": "error", "message": "Données manquantes"}), 400

    # En mode simulation, on retourne directement un succès
    if SANDBOX_MODE:
        print(f"Simulation d'achat de forfait {forfait_type} chez {operator} pour {beneficiary_number}")
        return jsonify({
            "status": "success", 
            "message": f"Forfait {forfait_type} activé avec succès pour {beneficiary_number} !",
            "transaction_id": "FORFAIT_" + str(hash(f"{forfait_type}{beneficiary_number}"))[:8]
        }), 200
    
    # En mode production, ici on intégrerait la logique réelle avec l'API des opérateurs
    # via Kkiapay ou d'autres agrégateurs
    try:
        # Logique d'achat de forfait réel à implémenter
        return jsonify({
            "status": "success", 
            "message": f"Forfait {forfait_type} activé avec succès pour {beneficiary_number} !"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Erreur lors de l'achat de forfait : {str(e)}"
        }), 500


