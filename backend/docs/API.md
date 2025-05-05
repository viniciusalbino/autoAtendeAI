# Auto Atende AI API Documentation

## Overview

The Auto Atende AI API provides endpoints for managing dealerships, vehicles, and user authentication. The API is built with Flask and uses SQLAlchemy for database operations.

## Base URL

```
http://localhost:5001
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. To access protected endpoints, include the JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /auth/register
```

Request body:
```json
{
    "email": "user@example.com",
    "password": "your_password"
}
```

Response (201 Created):
```json
{
    "message": "User registered successfully"
}
```

### Dealerships

#### List Dealerships
```http
GET /dealerships/
```

Response (200 OK):
```json
[
    {
        "id": 1,
        "name": "Example Dealership",
        "whatsapp_number": "5511999999999",
        "email": "contact@example.com",
        "cnpj": "12345678901234",
        "address": "123 Main St",
        "city": "São Paulo",
        "state": "SP",
        "phone": "5511999999999",
        "website": "https://example.com",
        "active": true
    }
]
```

#### Create Dealership
```http
POST /dealerships/
```

Request body:
```json
{
    "name": "New Dealership",
    "whatsapp_number": "5511999999999",
    "email": "contact@newdealership.com",
    "cnpj": "12345678901234",
    "address": "456 Market St",
    "city": "Rio de Janeiro",
    "state": "RJ",
    "phone": "5521999999999",
    "website": "https://newdealership.com"
}
```

Response (201 Created):
```json
{
    "id": 2,
    "name": "New Dealership",
    "whatsapp_number": "5511999999999",
    "email": "contact@newdealership.com",
    "cnpj": "12345678901234",
    "address": "456 Market St",
    "city": "Rio de Janeiro",
    "state": "RJ",
    "phone": "5521999999999",
    "website": "https://newdealership.com",
    "active": true
}
```

### Vehicles

#### List Vehicles
```http
GET /vehicles/
```

Query Parameters:
- `marca`: Filter by brand
- `modelo`: Filter by model
- `min_price`: Minimum price
- `max_price`: Maximum price
- `estado`: Filter by condition (Novo/Usado)
- `cambio`: Filter by transmission type
- `combustivel`: Filter by fuel type
- `final_placa`: Filter by license plate ending
- `destaque`: Filter featured vehicles (true/false)

Response (200 OK):
```json
[
    {
        "id": 1,
        "dealership_id": 1,
        "marca": "Toyota",
        "modelo": "Corolla",
        "versao": "XEi",
        "ano_fabricacao": 2023,
        "ano_modelo": 2024,
        "quilometragem": 0,
        "estado": "Novo",
        "cambio": "Automático",
        "combustivel": "Flex",
        "motor": "2.0",
        "potencia": "170cv",
        "final_placa": "1",
        "cor": "Prata",
        "preco": 150000.00,
        "preco_promocional": null,
        "destaque": false,
        "vendido": false
    }
]
```

#### Create Vehicle
```http
POST /vehicles/
```

Request body:
```json
{
    "dealership_id": 1,
    "marca": "Honda",
    "modelo": "Civic",
    "versao": "Touring",
    "ano_fabricacao": 2023,
    "ano_modelo": 2024,
    "quilometragem": 0,
    "estado": "Novo",
    "cambio": "Automático",
    "combustivel": "Flex",
    "motor": "1.5",
    "potencia": "173cv",
    "final_placa": "2",
    "cor": "Preto",
    "preco": 160000.00,
    "preco_promocional": null,
    "destaque": true,
    "itens_opcionais": "GPS;Camera de ré;Sensores de estacionamento",
    "link_fotos": "https://example.com/photo1.jpg;https://example.com/photo2.jpg",
    "observacoes": "Veículo em destaque"
}
```

Response (201 Created):
```json
{
    "id": 2,
    "dealership_id": 1,
    "marca": "Honda",
    "modelo": "Civic",
    "versao": "Touring",
    "ano_fabricacao": 2023,
    "ano_modelo": 2024,
    "quilometragem": 0,
    "estado": "Novo",
    "cambio": "Automático",
    "combustivel": "Flex",
    "motor": "1.5",
    "potencia": "173cv",
    "final_placa": "2",
    "cor": "Preto",
    "preco": 160000.00,
    "preco_promocional": null,
    "destaque": true,
    "vendido": false
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Missing required field: email"
}
```

### 401 Unauthorized
```json
{
    "error": "Missing Authorization header"
}
```

### 404 Not Found
```json
{
    "error": "Resource not found"
}
```

### 409 Conflict
```json
{
    "error": "Email already registered"
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error"
}
```

## Testing

To run the test suite:

```bash
cd backend
pytest tests/
```

## Swagger Documentation

The API includes Swagger documentation. To access it, visit:

```
http://localhost:5001/
```

This will show the interactive API documentation where you can:
- View all available endpoints
- See request/response schemas
- Test endpoints directly from the browser
- View authentication requirements 