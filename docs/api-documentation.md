# Documentação da API - AutoAtende AI

## Iniciando o Servidor Localmente

### Pré-requisitos
- Python 3.8+
- PostgreSQL
- Ambiente virtual Python (venv)

### Configuração do Ambiente
1. Clone o repositório
2. Navegue até a pasta do projeto
3. Crie e ative o ambiente virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

4. Instale as dependências:
```bash
pip install -r requirements.txt
```

5. Configure o arquivo `.env` na pasta `backend`:
```env
DATABASE_URL=postgresql://auto_atende:auto_atende@localhost:5432/auto_atende
FLASK_APP=src.main
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=http://localhost:3000
PORT=5001
```

### Iniciando o Servidor
Existem duas maneiras de iniciar o servidor:

1. Usando o script de inicialização:
```bash
cd backend
./start-server.sh
```

2. Manualmente:
```bash
cd backend
source venv/bin/activate
export FLASK_APP=src.main
export FLASK_ENV=development
export PYTHONPATH=$PYTHONPATH:.
flask run --port=5001 --host=0.0.0.0
```

O servidor estará disponível em `http://localhost:5001`

## Endpoints da API

### Health Check
```http
GET /health
```
Verifica o status do servidor e conexão com o banco de dados.

**Resposta:**
```json
{
    "status": "healthy",
    "database": "connected",
    "version": "1.0.0"
}
```

### Concessionárias

#### Listar Todas as Concessionárias
```http
GET /api/dealerships
```
Retorna todas as concessionárias ativas.

**Resposta:**
```json
{
    "dealerships": [
        {
            "id": 1,
            "name": "AutoShow Veículos",
            "whatsapp": "11999887766",
            "email": "contato@autoshow.com.br",
            "cnpj": "12345678901234",
            "address": "Av. Principal, 1000",
            "city": "São Paulo",
            "state": "SP",
            "phone": "1133445566",
            "website": "https://autoshow.com.br",
            "created_at": "2024-05-04T17:42:29"
        }
    ]
}
```

#### Obter Concessionária por ID
```http
GET /api/dealerships/{id}
```
Retorna os detalhes de uma concessionária específica.

#### Criar Nova Concessionária
```http
POST /api/dealerships
Content-Type: application/json

{
    "name": "AutoShow Veículos",
    "whatsapp": "11999887766",
    "email": "contato@autoshow.com.br",
    "cnpj": "12345678901234",
    "address": "Av. Principal, 1000",
    "city": "São Paulo",
    "state": "SP",
    "phone": "1133445566",
    "website": "https://autoshow.com.br"
}
```

### Veículos

#### Listar Veículos
```http
GET /api/vehicles
```
Retorna todos os veículos não vendidos. Suporta os seguintes parâmetros de query:
- `marca`: Filtra por marca
- `modelo`: Filtra por modelo
- `min_price`: Preço mínimo
- `max_price`: Preço máximo
- `min_year`: Ano mínimo
- `max_year`: Ano máximo
- `dealership_id`: ID da concessionária

**Resposta:**
```json
{
    "vehicles": [
        {
            "id": 1,
            "marca": "Toyota",
            "modelo": "Corolla",
            "ano_modelo": 2023,
            "preco": 120000.00,
            "quilometragem": 15000,
            "cor": "Prata",
            "cambio": "Automático",
            "combustivel": "Flex",
            "final_placa": "5",
            "itens_opcionais": ["Ar Condicionado", "GPS"],
            "link_fotos": ["http://exemplo.com/foto1.jpg"],
            "dealership_id": 1,
            "created_at": "2024-05-04T17:43:20"
        }
    ]
}
```

#### Obter Veículo por ID
```http
GET /api/vehicles/{id}
```
Retorna os detalhes de um veículo específico.

#### Criar Novo Veículo
```http
POST /api/vehicles
Content-Type: application/json

{
    "marca": "Toyota",
    "modelo": "Corolla",
    "ano_modelo": 2023,
    "preco": 120000.00,
    "quilometragem": 15000,
    "cor": "Prata",
    "cambio": "Automático",
    "combustivel": "Flex",
    "final_placa": "5",
    "itens_opcionais": ["Ar Condicionado", "GPS"],
    "link_fotos": ["http://exemplo.com/foto1.jpg"],
    "dealership_id": 1
}
```

#### Atualizar Veículo
```http
PUT /api/vehicles/{id}
Content-Type: application/json

{
    "preco": 115000.00,
    "quilometragem": 16000
}
```

#### Marcar Veículo como Vendido
```http
PUT /api/vehicles/{id}/mark-sold
```

### Upload de Veículos

#### Upload em Lote via CSV/Excel
```http
POST /api/upload/vehicles
Content-Type: multipart/form-data

file: [arquivo CSV ou Excel]
dealership_id: 1
```

O arquivo deve conter as seguintes colunas:
- Marca
- Modelo
- Versao
- Ano Fabricacao
- Ano Modelo
- Quilometragem
- Cor
- Cambio
- Combustivel
- Final Placa
- Itens Opcionais
- Link Fotos
- Preco

**Resposta:**
```json
{
    "message": "Veículos importados com sucesso",
    "imported_count": 10,
    "errors": []
}
```

## Códigos de Erro

- 200: Sucesso
- 201: Criado com sucesso
- 400: Erro na requisição
- 404: Recurso não encontrado
- 500: Erro interno do servidor

## Exemplos de Uso

### Criar uma Concessionária
```bash
curl -X POST http://localhost:5001/api/dealerships \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AutoShow Veículos",
    "whatsapp": "11999887766",
    "email": "contato@autoshow.com.br",
    "cnpj": "12345678901234",
    "address": "Av. Principal, 1000",
    "city": "São Paulo",
    "state": "SP",
    "phone": "1133445566",
    "website": "https://autoshow.com.br"
  }'
```

### Upload de Veículos
```bash
curl -X POST http://localhost:5001/api/upload/vehicles \
  -F "file=@exemplo_veiculos.csv" \
  -F "dealership_id=1"
``` 