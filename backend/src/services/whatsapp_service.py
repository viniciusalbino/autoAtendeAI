from flask import jsonify, current_app
from src.integrations.whatsapp_api import send_whatsapp_message
from src.ai_processor import process_message_with_ai
from src.models import Dealership, Vehicle
from sqlalchemy import or_, and_

def handle_whatsapp_webhook(request):
    try:
        data = request.get_json()
        current_app.logger.info(f"Payload recebido: {data}")
        if not data or 'entry' not in data:
            return jsonify({'error': 'Invalid webhook payload'}), 400
        entry = data['entry'][0]
        changes = entry.get('changes', [])
        if not changes:
            return jsonify({'error': 'No changes in webhook payload'}), 400
        value = changes[0].get('value', {})
        messages = value.get('messages', [])
        if not messages:
            # É um status, não uma mensagem de usuário
            return jsonify({'status': 'ignored'}), 200
        message = messages[0]
        sender_phone_number = message['from']
        
        # Trata diferentes tipos de mensagem
        if message.get('type') == 'interactive':
            interactive = message['interactive']
            if interactive.get('type') == 'button_reply':
                button_id = interactive['button_reply']['id']
                button_title = interactive['button_reply']['title'].strip().lower()
                
                # Trata cliques específicos nos botões
                if button_id.startswith('quero_saber_mais_'):
                    modelo = button_id.replace('quero_saber_mais_', '').replace('*', '').strip()
                    dealership = Dealership.query.first()
                    if dealership:
                        veiculo = Vehicle.query.filter(
                            and_(
                                Vehicle.dealership_id == dealership.id,
                                Vehicle.modelo.ilike(f"%{modelo}%"),
                                Vehicle.vendido == False
                            )
                        ).first()
                        if veiculo:
                            mensagem = f"*{veiculo.marca} {veiculo.modelo} {veiculo.ano_modelo}*\n\n" \
                                       f"Características Técnicas:\n" \
                                       f"• Motor: {veiculo.motor if hasattr(veiculo, 'motor') else 'Não informado'}\n" \
                                       f"• Câmbio: {veiculo.cambio}\n" \
                                       f"• Combustível: {veiculo.combustivel}\n" \
                                       f"• Quilometragem: {veiculo.quilometragem:,} km\n\n" \
                                       f"Itens de Série:\n" \
                                       f"• {veiculo.itens_opcionais.replace(';', '\n• ') if veiculo.itens_opcionais else 'Não informado'}\n\n" \
                                       f"Preço: R$ {veiculo.preco:,.2f}\n\n" \
                                       f"Gostaria de:\n" \
                                       f"• Ver mais fotos?"
                            send_whatsapp_message(sender_phone_number, mensagem)
                            # Se houver fotos, envia a primeira
                            if veiculo.link_fotos:
                                fotos = [url.strip() for url in veiculo.link_fotos.split(';') if url.strip()]
                                if fotos:
                                    send_whatsapp_message(sender_phone_number, "Aqui está uma foto do veículo:", fotos[0])
                            # Botão para ver mais fotos
                            buttons = [
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": f"ver_mais_fotos_{veiculo.modelo.lower()}",
                                        "title": "Ver mais fotos"
                                    }
                                },
                                {
                                    "type": "reply",
                                    "reply": {
                                        "id": "nao_obrigado",
                                        "title": "Não, obrigado"
                                    }
                                }
                            ]
                            send_whatsapp_message(sender_phone_number, "O que deseja fazer agora?", buttons=buttons)
                        else:
                            mensagem = f"Desculpe, não encontrei informações detalhadas sobre o {modelo}. " \
                                     f"Posso te ajudar com outro modelo?"
                            send_whatsapp_message(sender_phone_number, mensagem)
                    else:
                        mensagem = "Desculpe, houve um erro ao buscar as informações. Tente novamente mais tarde."
                        send_whatsapp_message(sender_phone_number, mensagem)
                    return jsonify({'status': 'ok'})
                elif button_id.startswith('ver_mais_fotos_'):
                    modelo = button_id.replace('ver_mais_fotos_', '').replace('*', '').strip()
                    dealership = Dealership.query.first()
                    if dealership:
                        veiculo = Vehicle.query.filter(
                            and_(
                                Vehicle.dealership_id == dealership.id,
                                Vehicle.modelo.ilike(f"%{modelo}%"),
                                Vehicle.vendido == False
                            )
                        ).first()
                        if veiculo and veiculo.link_fotos:
                            fotos = [url.strip() for url in veiculo.link_fotos.split(';') if url.strip()]
                            if fotos:
                                for idx, foto in enumerate(fotos):
                                    send_whatsapp_message(sender_phone_number, f"Foto {idx+1} do {veiculo.modelo}", foto)
                            else:
                                send_whatsapp_message(sender_phone_number, "Não há mais fotos disponíveis para este veículo.")
                        else:
                            send_whatsapp_message(sender_phone_number, "Não há mais fotos disponíveis para este veículo.")
                    else:
                        send_whatsapp_message(sender_phone_number, "Desculpe, houve um erro ao buscar as fotos. Tente novamente mais tarde.")
                    return jsonify({'status': 'ok'})
                elif button_id == 'nao_obrigado':
                    mensagem = "Entendi! Se precisar de mais informações sobre nossos veículos, é só me chamar. " \
                             "Estou à disposição para ajudar você a encontrar o carro ideal! 😊"
                    send_whatsapp_message(sender_phone_number, mensagem)
                    return jsonify({'status': 'ok'})
                incoming_msg = button_title
            elif interactive.get('type') == 'list_reply':
                incoming_msg = interactive['list_reply']['title'].strip().lower()
            else:
                incoming_msg = ''
        elif message.get('type') == 'text':
            incoming_msg = message['text']['body'].strip().lower()
        else:
            incoming_msg = ''
            
        dealership = Dealership.query.first()
        if not dealership:
            return jsonify({'error': 'Dealership not found'}), 404
            
        resposta = process_message_with_ai(dealership.id, incoming_msg)
        # Só envia botões se houver veículos encontrados
        if isinstance(resposta, list) and resposta and not resposta[0]['text'].startswith('😕'):
            primeiro_veiculo = resposta[0]
            mensagem = primeiro_veiculo['text']
            buttons = [
                {
                    "type": "reply",
                    "reply": {
                        "id": f"quero_saber_mais_{primeiro_veiculo['text'].split()[1].lower()}",
                        "title": "Quero saber mais"
                    }
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": f"ver_mais_fotos_{primeiro_veiculo['text'].split()[1].lower()}",
                        "title": "Ver mais fotos"
                    }
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": "nao_obrigado",
                        "title": "Não, obrigado"
                    }
                }
            ]
            send_whatsapp_message(sender_phone_number, mensagem, buttons=buttons)
        else:
            # Garante que sempre envia texto puro
            if isinstance(resposta, list) and resposta:
                send_whatsapp_message(sender_phone_number, resposta[0]['text'])
            elif isinstance(resposta, dict) and 'text' in resposta:
                send_whatsapp_message(sender_phone_number, resposta['text'])
            else:
                send_whatsapp_message(sender_phone_number, resposta)
        return jsonify({'status': 'ok'})
    except Exception as e:
        current_app.logger.error(f"Erro no webhook WhatsApp: {str(e)}")
        return jsonify({'error': str(e)}), 500 