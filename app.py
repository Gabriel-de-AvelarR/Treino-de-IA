from flask import Flask, render_template, request, jsonify
from chatbot import Chatbot

app = Flask(__name__)
chatbot = Chatbot()

@app.route("/")
def index(): 
    return render_template("index.html")

@app.route("/chat", methods = ["POST"])
def chat():
    data = request.json
    user_input = data.get("message", "")

    intent, entities = chatbot.model_analysis(user_input)

    if not intent:
        return jsonify({"response": "Desculpa nao "})