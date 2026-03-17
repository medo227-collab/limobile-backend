from flask import Blueprint, jsonify, request
from src.models.user import User, Account, Transaction, db
from datetime import datetime

user_bp = Blueprint('user', __name__)

# ============ AUTHENTIFICATION ============

@user_bp.route('/register', methods=['POST'])
def register():
    """Enregistrer un nouvel utilisateur"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        pin = data.get('pin')

        if not phone_number or not pin:
            return jsonify({'success': False, 'message': 'Numéro et PIN requis'}), 400

        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(phone_number=phone_number).first()
        if existing_user:
            return jsonify({'success': False, 'message': 'Numéro déjà enregistré'}), 400

        # Créer le nouvel utilisateur
        user = User(phone_number=phone_number)
        user.set_pin(pin)
        db.session.add(user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Utilisateur enregistré',
            'user': user.to_dict(),
            'user_id': user.id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@user_bp.route('/login', methods=['POST'])
def login():
    """Connecter un utilisateur"""
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        pin = data.get('pin')

        if not phone_number or not pin:
            return jsonify({'success': False, 'message': 'Numéro et PIN requis'}), 400

        # Chercher l'utilisateur
        user = User.query.filter_by(phone_number=phone_number).first()
        if not user or not user.check_pin(pin):
            return jsonify({'success': False, 'message': 'Identifiants incorrects'}), 401

        return jsonify({
            'success': True,
            'message': 'Connexion réussie',
            'user': user.to_dict(),
            'user_id': user.id
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ============ GESTION DES COMPTES ============

@user_bp.route('/user/<int:user_id>/accounts', methods=['GET'])
def get_accounts(user_id):
    """Récupérer tous les comptes d'un utilisateur"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        accounts = Account.query.filter_by(user_id=user_id).all()
        return jsonify({
            'success': True,
            'user_id': user_id,
            'accounts': [acc.to_dict() for acc in accounts]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@user_bp.route('/user/<int:user_id>/add-account', methods=['POST'])
def add_account(user_id):
    """Ajouter un compte opérateur"""
    try:
        data = request.get_json()
        operator = data.get('operator')

        if not operator:
            return jsonify({'success': False, 'message': 'Opérateur requis'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        # Vérifier si le compte existe déjà
        existing = Account.query.filter_by(user_id=user_id, operator=operator).first()
        if existing:
            return jsonify({'success': False, 'message': f'Compte {operator} déjà existant'}), 400

        # Créer le nouveau compte
        account = Account(user_id=user_id, operator=operator, balance=1000.0)
        db.session.add(account)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Compte {operator} ajouté',
            'account': account.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============ TRANSACTIONS ============

@user_bp.route('/user/<int:user_id>/transactions', methods=['GET'])
def get_transactions(user_id):
    """Récupérer l'historique des transactions"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
        return jsonify({
            'success': True,
            'user_id': user_id,
            'transactions': [t.to_dict() for t in transactions]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@user_bp.route('/user/<int:user_id>/transfer', methods=['POST'])
def transfer(user_id):
    """Effectuer un transfert de crédit"""
    try:
        data = request.get_json()
        source_operator = data.get('source_operator')
        destination_number = data.get('destination_number')
        amount = data.get('amount')

        if not all([source_operator, destination_number, amount]):
            return jsonify({'success': False, 'message': 'Données manquantes'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        # Chercher le compte source
        account = Account.query.filter_by(user_id=user_id, operator=source_operator).first()
        if not account:
            return jsonify({'success': False, 'message': f'Compte {source_operator} non trouvé'}), 404

        # Vérifier le solde
        if account.balance < amount:
            return jsonify({'success': False, 'message': 'Solde insuffisant'}), 400

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
            'success': True,
            'message': 'Transfert effectué',
            'transaction_id': transaction.id,
            'new_balance': account.balance
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============ FORFAITS ============

@user_bp.route('/user/<int:user_id>/buy-forfait', methods=['POST'])
def buy_forfait(user_id):
    """Acheter un forfait"""
    try:
        data = request.get_json()
        operator = data.get('operator')
        package_id = data.get('package_id')
        amount = data.get('amount', 100)

        if not operator or not package_id:
            return jsonify({'success': False, 'message': 'Données manquantes'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'message': 'Utilisateur non trouvé'}), 404

        # Chercher le compte
        account = Account.query.filter_by(user_id=user_id, operator=operator).first()
        if not account:
            return jsonify({'success': False, 'message': f'Compte {operator} non trouvé'}), 404

        # Vérifier le solde
        if account.balance < amount:
            return jsonify({'success': False, 'message': 'Solde insuffisant'}), 400

        # Effectuer l'achat
        account.balance -= amount
        
        # Enregistrer la transaction
        transaction = Transaction(
            user_id=user_id,
            account_id=account.id,
            type='forfait',
            amount=-amount,
            description=f'Achat de forfait {package_id}',
            operator=operator
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Forfait acheté',
            'transaction_id': transaction.id,
            'new_balance': account.balance
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
