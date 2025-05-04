# Guia Detalhado: Construindo um Agente de IA para Concessionárias (MVP)

## Introdução

Este documento apresenta um guia passo a passo para a construção de um Agente de Inteligência Artificial (IA) focado em atender clientes de concessionárias e revendedoras de veículos via WhatsApp. O objetivo é criar um Produto Mínimo Viável (MVP) que possa responder a perguntas sobre a disponibilidade de veículos com base em um estoque específico da loja, além de fornecer um painel de controle web para que cada concessionária gerencie seu inventário. A arquitetura proposta busca um equilíbrio entre funcionalidade, baixo custo operacional (seguindo a filosofia "Minimal Cost Platform" - MCP) e escalabilidade inicial para suportar até 50 concessionárias com volume moderado de interações. Seguindo as preferências definidas, utilizaremos Python com Flask para o backend, React para o frontend, PostgreSQL (via Supabase) como banco de dados, a API do Google Gemini como modelo de IA principal e a API do WhatsApp (via Twilio) para a comunicação.

## Visão Geral da Arquitetura e Tecnologias

Antes de iniciarmos a implementação, é fundamental compreendermos a arquitetura geral do sistema. O fluxo principal começa quando um cliente envia uma mensagem via WhatsApp. Essa mensagem é recebida pela API do WhatsApp (gerenciada pelo Twilio, neste guia) que, por sua vez, a encaminha para nosso backend através de um webhook. O backend, desenvolvido em Python com o framework Flask, é o cérebro do sistema. Ele identifica a qual concessionária a mensagem pertence, processa a solicitação do cliente utilizando a API de IA conversacional (Google Gemini) para entender a intenção (por exemplo, buscar um carro específico) e consulta o banco de dados PostgreSQL (hospedado no Supabase) para encontrar veículos que correspondam aos critérios. A resposta é então formatada e enviada de volta ao cliente via API do WhatsApp.

Paralelamente, os funcionários da concessionária terão acesso a um painel de controle web, construído com React. Este painel permitirá que eles façam login, cadastrem veículos manualmente ou subam uma planilha (em formato CSV, conforme template fornecido) com o inventário atualizado. Todas as interações do painel com os dados ocorrem através de chamadas de API para o mesmo backend Flask, que também lida com a autenticação e o gerenciamento dos dados no Supabase. Para a hospedagem, utilizaremos serviços com generosos níveis gratuitos: Vercel ou Netlify para o frontend React, Fly.io ou Render para o backend Flask, e Supabase para o banco de dados e autenticação. A escolha por esses serviços gerenciados simplifica a configuração inicial e a manutenção, alinhando-se ao objetivo de baixo custo e complexidade reduzida para o MVP.

## Preparação do Ambiente de Desenvolvimento

O primeiro passo prático é organizar nosso ambiente de desenvolvimento. Criaremos uma estrutura de pastas base para o projeto e inicializaremos um repositório Git para controle de versão, o que é essencial para um desenvolvimento organizado e colaborativo, mesmo que inicialmente seja um projeto individual. Recomenda-se o uso de um sistema operacional Linux ou macOS, ou o WSL (Windows Subsystem for Linux) no Windows, para maior compatibilidade com as ferramentas que utilizaremos.

Execute os seguintes comandos no seu terminal para criar a estrutura inicial do projeto:

```bash
mkdir ai_agent_concessionaria
cd ai_agent_concessionaria
git init
mkdir backend
mkdir frontend
mkdir docs
# Copie o template da planilha para a pasta docs como referência
# (Assumindo que template_veiculos.csv está no diretório anterior)
# cp ../template_veiculos.csv docs/

echo "# AI Agent para Concessionárias" > README.md
echo "venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "node_modules/" >> .gitignore
echo ".DS_Store" >> .gitignore

git add .
git commit -m "Initial project structure"
```

Com esta estrutura, teremos pastas separadas para o código do backend (Flask), frontend (React) e documentação (incluindo o template da planilha). O arquivo `.gitignore` garante que arquivos desnecessários ou sensíveis (como ambientes virtuais, caches e variáveis de ambiente) não sejam enviados para o repositório Git. O `README.md` servirá como a porta de entrada do projeto, onde podemos adicionar informações gerais sobre como configurar e rodar a aplicação.

Nos próximos capítulos, detalharemos a configuração e implementação de cada componente: o backend Flask, o banco de dados no Supabase, o frontend React, a integração com a IA e a conexão com a API do WhatsApp.



## Configurando o Backend com Flask e Supabase

Agora que nosso ambiente está preparado, vamos focar no coração do nosso sistema: o backend. Utilizaremos o Flask, um microframework Python conhecido por sua simplicidade e flexibilidade, juntamente com o Supabase, que nos fornecerá um banco de dados PostgreSQL gerenciado e funcionalidades de autenticação com um generoso nível gratuito. Começaremos configurando o projeto Flask e estabelecendo a conexão com o banco de dados.

Primeiro, navegaremos até a pasta `backend` e utilizaremos o comando `create_flask_app` para gerar a estrutura inicial do nosso projeto Flask, conforme as boas práticas recomendadas. Isso criará um ambiente virtual (`venv`) e uma estrutura básica de diretórios (`src`, `requirements.txt`).

```bash
cd backend
# Certifique-se de que create_flask_app está disponível no seu ambiente ou use o comando equivalente
# Exemplo genérico, ajuste se necessário:
python3.11 -m venv venv
source venv/bin/activate
pip3 install Flask Flask-SQLAlchemy python-dotenv psycopg2-binary pandas openpyxl requests google-generativeai twilio
# Crie a estrutura manualmente ou use um template se disponível
mkdir src
touch src/main.py
touch src/models.py
touch src/routes.py
touch requirements.txt
pip3 freeze > requirements.txt
# Crie um arquivo .env para variáveis de ambiente
touch .env 
```
*(Nota: O comando `create_flask_app` mencionado no guia de conhecimento pode não estar diretamente disponível; o snippet acima mostra a criação manual e instalação de dependências essenciais. Adapte conforme o ambiente exato.)*

Após criar a estrutura e ativar o ambiente virtual (`source venv/bin/activate`), precisamos configurar a conexão com o Supabase. Crie um projeto no Supabase (supabase.com). No dashboard do seu projeto, vá até "Project Settings" > "Database" e copie os dados de conexão (Host, Database name, User, Port). Guarde a senha que você definiu ao criar o projeto. Adicione essas informações ao arquivo `.env` na raiz da pasta `backend`:

```dotenv
# .env
DATABASE_URL=postgresql://[USER]:[PASSWORD]@[HOST]:[PORT]/[DATABASE_NAME]
SUPABASE_URL=SUA_SUPABASE_URL
SUPABASE_KEY=SUA_SUPABASE_ANON_KEY
# Adicione outras chaves conforme necessário (Gemini API Key, Twilio SID/Token, etc.)
GEMINI_API_KEY=SUA_GEMINI_API_KEY
TWILIO_ACCOUNT_SID=SEU_TWILIO_SID
TWILIO_AUTH_TOKEN=SEU_TWILIO_AUTH_TOKEN
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886 # Número sandbox Twilio ou seu número comprado
FLASK_SECRET_KEY=UMA_CHAVE_SECRETA_FORTE_E_ALEATORIA
```

Agora, vamos editar o arquivo `src/main.py` para inicializar o Flask e o SQLAlchemy, carregando a configuração do banco de dados a partir do arquivo `.env`. Também configuraremos o CORS para permitir requisições do nosso frontend React.

```python
# src/main.py
import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv

# Adiciona o diretório pai ao sys.path - NÃO ALTERE!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

load_dotenv() # Carrega variáveis do .env

app = Flask(__name__)
CORS(app) # Habilita CORS para todas as origens por enquanto (ajuste em produção)

# Configuração do Banco de Dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

db = SQLAlchemy(app)

# Importar modelos e rotas (após inicializar db)
# from src.models import Dealership, Vehicle # Exemplo
# from src.routes import main_bp # Exemplo

# Registrar Blueprints (rotas)
# app.register_blueprint(main_bp)

@app.route('/')
def hello():
    return "Backend do Agente de Concessionária está no ar!"

if __name__ == '__main__':
    # Para desenvolvimento, escute em todas as interfaces
    app.run(host='0.0.0.0', port=5001, debug=True)

```

Em seguida, definiremos os modelos do banco de dados em `src/models.py`, representando as tabelas `dealerships` e `vehicles`. Usaremos o SQLAlchemy ORM para mapear classes Python para tabelas do banco de dados.

```python
# src/models.py
from src.main import db # Importa a instância db de main.py
from datetime import datetime

class Dealership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    whatsapp_number = db.Column(db.String(20), unique=True, nullable=False) # Número associado
    # Adicione outros campos relevantes para a concessionária
    vehicles = db.relationship('Vehicle', backref='dealership', lazy=True)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dealership_id = db.Column(db.Integer, db.ForeignKey('dealership.id'), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    ano_fabricacao = db.Column(db.Integer)
    ano_modelo = db.Column(db.Integer)
    quilometragem = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(20)) # Novo, Usado
    preco = db.Column(db.Float)
    itens_opcionais = db.Column(db.Text) # Lista separada por ;
    cambio = db.Column(db.String(20)) # Manual, Automatico
    combustivel = db.Column(db.String(20)) # Flex, Gasolina, Diesel, Eletrico
    final_placa = db.Column(db.String(1))
    cor = db.Column(db.String(30))
    link_fotos = db.Column(db.Text) # URLs separadas por ;
    vendido = db.Column(db.Boolean, default=False, nullable=False)
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Vehicle {self.marca} {self.modelo} {self.ano_modelo}>'

# Não se esqueça de criar as tabelas no banco de dados!
# Dentro do shell Python (após ativar venv):
# from src.main import app, db
# with app.app_context():
#     db.create_all()
```

Finalmente, criaremos as rotas básicas da API em `src/routes.py`. Por enquanto, vamos apenas adicionar um endpoint de exemplo para listar veículos, que será expandido posteriormente para incluir upload de planilhas, cadastro manual e endpoints para o agente WhatsApp.

```python
# src/routes.py
from flask import Blueprint, jsonify, request
from src.main import db
from src.models import Vehicle, Dealership
import pandas as pd
import io

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    # Adicionar lógica de autenticação/autorização aqui!
    # Por enquanto, lista todos os veículos não vendidos
    vehicles = Vehicle.query.filter_by(vendido=False).all()
    output = []
    for vehicle in vehicles:
        vehicle_data = {
            'id': vehicle.id,
            'marca': vehicle.marca,
            'modelo': vehicle.modelo,
            'ano_modelo': vehicle.ano_modelo,
            'preco': vehicle.preco,
            'quilometragem': vehicle.quilometragem,
            'cor': vehicle.cor,
            'cambio': vehicle.cambio,
            'combustivel': vehicle.combustivel,
            'final_placa': vehicle.final_placa,
            'itens_opcionais': vehicle.itens_opcionais,
            'link_fotos': vehicle.link_fotos,
            'dealership_id': vehicle.dealership_id
        }
        output.append(vehicle_data)
    return jsonify({'vehicles': output})

# Rota para upload de planilha (exemplo inicial)
@main_bp.route('/api/upload/vehicles', methods=['POST'])
def upload_vehicles():
    # Adicionar lógica de autenticação para garantir que apenas a concessionária correta suba
    dealership_id = 1 # Exemplo - obter o ID da concessionária autenticada
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nome de arquivo vazio'}), 400
    
    if file and (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
        try:
            if file.filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file.read()))
            else: # .xlsx
                df = pd.read_excel(io.BytesIO(file.read()))

            # Processar o DataFrame (df)
            for index, row in df.iterrows():
                # Validação básica e mapeamento de colunas
                # Certifique-se que os nomes das colunas no CSV/Excel correspondem
                # Adicione tratamento de erros (ex: valores ausentes, tipos incorretos)
                new_vehicle = Vehicle(
                    dealership_id=dealership_id,
                    marca=row.get('Marca'),
                    modelo=row.get('Modelo'),
                    ano_fabricacao=row.get('Ano Fabricacao'),
                    ano_modelo=row.get('Ano Modelo'),
                    quilometragem=row.get('Quilometragem'),
                    estado=row.get('Estado'),
                    preco=row.get('Preco'),
                    itens_opcionais=row.get('Itens Opcionais'),
                    cambio=row.get('Cambio'),
                    combustivel=row.get('Combustivel'),
                    final_placa=str(row.get('Final Placa')) if pd.notna(row.get('Final Placa')) else None,
                    cor=row.get('Cor'),
                    link_fotos=row.get('Link Fotos (Separados por ;)'),
                    vendido=str(row.get('Vendido (SIM/NAO)')).upper() == 'SIM'
                )
                db.session.add(new_vehicle)
            
            db.session.commit()
            return jsonify({'message': f'{len(df)} veículos processados com sucesso!'}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Erro ao processar arquivo: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Formato de arquivo inválido. Use CSV ou XLSX.'}), 400

# Não se esqueça de registrar o blueprint em main.py:
# from src.routes import main_bp
# app.register_blueprint(main_bp)
```

Lembre-se de importar e registrar o `main_bp` no final do arquivo `src/main.py` e de executar o comando `db.create_all()` dentro de um contexto Flask para criar as tabelas no seu banco de dados Supabase pela primeira vez. Com isso, temos a estrutura básica do nosso backend pronta para ser expandida com as funcionalidades de IA e WhatsApp nos próximos capítulos.



## Desenvolvendo o Painel de Controle com React

Com o backend estruturado, podemos agora voltar nossa atenção para a interface que as concessionárias utilizarão para gerenciar seus veículos: o painel de controle web. Conforme solicitado, utilizaremos React, uma biblioteca JavaScript popular para construir interfaces de usuário interativas. Para agilizar o desenvolvimento e garantir um visual moderno, empregaremos o template `create_react_app` (ou uma ferramenta similar como Vite com template React) e bibliotecas de componentes como Tailwind CSS e shadcn/ui.

Primeiro, navegaremos até a pasta `frontend` e inicializaremos nosso projeto React. Usaremos `npm` ou `pnpm` (se disponível e preferido) como gerenciador de pacotes.

```bash
cd ../frontend # Voltando para a raiz do projeto e entrando em frontend
# Usando npm (padrão)
npm create vite@latest . -- --template react # Cria na pasta atual usando Vite com React
# Ou usando create-react-app (mais antigo, pode precisar de ajustes)
# npx create-react-app .

npm install
# Instalar dependências adicionais: axios para chamadas API, react-router-dom para navegação
npm install axios react-router-dom
# Instalar Tailwind CSS e shadcn/ui (siga os guias oficiais deles para integração com Vite/CRA)
# Exemplo para Vite + Tailwind: https://tailwindcss.com/docs/guides/vite
# Exemplo para shadcn/ui: https://ui.shadcn.com/docs/installation/vite
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
# Configure tailwind.config.js e index.css
# ... (instalação shadcn/ui) ...
```

Após a instalação, a estrutura básica do projeto React estará criada. O ponto de entrada principal será `src/main.jsx` (ou `src/index.js`) e o componente principal da aplicação será `src/App.jsx`. Precisaremos estruturar nossa aplicação com rotas para diferentes seções do painel, como login, dashboard, lista de veículos, formulário de cadastro/edição e upload de planilha. Utilizaremos `react-router-dom` para gerenciar essas rotas.

Vamos criar alguns componentes básicos. Por exemplo, um componente de Login (`src/components/Login.jsx`) que captura email e senha e envia para um endpoint de autenticação no backend (que precisaremos criar no Flask, possivelmente usando Flask-Login ou gerenciando tokens JWT). Um componente para listar veículos (`src/components/VehicleList.jsx`) que busca os dados da API `/api/vehicles` que criamos no backend e os exibe em uma tabela. Um formulário (`src/components/VehicleForm.jsx`) para adicionar ou editar veículos, enviando os dados para endpoints correspondentes no backend. E, crucialmente, um componente para upload de planilhas (`src/components/UploadForm.jsx`) que utiliza um input do tipo `file` e envia o arquivo selecionado para o endpoint `/api/upload/vehicles`.

Para a comunicação com o backend Flask (que estará rodando, durante o desenvolvimento, em `http://localhost:5001`), utilizaremos a biblioteca `axios`. É importante configurar uma instância base do axios ou gerenciar a URL base da API, especialmente ao preparar para o deploy.

Exemplo de chamada API com Axios em um componente React:

```jsx
// Em src/components/VehicleList.jsx (exemplo simplificado)
import React, { useState, useEffect } from 'react';
import axios from 'axios';

function VehicleList() {
    const [vehicles, setVehicles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchVehicles = async () => {
            try {
                // Certifique-se que a URL base está correta para dev/prod
                const response = await axios.get('http://localhost:5001/api/vehicles'); 
                setVehicles(response.data.vehicles);
                setLoading(false);
            } catch (err) {
                setError('Erro ao buscar veículos.');
                setLoading(false);
                console.error(err);
            }
        };

        fetchVehicles();
    }, []);

    if (loading) return <p>Carregando...</p>;
    if (error) return <p>{error}</p>;

    return (
        <div>
            <h2>Lista de Veículos Disponíveis</h2>
            {/* Renderize a lista/tabela de veículos aqui */}
            <ul>
                {vehicles.map(vehicle => (
                    <li key={vehicle.id}>{vehicle.marca} {vehicle.modelo} - R$ {vehicle.preco}</li>
                ))}
            </ul>
        </div>
    );
}

export default VehicleList;
```

O desenvolvimento do frontend envolverá a criação desses e outros componentes, estilização com Tailwind/shadcn, gerenciamento de estado (talvez com Context API ou Zustand para estados mais complexos como autenticação) e a integração completa com todos os endpoints necessários do backend Flask. Lembre-se de implementar a lógica de autenticação para proteger as rotas do painel e garantir que cada concessionária só veja e gerencie seus próprios veículos.

## Integrando o Agente com WhatsApp: Opções de Número

A funcionalidade central do nosso projeto é a interação via WhatsApp. Para conectar nosso agente à plataforma WhatsApp, utilizaremos a API oficial, preferencialmente através de um Provedor de Soluções de Negócios (BSP) como o Twilio, que simplifica a integração e o gerenciamento. Uma decisão crucial no início é definir qual número de telefone será usado para o agente de IA da concessionária. Existem duas abordagens principais:

**Opção 1: Utilizar um Número de Telefone Existente da Concessionária**

Muitas concessionárias já possuem um número de WhatsApp conhecido pelos clientes. Utilizar este número para o agente pode oferecer uma transição mais suave para os clientes.

*   **Requisitos:** Este processo, frequentemente chamado de "portabilidade" ou BYON (Bring Your Own Number) para a API do WhatsApp Business, é mais complexo. Exige que:
    *   A concessionária possua uma conta verificada no Gerenciador de Negócios da Meta (Meta Business Manager).
    *   O número de telefone (fixo ou móvel) possa receber chamadas ou SMS para verificação.
    *   **Importante:** O número a ser migrado para a API **não pode** estar ativo no aplicativo WhatsApp convencional ou no WhatsApp Business App simultaneamente. Ele será dedicado exclusivamente ao uso via API. A concessionária perderá o acesso à interface do aplicativo usual para aquele número específico.
*   **Processo (Simplificado via Twilio):**
    1.  A concessionária inicia o processo através do console do Twilio (ou do BSP escolhido), vinculando sua conta do Meta Business Manager.
    2.  O número desejado é registrado e passa por um processo de verificação pela Meta.
    3.  Pode haver um período de aprovação e configuração.
    4.  Após a aprovação, o número estará vinculado à conta Twilio e pronto para ser usado pela API.
*   **Vantagens:** Mantém o número já conhecido pelos clientes.
*   **Desvantagens:** Processo burocrático, perda do acesso ao app WhatsApp para aquele número, requisitos de verificação da empresa pela Meta.

**Opção 2: Adquirir um Novo Número de Telefone**

Esta opção envolve obter um novo número especificamente para ser usado com a API do WhatsApp Business.

*   **Requisitos:** Menos complexo em termos de burocracia da Meta inicialmente.
    *   Você pode adquirir um número virtual habilitado para voz/SMS através do próprio Twilio ou de outros provedores.
    *   Este novo número será então registrado na plataforma WhatsApp Business API através do Twilio.
*   **Processo (Simplificado via Twilio):**
    1.  Adquira um número de telefone no console do Twilio (ou adicione um número externo que você controla).
    2.  Associe este número ao seu perfil de remetente do WhatsApp no Twilio.
    3.  Complete o processo de registro e verificação (geralmente mais simples para um número novo dedicado).
*   **Vantagens:** Processo de configuração inicial mais rápido e simples, não interfere no uso de outros números existentes pela concessionária nos aplicativos WhatsApp.
*   **Desvantagens:** A concessionária precisará divulgar este novo número aos clientes como o canal para interagir com o agente de IA.

**Recomendação para o MVP:**
Para um MVP e visando simplicidade inicial, a **Opção 2 (Novo Número)** é frequentemente mais rápida de implementar, especialmente usando o Sandbox do Twilio para testes ou adquirindo um número diretamente pelo Twilio. A Opção 1 pode ser considerada posteriormente ou se for um requisito absoluto da concessionária, estando ciente das implicações.

**Configuração Técnica (Com Twilio):**
Independentemente da opção escolhida, o processo técnico subsequente envolve:
1.  Criar uma conta no Twilio (twilio.com).
2.  Obter seu `Account SID` e `Auth Token` (guardar no `.env`).
3.  Configurar o perfil do remetente do WhatsApp (seja com número novo ou portado).
4.  Configurar um **Webhook** no Twilio: Na seção do WhatsApp (Sandbox ou número comprado), no campo "WHEN A MESSAGE COMES IN" (ou configuração similar), insira a URL pública do seu endpoint de webhook no backend Flask. Durante o desenvolvimento local, use `ngrok` para expor sua porta local (5001) e obter uma URL pública temporária (ex: `https://<id_unico>.ngrok.io/whatsapp/webhook`). Em produção, será a URL do seu backend deployado (ex: `https://seu-app-backend.fly.dev/whatsapp/webhook`).

Agora, vamos criar esse endpoint de webhook no backend Flask (`src/routes.py`). Ele receberá as mensagens via POST do Twilio, processará a mensagem e enviará uma resposta.

```python
# Adicionar ao src/routes.py
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os
# Importar a lógica de IA que criaremos depois
# from src.ai_processor import process_message_with_ai 

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_client = Client(account_sid, auth_token)
twilio_whatsapp_number = os.getenv('TWILIO_WHATSAPP_NUMBER')

@main_bp.route("/whatsapp/webhook", methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').lower()
    sender_phone_number = request.values.get('From', '') # Número do cliente (ex: whatsapp:+5511999998888)
    
    print(f"Mensagem recebida de {sender_phone_number}: {incoming_msg}")

    # 1. Identificar a concessionária (ex: pelo número para o qual a msg foi enviada, se tiver múltiplos números Twilio, ou por lógica interna)
    # Por simplicidade, vamos assumir uma única concessionária no MVP ou uma lógica fixa
    dealership_id = 1 # Obter o ID correto da concessionária

    # 2. Processar a mensagem com a IA (próximo capítulo)
    # response_text = process_message_with_ai(dealership_id, incoming_msg)
    # Placeholder enquanto não temos a IA:
    if "corolla" in incoming_msg:
        response_text = "Estamos verificando nosso estoque de Corolla para você..."
        # Aqui, futuramente, a IA chamaria a busca no DB
    elif "oi" in incoming_msg or "olá" in incoming_msg:
        response_text = "Olá! Como posso ajudar você a encontrar seu próximo carro hoje?"
    else:
        response_text = "Desculpe, não entendi sua pergunta. Você pode perguntar sobre modelos, marcas ou faixas de preço de veículos."

    # 3. Enviar a resposta usando a API do Twilio (ou TwiML)
    # Usando TwiML (resposta síncrona simples)
    response = MessagingResponse()
    response.message(response_text)
    return str(response)

    # Alternativa: Usando a API REST (para respostas assíncronas ou mais complexas)
    # try:
    #     message = twilio_client.messages.create(
    #         from_=twilio_whatsapp_number,
    #         body=response_text,
    #         to=sender_phone_number
    #     )
    #     print(f"Resposta enviada, SID: {message.sid}")
    #     return '', 204 # Retorna sucesso sem conteúdo para o Twilio
    # except Exception as e:
    #     print(f"Erro ao enviar mensagem via Twilio: {e}")
    #     return '', 500
```

Este código configura o webhook. Ele recebe a mensagem, identifica o remetente e, por enquanto, usa uma lógica simples de palavras-chave para responder. O próximo passo crucial é substituir essa lógica placeholder pela integração com a IA para uma compreensão e resposta muito mais sofisticadas.

## Integrando Inteligência Artificial com Google Gemini

Para que nosso agente possa entender perguntas em linguagem natural e buscar informações relevantes no banco de dados, precisamos integrar um modelo de IA conversacional. Conforme nossa pesquisa e decisão, utilizaremos a API do Google Gemini (especificamente, o modelo `gemini-pro` que é adequado para tarefas de conversação e raciocínio) através do seu SDK Python.

Primeiro, certifique-se de que a biblioteca `google-generativeai` está instalada (já fizemos isso ao configurar o backend) e que sua `GEMINI_API_KEY` está no arquivo `.env`. Obtenha sua chave de API no Google AI Studio (makersuite.google.com).

Criaremos um novo arquivo, `src/ai_processor.py`, para encapsular a lógica de interação com a API Gemini e a busca no banco de dados.

```python
# src/ai_processor.py
import google.generativeai as genai
import os
from src.main import db
from src.models import Vehicle, Dealership
from sqlalchemy import or_

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

def format_vehicles_for_llm(vehicles):
    if not vehicles:
        return "Nenhum veículo encontrado com essas características."
    
    response = "Encontrei essas opções para você:\n\n"
    for v in vehicles:
        response += f"- {v.marca} {v.modelo} {v.ano_modelo}, Cor: {v.cor}, KM: {v.quilometragem}, Preço: R$ {v.preco:.2f}\n"
        # Adicionar mais detalhes se necessário
    return response

def search_vehicles_in_db(dealership_id, query_params):
    """Busca veículos no DB com base nos parâmetros extraídos pela IA."""
    base_query = Vehicle.query.filter_by(dealership_id=dealership_id, vendido=False)

    # Aplicar filtros baseados em query_params (extraídos pela IA)
    if query_params.get('modelo'):
        base_query = base_query.filter(Vehicle.modelo.ilike(f"%{query_params['modelo']}%"))
    if query_params.get('marca'):
        base_query = base_query.filter(Vehicle.marca.ilike(f"%{query_params['marca']}%"))
    if query_params.get('preco_max'):
        base_query = base_query.filter(Vehicle.preco <= query_params['preco_max'])
    if query_params.get('preco_min'):
        base_query = base_query.filter(Vehicle.preco >= query_params['preco_min'])
    if query_params.get('ano_min'):
        base_query = base_query.filter(Vehicle.ano_modelo >= query_params['ano_min'])
    # Adicionar mais filtros conforme necessário (cor, km, etc.)

    vehicles = base_query.limit(5).all() # Limitar resultados por enquanto
    return vehicles

def process_message_with_ai(dealership_id, user_message):
    """Processa a mensagem do usuário usando Gemini e busca no DB."""
    
    # Obter informações da concessionária (se necessário para o prompt)
    dealership = Dealership.query.get(dealership_id)
    if not dealership:
        return "Desculpe, não consegui identificar a concessionária."

    # Prompt para o Gemini extrair parâmetros de busca
    # Este prompt é crucial e precisa ser refinado!
    prompt = f"""
    Você é um assistente de vendas da concessionária '{dealership.name}'. 
    Analise a mensagem do cliente e extraia os seguintes parâmetros de busca de veículos, se mencionados:
    - marca (string)
    - modelo (string)
    - ano_min (integer)
    - ano_max (integer)
    - preco_min (float)
    - preco_max (float)
    - cor (string)
    - quilometragem_max (integer)
    
    Retorne APENAS um objeto JSON com os parâmetros extraídos. Se nenhum parâmetro for identificado, retorne um JSON vazio {{}}.
    Se a mensagem for uma saudação ou pergunta genérica, retorne {{"intent": "greeting"}}.
    Se a mensagem não parecer relacionada a busca de carros, retorne {{"intent": "other"}}.

    Mensagem do cliente: "{user_message}"
    
    JSON:
    """

    try:
        # Chamada para a API Gemini
        response = model.generate_content(prompt)
        
        # Extrair o JSON da resposta (pode precisar de tratamento de erros/parsing)
        json_response_text = response.text.strip().replace('`', '') # Limpeza básica
        if json_response_text.startswith("json"): # Remover possível prefixo 'json'
            json_response_text = json_response_text[4:].strip()
        
        print(f"Resposta Gemini (JSON bruto): {json_response_text}")
        import json
        try:
            extracted_params = json.loads(json_response_text)
        except json.JSONDecodeError:
            print("Erro ao decodificar JSON do Gemini")
            extracted_params = {"intent": "fallback"} # Falha no parsing

        # Lógica baseada nos parâmetros extraídos
        if extracted_params.get("intent") == "greeting":
            return f"Olá! Bem-vindo à {dealership.name}. Como posso ajudar você a encontrar seu próximo carro?"
        elif extracted_params.get("intent") == "other" or extracted_params.get("intent") == "fallback":
             return f"Entendido. Se precisar de ajuda para buscar um veículo em nosso estoque, é só me dizer a marca, modelo ou faixa de preço que procura."
        elif not extracted_params: # JSON vazio, nenhum parâmetro
            return "Não entendi quais características de veículo você procura. Pode me dar mais detalhes como marca, modelo ou preço?"
        else:
            # Realizar a busca no banco de dados
            vehicles_found = search_vehicles_in_db(dealership_id, extracted_params)
            # Formatar a resposta
            return format_vehicles_for_llm(vehicles_found)

    except Exception as e:
        print(f"Erro ao chamar a API Gemini ou processar a resposta: {e}")
        # Fallback em caso de erro na IA
        return "Desculpe, estou com dificuldades para processar sua solicitação no momento. Tente novamente mais tarde ou pergunte de forma mais simples."

```

Agora, precisamos atualizar nosso webhook em `src/routes.py` para usar esta nova função:

```python
# Em src/routes.py, dentro da função whatsapp_webhook():
# Substitua a lógica placeholder por:
from src.ai_processor import process_message_with_ai # Importe no início do arquivo

# ... (código anterior do webhook)

    # 2. Processar a mensagem com a IA
    response_text = process_message_with_ai(dealership_id, incoming_msg)

    # 3. Enviar a resposta usando a API do Twilio (ou TwiML)
    response = MessagingResponse()
    response.message(response_text)
    return str(response)

# ... (restante do código)
```

Com esta integração, o agente agora utiliza o Gemini para interpretar a mensagem do usuário, extrair parâmetros de busca, consultar o banco de dados e formular uma resposta relevante. O prompt enviado ao Gemini é um ponto chave e provavelmente precisará de vários ajustes e refinamentos para cobrir diferentes formas de perguntar e extrair os parâmetros corretamente.

## Deploy da Aplicação

Após desenvolver e testar localmente, o último passo é colocar nossa aplicação no ar. Faremos o deploy dos componentes separadamente, utilizando os serviços com free tier que escolhemos.

1.  **Deploy do Backend Flask (Fly.io ou Render):**
    *   **Preparação:** Certifique-se que seu `requirements.txt` está atualizado (`pip freeze > requirements.txt`). Crie um `Procfile` na raiz da pasta `backend` para indicar ao serviço como rodar sua aplicação: `web: gunicorn 'src.main:app'`. (Instale gunicorn: `pip install gunicorn` e adicione ao `requirements.txt`). Verifique se `src/main.py` está configurado para rodar em `host='0.0.0.0'` e a porta é definida por uma variável de ambiente (ex: `port=int(os.environ.get("PORT", 5001))`).
    *   **Fly.io:** Instale o `flyctl`, faça login (`fly auth login`), navegue até a pasta `backend` e execute `fly launch`. Siga as instruções, selecionando a região e configurando segredos (variáveis de ambiente como `DATABASE_URL`, `GEMINI_API_KEY`, etc.) com `fly secrets set VAR=VALOR`.
    *   **Render:** Conecte sua conta Render ao seu repositório Git (GitHub, GitLab). Crie um novo "Web Service", aponte para o repositório e a pasta `backend`, configure o comando de build (`pip install -r requirements.txt`) e o comando de start (`gunicorn 'src.main:app'`). Adicione as variáveis de ambiente na interface do Render.
    *   **Após o Deploy:** Anote a URL pública do seu backend (ex: `https://seu-app-backend.fly.dev`).

2.  **Deploy do Frontend React (Vercel ou Netlify):**
    *   **Preparação:** Certifique-se que seu código React faz chamadas para a URL *pública* do backend deployado, não mais `localhost:5001`. Você pode usar variáveis de ambiente (`process.env.REACT_APP_API_URL`) para gerenciar isso.
    *   **Vercel/Netlify:** Conecte sua conta ao seu repositório Git. Crie um novo projeto, aponte para o repositório e a pasta `frontend`. Configure o comando de build (geralmente `npm run build` ou `vite build`) e o diretório de publicação (geralmente `build` ou `dist`). Adicione as variáveis de ambiente necessárias (como `REACT_APP_API_URL`) na interface da plataforma.
    *   **Após o Deploy:** Anote a URL pública do seu frontend (ex: `https://seu-painel.vercel.app`).

3.  **Configuração Final:**
    *   **Supabase:** Certifique-se que as regras de Row Level Security (RLS) estão configuradas adequadamente para produção, garantindo que cada concessionária só acesse seus próprios dados.
    *   **Twilio:** Atualize a URL do webhook do WhatsApp para apontar para a URL pública do seu backend deployado (ex: `https://seu-app-backend.fly.dev/whatsapp/webhook`).
    *   **DNS (Opcional):** Se você tiver um domínio próprio, pode configurá-lo para apontar para as URLs do Vercel/Netlify e Fly.io/Render.

## Conclusão e Próximos Passos

Seguindo este guia, construímos um MVP funcional de um Agente de IA para concessionárias. Ele é capaz de responder perguntas básicas sobre veículos via WhatsApp, utilizando IA para compreensão e busca em banco de dados, e oferece um painel web para gerenciamento do inventário. A arquitetura priorizou o baixo custo inicial através do uso estratégico de níveis gratuitos.

Este MVP é apenas o começo. Existem muitas melhorias e funcionalidades que podem ser adicionadas, como:
*   **Melhoria da IA:** Refinamento contínuo do prompt do Gemini, tratamento de diálogos mais complexos (múltiplas perguntas, contexto da conversa), suporte a mais intenções (agendar visita, solicitar simulação).
*   **Funcionalidades do Painel:** Relatórios mais detalhados (conversões, mensagens por período), gerenciamento de usuários da concessionária, edição de veículos em lote, integração com outros sistemas da concessionária.
*   **Robustez e Escalabilidade:** Implementação de testes automatizados, monitoramento, logging mais detalhado, otimizações de banco de dados, estratégias de cache, migração para planos pagos dos serviços conforme o crescimento.
*   **Integração de Fotos:** Exibição e envio das fotos dos veículos via WhatsApp (requer APIs específicas).
*   **Autenticação Segura:** Implementação completa de autenticação JWT ou baseada em sessão para o painel e APIs.

Este projeto demonstra o potencial da combinação de IA conversacional, APIs de comunicação e desenvolvimento web para criar soluções práticas e de baixo custo para negócios específicos. Esperamos que este guia sirva como um ponto de partida sólido para o desenvolvimento do seu agente.
