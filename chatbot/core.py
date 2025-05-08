import spacy
from pathlib import Path

class Chatbot:
    def __init__(self, model_path = None):
        try:
            default_models_dir = Path(__file__).parent.parent/"models"
            self.model_path = Path(model_path) if model_path else default_models_dir/"model-best"

            self.nlp = spacy.load(self.model_path)
            
            self.required_entities = {
                "ligar": ["ROOM"],
                "desligar": ["ROOM"], 
                "diminuir a temperatura": ["ROOM", "VALUE"],
                "aumentar a temperatura": ["ROOM", "VALUE"],
                "consultar a temperatura": ["ROOM"],
                "ajustar a temperatura": ["ROOM", "VALUE"]
            }
            
        except Exception as e:
            raise RuntimeError(f"Erro ao carregar o modelo: {e}")
    
    def process_message(self, text, state = None):
        if state:
            intent = state["intent"]
            entities = state["entities"]
            missing = state["missing"]

            if missing:
                next_entity = missing[0]
                entities[next_entity] = text
                missing = missing[1:]

                if missing:
                    next_entity = missing[0]
                    question = self.ask_for_missing_entity(next_entity)
                    return{
                        "status": "missing_info",
                        "intent": intent,
                        "missing_entities": missing,
                        "current_entities": entities,
                        "questions": question,
                        "next_step": "ask_first_missing"
                    }
                
            return{
                "status": "sucess", 
                "response": self.generate_response(intent, entities),
                "entities": entities
            }

        intent, entities = self.model_analysis(text)

        if not intent:
            return{
                "status": "error",
                "message": "Não entendi seu comando. Poderia reformular?"
            }
        
        missing = self.get_missing_entities(intent, entities)

        if missing:
            next_entity = missing[0]
            question = self.ask_for_missing_entity(next_entity)

            return{
                "status": "missing_info",
                "intent": intent,
                "missing_entities": missing,
                "current_entities": entities,
                "questions": question,
                "next_step": "ask_first_missing"
            }
        
        return{
            "status": "sucess",
            "response": self.generate_response(intent, entities),
            "entities": entities
        }

    '''Funcoes auxiliares'''
    
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

    def ask_for_missing_entity(self, missing_entity):
        questions = {
            "ROOM": "De qual sala você está falando?",
            "VALUE": "Quantos graus deseja ajustar?"
        }
        
        return questions.get(missing_entity)

    def generate_response(self, intent, entities):
        room = entities.get("ROOM", "[sala não informada]")
        value = entities.get("VALUE", "[valor não informado]")

        responses = {
            "ligar": f"Ok, ligando o ar condicionado da sala {room}.",
            "desligar": f"Ok, desligando o ar condicionado da sala {room}.",
            "diminuir a temperatura": f"Ok, diminuindo a temperatura da sala {room} em {value} graus.",
            "aumentar a temperatura": f"Ok, aumentando a temperatura da sala {room} em {value} graus.",
            "consultar a temperatura": f"Ok, consultarei a temperatura atual da sala {room}.",
            "ajustar a temperatura": f"Ok, ajustarei a temperatura da sala {room} em {value} graus.",
            "no_intent": "Comando não listado, em que posso te ajudar?"
        }

        print(responses.get(intent))
        return responses.get(intent)
