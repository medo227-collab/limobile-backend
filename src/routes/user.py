from flask import Blueprint, jsonify, request
from src.models.user import User, db
from src.models.account import Account, Transaction

user_bp = Blueprint("user", __name__)

@user_bp.route("/register", methods=["POST"])
def register_user():
    data = request.json
    phone_number = data.get("phone_number")
    pin = data.get("pin")

    if not phone_number or not pin:
        return jsonify({"message": "Numéro de téléphone et code PIN sont requis"}), 400

    if len(pin) != 4 or not pin.isdigit():
        return jsonify({"message": "Le code PIN doit contenir exactement 4 chiffres"}), 400

    if User.query.filter_by(phone_number=phone_number).first():
        return jsonify({"message": "Ce numéro de téléphone est déjà enregistré"}), 409

    new_user = User(phone_number=phone_number)
    new_user.set_pin(pin)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "Utilisateur enregistré avec succès",
        "user_id": new_user.id,
        "user": new_user.to_dict()
    }), 201

@user_bp.route("/login", methods=["POST"])
def login_user():
    data = request.json
    phone_number = data.get("phone_number")
    pin = data.get("pin")

    if not phone_number or not pin:
        return jsonify({"message": "Numéro de téléphone et code PIN sont requis"}), 400

    user = User.query.filter_by(phone_number=phone_number).first()

    if user and user.check_pin(pin):
        return jsonify({
            "message": "Connexion réussie",
            "user_id": user.id,
            "user": user.to_dict()
        }), 200
    else:
        return jsonify({"message": "Numéro de téléphone ou code PIN incorrect"}), 401

@user_bp.route("/user/<int:user_id>/accounts", methods=["GET"])
def get_user_accounts(user_id):
    user = User.query.get_or_404(user_id)
    accounts = Account.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        "user_id": user_id,
        "accounts": [account.to_dict() for account in accounts]
    }), 200

@user_bp.route("/user/<int:user_id>/add-account", methods=["POST"])
def add_user_account(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    operator = data.get("operator")

    if not operator or operator not in ['airtel', 'moov', 'zamani']:
        return jsonify({"message": "Opérateur invalide"}), 400

    # Vérifier si l'utilisateur a déjà un compte pour cet opérateur
    existing_account = Account.query.filter_by(user_id=user_id, operator=operator).first()
    if existing_account:
        return jsonify({"message": f"Vous avez déjà un compte {operator.upper()}"}), 409

    # Créer un nouveau compte avec un solde initial
    new_account = Account(user_id=user_id, operator=operator, balance=1000)
    db.session.add(new_account)
    db.session.commit()

    return jsonify({
        "message": f"Compte {operator.upper()} créé avec succès",
        "account": new_account.to_dict()
    }), 201

@user_bp.route("/user/<int:user_id>/transactions", methods=["GET"])
def get_user_transactions(user_id):
    user = User.query.get_or_404(user_id)
    transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.date.desc()).all()
    
    return jsonify({
        "user_id": user_id,
        "transactions": [transaction.to_dict() for transaction in transactions]
    }), 200

@user_bp.route("/user/<int:user_id>/balance", methods=["GET"])
def get_user_balance(user_id):
    user = User.query.get_or_404(user_id)
    accounts = Account.query.filter_by(user_id=user_id).all()
    
    balances = {}
    for account in accounts:
        balances[account.operator] = account.balance
    
    return jsonify(balances), 200

@user_bp.route("/user/<int:user_id>/balance", methods=["PUT"])
def update_user_balance(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json

    for operator, balance in data.items():
        account = Account.query.filter_by(user_id=user_id, operator=operator).first()
        if account:
            account.balance = balance
    
    db.session.commit()
    return jsonify({"message": "Soldes mis à jour"}), 200
