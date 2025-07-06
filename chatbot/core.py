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
    
    def process_message(self, text, state=None):
        if state and state.get("missing"):
            intent = state["intent"]
            entities = state["entities"]
            missing = state["missing"]

            # Preencher a próxima entidade faltante
            next_entity = missing[0]
            entities[next_entity] = text
            missing = missing[1:]

            if missing:
                question = self.ask_for_missing_entity(missing[0])
                return self.build_missing_response(intent, entities, missing, question)
            
        else:
            intent, entities = self.model_analysis(text)

            if not intent:
                return self.build_error("Não entendi seu comando. Poderia reformular?")
            missing = self.get_missing_entities(intent, entities)

            if missing:
                question = self.ask_for_missing_entity(missing[0])
                return self.build_missing_response(intent, entities, missing, question)

        # Com todas as entidades preenchidas, executa a ação
        return self.check_ac(intent, entities)

    '''Funcoes auxiliares'''
    def check_ac(self, intent, entities):
        
        process_result = self.process_intent(intent, entities)
        if isinstance(process_result, dict):  # Se retornar um erro
            return process_result

        # Comunicação MQTT
        if(intent in ["ligar", "desligar", "aumentar a temperatura", "diminuir a temperatura", "ajustar a temperatura"]):
            success = True #send_command(intent, entities)
            if not success:
                return self.build_error("Falha na comunicação com o dispositivo IoT")

        # Atualização de estado
        self.update_ac_state(intent, entities)

        # Resposta final
        return self.generate_response(intent, entities)

    def build_missing_response(self, intent, entities, missing, question):
        return {
            "status": "missing_info",
            "intent": intent,
            "missing_entities": missing,
            "current_entities": entities,
            "questions": question,
            "next_step": "ask_first_missing"
        }

    def build_error(self, message):
        return {
            "status": "error",
            "message": message
        }
    
    def generate_response(self, intent, entities):
        room = entities.get("ROOM", "[sala não informada]")
        value = entities.get("VALUE", "[valor não informado]")

        responses = {
            "ligar": f"Ok, ligando o ar condicionado da sala {room}.",
            "desligar": f"Ok, desligando o ar condicionado da sala {room}.",
            "diminuir a temperatura": f"Ok, diminuindo a temperatura da sala {room} para {value} graus.",
            "aumentar a temperatura": f"Ok, aumentando a temperatura da sala {room} para {value} graus.",
            "consultar a temperatura": f"A temperatura atual da sala {room} é {self.ac_states[room]['temperature']} graus.",
            "ajustar a temperatura": f"Ok, ajustarei a temperatura da sala {room} em {value} graus.",
            "no_intent": "Comando não listado, em que posso te ajudar?"
        }

        return{
            "status": "sucess", 
            "response": responses.get(intent),
            "entities": entities
        }

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

    def process_intent(self, intent, entities):
        room = entities.get("ROOM")
        
        # Verifica se o AC está desligado para operações que requerem ligado
        if intent in ["desligar", "diminuir a temperatura", "aumentar a temperatura", 
                    "ajustar a temperatura", "consultar a temperatura"]:
            if room not in self.ac_states or not self.ac_states[room].get("power", False):
                return self.build_error(f"O ar condicionado da sala {room} está desligado.")
            
            # Ajuste de temperatura
            if intent in ["diminuir a temperatura", "aumentar a temperatura"]:
                return self.adjust_temperature(intent, entities, room)
        
        # Verifica se o AC já está ligado para operação de ligar
        elif intent == "ligar":
            if self.ac_states.get(room, {}).get("power", False):
                return self.build_error(f"O ar condicionado da sala {room} já está ligado.")
            entities["VALUE"] = 20  # valor padrão para ligar o ar
        
        return True

    def adjust_temperature(self, intent, entities, room):
        current_temp = self.ac_states.get(room, {}).get("temperature")
        try:
            value = int(entities.get("VALUE", 0))
            if intent == "diminuir a temperatura":
                entities["VALUE"] = str(current_temp - value)
            else:
                entities["VALUE"] = str(current_temp + value)
        except ValueError:
            return self.build_error("Valor de temperatura inválido")

    def update_ac_state(self, intent, entities):
        room = entities.get("ROOM")
        if not room:
            return
        
        if room not in self.ac_states:
            self.ac_states[room] = {}
        
        if intent == "ligar":
            self.ac_states[room]["power"] = True
            self.ac_states[room]["temperature"] = entities["VALUE"]
        elif intent == "desligar":
            self.ac_states[room]["power"] = False
        elif intent in ["diminuir a temperatura", "aumentar a temperatura", "ajustar a temperatura"]:
            try:
                self.ac_states[room]["temperature"] = int(entities["VALUE"])
            except (ValueError, KeyError):
                pass

    def create_success_response(self, intent, entities):
        return {
            "status": "success",
            "response": self.generate_response(intent, entities),
            "entities": entities
        }

            
