from flask import Blueprint, request, jsonify
from kkiapay import Kkiapay
import os
from src.models.user import User, db
from src.models.account import Account, Transaction

forfait_bp = Blueprint("forfait", __name__)

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
    user_id = data.get("user_id")
    operator = data.get("operator")
    beneficiary_number = data.get("beneficiary_number")
    package_id = data.get("package_id")
    package_type = data.get("package_type")  # 'call' or 'internet'

    # Validation
    if not all([user_id, operator, beneficiary_number, package_id, package_type]):
        return jsonify({"message": "Tous les champs sont requis"}), 400

    # Vérifier l'utilisateur
    user = User.query.get_or_404(user_id)

    # Vérifier le compte source
    source_account = Account.query.filter_by(
        user_id=user_id,
        operator=operator
    ).first()

    if not source_account:
        return jsonify({"message": f"Compte {operator.upper()} non trouvé"}), 404

    # Définir les prix des forfaits
    package_prices = {
        1: 150, 2: 500, 3: 2000,  # Forfaits appel
        4: 100, 5: 500, 6: 2000   # Forfaits internet
    }

    package_names = {
        1: "Forfait Jour Appel", 2: "Forfait Semaine Appel", 3: "Forfait Mois Appel",
        4: "Forfait Jour Internet", 5: "Forfait Semaine Internet", 6: "Forfait Mois Internet"
    }

    price = package_prices.get(package_id)
    package_name = package_names.get(package_id)

    if not price:
        return jsonify({"message": "Forfait invalide"}), 400

    if source_account.balance < price:
        return jsonify({"message": "Solde insuffisant"}), 400

    # Effectuer l'achat
    source_account.balance -= price

    # Créer une transaction
    transaction = Transaction(
        user_id=user_id,
        account_id=source_account.id,
        type="forfait",
        description=f"{package_name} pour {beneficiary_number}",
        amount=-price,
        operator=operator
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"{package_name} acheté avec succès",
        "new_balance": source_account.balance
    }), 200
