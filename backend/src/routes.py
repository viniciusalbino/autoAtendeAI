# src/routes.py
from flask import Blueprint, jsonify, request, current_app
from src.database import db
from src.models import Vehicle, Dealership
from sqlalchemy import or_, and_
from datetime import datetime
import pandas as pd
import io
import logging

main_bp = Blueprint('main', __name__)

# Dealership Routes
@main_bp.route('/api/dealerships', methods=['GET'])
def get_dealerships():
    try:
        dealerships = Dealership.query.filter_by(active=True).all()
        return jsonify({
            'dealerships': [{
                'id': d.id,
                'name': d.name,
                'whatsapp_number': d.whatsapp_number,
                'email': d.email,
                'city': d.city,
                'state': d.state,
                'website': d.website
            } for d in dealerships]
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching dealerships: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/api/dealerships/<int:dealership_id>', methods=['GET'])
def get_dealership(dealership_id):
    try:
        dealership = Dealership.query.get_or_404(dealership_id)
        return jsonify({
            'id': dealership.id,
            'name': dealership.name,
            'whatsapp_number': dealership.whatsapp_number,
            'email': dealership.email,
            'cnpj': dealership.cnpj,
            'address': dealership.address,
            'city': dealership.city,
            'state': dealership.state,
            'phone': dealership.phone,
            'website': dealership.website,
            'active': dealership.active,
            'created_at': dealership.created_at.isoformat(),
            'updated_at': dealership.updated_at.isoformat()
        })
    except Exception as e:
        current_app.logger.error(f"Error fetching dealership {dealership_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/api/dealerships', methods=['POST'])
def create_dealership():
    try:
        data = request.get_json()
        required_fields = ['name', 'whatsapp_number', 'email', 'cnpj']
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if dealership already exists
        if Dealership.query.filter_by(cnpj=data['cnpj']).first():
            return jsonify({'error': 'CNPJ already registered'}), 409
        
        dealership = Dealership(
            name=data['name'],
            whatsapp_number=data['whatsapp_number'],
            email=data['email'],
            cnpj=data['cnpj'],
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            phone=data.get('phone'),
            website=data.get('website')
        )
        
        db.session.add(dealership)
        db.session.commit()
        
        return jsonify({
            'message': 'Dealership created successfully',
            'dealership_id': dealership.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating dealership: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Vehicle Routes
@main_bp.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    try:
        # Get query parameters
        marca = request.args.get('marca')
        modelo = request.args.get('modelo')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        estado = request.args.get('estado')
        cambio = request.args.get('cambio')
        combustivel = request.args.get('combustivel')
        final_placa = request.args.get('final_placa')
        destaque = request.args.get('destaque', type=bool)
        
        # Build query
        query = Vehicle.query.filter_by(vendido=False)
        
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
        return jsonify({'vehicles': [vehicle.to_dict() for vehicle in vehicles]})
        
    except Exception as e:
        current_app.logger.error(f"Error fetching vehicles: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/api/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle(vehicle_id):
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        return jsonify(vehicle.to_dict())
    except Exception as e:
        current_app.logger.error(f"Error fetching vehicle {vehicle_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/api/vehicles', methods=['POST'])
def create_vehicle():
    try:
        data = request.get_json()
        required_fields = ['dealership_id', 'marca', 'modelo']
        
        # Validate required fields
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if dealership exists
        dealership = Dealership.query.get(data['dealership_id'])
        if not dealership:
            return jsonify({'error': 'Dealership not found'}), 404
        
        vehicle = Vehicle(
            dealership_id=data['dealership_id'],
            marca=data['marca'],
            modelo=data['modelo'],
            versao=data.get('versao'),
            ano_fabricacao=data.get('ano_fabricacao'),
            ano_modelo=data.get('ano_modelo'),
            quilometragem=data.get('quilometragem', 0),
            estado=data.get('estado'),
            cambio=data.get('cambio'),
            combustivel=data.get('combustivel'),
            motor=data.get('motor'),
            potencia=data.get('potencia'),
            final_placa=data.get('final_placa'),
            cor=data.get('cor'),
            preco=data.get('preco'),
            preco_promocional=data.get('preco_promocional'),
            destaque=data.get('destaque', False),
            destaque_ate=datetime.fromisoformat(data['destaque_ate']) if data.get('destaque_ate') else None,
            itens_opcionais=data.get('itens_opcionais'),
            link_fotos=data.get('link_fotos'),
            observacoes=data.get('observacoes')
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'message': 'Vehicle created successfully',
            'vehicle_id': vehicle.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating vehicle: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

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
                    'estado': ['Estado', 'ESTADO'],
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

# Não se esqueça de registrar o blueprint em main.py:
# from src.routes import main_bp
# app.register_blueprint(main_bp)
