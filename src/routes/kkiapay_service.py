from flask import Blueprint, jsonify, request

kkiapay_bp = Blueprint("kkiapay", __name__)

@kkiapay_bp.route("/payment", methods=["POST"])
def kkiapay_payment():
    return jsonify({"message": "Paiement traité", "status": "success"}), 200

@kkiapay_bp.route("/callback", methods=["POST"])
def kkiapay_callback():
    return jsonify({"message": "Callback reçu"}), 200
