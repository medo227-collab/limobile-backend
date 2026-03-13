import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request
from flask_cors import CORS
from src.models.user import db
from src.models.account import Account, Transaction
from src.routes.user import user_bp
from src.routes.transfer import transfer_bp
from src.routes.forfait import forfait_bp
from src.routes.kkiapay_service import kkiapay_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Activation de CORS pour permettre les requêtes cross-origin
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

# Enregistrer les blueprints API EN PREMIER (avant les routes statiques)
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(transfer_bp, url_prefix='/api')
app.register_blueprint(forfait_bp, url_prefix='/api')
app.register_blueprint(kkiapay_bp, url_prefix='/api/kkiapay')

# Route pour servir les fichiers statiques (doit être après les blueprints API)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    # Ne pas servir les fichiers statiques pour les routes API
    if path.startswith('api'):
        return "Not Found", 404
    
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    # Essayer de servir le fichier demandé
    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    
    # Sinon, servir index.html pour les routes React
    index_path = os.path.join(static_folder_path, 'index.html')
    if os.path.exists(index_path):
        return send_from_directory(static_folder_path, 'index.html')
    
    return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
