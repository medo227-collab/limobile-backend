"""
Africa's Talking Integration Module
Prêt pour intégration avec l'API réelle Africa's Talking
Pour le moment, utilise des données mock pour les tests
"""

from flask import Blueprint, request, jsonify
from src.models.user import Account, Transaction, db
import os

africas_talking_bp = Blueprint("africas_talking", __name__)

# Configuration Africa's Talking
AT_API_KEY = os.getenv("AFRICAS_TALKING_API_KEY", "mock_key_for_testing")
AT_USERNAME = os.getenv("AFRICAS_TALKING_USERNAME", "limobile")

# Forfaits réels Africa's Talking (Mock pour tests)
AFRICAS_TALKING_PACKAGES = {
    'airtel': [
        {'id': 1, 'name': 'Jour Appel', 'amount': 150, 'type': 'airtime', 'validity': '1 day'},
        {'id': 2, 'name': 'Semaine Appel', 'amount': 500, 'type': 'airtime', 'validity': '7 days'},
        {'id': 3, 'name': 'Mois Appel', 'amount': 2000, 'type': 'airtime', 'validity': '30 days'},
        {'id': 4, 'name': 'Jour Internet 1GB', 'amount': 100, 'type': 'data', 'validity': '1 day'},
        {'id': 5, 'name': 'Semaine Internet 5GB', 'amount': 500, 'type': 'data', 'validity': '7 days'},
        {'id': 6, 'name': 'Mois Internet 25GB', 'amount': 2000, 'type': 'data', 'validity': '30 days'},
    ],
    'moov': [
        {'id': 1, 'name': 'Jour Appel', 'amount': 150, 'type': 'airtime', 'validity': '1 day'},
        {'id': 2, 'name': 'Semaine Appel', 'amount': 500, 'type': 'airtime', 'validity': '7 days'},
        {'id': 3, 'name': 'Mois Appel', 'amount': 2000, 'type': 'airtime', 'validity': '30 days'},
        {'id': 4, 'name': 'Jour Internet 1GB', 'amount': 100, 'type': 'data', 'validity': '1 day'},
        {'id': 5, 'name': 'Semaine Internet 5GB', 'amount': 500, 'type': 'data', 'validity': '7 days'},
        {'id': 6, 'name': 'Mois Internet 25GB', 'amount': 2000, 'type': 'data', 'validity': '30 days'},
    ],
    'zamani': [
        {'id': 1, 'name': 'Jour Appel', 'amount': 150, 'type': 'airtime', 'validity': '1 day'},
        {'id': 2, 'name': 'Semaine Appel', 'amount': 500, 'type': 'airtime', 'validity': '7 days'},
        {'id': 3, 'name': 'Mois Appel', 'amount': 2000, 'type': 'airtime', 'validity': '30 days'},
        {'id': 4, 'name': 'Jour Internet 1GB', 'amount': 100, 'type': 'data', 'validity': '1 day'},
        {'id': 5, 'name': 'Semaine Internet 5GB', 'amount': 500, 'type': 'data', 'validity': '7 days'},
        {'id': 6, 'name': 'Mois Internet 25GB', 'amount': 2000, 'type': 'data', 'validity': '30 days'},
    ],
}

@africas_talking_bp.route("/at/packages/<operator>", methods=["GET"])
def get_packages(operator):
    """
    Récupérer les forfaits disponibles pour un opérateur
    Endpoint: GET /api/at/packages/{operator}
    """
    try:
        operator = operator.lower()
        
        if operator not in AFRICAS_TALKING_PACKAGES:
            return jsonify({
                "success": False,
                "message": f"Opérateur '{operator}' non supporté",
                "supported_operators": list(AFRICAS_TALKING_PACKAGES.keys())
            }), 400
        
        packages = AFRICAS_TALKING_PACKAGES[operator]
        
        return jsonify({
            "success": True,
            "operator": operator,
            "packages": packages,
            "count": len(packages)
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur: {str(e)}"
        }), 500


@africas_talking_bp.route("/at/send-airtime", methods=["POST"])
def send_airtime():
    """
    Envoyer du crédit (airtime) à un numéro
    Endpoint: POST /api/at/send-airtime
    
    Body:
    {
        "user_id": 1,
        "source_operator": "airtel",
        "destination_number": "+22790123456",
        "amount": 500,
        "package_id": 2
    }
    """
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        source_operator = data.get("source_operator", "").lower()
        destination_number = data.get("destination_number")
        amount = data.get("amount")
        package_id = data.get("package_id")
        
        # Validation
        if not all([user_id, source_operator, destination_number, amount]):
            return jsonify({
                "success": False,
                "message": "Données manquantes: user_id, source_operator, destination_number, amount"
            }), 400
        
        # Vérifier l'opérateur
        if source_operator not in AFRICAS_TALKING_PACKAGES:
            return jsonify({
                "success": False,
                "message": f"Opérateur '{source_operator}' non supporté"
            }), 400
        
        # Vérifier le compte source
        account = Account.query.filter_by(
            user_id=user_id,
            operator=source_operator
        ).first()
        
        if not account:
            return jsonify({
                "success": False,
                "message": f"Compte {source_operator} non trouvé pour l'utilisateur"
            }), 404
        
        # Vérifier le solde
        if account.balance < amount:
            return jsonify({
                "success": False,
                "message": f"Solde insuffisant. Solde: {account.balance} F, Montant: {amount} F"
            }), 400
        
        # Effectuer le transfert
        account.balance -= amount
        
        # Enregistrer la transaction
        transaction = Transaction(
            user_id=user_id,
            account_id=account.id,
            type='airtime_transfer',
            amount=-amount,
            description=f'Transfert de crédit vers {destination_number}',
            operator=source_operator,
            metadata={
                'destination': destination_number,
                'package_id': package_id,
                'provider': 'africas_talking'
            }
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Crédit envoyé avec succès",
            "transaction_id": transaction.id,
            "destination": destination_number,
            "amount": amount,
            "new_balance": account.balance,
            "timestamp": transaction.created_at.isoformat() if hasattr(transaction, 'created_at') else None
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erreur: {str(e)}"
        }), 500


@africas_talking_bp.route("/at/buy-package", methods=["POST"])
def buy_package():
    """
    Acheter un forfait (package)
    Endpoint: POST /api/at/buy-package
    
    Body:
    {
        "user_id": 1,
        "operator": "airtel",
        "phone_number": "+22790123456",
        "package_id": 2
    }
    """
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        operator = data.get("operator", "").lower()
        phone_number = data.get("phone_number")
        package_id = data.get("package_id")
        
        # Validation
        if not all([user_id, operator, phone_number, package_id is not None]):
            return jsonify({
                "success": False,
                "message": "Données manquantes: user_id, operator, phone_number, package_id"
            }), 400
        
        # Vérifier l'opérateur
        if operator not in AFRICAS_TALKING_PACKAGES:
            return jsonify({
                "success": False,
                "message": f"Opérateur '{operator}' non supporté"
            }), 400
        
        # Trouver le forfait
        packages = AFRICAS_TALKING_PACKAGES[operator]
        package = next((p for p in packages if p['id'] == package_id), None)
        
        if not package:
            return jsonify({
                "success": False,
                "message": f"Forfait {package_id} non trouvé pour {operator}"
            }), 404
        
        # Vérifier le compte
        account = Account.query.filter_by(
            user_id=user_id,
            operator=operator
        ).first()
        
        if not account:
            return jsonify({
                "success": False,
                "message": f"Compte {operator} non trouvé"
            }), 404
        
        # Vérifier le solde
        amount = package['amount']
        if account.balance < amount:
            return jsonify({
                "success": False,
                "message": f"Solde insuffisant. Solde: {account.balance} F, Montant: {amount} F"
            }), 400
        
        # Effectuer l'achat
        account.balance -= amount
        
        # Enregistrer la transaction
        transaction = Transaction(
            user_id=user_id,
            account_id=account.id,
            type='package_purchase',
            amount=-amount,
            description=f'Achat de {package["name"]}',
            operator=operator,
            metadata={
                'package_id': package_id,
                'package_name': package['name'],
                'phone_number': phone_number,
                'provider': 'africas_talking'
            }
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Forfait acheté avec succès",
            "transaction_id": transaction.id,
            "package": package['name'],
            "phone_number": phone_number,
            "amount": amount,
            "new_balance": account.balance,
            "validity": package['validity'],
            "timestamp": transaction.created_at.isoformat() if hasattr(transaction, 'created_at') else None
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Erreur: {str(e)}"
        }), 500


@africas_talking_bp.route("/at/balance/<operator>/<phone_number>", methods=["GET"])
def check_balance(operator, phone_number):
    """
    Vérifier le solde d'un numéro
    Endpoint: GET /api/at/balance/{operator}/{phone_number}
    """
    try:
        operator = operator.lower()
        
        if operator not in AFRICAS_TALKING_PACKAGES:
            return jsonify({
                "success": False,
                "message": f"Opérateur '{operator}' non supporté"
            }), 400
        
        # Mock: retourner un solde aléatoire
        import random
        mock_balance = random.randint(100, 5000)
        
        return jsonify({
            "success": True,
            "operator": operator,
            "phone_number": phone_number,
            "balance": mock_balance,
            "currency": "F",
            "note": "Mock data for testing"
        }), 200
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Erreur: {str(e)}"
        }), 500
