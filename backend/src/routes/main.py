from flask import Blueprint, jsonify, request, current_app
from src.database import db
from src.models import Vehicle, Dealership, User, Plan
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
import pandas as pd
import io
import logging
import os
from src.ai_processor import process_message_with_ai
import traceback
import requests
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Api, Resource, fields, Namespace

main_bp = Blueprint('main', __name__)
api = Api(main_bp, version='1.0', title='Auto Atende AI API',
          description='API para sistema de atendimento automatizado via WhatsApp para concessionárias')

# Namespaces
auth_ns = Namespace('auth', description='Operações de autenticação')
dealership_ns = Namespace('dealerships', description='Operações de concessionárias')
vehicle_ns = Namespace('vehicles', description='Operações de veículos')

api.add_namespace(auth_ns)
api.add_namespace(dealership_ns)
api.add_namespace(vehicle_ns)

# Models for Swagger
user_model = api.model('User', {
    'id': fields.Integer(readonly=True),
    'email': fields.String(required=True, description='Email do usuário'),
    'active': fields.Boolean(description='Status do usuário'),
    'dealership_id': fields.Integer(description='ID da concessionária associada'),
    'created_at': fields.DateTime(readonly=True)
})

user_registration = api.model('UserRegistration', {
    'email': fields.String(required=True, description='Email do usuário'),
    'password': fields.String(required=True, description='Senha do usuário')
})

dealership_model = api.model('Dealership', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True, description='Nome da concessionária'),
    'whatsapp_number': fields.String(required=True, description='Número do WhatsApp'),
    'email': fields.String(required=True, description='Email da concessionária'),
    'cnpj': fields.String(required=True, description='CNPJ da concessionária'),
    'address': fields.String(description='Endereço'),
    'city': fields.String(description='Cidade'),
    'state': fields.String(description='Estado'),
    'phone': fields.String(description='Telefone'),
    'website': fields.String(description='Website'),
    'active': fields.Boolean(description='Status da concessionária')
})

vehicle_model = api.model('Vehicle', {
    'id': fields.Integer(readonly=True),
    'dealership_id': fields.Integer(required=True, description='ID da concessionária'),
    'marca': fields.String(required=True, description='Marca do veículo'),
    'modelo': fields.String(required=True, description='Modelo do veículo'),
    'versao': fields.String(description='Versão do veículo'),
    'ano_fabricacao': fields.Integer(description='Ano de fabricação'),
    'ano_modelo': fields.Integer(description='Ano do modelo'),
    'quilometragem': fields.Integer(description='Quilometragem'),
    'estado': fields.String(description='Estado do veículo (Novo/Usado)'),
    'cambio': fields.String(description='Tipo de câmbio'),
    'combustivel': fields.String(description='Tipo de combustível'),
    'motor': fields.String(description='Motor'),
    'potencia': fields.String(description='Potência'),
    'final_placa': fields.String(description='Final da placa'),
    'cor': fields.String(description='Cor'),
    'preco': fields.Float(description='Preço'),
    'preco_promocional': fields.Float(description='Preço promocional'),
    'destaque': fields.Boolean(description='Veículo em destaque'),
    'vendido': fields.Boolean(description='Status de venda')
})

# JWT Setup
jwt = JWTManager()

def init_jwt(app):
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'super-secret')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=int(os.getenv('JWT_EXPIRATION', '1').replace('d','')))
    jwt.init_app(app)

# Auth Routes
@auth_ns.route('/register')
class UserRegistration(Resource):
    @auth_ns.expect(user_registration)
    @auth_ns.response(201, 'User registered successfully')
    @auth_ns.response(400, 'Invalid input')
    @auth_ns.response(409, 'Email already registered')
    def post(self):
        """Register a new user"""
        try:
            data = request.get_json()
            current_app.logger.debug(f"Received registration data: {data}")
            if not data or 'email' not in data or 'password' not in data:
                current_app.logger.warning("Missing email or password in registration request")
                return {'error': 'Email and password are required'}, 400
            email = data['email']
            password = data['password']
            if User.query.filter_by(email=email).first():
                current_app.logger.warning(f"Email {email} already registered")
                return {'error': 'Email already registered'}, 409
            user = User(email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f"User {email} registered successfully")
            return {'message': 'User registered successfully'}, 201
        except Exception as e:
            current_app.logger.error(f"Error during registration: {str(e)}")
            db.session.rollback()
            return {'error': 'Internal server error'}, 500

@auth_ns.route('/login')
class UserLogin(Resource):
    @auth_ns.expect(api.model('UserLogin', {
        'email': fields.String(required=True, description='Email do usuário'),
        'password': fields.String(required=True, description='Senha do usuário')
    }))
    @auth_ns.response(200, 'Login successful')
    @auth_ns.response(401, 'Invalid credentials')
    def post(self):
        """Login user and return JWT token"""
        try:
            data = request.get_json()
            current_app.logger.debug(f"Received login data for email: {data.get('email')}")
            
            if not data or 'email' not in data or 'password' not in data:
                current_app.logger.warning("Missing email or password in login request")
                return {'error': 'Email and password are required'}, 400
                
            user = User.query.filter_by(email=data['email']).first()
            
            if not user or not user.check_password(data['password']):
                current_app.logger.warning(f"Failed login attempt for email: {data.get('email')}")
                return {'error': 'Invalid email or password'}, 401
                
            if not user.active:
                current_app.logger.warning(f"Login attempt for inactive user: {data.get('email')}")
                return {'error': 'Account is inactive'}, 401
            
            # Create access token
            access_token = create_access_token(identity=user.id)
            
            current_app.logger.info(f"User {user.email} logged in successfully")
            return {
                'access_token': access_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'dealership_id': user.dealership_id
                }
            }, 200
            
        except Exception as e:
            current_app.logger.error(f"Error during login: {str(e)}")
            return {'error': 'Internal server error'}, 500

# Dealership Routes
@dealership_ns.route('/')
class DealershipList(Resource):
    @dealership_ns.marshal_list_with(dealership_model)
    def get(self):
        """List all active dealerships"""
        try:
            dealerships = Dealership.query.filter_by(active=True).all()
            return dealerships
        except Exception as e:
            current_app.logger.error(f"Error fetching dealerships: {str(e)}")
            return {'error': 'Internal server error'}, 500

    @dealership_ns.expect(dealership_model)
    @dealership_ns.marshal_with(dealership_model, code=201)
    def post(self):
        """Create a new dealership"""
        try:
            data = request.get_json()
            required_fields = ['name', 'whatsapp_number', 'email', 'cnpj']
            
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400
            
            if Dealership.query.filter_by(cnpj=data['cnpj']).first():
                return {'error': 'CNPJ already registered'}, 409
            
            dealership = Dealership(**data)
            db.session.add(dealership)
            db.session.commit()
            
            return dealership, 201
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating dealership: {str(e)}")
            return {'error': 'Internal server error'}, 500

# Vehicle Routes
@vehicle_ns.route('/')
class VehicleList(Resource):
    @vehicle_ns.marshal_list_with(vehicle_model)
    def get(self):
        """List all vehicles with optional filters"""
        try:
            dealership_id = request.args.get('dealership_id', type=int)
            if not dealership_id:
                return {'error': 'dealership_id is required'}, 400

            marca = request.args.get('marca')
            modelo = request.args.get('modelo')
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            estado = request.args.get('estado')
            cambio = request.args.get('cambio')
            combustivel = request.args.get('combustivel')
            final_placa = request.args.get('final_placa')
            destaque = request.args.get('destaque', type=bool)
            
            query = Vehicle.query.filter_by(dealership_id=dealership_id, vendido=False)
            
            if marca:
                query = query.filter(Vehicle.marca.ilike(f'%{marca}%'))
            if modelo:
                query = query.filter(Vehicle.modelo.ilike(f'%{modelo}%'))
            if min_price is not None:
                query = query.filter(Vehicle.preco >= min_price)
            if max_price is not None:
                query = query.filter(Vehicle.preco <= max_price)
            if estado:
                query = query.filter(Vehicle.estado == estado)
            if cambio:
                query = query.filter(Vehicle.cambio == cambio)
            if combustivel:
                query = query.filter(Vehicle.combustivel == combustivel)
            if final_placa:
                query = query.filter(Vehicle.final_placa == final_placa)
            if destaque:
                query = query.filter(
                    and_(
                        Vehicle.destaque == True,
                        or_(
                            Vehicle.destaque_ate == None,
                            Vehicle.destaque_ate > datetime.utcnow()
                        )
                    )
                )
            
            vehicles = query.all()
            return vehicles
            
        except Exception as e:
            current_app.logger.error(f"Error fetching vehicles: {str(e)}")
            return {'error': 'Internal server error'}, 500

    @vehicle_ns.expect(vehicle_model)
    @vehicle_ns.marshal_with(vehicle_model, code=201)
    def post(self):
        """Create a new vehicle"""
        try:
            data = request.get_json()
            required_fields = ['dealership_id', 'marca', 'modelo']
            
            for field in required_fields:
                if field not in data:
                    return {'error': f'Missing required field: {field}'}, 400
            
            dealership = Dealership.query.get(data['dealership_id'])
            if not dealership:
                return {'error': 'Dealership not found'}, 404
            
            vehicle = Vehicle(**data)
            db.session.add(vehicle)
            db.session.commit()
            
            return vehicle, 201
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating vehicle: {str(e)}")
            return {'error': 'Internal server error'}, 500

@main_bp.route('/api/vehicles/<int:vehicle_id>', methods=['PUT'])
def update_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        data = request.get_json()
        
        # Update fields
        for field, value in data.items():
            if hasattr(vehicle, field):
                if field == 'destaque_ate' and value:
                    value = datetime.fromisoformat(value)
                setattr(vehicle, field, value)
        
        db.session.commit()
        return jsonify({
            'message': 'Vehicle updated successfully',
            'vehicle': vehicle.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating vehicle {vehicle_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/api/vehicles/<int:vehicle_id>/mark-sold', methods=['PUT'])
def mark_vehicle_sold(vehicle_id):
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        vehicle.vendido = True
        vehicle.data_venda = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Vehicle marked as sold successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error marking vehicle {vehicle_id} as sold: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/api/upload/vehicles', methods=['POST'])
def upload_vehicles():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400
        
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            return jsonify({'error': 'Invalid file format. Use CSV or XLSX.'}), 400
        
        # Get dealership_id from request
        dealership_id = request.form.get('dealership_id')
        if not dealership_id:
            return jsonify({'error': 'Dealership ID is required'}), 400
            
        # Verify dealership exists
        dealership = Dealership.query.get(dealership_id)
        if not dealership:
            return jsonify({'error': 'Dealership not found'}), 404
        
        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file.read()))
        else:  # .xlsx
            df = pd.read_excel(io.BytesIO(file.read()))
        
        # Process vehicles
        vehicles_created = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Map column names (case-insensitive)
                column_mapping = {
                    'marca': ['Marca', 'MARCA', 'marca'],
                    'modelo': ['Modelo', 'MODELO', 'modelo'],
                    'versao': ['Versão', 'Versao', 'VERSÃO', 'VERSAO'],
                    'ano_fabricacao': ['Ano Fabricação', 'Ano Fabricacao', 'ANO FABRICAÇÃO', 'ANO FABRICACAO'],
                    'ano_modelo': ['Ano Modelo', 'ANO MODELO'],
                    'quilometragem': ['Quilometragem', 'QUILOMETRAGEM'],
                    "estado": ['Estado', 'ESTADO'],
                    'cambio': ['Câmbio', 'Cambio', 'CÂMBIO', 'CAMBIO'],
                    'combustivel': ['Combustível', 'Combustivel', 'COMBUSTÍVEL', 'COMBUSTIVEL'],
                    'motor': ['Motor', 'MOTOR'],
                    'potencia': ['Potência', 'Potencia', 'POTÊNCIA', 'POTENCIA'],
                    'final_placa': ['Final Placa', 'FINAL PLACA'],
                    'cor': ['Cor', 'COR'],
                    'preco': ['Preço', 'Preco', 'PREÇO', 'PRECO'],
                    'preco_promocional': ['Preço Promocional', 'Preco Promocional', 'PREÇO PROMOCIONAL', 'PRECO PROMOCIONAL'],
                    'itens_opcionais': ['Itens Opcionais', 'ITENS OPCIONAIS'],
                    'link_fotos': ['Link Fotos', 'LINK FOTOS'],
                    'observacoes': ['Observações', 'Observacoes', 'OBSERVAÇÕES', 'OBSERVACOES']
                }
                
                # Create vehicle data dictionary
                vehicle_data = {'dealership_id': dealership_id}
                
                for field, possible_names in column_mapping.items():
                    for name in possible_names:
                        if name in df.columns and pd.notna(row[name]):
                            vehicle_data[field] = row[name]
                            break
                
                # Create vehicle
                vehicle = Vehicle(**vehicle_data)
                db.session.add(vehicle)
                vehicles_created += 1
                
            except Exception as e:
                errors.append(f"Error in row {index + 2}: {str(e)}")
                continue
        
        if vehicles_created > 0:
            db.session.commit()
            return jsonify({
                'message': f'{vehicles_created} vehicles processed successfully',
                'errors': errors if errors else None
            }), 201
        else:
            return jsonify({
                'error': 'No vehicles were processed',
                'errors': errors
            }), 400
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error processing file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def send_whatsapp_message(phone_number, message, image_url=None):
    """Envia mensagem usando a API do WhatsApp Business."""
    url = f"https://graph.facebook.com/v17.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {"body": message}
    }
    
    if image_url:
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "image",
            "image": {
                "link": image_url
            }
        }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        current_app.logger.error(f"Error sending WhatsApp message: {str(e)}")
        return None

@main_bp.route("/whatsapp/webhook", methods=['POST'])
def whatsapp_webhook():
    try:
        data = request.get_json()
        if not data or 'entry' not in data:
            return jsonify({'error': 'Invalid webhook payload'}), 400
            
        # Extrai a mensagem do payload do WhatsApp Business API
        entry = data['entry'][0]
        changes = entry.get('changes', [])
        if not changes:
            return jsonify({'error': 'No changes in webhook payload'}), 400
            
        value = changes[0].get('value', {})
        messages = value.get('messages', [])
        if not messages:
            return jsonify({'error': 'No messages in webhook payload'}), 400
            
        message = messages[0]
        incoming_msg = message.get('text', {}).get('body', '').strip().lower()
        sender_phone_number = message.get('from', '')

        current_app.logger.info(f"Mensagem recebida de {sender_phone_number}: {incoming_msg}")
        dealership = Dealership.query.filter_by(active=True).first()
        if not dealership:
            return jsonify({'error': 'No active dealership found'}), 404

        # Detecta resposta de botão
        if incoming_msg.startswith("quero saber mais"):
            # Tenta extrair o modelo do texto
            modelo = None
            palavras = incoming_msg.split()
            if len(palavras) > 3:
                modelo = ' '.join(palavras[3:]).strip()
            if not modelo:
                modelo = None
            # Busca veículo pelo modelo
            veiculo = None
            if modelo:
                veiculo = Vehicle.query.filter(
                    Vehicle.dealership_id == dealership.id,
                    Vehicle.modelo.ilike(f"%{modelo}%"),
                    Vehicle.vendido == False
                ).first()
            if veiculo:
                fotos = [url.strip() for url in (veiculo.link_fotos or '').split(';') if url.strip()]
                image_url = fotos[0] if fotos else None
                mensagem = f"*{veiculo.marca} {veiculo.modelo} {veiculo.ano_modelo}*\n" \
                           f"Preço: R$ {veiculo.preco:,.2f}\n" \
                           f"Cor: {veiculo.cor}\n" \
                           f"Quilometragem: {veiculo.quilometragem:,} km\n" \
                           f"Câmbio: {veiculo.cambio}\n" \
                           f"Combustível: {veiculo.combustivel}\n" \
                           f"Itens: {veiculo.itens_opcionais if veiculo.itens_opcionais else 'Não informado'}"
                if image_url:
                    send_whatsapp_message(sender_phone_number, mensagem, image_url=image_url)
                else:
                    send_whatsapp_message(sender_phone_number, mensagem)
                current_app.logger.info("--- MENSAGEM WHATSAPP (DETALHE VEÍCULO) ---")
                current_app.logger.info(f"Para: {sender_phone_number}")
                current_app.logger.info(f"Texto: {mensagem}")
                if image_url:
                    current_app.logger.info(f"Imagem: {image_url}")
                current_app.logger.info("-------------------------------")
                return ('', 204)
            else:
                mensagem = f"Desculpe, não encontrei informações detalhadas sobre esse veículo. Posso te ajudar com outro modelo?"
                send_whatsapp_message(sender_phone_number, mensagem)
                return ('', 204)
        elif incoming_msg in ["não, obrigado", "nao, obrigado", "não obrigado", "nao obrigado"]:
            prompt = "Responda de forma simpática e cordial, agradecendo o interesse e se colocando à disposição para futuras dúvidas."
            resposta_ia = process_message_with_ai(dealership.id, prompt)
            mensagem = resposta_ia['text'] if isinstance(resposta_ia, dict) else resposta_ia
            send_whatsapp_message(sender_phone_number, mensagem)
            current_app.logger.info("--- MENSAGEM WHATSAPP (DESPEDIDA) ---")
            current_app.logger.info(f"Para: {sender_phone_number}")
            current_app.logger.info(f"Texto: {mensagem}")
            current_app.logger.info("-------------------------------")
            return ('', 204)

        # Caso padrão: busca veículos e envia template com botões
        resposta = process_message_with_ai(dealership.id, incoming_msg)
        if isinstance(resposta, list) and resposta:
            primeiro_veiculo = resposta[0]
            mensagem = primeiro_veiculo['text']
            image_url = primeiro_veiculo.get('image')
            if image_url:
                send_whatsapp_message(sender_phone_number, mensagem, image_url=image_url)
            else:
                send_whatsapp_message(sender_phone_number, mensagem)
            current_app.logger.info("--- MENSAGEM WHATSAPP (VEÍCULO) ---")
            current_app.logger.info(f"Para: {sender_phone_number}")
            current_app.logger.info(f"Texto: {mensagem}")
            if image_url:
                current_app.logger.info(f"Imagem: {image_url}")
            current_app.logger.info("-------------------------------")
            return ('', 204)
        elif isinstance(resposta, dict):
            mensagem = resposta['text']
            image_url = resposta.get('image')
            if image_url:
                send_whatsapp_message(sender_phone_number, mensagem, image_url=image_url)
            else:
                send_whatsapp_message(sender_phone_number, mensagem)
            current_app.logger.info("--- MENSAGEM WHATSAPP ---")
            current_app.logger.info(f"Para: {sender_phone_number}")
            current_app.logger.info(f"Texto: {mensagem}")
            if image_url:
                current_app.logger.info(f"Imagem: {image_url}")
            current_app.logger.info("-------------------------------")
            return ('', 204)
        else:
            send_whatsapp_message(sender_phone_number, str(resposta))
            return ('', 204)
    except Exception as e:
        current_app.logger.error(f"Error in WhatsApp webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

@main_bp.route('/debug/env')
def debug_env():
    return {"GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")}

@main_bp.route('/debug/vehicles', methods=['GET'])
def debug_vehicles():
    """Rota de debug para listar todos os veículos, incluindo vendidos."""
    try:
        vehicles = Vehicle.query.all()
        output = []
        for vehicle in vehicles:
            vehicle_data = {
                'id': vehicle.id,
                'dealership_id': vehicle.dealership_id,
                'marca': vehicle.marca,
                'modelo': vehicle.modelo,
                'ano_fabricacao': vehicle.ano_fabricacao,
                'ano_modelo': vehicle.ano_modelo,
                'quilometragem': vehicle.quilometragem,
                'estado': vehicle.estado,
                'preco': vehicle.preco,
                'itens_opcionais': vehicle.itens_opcionais,
                'cambio': vehicle.cambio,
                'combustivel': vehicle.combustivel,
                'final_placa': vehicle.final_placa,
                'cor': vehicle.cor,
                'link_fotos': vehicle.link_fotos,
                'vendido': vehicle.vendido,
                'data_cadastro': vehicle.data_cadastro.isoformat() if vehicle.data_cadastro else None
            }
            output.append(vehicle_data)
        return jsonify({
            'status': 'success',
            'count': len(output),
            'vehicles': output
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
