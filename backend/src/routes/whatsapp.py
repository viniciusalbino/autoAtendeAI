from flask import Blueprint, request, current_app
import os
from src.services.whatsapp_service import handle_whatsapp_webhook

whatsapp_bp = Blueprint('whatsapp', __name__)

@whatsapp_bp.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe' and token == verify_token:
            current_app.logger.info('Webhook verified successfully.')
            return challenge, 200
        else:
            current_app.logger.warning('Webhook verification failed.')
            return 'Verification token mismatch', 403
    # POST: já está implementado para receber mensagens
    return handle_whatsapp_webhook(request) 