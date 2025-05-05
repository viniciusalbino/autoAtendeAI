import os
import requests
from flask import current_app
import json

def send_whatsapp_message(to_number, message, image_url=None, buttons=None):
    """
    Envia uma mensagem usando a API do WhatsApp Business.
    
    Args:
        to_number (str): Número do destinatário no formato internacional (ex: 5511999999999)
        message (str): Texto da mensagem
        image_url (str, optional): URL da imagem a ser enviada
        buttons (list, optional): Lista de botões para mensagem interativa
    """
    try:
        # Remove prefixos e caracteres não numéricos
        to_number = to_number.replace('whatsapp:', '').replace('+', '').strip()
        
        # Configuração da API
        api_url = f"https://graph.facebook.com/v17.0/{os.getenv('WHATSAPP_PHONE_NUMBER_ID')}/messages"
        headers = {
            "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
            "Content-Type": "application/json"
        }
        
        # Prepara o payload base
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number
        }
        
        # Se tiver botões, cria mensagem interativa
        if buttons:
            payload["type"] = "interactive"
            payload["interactive"] = {
                "type": "button",
                "body": {
                    "text": message
                },
                "action": {
                    "buttons": buttons
                }
            }
        # Se tiver imagem, envia como mensagem com mídia
        elif image_url:
            payload["type"] = "image"
            payload["image"] = {
                "link": image_url,
                "caption": message
            }
        # Caso contrário, envia mensagem de texto simples
        else:
            payload["type"] = "text"
            payload["text"] = {
                "body": message
            }
        
        # Log detalhado do payload
        current_app.logger.info(f"Payload WhatsApp: {json.dumps(payload, ensure_ascii=False)}")
        
        # Faz a requisição
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        current_app.logger.info(f"Mensagem enviada com sucesso para {to_number}")
        return response.json()
        
    except Exception as e:
        current_app.logger.error(f"Erro ao enviar mensagem WhatsApp: {str(e)}")
        raise 