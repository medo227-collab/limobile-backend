from flask import Blueprint, request, jsonify
import random
import string

operator_api_bp = Blueprint("operator_api", __name__)

# ============ MOCK OPERATOR APIS ============
# Ces APIs simulent les vraies APIs des opérateurs (Airtel, Moov, Zamani)
# Format: Requête texte → Réponse texte

class OperatorAPIService:
    """Service pour communiquer avec les APIs texte des opérateurs"""
    
    @staticmethod
    def check_balance(phone_number, operator):
        """Vérifier le solde d'un numéro auprès d'un opérateur"""
        # Simulation d'une API texte
        # Format: "CHECK_BALANCE|+22790123456|airtel"
        # Réponse: "BALANCE|+22790123456|5000|XOF"
        
        try:
            balance = random.randint(1000, 50000)
            return {
                "success": True,
                "phone_number": phone_number,
                "operator": operator,
                "balance": balance,
                "currency": "XOF",
                "timestamp": "2026-03-16T09:30:00Z"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def transfer_credit(source_number, destination_number, amount, operator):
        """Effectuer un transfert de crédit"""
        # Format: "TRANSFER|+22790123456|+22790654321|1000|airtel"
        # Réponse: "TRANSFER_OK|TXN123456|+22790123456|+22790654321|1000"
        
        try:
            transaction_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            return {
                "success": True,
                "transaction_id": transaction_id,
                "source": source_number,
                "destination": destination_number,
                "amount": amount,
                "operator": operator,
                "status": "completed",
                "timestamp": "2026-03-16T09:30:00Z"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def buy_package(phone_number, package_code, operator):
        """Acheter un forfait"""
        # Format: "BUY_PACKAGE|+22790123456|FORFAIT_APPEL_500|airtel"
        # Réponse: "PACKAGE_OK|PKG123456|+22790123456|FORFAIT_APPEL_500|150"
        
        try:
            package_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            return {
                "success": True,
                "package_id": package_id,
                "phone_number": phone_number,
                "package_code": package_code,
                "operator": operator,
                "status": "activated",
                "timestamp": "2026-03-16T09:30:00Z"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_transaction_history(phone_number, operator, days=30):
        """Récupérer l'historique des transactions"""
        # Format: "GET_HISTORY|+22790123456|airtel|30"
        # Réponse: JSON array de transactions
        
        try:
            transactions = []
            for i in range(random.randint(5, 15)):
                transactions.append({
                    "id": f"TXN{i:06d}",
                    "type": random.choice(["transfer", "package", "recharge"]),
                    "amount": random.randint(100, 5000),
                    "date": f"2026-03-{random.randint(1,16):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z"
                })
            return {
                "success": True,
                "phone_number": phone_number,
                "operator": operator,
                "transactions": transactions
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# ============ API ENDPOINTS ============

@operator_api_bp.route("/check-balance", methods=["POST"])
def check_balance():
    """Vérifier le solde d'un numéro"""
    try:
        data = request.get_json()
        phone_number = data.get("phone_number")
        operator = data.get("operator")
        
        if not phone_number or not operator:
            return jsonify({"success": False, "message": "Données manquantes"}), 400
        
        result = OperatorAPIService.check_balance(phone_number, operator)
        return jsonify(result), 200 if result["success"] else 400
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@operator_api_bp.route("/transfer-credit", methods=["POST"])
def transfer_credit():
    """Effectuer un transfert de crédit"""
    try:
        data = request.get_json()
        source_number = data.get("source_number")
        destination_number = data.get("destination_number")
        amount = data.get("amount")
        operator = data.get("operator")
        
        if not all([source_number, destination_number, amount, operator]):
            return jsonify({"success": False, "message": "Données manquantes"}), 400
        
        result = OperatorAPIService.transfer_credit(source_number, destination_number, amount, operator)
        return jsonify(result), 200 if result["success"] else 400
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@operator_api_bp.route("/buy-package", methods=["POST"])
def buy_package():
    """Acheter un forfait auprès de l'opérateur"""
    try:
        data = request.get_json()
        phone_number = data.get("phone_number")
        package_code = data.get("package_code")
        operator = data.get("operator")
        
        if not all([phone_number, package_code, operator]):
            return jsonify({"success": False, "message": "Données manquantes"}), 400
        
        result = OperatorAPIService.buy_package(phone_number, package_code, operator)
        return jsonify(result), 200 if result["success"] else 400
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@operator_api_bp.route("/transaction-history", methods=["POST"])
def transaction_history():
    """Récupérer l'historique des transactions"""
    try:
        data = request.get_json()
        phone_number = data.get("phone_number")
        operator = data.get("operator")
        days = data.get("days", 30)
        
        if not phone_number or not operator:
            return jsonify({"success": False, "message": "Données manquantes"}), 400
        
        result = OperatorAPIService.get_transaction_history(phone_number, operator, days)
        return jsonify(result), 200 if result["success"] else 400
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
