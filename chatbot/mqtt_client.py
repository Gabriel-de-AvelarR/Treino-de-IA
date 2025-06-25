import paho.mqtt.client as mqtt
import json 
import time 

def send_command(intent, entities):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado ao broker com sucesso")
        else:
            print(f"Falha na conexao. Codigo de retorno: {rc}")
    
    def on_disconnect(client, userdata, rc):
        print("Desconectado do broker MQTT")
        
        if rc != 0:
            print("Reconectando automaticamente")
            try:
                client.reconnect()
            except Exception as e:
                print(f"Erro ao tentar reconectar {e}")

    def on_publish(client, userdata, mid):
        print("Mensagem publicada com sucesso")

    
    client = mqtt.Client() 
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    try:
        client.connect("andromeda.lasdpc.icmc.usp.br", 60102, 60)
        client.loop_start()

        room = entities.get("ROOM")
        if room:
            room = room.replace("sala", "").strip()
        
        intents_ligar = ["ligar", "ajustar a temperatura", "diminuir a temperatura", "aumentar a temperatura"]
        intents_desligar = ["desligar"]

        power = True if intent in intents_ligar else False if intent in intents_desligar else False
        
        payload = {
            "enviromentId": room,
            "deviceId": None,
            "mode": 0,
            "temperature": entities.get("VALUE", 20),
            "power": power
        }

        client.publish("aircon/command/", json.dumps(payload))

        client.loop(timeout = 2.0)
        client.loop_stop()
        client.disconnect()

        return True

    except Exception as e:
        print(f"Erro ao enviar comando MQTT: {e}")
        return False


#send_command("ligar", {"ROOM": "1"})
