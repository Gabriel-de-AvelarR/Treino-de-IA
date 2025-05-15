from flask import Blueprint, request, jsonify
from core import Chatbot

bp = Blueprint('chatbot_routes', __name__)

chatbot = Chatbot()

@bp.route('/api/chat', methods = ['POST'])
def chat():
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                "status": "error",
                "message": "Mensagem não recebida"
            }), 400
        
        user_message = data['message']
        state = data.get('state')
        response = chatbot.process_message(user_message, state)

        return jsonify(response)
    
    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Error interno: {str(e)}"
        }), 500