from flask import Blueprint, request, jsonify
from src.models.user import Account, Transaction, db

forfait_bp = Blueprint("forfait", __name__)

# Forfaits disponibles par opérateur
FORFAITS = {
    'airtel': {
        'forfait_appel_500': {'price': 100, 'name': 'Forfait Appel 500'},
        'forfait_appel_1000': {'price': 200, 'name': 'Forfait Appel 1000'},
        'forfait_internet_1gb': {'price': 150, 'name': 'Forfait Internet 1GB'},
        'forfait_internet_5gb': {'price': 500, 'name': 'Forfait Internet 5GB'},
    },
    'moov': {
        'forfait_appel_500': {'price': 100, 'name': 'Forfait Appel 500'},
        'forfait_appel_1000': {'price': 200, 'name': 'Forfait Appel 1000'},
        'forfait_internet_1gb': {'price': 150, 'name': 'Forfait Internet 1GB'},
        'forfait_internet_5gb': {'price': 500, 'name': 'Forfait Internet 5GB'},
    },
    'zamani': {
        'forfait_appel_500': {'price': 100, 'name': 'Forfait Appel 500'},
        'forfait_appel_1000': {'price': 200, 'name': 'Forfait Appel 1000'},
        'forfait_internet_1gb': {'price': 150, 'name': 'Forfait Internet 1GB'},
        'forfait_internet_5gb': {'price': 500, 'name': 'Forfait Internet 5GB'},
    }
}

@forfait_bp.route("/forfait", methods=["POST"])
def buy_forfait():
    """Acheter un forfait"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        operator = data.get("operator")
        package_id = data.get("package_id")

        if not all([user_id, operator, package_id]):
            return jsonify({"success": False, "message": "Données manquantes"}), 400

        # Vérifier que l'opérateur existe
        if operator not in FORFAITS:
            return jsonify({"success": False, "message": "Opérateur non supporté"}), 400

        # Vérifier que le forfait existe
        if package_id not in FORFAITS[operator]:
            return jsonify({"success": False, "message": "Forfait non trouvé"}), 404

        forfait = FORFAITS[operator][package_id]
        amount = forfait['price']

        # Chercher le compte
        account = Account.query.filter_by(user_id=user_id, operator=operator).first()
        if not account:
            return jsonify({"success": False, "message": "Compte non trouvé"}), 404

        # Vérifier le solde
        if account.balance < amount:
            return jsonify({"success": False, "message": "Solde insuffisant"}), 400

        # Effectuer l'achat
        account.balance -= amount
        
        # Enregistrer la transaction
        transaction = Transaction(
            user_id=user_id,
            account_id=account.id,
            type='forfait',
            amount=-amount,
            description=f'Achat de {forfait["name"]}',
            operator=operator
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Forfait acheté",
            "transaction_id": transaction.id,
            "forfait": forfait['name'],
            "new_balance": account.balance
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


@forfait_bp.route("/forfaits/<operator>", methods=["GET"])
def get_forfaits(operator):
    """Récupérer les forfaits disponibles pour un opérateur"""
    try:
        if operator not in FORFAITS:
            return jsonify({"success": False, "message": "Opérateur non supporté"}), 400

        forfaits = FORFAITS[operator]
        return jsonify({
            "success": True,
            "operator": operator,
            "forfaits": forfaits
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
