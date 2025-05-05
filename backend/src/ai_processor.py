import google.generativeai as genai
import os
from src.models import Vehicle, Dealership
from src.database import db
from sqlalchemy import or_, and_
import json
import logging
import traceback

# Configura logger para imprimir no console
logger = logging.getLogger("ai_processor")
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Lista de opcionais conhecidos para busca
KNOWN_OPCIONAIS = [
    "ar condicionado", "direção hidráulica", "direção elétrica", "vidros elétricos", "teto solar", "rodas de liga leve", "banco de couro", "sensor de estacionamento", "câmera de ré", "piloto automático", "airbag", "freios abs", "multimídia", "gps", "alarme", "travas elétricas"
]

def log_ai_event(event: str, data: dict):
    logger.info(f"[AI Gemini] {event}: {json.dumps(data, ensure_ascii=False)}")

def format_vehicles_for_whatsapp(vehicles):
    if not vehicles:
        return [{
            'text': '😕 Não encontrei veículos com essas características. Tente mudar algum filtro ou peça ajuda!',
            'image': None
        }]
    results = []
    for v in vehicles:
        fotos = [url.strip() for url in (v.link_fotos or '').split(';') if url.strip()]
        image_url = fotos[0] if fotos else None
        text = f"*{v.marca} {v.modelo} {v.ano_modelo}*\n" \
               f"Preço: R$ {v.preco:,.2f}\n" \
               f"Cor: {v.cor}\n" \
               f"Quilometragem: {v.quilometragem:,} km\n" \
               f"Câmbio: {v.cambio}\n" \
               f"Combustível: {v.combustivel}\n" \
               f"Itens: {v.itens_opcionais if v.itens_opcionais else 'Não informado'}"
        results.append({
            'text': text,
            'image': image_url
        })
    return results

def search_vehicles_in_db(dealership_id, query_params):
    """Busca veículos no DB com base nos parâmetros extraídos pela IA."""
    base_query = Vehicle.query.filter_by(dealership_id=dealership_id, vendido=False)

    # Aplicar filtros baseados em query_params (extraídos pela IA)
    if query_params.get('modelo'):
        # Busca exata por modelo, evitando confusões (ex: Gol vs Golf)
        modelo = query_params['modelo'].strip().lower()
        base_query = base_query.filter(
            or_(
                Vehicle.modelo.ilike(f"{modelo}"),  # Busca exata
                Vehicle.modelo.ilike(f"{modelo} %"),  # Modelo seguido de espaço
                Vehicle.modelo.ilike(f"% {modelo}"),  # Modelo precedido de espaço
                Vehicle.modelo.ilike(f"% {modelo} %")  # Modelo entre espaços
            )
        )
    if query_params.get('marca'):
        marca = query_params['marca'].strip().lower()
        base_query = base_query.filter(
            or_(
                Vehicle.marca.ilike(f"{marca}"),  # Busca exata
                Vehicle.marca.ilike(f"{marca} %"),  # Marca seguida de espaço
                Vehicle.marca.ilike(f"% {marca}"),  # Marca precedida de espaço
                Vehicle.marca.ilike(f"% {marca} %")  # Marca entre espaços
            )
        )
    if query_params.get('preco_max'):
        base_query = base_query.filter(Vehicle.preco <= query_params['preco_max'])
    if query_params.get('preco_min'):
        base_query = base_query.filter(Vehicle.preco >= query_params['preco_min'])
    if query_params.get('ano_min'):
        base_query = base_query.filter(Vehicle.ano_modelo >= query_params['ano_min'])
    if query_params.get('ano_max'):
        base_query = base_query.filter(Vehicle.ano_modelo <= query_params['ano_max'])
    if query_params.get('cor'):
        cor = query_params['cor'].strip().lower()
        base_query = base_query.filter(Vehicle.cor.ilike(f"%{cor}%"))
    if query_params.get('quilometragem_max'):
        base_query = base_query.filter(Vehicle.quilometragem <= query_params['quilometragem_max'])

    vehicles = base_query.limit(5).all()  # Limitar resultados
    return vehicles

def process_message_with_ai(dealership_id, user_message):
    dealership = Dealership.query.get(dealership_id)
    if not dealership:
        log_ai_event("erro_concessionaria", {"dealership_id": dealership_id})
        return [{"text": "Desculpe, não consegui identificar a concessionária.", "image": None}]
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
    - opcionais (lista de strings, apenas se o cliente mencionar opcionais como ar condicionado, direção hidráulica, teto solar, etc)
    IMPORTANTE: Retorne APENAS um objeto JSON válido, sem explicações, sem comentários, sem texto extra.
    Se nenhum parâmetro for identificado, retorne um JSON vazio {{}}.
    Se a mensagem for uma saudação ou pergunta genérica, retorne {{"intent": "greeting"}}.
    Se a mensagem não parecer relacionada a busca de carros, retorne {{"intent": "other"}}.
    Mensagem do cliente: "{user_message}"
    JSON:
    """
    try:
        log_ai_event("prompt_enviado", {"prompt": prompt, "user_message": user_message})
        response = model.generate_content(prompt)
        raw_text = response.text.strip().replace('`', '')
        log_ai_event("resposta_bruta_gemini", {"raw_text": raw_text})
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:].strip()
        try:
            start = raw_text.find('{')
            end = raw_text.rfind('}') + 1
            json_candidate = raw_text[start:end] if start != -1 and end != -1 else raw_text
            extracted_params = json.loads(json_candidate)
            log_ai_event("parametros_extraidos", {"params": extracted_params})
        except Exception as e:
            log_ai_event("erro_json_parse", {"erro": str(e), "raw_text": raw_text, "trace": traceback.format_exc()})
            return [{"text": f"[DEBUG] Erro ao decodificar JSON: {str(e)}\nResposta bruta: {raw_text}", "image": None}]
        if extracted_params.get("intent") == "greeting":
            return [{"text": f"Olá! 👋 Bem-vindo à {dealership.name}. Como posso ajudar você a encontrar seu próximo carro? Me diga o que procura!", "image": None}]
        elif extracted_params.get("intent") in ["other", "fallback"]:
            return [{"text": "Entendido! Se precisar de ajuda para buscar um veículo, é só me dizer a marca, modelo, opcionais ou faixa de preço que procura. 😉", "image": None}]
        elif not extracted_params:
            return [{"text": "Não entendi quais características de veículo você procura. Pode me dar mais detalhes como marca, modelo, opcionais ou preço?", "image": None}]
        else:
            # Normalizar opcionais para busca
            if "opcionais" in extracted_params and isinstance(extracted_params["opcionais"], list):
                extracted_params["opcionais"] = [op.lower() for op in extracted_params["opcionais"] if op.lower() in KNOWN_OPCIONAIS]
            vehicles_found = search_vehicles_in_db(dealership_id, extracted_params)
            return format_vehicles_for_whatsapp(vehicles_found)
    except Exception as e:
        log_ai_event("erro_geral", {"erro": str(e), "trace": traceback.format_exc()})
        return [{"text": f"[DEBUG] Erro geral: {str(e)}\nTraceback: {traceback.format_exc()}", "image": None}] 