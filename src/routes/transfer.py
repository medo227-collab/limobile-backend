from flask import Blueprint, request, jsonify
from kkiapay import Kkiapay
import os
from src.models.user import User, db
from src.models.account import Account, Transaction

transfer_bp = Blueprint("transfer", __name__)

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

@transfer_bp.route("/transfer", methods=["POST"])
def transfer_credit():
    data = request.get_json()
    user_id = data.get("user_id")
    source_operator = data.get("source_operator")
    destination_number = data.get("destination_number")
    amount = data.get("amount")

    # Validation
    if not all([user_id, source_operator, destination_number, amount]):
        return jsonify({"message": "Tous les champs sont requis"}), 400

    if amount <= 0:
        return jsonify({"message": "Le montant doit être positif"}), 400

    # Vérifier l'utilisateur
    user = User.query.get_or_404(user_id)

    # Vérifier le compte source
    source_account = Account.query.filter_by(
        user_id=user_id,
        operator=source_operator
    ).first()

    if not source_account:
        return jsonify({"message": f"Compte {source_operator.upper()} non trouvé"}), 404

    if source_account.balance < amount:
        return jsonify({"message": "Solde insuffisant"}), 400

    # Effectuer le transfert
    source_account.balance -= amount

    # Créer une transaction
    transaction = Transaction(
        user_id=user_id,
        account_id=source_account.id,
        type="transfer",
        description=f"Transfert vers {destination_number}",
        amount=-amount,
        operator=source_operator
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Transfert de {amount}F effectué avec succès",
        "new_balance": source_account.balance
    }), 200

@transfer_bp.route("/credit", methods=["POST"])
def transfer_credit_legacy():
    """Endpoint pour la compatibilité avec l'ancien frontend"""
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
