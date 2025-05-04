# src/models.py
from src.database import db # Importa a instância db de database.py
from datetime import datetime
from sqlalchemy.orm import validates
import re

class Dealership(db.Model):
    __tablename__ = 'dealerships'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whatsapp_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicles = db.relationship('Vehicle', backref='dealership', lazy=True, cascade='all, delete-orphan')
    
    @validates('whatsapp_number', 'phone')
    def validate_phone_number(self, key, value):
        if not value:
            return value
        # Remove non-numeric characters
        cleaned = re.sub(r'\D', '', value)
        if len(cleaned) < 10 or len(cleaned) > 11:
            raise ValueError(f'Invalid {key} number format')
        return value
    
    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError('Email is required')
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError('Invalid email format')
        return email
    
    @validates('cnpj')
    def validate_cnpj(self, key, cnpj):
        if not cnpj:
            raise ValueError('CNPJ is required')
        # Remove non-numeric characters
        cleaned = re.sub(r'\D', '', cnpj)
        if len(cleaned) != 14:
            raise ValueError('CNPJ must have 14 digits')
        return cnpj
    
    def __repr__(self):
        return f'<Dealership {self.name}>'

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    dealership_id = db.Column(db.Integer, db.ForeignKey('dealerships.id'), nullable=False)
    
    # Basic Information
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    versao = db.Column(db.String(100))
    ano_fabricacao = db.Column(db.Integer)
    ano_modelo = db.Column(db.Integer)
    
    # Technical Specifications
    quilometragem = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(20))  # Novo, Usado
    cambio = db.Column(db.String(20))  # Manual, Automático
    combustivel = db.Column(db.String(20))  # Flex, Gasolina, Diesel, Elétrico
    motor = db.Column(db.String(50))  # 1.0, 1.6, 2.0, etc.
    potencia = db.Column(db.String(20))  # 85cv, 120cv, etc.
    final_placa = db.Column(db.String(1))
    cor = db.Column(db.String(30))
    
    # Commercial Information
    preco = db.Column(db.Float)
    preco_promocional = db.Column(db.Float)
    destaque = db.Column(db.Boolean, default=False)
    destaque_ate = db.Column(db.DateTime)
    vendido = db.Column(db.Boolean, default=False, nullable=False)
    
    # Additional Information
    itens_opcionais = db.Column(db.Text)  # Lista separada por ;
    link_fotos = db.Column(db.Text)  # URLs separadas por ;
    observacoes = db.Column(db.Text)
    
    # Metadata
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_venda = db.Column(db.DateTime)
    
    @validates('ano_fabricacao', 'ano_modelo')
    def validate_year(self, key, year):
        if year is None:
            return year
        current_year = datetime.now().year
        if not (1900 <= year <= current_year + 1):
            raise ValueError(f'Invalid {key}: must be between 1900 and {current_year + 1}')
        return year
    
    @validates('quilometragem')
    def validate_quilometragem(self, key, value):
        if value is None:
            return 0
        if value < 0:
            raise ValueError('Quilometragem cannot be negative')
        return value
    
    @validates('preco', 'preco_promocional')
    def validate_price(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f'{key} cannot be negative')
        return value
    
    @validates('estado')
    def validate_estado(self, key, value):
        if value not in ['Novo', 'Usado', None]:
            raise ValueError('Estado must be either "Novo" or "Usado"')
        return value
    
    @validates('cambio')
    def validate_cambio(self, key, value):
        valid_values = ['Manual', 'Automático', None]
        if value not in valid_values:
            raise ValueError('Câmbio must be either "Manual" or "Automático"')
        return value
    
    @validates('combustivel')
    def validate_combustivel(self, key, value):
        valid_values = ['Flex', 'Gasolina', 'Diesel', 'Elétrico', 'Híbrido', None]
        if value not in valid_values:
            raise ValueError('Invalid combustível value')
        return value
    
    def to_dict(self):
        """Convert vehicle instance to dictionary"""
        return {
            'id': self.id,
            'dealership_id': self.dealership_id,
            'marca': self.marca,
            'modelo': self.modelo,
            'versao': self.versao,
            'ano_fabricacao': self.ano_fabricacao,
            'ano_modelo': self.ano_modelo,
            'quilometragem': self.quilometragem,
            'estado': self.estado,
            'cambio': self.cambio,
            'combustivel': self.combustivel,
            'motor': self.motor,
            'potencia': self.potencia,
            'final_placa': self.final_placa,
            'cor': self.cor,
            'preco': self.preco,
            'preco_promocional': self.preco_promocional,
            'destaque': self.destaque,
            'destaque_ate': self.destaque_ate.isoformat() if self.destaque_ate else None,
            'vendido': self.vendido,
            'itens_opcionais': self.itens_opcionais.split(';') if self.itens_opcionais else [],
            'link_fotos': self.link_fotos.split(';') if self.link_fotos else [],
            'observacoes': self.observacoes,
            'data_cadastro': self.data_cadastro.isoformat(),
            'data_atualizacao': self.data_atualizacao.isoformat(),
            'data_venda': self.data_venda.isoformat() if self.data_venda else None
        }
    
    def __repr__(self):
        return f'<Vehicle {self.marca} {self.modelo} {self.ano_modelo}>'

# Não se esqueça de criar as tabelas no banco de dados!
# Dentro do shell Python (após ativar venv):
# from src.main import app, db
# with app.app_context():
#     db.create_all()
