import spacy
from pathlib import Path

class Chatbot:
    def __init__(self, model_path="myfirstmodel/model-best"):
        try:
            self.nlp = spacy.load(model_path)
            print("Modelo carregado com sucesso")
            
            self.required_entities = {
                "ligar": ["ROOM"],
                "desligar": ["ROOM"], 
                "diminuir_temp": ["ROOM", "VALUE"],
                "aumentar_temp": ["ROOM", "VALUE"],
                "consultar_temp": ["ROOM"],
                "setar_temp": ["ROOM", "VALUE"]
            }
            
        except Exception as e:
            print(f"Erro ao carregar o modelo: {e}")
            exit()

    def model_analysis(self, text):
        doc = self.nlp(text)
        intent = max(doc.cats.items(), key=lambda x: x[1])[0] if doc.cats else None
        entities = {ent.label_: ent.text for ent in doc.ents}
        
        return intent, entities

    def get_missing_entities(self, intent, entities):
        if intent not in self.required_entities:
            return []
        
        missing = []
        for entity in self.required_entities[intent]:
            if entity not in entities:
                missing.append(entity)
        
        return missing

    def ask_for_missing_entities(self, missing_entities):
        questions = {
            "ROOM": "De qual sala você está falando?",
            "VALUE": "Quantos graus deseja ajustar?"
        }
        
        responses = {}
        for entity in missing_entities:
            if entity in questions:
                response = input(f"Chat: {questions[entity]} ")
                responses[entity] = response
        
        return responses

    def generate_response(self, intent, entities):
        if intent == "ligar":
            return f"Ok, ligando o ar condicionado da sala {entities['ROOM']}."
        elif intent == "desligar":
            return f"Ok, desligando o ar condicionado da sala {entities['ROOM']}."
        elif intent == "diminuir_temp":
            return f"Ok, diminuindo a temperatura da sala {entities['ROOM']} em {entities['VALUE']} graus."
        elif intent == "aumentar_temp":
            return f"Ok, aumentando a temperatura da sala {entities['ROOM']} em {entities['VALUE']} graus."
        elif intent == "consultar_temp":
            return f"Ok, consultarei a temperatura atual da sala {entities['ROOM']}"
        elif intent == "setar_temp":
            return f"Ok, ajustarei a temperatura da sala {entities['ROOM']} em {entities['VALUE']} graus."
        else:
            return "Desculpe, não entendi o que você quer fazer."

    def start_chat(self):
        print("Chat: Olá! Como posso ajudar? (Digite 'sair' para encerrar)")
        
        while True:
            user_input = input("Usuário: ").strip()

            if user_input.lower() in ["sair", "exit", "tchau", "bye", "adeus", "fim"]:
                break

            intent, entities = self.model_analysis(user_input)
            
            if not intent:
                print("Chat: Comando não listado")
                continue
            
            missing_entities = self.get_missing_entities(intent, entities)
            
            if missing_entities:
                print(f"Chat: Entendi que você quer {intent.replace('_', ' ')}, mas preciso de mais informações.")
                additional_entities = self.ask_for_missing_entities(missing_entities)
                entities.update(additional_entities)
            
            response = self.generate_response(intent, entities)
            print(f"Chat: {response}")
        
        print("Chat: Até mais!")

if __name__ == "__main__":
    chat = Chatbot()      
    chat.start_chat()