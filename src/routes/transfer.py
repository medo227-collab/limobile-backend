from flask import Blueprint, request, jsonify
from src.models.user import Account, Transaction, db

transfer_bp = Blueprint("transfer", __name__)

@transfer_bp.route("/transfer", methods=["POST"])
def transfer_credit():
    """Transfert de crédit entre comptes"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        source_operator = data.get("source_operator")
        destination_number = data.get("destination_number")
        amount = data.get("amount")

        if not all([user_id, source_operator, destination_number, amount]):
            return jsonify({"success": False, "message": "Données manquantes"}), 400

        # Chercher le compte source
        account = Account.query.filter_by(user_id=user_id, operator=source_operator).first()
        if not account:
            return jsonify({"success": False, "message": "Compte non trouvé"}), 404

        # Vérifier le solde
        if account.balance < amount:
            return jsonify({"success": False, "message": "Solde insuffisant"}), 400

        # Effectuer le transfert
        account.balance -= amount
        
        # Enregistrer la transaction
        transaction = Transaction(
            user_id=user_id,
            account_id=account.id,
            type='transfer',
            amount=-amount,
            description=f'Transfert vers {destination_number}',
            operator=source_operator
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Transfert effectué",
            "transaction_id": transaction.id,
            "new_balance": account.balance
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
