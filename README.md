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
│   │   │   └── whatsapp.py   # Rotas do webhook do WhatsApp
│   │   └── services/
│   │       └── whatsapp_service.py  # Lógica de processamento do WhatsApp
│   ├── venv/                 # Ambiente virtual Python
│   ├── .env                  # Variáveis de ambiente
│   └── requirements.txt      # Dependências Python
└── frontend/                 # (A ser implementado)
```

## Configuração do Backend

### Dependências Principais
- Python 3.11+
- Flask
- Flask-SQLAlchemy
- Flask-CORS
- python-dotenv
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

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://seu-dominio.com
```

### Modelos do Banco de Dados

#### Dealership (Concessionária)
- id (PK)
- name (nome da concessionária)
- whatsapp_number (número do WhatsApp)
- vehicles (relacionamento com Vehicle)

#### Vehicle (Veículo)
- id (PK)
- dealership_id (FK para Dealership)
- marca
- modelo
- ano_fabricacao
- ano_modelo
- quilometragem
- estado (Novo/Usado)
- preco
- itens_opcionais
- cambio
- combustivel
- final_placa
- cor
- link_fotos
- vendido (boolean)
- data_cadastro

### Rotas Implementadas

#### Endpoints Principais
- `GET /health` - Verificação de saúde da API
- `GET /` - Mensagem de boas-vindas
- `GET /debug/vehicles` - Lista todos os veículos (debug)

#### Webhook WhatsApp
- `POST /whatsapp/webhook` - Recebe mensagens do WhatsApp
- `GET /whatsapp/webhook` - Verificação do webhook (Twilio)

### Serviços Implementados

#### WhatsApp Service
- `handle_whatsapp_webhook()` - Processa mensagens recebidas
- Integração com Twilio para envio de respostas
- Processamento de mensagens com Google Gemini AI

## Estado Atual do Projeto

### Backend
- ✅ Configuração básica do Flask
- ✅ Conexão com banco de dados PostgreSQL
- ✅ Modelos de dados (Dealership e Vehicle)
- ✅ Webhook do WhatsApp
- ✅ Integração com Twilio
- ✅ Integração com Google Gemini AI
- ✅ Sistema de logging
- ✅ Tratamento de erros
- ✅ CORS configurado

### Frontend
- ⏳ A ser implementado

## Próximos Passos

1. Implementar o frontend React com:
   - Painel de controle para concessionárias
   - Gerenciamento de veículos
   - Upload de planilhas
   - Autenticação de usuários

2. Melhorias no backend:
   - Autenticação JWT
   - Validação de dados
   - Testes automatizados
   - Documentação da API (Swagger/OpenAPI)

3. Melhorias na IA:
   - Refinamento do prompt do Gemini
   - Tratamento de contexto de conversa
   - Suporte a mais intenções

## Como Executar

1. Clone o repositório
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

5. Inicialize o banco de dados:
```bash
python src/main.py
```

6. O servidor estará rodando em `http://localhost:5001`

## Notas para Desenvolvimento

- O projeto usa SQLAlchemy como ORM
- As rotas do WhatsApp estão em `src/routes/whatsapp.py`
- A lógica de processamento do WhatsApp está em `src/services/whatsapp_service.py`
- O sistema de logging está configurado em `logs/backend.log`
- O CORS está configurado para permitir requisições do frontend
- As variáveis de ambiente são carregadas via python-dotenv

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request
