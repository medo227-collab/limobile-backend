from flask import Blueprint, request, jsonify
from src.models.user import Account, Transaction, db

forfait_bp = Blueprint("forfait", __name__)

# Forfaits disponibles par opérateur - Mapping des IDs numériques aux forfaits
FORFAITS_MAP = {
    # Forfaits Appel
    1: {'id': 'forfait_appel_500', 'price': 150, 'name': 'Forfait Jour Appel', 'type': 'appel'},
    2: {'id': 'forfait_appel_1000', 'price': 500, 'name': 'Forfait Semaine Appel', 'type': 'appel'},
    3: {'id': 'forfait_appel_2000', 'price': 2000, 'name': 'Forfait Mois Appel', 'type': 'appel'},
    # Forfaits Internet
    4: {'id': 'forfait_internet_1gb', 'price': 100, 'name': 'Forfait Jour Internet', 'type': 'internet'},
    5: {'id': 'forfait_internet_5gb', 'price': 500, 'name': 'Forfait Semaine Internet', 'type': 'internet'},
    6: {'id': 'forfait_internet_25gb', 'price': 2000, 'name': 'Forfait Mois Internet', 'type': 'internet'},
}

# Forfaits disponibles par opérateur
FORFAITS = {
    'airtel': {
        'forfait_appel_500': {'price': 150, 'name': 'Forfait Jour Appel'},
        'forfait_appel_1000': {'price': 500, 'name': 'Forfait Semaine Appel'},
        'forfait_appel_2000': {'price': 2000, 'name': 'Forfait Mois Appel'},
        'forfait_internet_1gb': {'price': 100, 'name': 'Forfait Jour Internet'},
        'forfait_internet_5gb': {'price': 500, 'name': 'Forfait Semaine Internet'},
        'forfait_internet_25gb': {'price': 2000, 'name': 'Forfait Mois Internet'},
    },
    'moov': {
        'forfait_appel_500': {'price': 150, 'name': 'Forfait Jour Appel'},
        'forfait_appel_1000': {'price': 500, 'name': 'Forfait Semaine Appel'},
        'forfait_appel_2000': {'price': 2000, 'name': 'Forfait Mois Appel'},
        'forfait_internet_1gb': {'price': 100, 'name': 'Forfait Jour Internet'},
        'forfait_internet_5gb': {'price': 500, 'name': 'Forfait Semaine Internet'},
        'forfait_internet_25gb': {'price': 2000, 'name': 'Forfait Mois Internet'},
    },
    'zamani': {
        'forfait_appel_500': {'price': 150, 'name': 'Forfait Jour Appel'},
        'forfait_appel_1000': {'price': 500, 'name': 'Forfait Semaine Appel'},
        'forfait_appel_2000': {'price': 2000, 'name': 'Forfait Mois Appel'},
        'forfait_internet_1gb': {'price': 100, 'name': 'Forfait Jour Internet'},
        'forfait_internet_5gb': {'price': 500, 'name': 'Forfait Semaine Internet'},
        'forfait_internet_25gb': {'price': 2000, 'name': 'Forfait Mois Internet'},
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

        if not all([user_id, operator, package_id is not None]):
            return jsonify({"success": False, "message": "Données manquantes"}), 400

        # Vérifier que l'opérateur existe
        if operator not in FORFAITS:
            return jsonify({"success": False, "message": "Opérateur non supporté"}), 400

        # Mapper l'ID numérique au forfait texte
        if package_id not in FORFAITS_MAP:
            return jsonify({"success": False, "message": "Forfait non trouvé"}), 404

        forfait_info = FORFAITS_MAP[package_id]
        forfait_id = forfait_info['id']
        
        # Vérifier que le forfait existe pour cet opérateur
        if forfait_id not in FORFAITS[operator]:
            return jsonify({"success": False, "message": "Forfait non disponible pour cet opérateur"}), 404

        forfait = FORFAITS[operator][forfait_id]
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
