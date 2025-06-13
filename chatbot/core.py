import spacy
from pathlib import Path
from mqtt_client import send_command

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

            self.ac_states = {} #Exemplo:{"1": {"power": False, "temperature": 22}}
            
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
        
        #VERIFICACOES LOGICAS 

        room = entities.get("ROOM")
        if intent in ["desligar", "diminuir a  temperatura", "aumentar a temperatura", "ajustar a temperatura", "consultar a temperatura"]:
            if room not in self.ac_states or self.ac_states[room].get("power", False):
                return{
                    "status": "error",
                    "message": f"O ar condicionado da sala {room} esta desligado."
                }
            
            elif intent in ["diminuir a  temperatura", "aumentar a temperatura"]:
                current_temp = self.ac_states.get(room, {}).get("temperature")
                try:
                    value = int(entities.get("VALUE", 0))
                    if intent == "diminuir a temperatura":
                        entities["VALUE"] = str(current_temp - value)
                    else:
                        entities["VALUE"] = str(current_temp + value)
                
                except ValueError:
                    return{
                        "status": "error",
                        "message": "Valor de temperatura invalido"
                    }
        
        if intent == "ligar":
            if self.ac_states[room].get("power", True):
                return{
                    "status": "error",
                    "message": f"O ar condicionado da sala {room} já esta ligado."

                }
            else:
                entities["VALUE"] = 20 #valor padrao para ligar o ar
        
        if intent == "no_intent":
            return{
                "status": "error",
                "message": "Comando não listado, em que posso te ajudar?"
                }


        #COMUNICACAO MQTT
        sucess = True #send_command(intent, entities)

        if not sucess:
            return{
                "status": "error",
                "message": "Falha na comunicação com o dispositivo IoT"
            }

        #ATUALIZACAO DA MAQUINA DE ESTADO DO AR
        else:
            if room:
                if room not in self.ac_states:
                    self.ac_states[room] = {}
                
                if intent == "ligar":
                    self.ac_states[room]["power"] = True
                    self.ac_states[room]["temperature"] = entities["VALUE"]
                elif intent == "desligar":
                    self.ac_states[room]["power"] = False
                elif intent in ["diminuir a  temperatura", "aumentar a temperatura", "ajustar a temperatura"]:
                    try:
                        self.ac_states[room]["temperature"] = int(entities["VALUE"])
                    except (ValueError, KeyError):
                        pass


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
            "consultar a temperatura": f"A temperatura atual da sala {room} é {self.ac_states[room]['temperature']} graus.",
            "ajustar a temperatura": f"Ok, ajustarei a temperatura da sala {room} em {value} graus."
        }
        
        return responses.get(intent)
