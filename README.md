# Auto Atende AI - Agente de IA para Concessionárias

Um sistema de atendimento automatizado via WhatsApp para concessionárias, utilizando IA para responder perguntas sobre veículos disponíveis no estoque.

## Estrutura do Projeto

```
autoAtendeAI/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py           # Ponto de entrada da aplicação Flask
│   │   ├── database.py       # Configuração do SQLAlchemy
│   │   ├── models.py         # Modelos do banco de dados
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── main.py      # Rotas principais da API (auth, dealerships, vehicles)
│   │   │   └── whatsapp.py  # Rotas do webhook do WhatsApp
│   │   └── services/
│   │       └── whatsapp_service.py  # Lógica de processamento do WhatsApp
│   ├── tests/               # Testes automatizados
│   ├── migrations/         # Migrações do banco de dados
│   ├── venv/              # Ambiente virtual Python
│   ├── .env              # Variáveis de ambiente
│   └── requirements.txt   # Dependências Python
└── frontend/            # (A ser implementado)
```

## Configuração do Backend

### Dependências Principais
- Python 3.11+
- Flask e extensões:
  - Flask-SQLAlchemy (ORM)
  - Flask-CORS (CORS support)
  - Flask-JWT-Extended (Autenticação)
  - Flask-RESTX (API documentation)
  - Flask-Migrate (Migrações)
- python-dotenv (Variáveis de ambiente)
- psycopg2-binary (PostgreSQL)
- twilio (API WhatsApp)
- google-generativeai (Gemini AI)

### Variáveis de Ambiente (.env)
```env
# Banco de Dados
DATABASE_URL=postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE_NAME]

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=seu_sid
TWILIO_AUTH_TOKEN=seu_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Google Gemini AI
GEMINI_API_KEY=sua_chave_api

# Flask
FLASK_SECRET_KEY=sua_chave_secreta
FLASK_ENV=development
PORT=5001

# JWT
JWT_SECRET_KEY=sua_chave_jwt
JWT_ACCESS_TOKEN_EXPIRES=1d

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://seu-dominio.com
```

### Modelos do Banco de Dados

#### User (Usuário)
- id (PK)
- email (único)
- password_hash
- active (boolean)
- dealership_id (FK para Dealership)
- created_at
- plans (relacionamento com Plan)

#### Dealership (Concessionária)
- id (PK)
- name (nome da concessionária)
- whatsapp_number (número do WhatsApp)
- email
- cnpj
- address
- city
- state
- phone
- website
- active (boolean)
- vehicles (relacionamento com Vehicle)

#### Vehicle (Veículo)
- id (PK)
- dealership_id (FK para Dealership)
- marca
- modelo
- versao
- ano_fabricacao
- ano_modelo
- quilometragem
- estado (Novo/Usado)
- preco
- preco_promocional
- destaque (boolean)
- vendido (boolean)
- itens_opcionais
- cambio
- combustivel
- motor
- potencia
- final_placa
- cor
- link_fotos
- data_cadastro

#### Plan (Plano)
- id (PK)
- user_id (FK para User)
- plan_type
- is_active
- start_date
- end_date
- last_payment_date
- next_payment_due
- created_at

### Endpoints da API

#### Autenticação
- `POST /auth/register` - Registro de usuário
- `POST /auth/login` - Login de usuário (retorna JWT)

#### Concessionárias
- `GET /dealerships/` - Lista concessionárias
- `POST /dealerships/` - Cria nova concessionária
- `GET /dealerships/<id>` - Detalhes da concessionária
- `PUT /dealerships/<id>` - Atualiza concessionária
- `DELETE /dealerships/<id>` - Desativa concessionária

#### Veículos
- `GET /vehicles/` - Lista veículos (com filtros)
- `POST /vehicles/` - Cadastra novo veículo
- `GET /vehicles/<id>` - Detalhes do veículo
- `PUT /vehicles/<id>` - Atualiza veículo
- `PUT /vehicles/<id>/mark-sold` - Marca veículo como vendido

#### WhatsApp
- `POST /whatsapp/webhook` - Recebe mensagens
- `GET /whatsapp/webhook` - Verificação do webhook

## Guia Passo a Passo: Criando uma Nova Concessionária

### 1. Registro de Usuário
```bash
curl -X POST http://localhost:5001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu.email@exemplo.com",
    "password": "sua_senha"
  }'
```

### 2. Login para Obter Token JWT
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seu.email@exemplo.com",
    "password": "sua_senha"
  }'
```
Guarde o token JWT retornado para usar nas próximas requisições.

### 3. Criar Concessionária
```bash
curl -X POST http://localhost:5001/dealerships/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_JWT" \
  -d '{
    "name": "Nome da Concessionária",
    "whatsapp_number": "5511999999999",
    "email": "concessionaria@exemplo.com",
    "cnpj": "12345678901234",
    "address": "Rua Exemplo, 123",
    "city": "São Paulo",
    "state": "SP",
    "phone": "1133334444",
    "website": "https://exemplo.com"
  }'
```

### 4. Verificar Criação
```bash
curl -X GET http://localhost:5001/dealerships/ \
  -H "Authorization: Bearer SEU_TOKEN_JWT"
```

## Como Executar

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/autoAtendeAI.git
cd autoAtendeAI
```

2. Configure o ambiente virtual:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
.\venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o arquivo .env com suas credenciais

5. Execute as migrações do banco de dados:
```bash
flask db upgrade
```

6. Inicie o servidor:
```bash
flask run --port 5001
```

O servidor estará rodando em `http://localhost:5001`

## Testes

Para executar os testes:
```bash
pytest
```

## Notas de Desenvolvimento

- O projeto usa SQLAlchemy como ORM
- Autenticação via JWT com Flask-JWT-Extended
- Documentação da API com Flask-RESTX (Swagger)
- CORS habilitado para desenvolvimento local
- Sistema de logging configurado em `logs/backend.log`
- Migrações do banco gerenciadas com Flask-Migrate

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request
