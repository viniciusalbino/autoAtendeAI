# src/main.py
import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
from sqlalchemy import text
from src.database import db

# Adiciona o diretório pai ao sys.path - NÃO ALTERE!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

load_dotenv() # Carrega variáveis do .env

# Configuração do logging
def setup_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/backend.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Backend startup')

app = Flask(__name__)
setup_logging(app)

# Configuração do CORS
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('ALLOWED_ORIGINS', '*').split(','),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuração do Banco de Dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')
app.config['JSON_SORT_KEYS'] = False  # Mantém a ordem das chaves no JSON

# Inicializa o SQLAlchemy com a app
db.init_app(app)

# Importar modelos e rotas
from src.models import Dealership, Vehicle
from src.routes.whatsapp import whatsapp_bp

# Registrar Blueprints
app.register_blueprint(whatsapp_bp, url_prefix='/whatsapp')

# Error handlers
@app.errorhandler(HTTPException)
def handle_exception(e):
    response = {
        "code": e.code,
        "name": e.name,
        "description": e.description,
    }
    return jsonify(response), e.code

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    app.logger.error(f"Unexpected error: {str(e)}")
    response = {
        "code": 500,
        "name": "Internal Server Error",
        "description": "An unexpected error occurred.",
    }
    return jsonify(response), 500

@app.route('/health')
def health_check():
    try:
        # Testa a conexão com o banco de dados usando text()
        db.session.execute(text('SELECT 1'))
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        })
    except Exception as e:
        app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/')
def hello():
    return jsonify({
        "message": "Backend do Agente de Concessionária está no ar!",
        "version": "1.0.0",
        "status": "operational"
    })

@app.route('/debug/vehicles')
def debug_vehicles():
    try:
        vehicles = Vehicle.query.all()
        return jsonify({
            "status": "success",
            "count": len(vehicles),
            "vehicles": [vehicle.to_dict() for vehicle in vehicles]
        })
    except Exception as e:
        app.logger.error(f"Error fetching vehicles: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def init_db():
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created successfully")

if __name__ == '__main__':
    init_db()
    # Para desenvolvimento, escute em todas as interfaces
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5001)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )

