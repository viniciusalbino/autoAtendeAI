import pytest
from src.main import app, db
from src.models import User, Dealership, Vehicle
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_register_user(client):
    """Test user registration endpoint"""
    response = client.post('/auth/register',
                          json={'email': 'test@example.com', 'password': 'testpass123'},
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'message' in data
    assert data['message'] == 'User registered successfully'

def test_register_duplicate_user(client):
    """Test registering a user with an existing email"""
    # First registration
    client.post('/auth/register',
                json={'email': 'test@example.com', 'password': 'testpass123'},
                content_type='application/json')
    
    # Second registration with same email
    response = client.post('/auth/register',
                          json={'email': 'test@example.com', 'password': 'testpass123'},
                          content_type='application/json')
    assert response.status_code == 409
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Email already registered'

def test_register_missing_fields(client):
    """Test registration with missing required fields"""
    response = client.post('/auth/register',
                          json={'email': 'test@example.com'},
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Email and password are required'

def test_create_dealership(client):
    """Test dealership creation endpoint"""
    response = client.post('/dealerships/',
                          json={
                              'name': 'Test Dealership',
                              'whatsapp_number': '5511999999999',
                              'email': 'test@dealership.com',
                              'cnpj': '12345678901234'
                          },
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'name' in data
    assert data['name'] == 'Test Dealership'

def test_create_vehicle(client):
    """Test vehicle creation endpoint"""
    # First create a dealership
    dealership_response = client.post('/dealerships/',
                                    json={
                                        'name': 'Test Dealership',
                                        'whatsapp_number': '5511999999999',
                                        'email': 'test@dealership.com',
                                        'cnpj': '12345678901234'
                                    },
                                    content_type='application/json')
    dealership_id = json.loads(dealership_response.data)['id']
    
    # Then create a vehicle
    response = client.post('/vehicles/',
                          json={
                              'dealership_id': dealership_id,
                              'marca': 'Toyota',
                              'modelo': 'Corolla',
                              'ano_fabricacao': 2023,
                              'ano_modelo': 2024,
                              'preco': 150000.00
                          },
                          content_type='application/json')
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'marca' in data
    assert data['marca'] == 'Toyota'
    assert data['modelo'] == 'Corolla'

def test_get_vehicles(client):
    """Test getting vehicles with filters"""
    # First create a dealership
    dealership_response = client.post('/dealerships/',
                                    json={
                                        'name': 'Test Dealership',
                                        'whatsapp_number': '5511999999999',
                                        'email': 'test@dealership.com',
                                        'cnpj': '12345678901234'
                                    },
                                    content_type='application/json')
    dealership_id = json.loads(dealership_response.data)['id']
    
    # Create some vehicles
    client.post('/vehicles/',
                json={
                    'dealership_id': dealership_id,
                    'marca': 'Toyota',
                    'modelo': 'Corolla',
                    'ano_fabricacao': 2023,
                    'ano_modelo': 2024,
                    'preco': 150000.00
                },
                content_type='application/json')
    
    client.post('/vehicles/',
                json={
                    'dealership_id': dealership_id,
                    'marca': 'Honda',
                    'modelo': 'Civic',
                    'ano_fabricacao': 2023,
                    'ano_modelo': 2024,
                    'preco': 160000.00
                },
                content_type='application/json')
    
    # Test getting all vehicles
    response = client.get('/vehicles/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    
    # Test filtering by marca
    response = client.get('/vehicles/?marca=Toyota')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['marca'] == 'Toyota'
    
    # Test filtering by price range
    response = client.get('/vehicles/?min_price=155000&max_price=165000')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['marca'] == 'Honda' 